"""
Step 2: Initial exploration of the raw RURA ICT complaints dataset.

Goal: understand what we're dealing with BEFORE cleaning anything.
No transformations happen here — this is read-only profiling.
"""
import pandas as pd

RAW_PATH = "data/raw/rura_ict_complaints_raw.csv"

df = pd.read_csv(RAW_PATH)

print("=" * 60)
print("1. SHAPE")
print("=" * 60)
print(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")

print("\n" + "=" * 60)
print("2. COLUMN DTYPES (as pandas inferred them)")
print("=" * 60)
print(df.dtypes)

print("\n" + "=" * 60)
print("3. FIRST 5 ROWS")
print("=" * 60)
print(df.head())

print("\n" + "=" * 60)
print("4. MISSING VALUES PER COLUMN")
print("=" * 60)
missing = df.isna().sum()
missing_pct = (missing / len(df) * 100).round(1)
print(pd.DataFrame({"missing_count": missing, "missing_pct": missing_pct}))

print("\n" + "=" * 60)
print("5. DUPLICATE ROWS (exact duplicates across all columns)")
print("=" * 60)
print(f"Exact duplicate rows: {df.duplicated().sum()}")

print("\n" + "=" * 60)
print("6. DUPLICATE complaint_id (same ID, different data = data entry error)")
print("=" * 60)
dup_ids = df[df.duplicated(subset=['complaint_id'], keep=False)].sort_values('complaint_id')
print(f"Rows sharing a complaint_id with another row: {len(dup_ids)}")

print("\n" + "=" * 60)
print("7. UNIQUE VALUES IN CATEGORICAL-LOOKING COLUMNS")
print("=" * 60)
for col in ["province", "district", "operator", "service_type", "status", "customer_gender"]:
    print(f"\n--- {col} ({df[col].nunique(dropna=False)} unique values) ---")
    print(df[col].value_counts(dropna=False).head(15))

print("\n" + "=" * 60)
print("8. NUMERIC COLUMN RANGES (min/max reveal outliers)")
print("=" * 60)
for col in ["customer_age", "resolution_days", "satisfaction_score"]:
    numeric_col = pd.to_numeric(df[col], errors="coerce")
    print(f"\n--- {col} ---")
    print(f"min={numeric_col.min()}, max={numeric_col.max()}, "
          f"mean={numeric_col.mean():.1f}, non-numeric/NaN count={numeric_col.isna().sum()}")

print("\n" + "=" * 60)
print("9. date_received SAMPLE FORMATS (proves inconsistent formatting)")
print("=" * 60)
print(df["date_received"].sample(15, random_state=1).tolist())
