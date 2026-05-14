import pandas as pd
df = pd.read_csv("data/raw/scopus/scopus_all_7181.csv", low_memory=False)
print("--- First 3 Authors values ---")
for i in range(3):
    val = df["Authors"].iloc[i]
    print(f"Row {i}: {repr(val)}")
print()
print("--- Separator stats ---")
n = len(df)
n_semi = df["Authors"].astype(str).str.contains(";").sum()
n_comma = df["Authors"].astype(str).str.contains(",").sum()
print(f"Records with ';' in Authors: {n_semi}/{n} ({100*n_semi/n:.1f}%)")
print(f"Records with ',' in Authors: {n_comma}/{n} ({100*n_comma/n:.1f}%)")
