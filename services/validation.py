import math
import re


EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def validate_email(value):
    email = str(value or "").strip().lower()[:180]
    return email if EMAIL_RE.fullmatch(email) else None


def validate_prediction_input(p):
    try:
        drug=str(p.get("drug_name","")).strip()
        dosage=float(p.get("dosage_mg", p.get("dosage_strength", 0)))
        status=str(p.get("brand_status","")).strip()
        prices=[float(p.get(f"q{i}_price",0)) for i in range(1,5)]
    except (TypeError, ValueError):
        return None, "Dosage and quarterly prices must be numeric."
    if not 1 <= len(drug) <= 120: return None, "Enter a valid drug name."
    if not math.isfinite(dosage) or dosage <= 0 or dosage > 10000: return None, "Dosage must be between 0 and 10,000 mg."
    if status not in ("Generic","Brand"): return None, "Choose Brand or Generic."
    if any(not math.isfinite(x) or x <= 0 or x > 100000 for x in prices): return None, "Quarterly prices must be positive."
    return {"drug_name":drug,"dosage_strength":dosage,"brand_status":status,
            "q1_price":prices[0],"q2_price":prices[1],"q3_price":prices[2],"q4_price":prices[3]}, None
