"""
Demand forecasting for medicines (basic time-series / average-based).
Uses historical sales from Firestore (bills + sales) to predict future demand per medicine.
Helps pharmacies avoid overstocking.
"""
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Any, Optional


def _parse_sold_at(sold_at) -> Optional[date]:
    """Extract date from sold_at (ISO string or Firestore timestamp)."""
    if sold_at is None:
        return None
    if hasattr(sold_at, "date") and callable(getattr(sold_at, "date")):
        return sold_at.date()
    if isinstance(sold_at, date) and not isinstance(sold_at, datetime):
        return sold_at
    try:
        s = str(sold_at)[:10]
        return date.fromisoformat(s)
    except Exception:
        return None

def get_sales_by_day(db, pharmacy_email: str, medicine_name: Optional[str] = None, days_back: int = 90):
    """
    Aggregate quantity_sold by (date, medicine_name) from bills and sales.
    Returns: dict mapping (date_str, medicine_name) -> total_quantity_sold.
    """
    out = defaultdict(float)
    if not db:
        return dict(out)

    # From bills
    for doc in db.collection("bills").where("pharmacy_email", "==", pharmacy_email).stream():
        d = doc.to_dict()
        sold_at = d.get("sold_at")
        day = _parse_sold_at(sold_at)
        if not day:
            continue
        if (date.today() - day).days > days_back:
            continue
        name = (d.get("medicine_name") or "").strip()
        if medicine_name and name.lower() != medicine_name.lower():
            continue
        qty = int(d.get("quantity_sold") or 0)
        out[(day.isoformat(), name)] += qty

    # From sales (quick_sell)
    for doc in db.collection("sales").where("pharmacy_email", "==", pharmacy_email).stream():
        d = doc.to_dict()
        sold_at = d.get("sold_at")
        day = _parse_sold_at(sold_at)
        if not day:
            continue
        if (date.today() - day).days > days_back:
            continue
        name = (d.get("medicine_name") or "").strip()
        if medicine_name and name.lower() != medicine_name.lower():
            continue
        qty = int(d.get("quantity_sold") or 0)
        out[(day.isoformat(), name)] += qty

    return dict(out)


def forecast_demand(db, pharmacy_email: str, horizon_days: int = 30, history_days: int = 60):
    """
    Predict demand per medicine for the next horizon_days.
    Uses average daily demand over the last history_days (basic time-series).
    Returns: list of {"medicine_name": str, "daily_avg": float, "forecast_total": float, "forecast_per_day": list}.
    """
    sales = get_sales_by_day(db, pharmacy_email, medicine_name=None, days_back=history_days)
    # Aggregate by medicine: list of (date, qty) then daily average
    by_medicine = defaultdict(list)  # medicine_name -> [(date_str, qty), ...]
    for (date_str, name), qty in sales.items():
        if not name:
            continue
        by_medicine[name].append((date_str, qty))

    result = []
    for name, points in by_medicine.items():
        if not points:
            continue
        total_qty = sum(p[1] for p in points)
        days_with_sales = len(set(p[0] for p in points))
        if days_with_sales == 0:
            continue
        daily_avg = total_qty / max(days_with_sales, 1)
        forecast_total = daily_avg * horizon_days
        forecast_per_day = [round(daily_avg, 2)] * horizon_days
        result.append({
            "medicine_name": name,
            "daily_avg": round(daily_avg, 2),
            "forecast_total": round(forecast_total, 2),
            "forecast_per_day": forecast_per_day,
            "history_days": days_with_sales,
            "history_total": total_qty,
        })
    result.sort(key=lambda x: -x["forecast_total"])
    return result
