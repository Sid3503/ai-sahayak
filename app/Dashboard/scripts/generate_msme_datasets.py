import argparse
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

PROFILES = {
    "ramesh": {
        "store_id": "IND_RAMESH_101",
        "store_city": "Bhopal",
        "domain": "Pharmacy",
        "sku_prefix": "RM",
        "price_mult": 1.28,
        "qty_mult": 0.55,
        "margin_shift": 0.05,
        "festival_qty": 1.10,
    },
    "suresh": {
        "store_id": "IND_SURESH_202",
        "store_city": "Jaipur",
        "domain": "Hardware",
        "sku_prefix": "SR",
        "price_mult": 1.95,
        "qty_mult": 0.42,
        "margin_shift": 0.07,
        "festival_qty": 1.20,
    },
    "kanta": {
        "store_id": "IND_KANTA_303",
        "store_city": "Surat",
        "domain": "Boutique",
        "sku_prefix": "KT",
        "price_mult": 2.40,
        "qty_mult": 0.35,
        "margin_shift": 0.10,
        "festival_qty": 1.55,
    },
    "lakshmi": {
        "store_id": "IND_LAKSHMI_404",
        "store_city": "Hyderabad",
        "domain": "MobileAccessories",
        "sku_prefix": "LK",
        "price_mult": 1.65,
        "qty_mult": 0.48,
        "margin_shift": 0.08,
        "festival_qty": 1.28,
    },
}

PHARMA_ITEMS = [
    ("Paracetamol 650mg", "OTC"), ("Cough Syrup 100ml", "OTC"), ("Vitamin C 30 tabs", "Supplements"),
    ("ORS Sachet", "OTC"), ("Pain Relief Spray", "OTC"), ("Antacid Tablets", "OTC"),
    ("Digital Thermometer", "Devices"), ("Hand Sanitizer 500ml", "Hygiene"), ("Face Mask Pack", "Hygiene"),
    ("Bandage Roll", "FirstAid"), ("Cotton 100g", "FirstAid"), ("Antiseptic Liquid", "FirstAid"),
    ("BP Monitor", "Devices"), ("Calcium Tablets", "Supplements"), ("Iron Tablets", "Supplements"),
]
HARDWARE_ITEMS = [
    ("Cement 50kg", "Building"), ("Wall Putty 20kg", "Building"), ("PVC Pipe 1 inch", "Plumbing"),
    ("Steel Nails 1kg", "Fasteners"), ("Screw Set", "Fasteners"), ("Paint Roller", "Painting"),
    ("Emulsion Paint 10L", "Painting"), ("Drill Bit Set", "Tools"), ("Measuring Tape", "Tools"),
    ("LED Bulb 12W", "Electrical"), ("Switch Board", "Electrical"), ("Wire Coil", "Electrical"),
    ("Adhesive Sealant", "Chemicals"), ("Water Tap", "Plumbing"), ("Door Lock", "Fittings"),
]
BOUTIQUE_ITEMS = [
    ("Cotton Kurti", "Apparel"), ("Silk Saree", "Apparel"), ("Leggings", "Apparel"),
    ("Dupatta", "Apparel"), ("Blouse Piece", "Fabric"), ("Dress Material", "Fabric"),
    ("Stole", "Accessories"), ("Imitation Earrings", "Accessories"), ("Bangle Set", "Accessories"),
    ("Handbag", "Accessories"), ("Kids Frock", "Apparel"), ("Men Shirt", "Apparel"),
    ("Tailoring Thread", "Tailoring"), ("Lace Pack", "Tailoring"), ("Fabric Buttons", "Tailoring"),
]
MOBILE_ITEMS = [
    ("USB Cable", "Cables"), ("Fast Charger", "Chargers"), ("Earphones", "Audio"),
    ("Bluetooth Neckband", "Audio"), ("Power Bank 10000mAh", "Power"), ("Phone Cover", "Protection"),
    ("Tempered Glass", "Protection"), ("Car Charger", "Chargers"), ("OTG Adapter", "Cables"),
    ("Mobile Stand", "Accessories"), ("Memory Card 64GB", "Storage"), ("Pendrive 32GB", "Storage"),
    ("Smart Watch Strap", "Wearables"), ("Tripod", "Accessories"), ("Cleaning Kit", "Accessories"),
]

DOMAIN_ITEMS = {
    "Pharmacy": PHARMA_ITEMS,
    "Hardware": HARDWARE_ITEMS,
    "Boutique": BOUTIQUE_ITEMS,
    "MobileAccessories": MOBILE_ITEMS,
}


def stable_index(x: str, n: int) -> int:
    h = hashlib.sha1(x.encode("utf-8")).hexdigest()
    return int(h[:8], 16) % n


