import argparse
import json
from pathlib import Path

import pandas as pd


def build_deepar_jsonl(input_csv: str, output_jsonl: str):
    df = pd.read_csv(input_csv, low_memory=False)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date", "sku_id"])

    if "units_sold" not in df.columns and "quantity_sold" in df.columns:
        df["units_sold"] = pd.to_numeric(df["quantity_sold"], errors="coerce")
    if "promo_depth_pct" not in df.columns and "discount_pct" in df.columns:
        df["promo_depth_pct"] = pd.to_numeric(df["discount_pct"], errors="coerce")
    if "festival_lift" not in df.columns and "festival_impact" in df.columns:
        df["festival_lift"] = pd.to_numeric(df["festival_impact"], errors="coerce")
    if "local_price" not in df.columns and "selling_price" in df.columns:
        df["local_price"] = pd.to_numeric(df["selling_price"], errors="coerce")

    daily = (
        df.groupby(["sku_id", "date"], as_index=False)
        .agg(
            target=("units_sold", "sum"),
            promo_depth_pct=("promo_depth_pct", "mean"),
            festival_lift=("festival_lift", "max"),
            local_price=("local_price", "mean"),
        )
        .sort_values(["sku_id", "date"])
    )

    Path(output_jsonl).parent.mkdir(parents=True, exist_ok=True)
    sku_to_cat = {sku: idx for idx, sku in enumerate(sorted(daily["sku_id"].astype(str).unique().tolist()))}

    with open(output_jsonl, "w", encoding="utf-8") as f:
        for sku, sdf in daily.groupby("sku_id"):
            sdf = sdf.sort_values("date")
            target = [float(x) for x in sdf["target"].fillna(0).tolist()]
            promo = [float(x) for x in sdf["promo_depth_pct"].fillna(0).tolist()]
            festival = [float(x) for x in sdf["festival_lift"].fillna(1).tolist()]
            price = [float(x) for x in sdf["local_price"].ffill().bfill().fillna(0).tolist()]
            start = str(sdf["date"].min().date())
            record = {
                "start": start,
                "target": target,
                "cat": [int(sku_to_cat[str(sku)])],
                "dynamic_feat": [promo, festival, price],
            }
            f.write(json.dumps(record) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Prepare DeepAR JSONL training data from AI Sahayak CSV")
    parser.add_argument("--input", required=True, help="Input CSV path")
    parser.add_argument("--output", required=True, help="Output JSONL path")
    args = parser.parse_args()
    build_deepar_jsonl(args.input, args.output)
    print(f"DeepAR dataset written to {args.output}")


if __name__ == "__main__":
    main()
