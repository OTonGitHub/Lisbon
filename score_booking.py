#!/usr/bin/env python
"""Score a single new hotel booking for cancellation risk.

Usage:
    python score_booking.py booking.json

Input: a JSON file with the fields available at booking time (see booking.json
for a complete sample). Output: the predicted cancellation probability and the
decision at the operating threshold chosen in the notebook.

The script reuses the fitted pipeline from `artifacts/model.joblib` (produced by
lisbon.ipynb) and rebuilds the guest-history features from the artefact lookup
tables with the same time-aware logic used in training: only bookings *made*
before this one count, and only cancellations *known* before this one count.
"""
import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

ART = Path(__file__).resolve().parent / "artifacts"

# JSON field -> training column for the fields passed straight through
FIELD_MAP = {
    "adults": "Adults",
    "children": "Children",
    "babies": "Babies",
    "adr": "ADR",
    "stays_in_weekend_nights": "StaysInWeekendNights",
    "stays_in_week_nights": "StaysInWeekNights",
    "required_car_parking_spaces": "RequiredCarParkingSpaces",
    "total_of_special_requests": "TotalOfSpecialRequests",
    "hotel": "hotel",
    "meal": "Meal",
    "country": "Country",
    "market_segment": "MarketSegment",
    "distribution_channel": "DistributionChannel",
    "reserved_room_type": "ReservedRoomType",
    "deposit_type": "DepositType",
    "customer_type": "CustomerType",
}


def guest_history(guest_id: str, booking_date: pd.Timestamp) -> dict:
    """Time-aware history: what was known about this guest before booking_date."""
    hist = pd.read_csv(ART / "booking_history.csv",
                       parse_dates=["booking_date", "outcome_known"])
    mine = hist[hist.GuestID == guest_id]
    prior = mine[mine.booking_date < booking_date]
    resolved = mine[(mine.outcome_known < booking_date)]
    n_cancelled = int((resolved.IsCanceled == 1).sum())
    return {
        "prior_bookings": float(len(prior)),
        "prior_cancellations": float(n_cancelled),
        "prior_cancel_rate": n_cancelled / len(resolved) if len(resolved) else 0.0,
    }


def build_feature_row(rec: dict, meta: dict) -> pd.DataFrame:
    booking_date = pd.Timestamp(rec["booking_date"])
    arrival_date = pd.Timestamp(rec["arrival_date"])
    if arrival_date < booking_date:
        raise ValueError("arrival_date is before booking_date")

    row = {col: rec[field] for field, col in FIELD_MAP.items()}

    # the same normalisations applied in cleaning (Part 2 of the notebook)
    for c in ["hotel", "Meal", "Country", "MarketSegment", "DistributionChannel",
              "ReservedRoomType", "DepositType", "CustomerType"]:
        row[c] = str(row[c]).strip()
    row["Country"] = row["Country"].upper().replace("CN", "CHN") if len(row["Country"]) == 2 else row["Country"].upper()
    if row["Meal"] == "Undefined":
        row["Meal"] = "SC"

    # derived at booking time
    row["LeadTime"] = (arrival_date - booking_date).days
    row["arrival_month"] = str(arrival_date.month)
    row["has_agent"] = int(rec.get("agent") is not None)
    row["has_company"] = int(rec.get("company") is not None)
    # a brand-new booking normally has no payment events yet; allow declines if known
    row["n_card_declined"] = float(rec.get("card_declines_so_far", 0))

    # lookups
    guests = pd.read_csv(ART / "guest_lookup.csv")
    age = guests.loc[guests.guest_id == rec["guest_id"], "age"]
    row["age"] = float(age.iloc[0]) if len(age) and pd.notna(age.iloc[0]) else np.nan
    row |= guest_history(rec["guest_id"], booking_date)

    cols = meta["num_features"] + meta["cat_features"]
    return pd.DataFrame([row])[cols]


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    rec = json.loads(Path(sys.argv[1]).read_text())
    meta = json.loads((ART / "metadata.json").read_text())
    model = joblib.load(ART / "model.joblib")

    X = build_feature_row(rec, meta)
    prob = float(model.predict_proba(X)[0, 1])
    threshold = meta["threshold"]
    result = {
        "booking": {"guest_id": rec["guest_id"], "hotel": rec["hotel"],
                    "arrival_date": rec["arrival_date"],
                    "lead_time_days": int(X.LeadTime.iloc[0])},
        "guest_history_used": {k: X[k].iloc[0] for k in
                               ["prior_bookings", "prior_cancellations", "prior_cancel_rate"]},
        "cancellation_probability": round(prob, 4),
        "threshold": threshold,
        "decision": "FLAG - high cancellation risk" if prob >= threshold else "OK - low risk",
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