def build_sku_map(base_skus, profile):
    items = DOMAIN_ITEMS[profile["domain"]]
    mapping = {}
    for i, sku in enumerate(base_skus, start=1):
        name, cat = items[stable_index(sku, len(items))]
        mapping[sku] = (f"{profile['sku_prefix']}{i:03d}", name, cat)
    return mapping


def transform(df: pd.DataFrame, profile_name: str, profile: dict) -> pd.DataFrame:
    out = df.copy()
    sku_list = sorted(out["sku_id"].astype(str).unique())
    sku_map = build_sku_map(sku_list, profile)

    out["store_id"] = profile["store_id"]
    out["store_city"] = profile["store_city"]

    out["orig_sku"] = out["sku_id"].astype(str)
    out["sku_id"] = out["orig_sku"].map(lambda s: sku_map[s][0])
    out["item_name"] = out["orig_sku"].map(lambda s: sku_map[s][1])
    out["item_category"] = out["orig_sku"].map(lambda s: sku_map[s][2])

    out["selling_price"] = (pd.to_numeric(out["selling_price"], errors="coerce").fillna(0) * profile["price_mult"]).round(2)
    out["market_price"] = (out["selling_price"] * np.random.default_rng(42).uniform(0.95, 1.08, len(out))).round(2)

    q = pd.to_numeric(out["quantity_sold"], errors="coerce").fillna(0)
    fest = pd.to_numeric(out["is_festival_day"], errors="coerce").fillna(0)
    pre = pd.to_numeric(out["is_pre_festival_window"], errors="coerce").fillna(0)
    fmult = np.where((fest + pre) > 0, profile["festival_qty"], 1.0)
    out["quantity_sold"] = np.maximum(0, np.round(q * profile["qty_mult"] * fmult)).astype(int)

    out["discount_pct"] = np.where((fest + pre) > 0, np.maximum(pd.to_numeric(out["discount_pct"], errors="coerce").fillna(0), 0.04), pd.to_numeric(out["discount_pct"], errors="coerce").fillna(0))
    out["discount_pct"] = out["discount_pct"].clip(0, 0.2).round(4)
    out["effective_price"] = (out["selling_price"] * (1 - out["discount_pct"])).round(2)

    margin = (pd.to_numeric(out["gross_margin_pct"], errors="coerce").fillna(0.11) + profile["margin_shift"]).clip(0.09, 0.42)
    out["revenue"] = (out["quantity_sold"] * out["effective_price"]).round(2)
    out["cost_amt"] = (out["quantity_sold"] * out["effective_price"] * (1 - margin)).round(2)
    out["profit_amt"] = (out["revenue"] - out["cost_amt"]).round(2)
    out["gross_margin_pct"] = np.where(out["revenue"] > 0, (out["profit_amt"] / out["revenue"]).round(4), margin.round(4))

    out["reorder_point"] = np.maximum(5, np.round(out["quantity_sold"] * (2.6 if profile_name == "hardware" else 2.2))).astype(int)
    out["opening_stock"] = np.maximum(out["reorder_point"] + out["quantity_sold"], pd.to_numeric(out["opening_stock"], errors="coerce").fillna(0)).astype(int)
    out["stock_on_hand"] = np.maximum(0, out["opening_stock"] - out["quantity_sold"]).astype(int)
    out["needs_reorder"] = (out["stock_on_hand"] <= out["reorder_point"]).astype(int)
    out["empty_shelf_flag"] = ((out["stock_on_hand"] == 0) | (pd.to_numeric(out["empty_shelf_flag"], errors="coerce").fillna(0) > 0)).astype(int)

    out["record_id"] = out["date"].str.replace("-", "", regex=False) + "-" + out["sku_id"] + "-" + out["time_slot"]
    out["price_gap_pct"] = np.where(out["market_price"] > 0, ((out["effective_price"] - out["market_price"]) / out["market_price"]).round(4), 0.0)
    out["footfall_est"] = np.maximum(1, np.round(out["quantity_sold"] / np.maximum(1.1, pd.to_numeric(out["basket_size_est"], errors="coerce").fillna(1.6)))).astype(int)

    out.drop(columns=["orig_sku"], inplace=True)
    return out


def main():
    parser = argparse.ArgumentParser(description="Generate multiple MSME datasets from base retail dataset")
    parser.add_argument("--input", default="raju_kirana_2yr.csv")
    parser.add_argument("--out-dir", default=".")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for name, cfg in PROFILES.items():
        transformed = transform(df, name, cfg)
        out_path = out_dir / f"{name}_msme_2yr.csv"
        transformed.to_csv(out_path, index=False)
        print(f"Wrote {out_path} rows={len(transformed):,} skus={transformed['sku_id'].nunique()}")


if __name__ == "__main__":
    main()
