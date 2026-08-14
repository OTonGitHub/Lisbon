#!/usr/bin/env python
"""Score a single new hotel booking for cancellation risk.

Usage:
    python score_booking.py booking.json

Input: a JSON file with the fields available at booking time (see booking.json
for a complete sample). Output: the predicted cancellation probability and the
decision at the threshold chosen in the notebook.

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

ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"

# JSON field -> training column, for the fields that pass straight through
FIELD_TO_COLUMN = {
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

CATEGORICAL_COLUMNS = ["hotel", "Meal", "Country", "MarketSegment",
                       "DistributionChannel", "ReservedRoomType",
                       "DepositType", "CustomerType"]


def look_up_guest_age(guest_id: str) -> float:
    guests = pd.read_csv(ARTIFACT_DIR / "guest_lookup.csv")
    age = guests.loc[guests.guest_id == guest_id, "age"]
    if len(age) == 0 or pd.isna(age.iloc[0]):
        return np.nan   # unknown guest or unknown age: the pipeline handles missing
    return float(age.iloc[0])


def look_up_guest_history(guest_id: str, booking_date: pd.Timestamp) -> dict:
    """Time-aware history: what was known about this guest before booking_date."""
    history = pd.read_csv(ARTIFACT_DIR / "booking_history.csv",
                          parse_dates=["booking_date", "outcome_known_date"])
    guest_history = history[history.GuestID == guest_id]
    made_before = guest_history[guest_history.booking_date < booking_date]
    resolved_before = guest_history[guest_history.outcome_known_date < booking_date]
    n_cancelled = int((resolved_before.IsCanceled == 1).sum())
    if len(resolved_before) > 0:
        cancel_rate = n_cancelled / len(resolved_before)
    else:
        cancel_rate = 0.0
    return {
        "prior_bookings": float(len(made_before)),
        "prior_cancellations": float(n_cancelled),
        "prior_cancel_rate": cancel_rate,
    }


def build_feature_row(record: dict, metadata: dict) -> pd.DataFrame:
    booking_date = pd.Timestamp(record["booking_date"])
    arrival_date = pd.Timestamp(record["arrival_date"])
    if arrival_date < booking_date:
        raise ValueError("arrival_date is before booking_date")

    row = {column: record[field] for field, column in FIELD_TO_COLUMN.items()}

    # the same normalisations applied during cleaning (Part 2 of the notebook)
    for column in CATEGORICAL_COLUMNS:
        row[column] = str(row[column]).strip()
    row["Country"] = row["Country"].upper()
    if row["Country"] == "CN":
        row["Country"] = "CHN"
    if row["Meal"] == "Undefined":
        row["Meal"] = "SC"

    # fields derived at booking time
    row["LeadTime"] = (arrival_date - booking_date).days
    row["arrival_month"] = str(arrival_date.month)
    row["has_agent"] = int(record.get("agent") is not None)
    row["has_company"] = int(record.get("company") is not None)
    # a brand-new booking normally has no payment events yet; allow declines if known
    row["n_card_declined"] = float(record.get("card_declines_so_far", 0))

    # lookups from the artefact tables
    row["age"] = look_up_guest_age(record["guest_id"])
    history = look_up_guest_history(record["guest_id"], booking_date)
    row["prior_bookings"] = history["prior_bookings"]
    row["prior_cancellations"] = history["prior_cancellations"]
    row["prior_cancel_rate"] = history["prior_cancel_rate"]

    feature_order = metadata["num_features"] + metadata["cat_features"]
    return pd.DataFrame([row])[feature_order]


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    record = json.loads(Path(sys.argv[1]).read_text())
    metadata = json.loads((ARTIFACT_DIR / "metadata.json").read_text())
    model = joblib.load(ARTIFACT_DIR / "model.joblib")

    features = build_feature_row(record, metadata)
    probability = float(model.predict_proba(features)[0, 1])
    threshold = metadata["threshold"]
    if probability >= threshold:
        decision = "FLAG - high cancellation risk"
    else:
        decision = "OK - low risk"

    result = {
        "booking": {
            "guest_id": record["guest_id"],
            "hotel": record["hotel"],
            "arrival_date": record["arrival_date"],
            "lead_time_days": int(features.LeadTime.iloc[0]),
        },
        "guest_history_used": {
            "prior_bookings": features.prior_bookings.iloc[0],
            "prior_cancellations": features.prior_cancellations.iloc[0],
            "prior_cancel_rate": features.prior_cancel_rate.iloc[0],
        },
        "cancellation_probability": round(probability, 4),
        "threshold": threshold,
        "decision": decision,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
