"""
Generates a synthetic, intentionally messy raw dataset modeled on
RURA's ICT Department: consumer complaints about telecom, mobile
money, and internet services in Rwanda.

This is synthetic data for learning purposes only, not real RURA
records. Messiness is injected on purpose (missing values, typos,
inconsistent casing/formats, duplicates, outliers) to practice a
real data-cleaning workflow.
"""
import csv
import random
from datetime import date, timedelta

random.seed(42)

PROVINCES_DISTRICTS = {
    "Kigali City": ["Gasabo", "Kicukiro", "Nyarugenge"],
    "Northern Province": ["Musanze", "Burera", "Gicumbi", "Rulindo", "Gakenke"],
    "Southern Province": ["Huye", "Nyanza", "Muhanga", "Kamonyi", "Gisagara", "Nyamagabe", "Nyaruguru", "Ruhango"],
    "Eastern Province": ["Rwamagana", "Kayonza", "Ngoma", "Kirehe", "Nyagatare", "Gatsibo", "Bugesera"],
    "Western Province": ["Rubavu", "Rusizi", "Nyamasheke", "Karongi", "Rutsiro", "Ngororero", "Nyabihu"],
}

# Intentional inconsistent spellings/casing for a few districts (real-world messiness)
DISTRICT_VARIANTS = {
    "Gasabo": ["Gasabo", "gasabo", "GASABO", "Gasabo "],
    "Musanze": ["Musanze", "musanze", "Musanze District"],
    "Huye": ["Huye", "huye", "Huye "],
    "Rubavu": ["Rubavu", "rubavu", "Rubavu "],
    "Nyagatare": ["Nyagatare", "Nyagatre", "nyagatare"],
}

OPERATORS = [
    ("MTN Rwanda", ["MTN Rwanda", "MTN", "mtn rwanda", "MTN RWANDA", "M.T.N Rwanda"]),
    ("Airtel Rwanda", ["Airtel Rwanda", "Airtel", "airtel rwanda", "AIRTEL"]),
    ("Liquid Telecom Rwanda", ["Liquid Telecom Rwanda", "Liquid Telecom", "liquid telecom"]),
    ("Broadband Systems Corporation", ["Broadband Systems Corporation", "BSC", "broadband systems"]),
    ("Onatracom/REG-ICT", ["REG-ICT", "REG ICT", None]),  # occasionally missing operator
]

SERVICE_TYPES = ["Mobile Voice", "Mobile Data/Internet", "Mobile Money", "Fixed Internet", "SMS", "Fixed Voice"]

COMPLAINT_CATEGORIES = [
    "Network Outage",
    "Poor Network Quality",
    "Billing Dispute",
    "Mobile Money Transaction Failure",
    "Mobile Money Fraud/Scam",
    "SIM Registration Issue",
    "Data Bundle Deduction Issue",
    "Unsolicited SMS/Spam",
    "Customer Care Unresponsive",
    "Slow Internet Speed",
    "Service Activation Delay",
]

CHANNELS = ["Call Center", "Walk-in", "Email", "Social Media", "USSD", "Web Portal"]

STATUS_VARIANTS = ["Open", "open", "OPEN", "Closed", "closed", "Resolved", "resolved", "Pending", "pending ", "In Progress"]

GENDER_VARIANTS = ["M", "F", "Male", "Female", "male", "female", "", "Other"]

DESCRIPTIONS = [
    "Customer reports repeated call drops in {district}.",
    "Complainant charged twice for the same data bundle.",
    "No network coverage since yesterday evening.",
    "Mobile money transfer deducted but recipient did not receive funds.",
    "Received suspicious SMS asking for mobile money PIN.",
    "SIM card registered under wrong national ID.",
    "Internet speed far below advertised package.",
    "Customer care line not answering after multiple attempts.",
    "Received unsolicited promotional SMS despite opt-out request.",
    "Delay of over a week in activating new fixed internet line.",
    "Billed for services not subscribed to.",
    "",  # some blank descriptions
    None,
]


def random_date(start_year=2023, end_year=2024):
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    delta_days = (end - start).days
    d = start + timedelta(days=random.randint(0, delta_days))
    fmt = random.choice(["%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y", "%d-%b-%Y"])
    return d.strftime(fmt)


def pick_district():
    province = random.choice(list(PROVINCES_DISTRICTS.keys()))
    district = random.choice(PROVINCES_DISTRICTS[province])
    if district in DISTRICT_VARIANTS and random.random() < 0.35:
        district = random.choice(DISTRICT_VARIANTS[district])
    return province, district


def pick_operator():
    canonical, variants = random.choice(OPERATORS)
    return random.choice(variants)


def pick_age():
    r = random.random()
    if r < 0.08:
        return ""  # missing
    if r < 0.10:
        return random.choice([-5, 0, 150, 210])  # bad outliers
    return random.randint(16, 85)


def pick_satisfaction():
    r = random.random()
    if r < 0.30:
        return ""  # often missing, only collected on closed tickets
    if r < 0.33:
        return random.choice([0, 6, -1])  # out-of-range outliers
    return random.randint(1, 5)


def pick_resolution_days(status):
    if status.strip().lower() in ("open", "pending"):
        return ""
    r = random.random()
    if r < 0.05:
        return random.choice([-2, 999])  # bad outliers
    return random.randint(0, 30)


def make_row(complaint_id):
    province, district = pick_district()
    operator = pick_operator()
    service_type = random.choice(SERVICE_TYPES)
    category = random.choice(COMPLAINT_CATEGORIES)
    channel = random.choice(CHANNELS)
    status = random.choice(STATUS_VARIANTS)
    desc_template = random.choice(DESCRIPTIONS)
    description = desc_template.format(district=district) if desc_template and "{district}" in str(desc_template) else desc_template

    return {
        "complaint_id": complaint_id,
        "date_received": random_date(),
        "province": province,
        "district": district,
        "operator": operator if operator else "",
        "service_type": service_type,
        "complaint_category": category,
        "channel": channel,
        "description": description if description is not None else "",
        "customer_age": pick_age(),
        "customer_gender": random.choice(GENDER_VARIANTS),
        "status": status,
        "resolution_days": pick_resolution_days(status),
        "satisfaction_score": pick_satisfaction(),
    }


def main():
    n_rows = 900
    rows = []
    for i in range(1, n_rows + 1):
        rows.append(make_row(f"RURA-ICT-{i:05d}"))

    # Inject exact duplicate rows (common real-world issue: double submission)
    duplicates = random.sample(rows, 25)
    rows.extend(duplicates)

    # Inject a few rows with duplicated complaint_id but different content (data entry error)
    for i in range(5):
        dup = make_row(rows[random.randint(0, n_rows - 1)]["complaint_id"])
        rows.append(dup)

    random.shuffle(rows)

    fieldnames = list(rows[0].keys())
    out_path = "/home/user/self-pace/data/raw/rura_ict_complaints_raw.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {out_path}")


if __name__ == "__main__":
    main()
