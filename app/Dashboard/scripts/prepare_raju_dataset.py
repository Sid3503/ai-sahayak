#!/usr/bin/env python3
import argparse
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd


REQUIRED_COLUMNS = [
    "date",
    "sku_id",
    "category",
    "channel",
    "region",
    "competitor_price",
    "final_price",
    "units_sold",
    "inventory_level",
    "is_stockout",
    "margin",
    "festival_lift",
]

FESTIVALS = {
    "2024-01-15": "Makar Sankranti",
    "2024-01-26": "Republic Day",
    "2024-03-08": "Maha Shivratri",
    "2024-03-25": "Holi",
    "2024-04-11": "Eid al-Fitr",
    "2024-08-19": "Raksha Bandhan",
    "2024-08-26": "Janmashtami",
    "2024-10-03": "Navratri Start",
    "2024-10-12": "Dussehra",
    "2024-11-01": "Diwali",
    "2024-11-07": "Chhath Puja",
    "2024-12-25": "Christmas",
    "2025-01-14": "Makar Sankranti",
    "2025-01-26": "Republic Day",
    "2025-03-14": "Holi",
    "2025-03-31": "Eid al-Fitr",
    "2025-08-09": "Raksha Bandhan",
    "2025-08-16": "Janmashtami",
    "2025-09-22": "Navratri Start",
    "2025-10-02": "Dussehra",
    "2025-10-20": "Diwali",
    "2025-10-27": "Chhath Puja",
    "2025-12-25": "Christmas",
}

TIME_SLOTS = [
    ("07-09", 7, 0.06),
    ("09-11", 9, 0.10),
    ("11-13", 11, 0.13),
    ("13-15", 13, 0.14),
    ("15-17", 15, 0.15),
    ("17-19", 17, 0.17),
    ("19-21", 19, 0.18),
    ("21-23", 21, 0.07),
]

PRODUCT_CATALOG = [
    {"item_name": "Wheat Atta 5kg", "category": "Staples", "base_price": 245, "margin_pct": 0.10},
    {"item_name": "Wheat Atta 10kg", "category": "Staples", "base_price": 475, "margin_pct": 0.10},
    {"item_name": "Basmati Rice 1kg", "category": "Staples", "base_price": 110, "margin_pct": 0.11},
    {"item_name": "Basmati Rice 5kg", "category": "Staples", "base_price": 520, "margin_pct": 0.11},
    {"item_name": "Sona Masoori Rice 5kg", "category": "Staples", "base_price": 420, "margin_pct": 0.10},
    {"item_name": "Poha 1kg", "category": "Staples", "base_price": 62, "margin_pct": 0.12},
    {"item_name": "Sugar 1kg", "category": "Staples", "base_price": 45, "margin_pct": 0.09},
    {"item_name": "Salt 1kg", "category": "Staples", "base_price": 24, "margin_pct": 0.08},
    {"item_name": "Iodized Salt 1kg", "category": "Staples", "base_price": 27, "margin_pct": 0.08},
    {"item_name": "Jaggery 1kg", "category": "Staples", "base_price": 62, "margin_pct": 0.12},
    {"item_name": "Tur Dal 1kg", "category": "Pulses", "base_price": 140, "margin_pct": 0.11},
    {"item_name": "Chana Dal 1kg", "category": "Pulses", "base_price": 92, "margin_pct": 0.11},
    {"item_name": "Moong Dal 1kg", "category": "Pulses", "base_price": 126, "margin_pct": 0.12},
    {"item_name": "Masoor Dal 1kg", "category": "Pulses", "base_price": 110, "margin_pct": 0.11},
    {"item_name": "Rajma 1kg", "category": "Pulses", "base_price": 145, "margin_pct": 0.12},
    {"item_name": "Kabuli Chana 1kg", "category": "Pulses", "base_price": 135, "margin_pct": 0.12},
    {"item_name": "Mustard Oil 1L", "category": "Oils", "base_price": 175, "margin_pct": 0.10},
    {"item_name": "Mustard Oil 5L", "category": "Oils", "base_price": 840, "margin_pct": 0.09},
    {"item_name": "Refined Oil 1L", "category": "Oils", "base_price": 160, "margin_pct": 0.10},
    {"item_name": "Refined Oil 5L", "category": "Oils", "base_price": 760, "margin_pct": 0.09},
    {"item_name": "Groundnut Oil 1L", "category": "Oils", "base_price": 195, "margin_pct": 0.10},
    {"item_name": "Ghee 500ml", "category": "Oils", "base_price": 335, "margin_pct": 0.12},
    {"item_name": "Ghee 1L", "category": "Oils", "base_price": 640, "margin_pct": 0.11},
    {"item_name": "Vanaspati 1L", "category": "Oils", "base_price": 145, "margin_pct": 0.10},
    {"item_name": "Tea 250g", "category": "Beverages", "base_price": 145, "margin_pct": 0.13},
    {"item_name": "Tea 500g", "category": "Beverages", "base_price": 280, "margin_pct": 0.13},
    {"item_name": "Instant Coffee 50g", "category": "Beverages", "base_price": 165, "margin_pct": 0.15},
    {"item_name": "Milk Powder 500g", "category": "Beverages", "base_price": 295, "margin_pct": 0.13},
    {"item_name": "Glucose Biscuits", "category": "Snacks", "base_price": 10, "margin_pct": 0.16},
    {"item_name": "Cream Biscuits", "category": "Snacks", "base_price": 30, "margin_pct": 0.18},
    {"item_name": "Salted Namkeen 200g", "category": "Snacks", "base_price": 55, "margin_pct": 0.17},
    {"item_name": "Bhujia 400g", "category": "Snacks", "base_price": 120, "margin_pct": 0.17},
    {"item_name": "Potato Chips 90g", "category": "Snacks", "base_price": 25, "margin_pct": 0.18},
    {"item_name": "Rusk 300g", "category": "Snacks", "base_price": 45, "margin_pct": 0.16},
    {"item_name": "Maggi Masala 70g", "category": "Instant Food", "base_price": 14, "margin_pct": 0.15},
    {"item_name": "Instant Noodles Cup", "category": "Instant Food", "base_price": 45, "margin_pct": 0.16},
    {"item_name": "Pasta 500g", "category": "Instant Food", "base_price": 75, "margin_pct": 0.15},
    {"item_name": "Suji 1kg", "category": "Instant Food", "base_price": 48, "margin_pct": 0.12},
    {"item_name": "Besan 1kg", "category": "Cooking", "base_price": 88, "margin_pct": 0.12},
    {"item_name": "Maida 1kg", "category": "Cooking", "base_price": 52, "margin_pct": 0.11},
    {"item_name": "Corn Flour 500g", "category": "Cooking", "base_price": 46, "margin_pct": 0.13},
    {"item_name": "Turmeric Powder 200g", "category": "Spices", "base_price": 62, "margin_pct": 0.18},
    {"item_name": "Red Chilli Powder 200g", "category": "Spices", "base_price": 72, "margin_pct": 0.18},
    {"item_name": "Coriander Powder 200g", "category": "Spices", "base_price": 58, "margin_pct": 0.17},
    {"item_name": "Garam Masala 100g", "category": "Spices", "base_price": 65, "margin_pct": 0.19},
    {"item_name": "Cumin Seeds 200g", "category": "Spices", "base_price": 95, "margin_pct": 0.16},
    {"item_name": "Black Pepper 100g", "category": "Spices", "base_price": 120, "margin_pct": 0.17},
    {"item_name": "Toor Papad 200g", "category": "Snacks", "base_price": 75, "margin_pct": 0.16},
    {"item_name": "Pickle Mango 500g", "category": "Condiments", "base_price": 95, "margin_pct": 0.17},
    {"item_name": "Tomato Ketchup 500g", "category": "Condiments", "base_price": 105, "margin_pct": 0.16},
    {"item_name": "Soy Sauce 200ml", "category": "Condiments", "base_price": 70, "margin_pct": 0.18},
    {"item_name": "Green Chutney 200g", "category": "Condiments", "base_price": 45, "margin_pct": 0.17},
    {"item_name": "Dry Fruits Mix 250g", "category": "Premium", "base_price": 210, "margin_pct": 0.16},
    {"item_name": "Almonds 250g", "category": "Premium", "base_price": 260, "margin_pct": 0.15},
    {"item_name": "Cashews 250g", "category": "Premium", "base_price": 285, "margin_pct": 0.15},
    {"item_name": "Raisins 250g", "category": "Premium", "base_price": 120, "margin_pct": 0.15},
    {"item_name": "Vermicelli 500g", "category": "Festive", "base_price": 42, "margin_pct": 0.14},
    {"item_name": "Gulal Color Packet", "category": "Festive", "base_price": 35, "margin_pct": 0.20},
    {"item_name": "Diya Pack 20pc", "category": "Festive", "base_price": 65, "margin_pct": 0.22},
    {"item_name": "Cotton Wick 100pc", "category": "Festive", "base_price": 30, "margin_pct": 0.19},
]

assert len(PRODUCT_CATALOG) >= 60


@dataclass
class Config:
    input_csv: Path
    output_csv: Path
    region: str
    channel: str
    start_date: str
    end_date: str
    chunksize: int
    sku_count: int


def stable_seed(*parts: str) -> int:
    joined = "|".join(parts)
    return int(hashlib.sha1(joined.encode("utf-8")).hexdigest()[:8], 16)


def validate_columns(input_csv: Path) -> None:
    cols = pd.read_csv(input_csv, nrows=1, encoding="cp1252").columns.tolist()
    missing = sorted(set(REQUIRED_COLUMNS) - set(cols))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def ingest_base(cfg: Config) -> pd.DataFrame:
    frames: List[pd.DataFrame] = []
    usecols = REQUIRED_COLUMNS

    for chunk in pd.read_csv(
        cfg.input_csv,
        usecols=usecols,
        chunksize=cfg.chunksize,
        parse_dates=["date"],
        encoding="cp1252",
    ):
        f = chunk[(chunk["region"] == cfg.region) & (chunk["channel"] == cfg.channel)].copy()
        if f.empty:
            continue
        f["units_sold"] = pd.to_numeric(f["units_sold"], errors="coerce").fillna(0)
        f["final_price"] = pd.to_numeric(f["final_price"], errors="coerce").fillna(0)
        f["competitor_price"] = pd.to_numeric(f["competitor_price"], errors="coerce").fillna(0)
        f["inventory_level"] = pd.to_numeric(f["inventory_level"], errors="coerce").fillna(0)
        f["margin"] = pd.to_numeric(f["margin"], errors="coerce").fillna(0)
        f["festival_lift"] = pd.to_numeric(f["festival_lift"], errors="coerce").fillna(1)
        f["is_stockout"] = pd.to_numeric(f["is_stockout"], errors="coerce").fillna(0)

        f["sell_w"] = f["final_price"] * f["units_sold"]
        f["mkt_w"] = f["competitor_price"] * f["units_sold"]

        frames.append(
            f[
                [
                    "date",
                    "sku_id",
                    "category",
                    "units_sold",
                    "inventory_level",
                    "is_stockout",
                    "margin",
                    "festival_lift",
                    "sell_w",
                    "mkt_w",
                ]
            ]
        )

    if not frames:
        raise ValueError("No data after region/channel filtering.")

    d = pd.concat(frames, ignore_index=True)
    agg = (
        d.groupby(["date", "sku_id", "category"], as_index=False)
        .agg(
            quantity_sold=("units_sold", "sum"),
            stock_on_hand=("inventory_level", "sum"),
            empty_shelf_flag=("is_stockout", "max"),
            profit_amt=("margin", "sum"),
            festival_impact=("festival_lift", "max"),
            sell_w=("sell_w", "sum"),
            mkt_w=("mkt_w", "sum"),
        )
    )
    q = agg["quantity_sold"].replace(0, np.nan)
    agg["selling_price"] = (agg["sell_w"] / q).fillna(0)
    agg["market_price"] = (agg["mkt_w"] / q).fillna(0)
    agg.drop(columns=["sell_w", "mkt_w"], inplace=True)
    return agg


def map_to_kirana_catalog(df: pd.DataFrame, sku_count: int) -> pd.DataFrame:
    sku_rank = (
        df.groupby("sku_id", as_index=False)["quantity_sold"].sum().sort_values("quantity_sold", ascending=False)
    )
    picked = sku_rank.head(sku_count)["sku_id"].tolist()
    out = df[df["sku_id"].isin(picked)].copy()

    catalog = PRODUCT_CATALOG[:sku_count]
    mapping_rows = []
    for i, raw in enumerate(picked, start=1):
        prod = catalog[i - 1]
        mapping_rows.append(
            {
            "source_sku_name": raw,
            "sku_id": f"KR{i:03d}",
            "item_name": prod["item_name"],
            "item_category": prod["category"],
            "base_price": float(prod["base_price"]),
            "target_margin_pct": float(prod["margin_pct"]),
            }
        )

    map_df = pd.DataFrame(mapping_rows)
    out.rename(columns={"sku_id": "source_sku_name"}, inplace=True)
    out = out.merge(map_df, on="source_sku_name", how="left")

    old_mean = out.groupby("sku_id")["selling_price"].transform("mean").replace(0, np.nan)
    old_idx = (out["selling_price"] / old_mean).fillna(1.0)

    out["selling_price"] = out["base_price"] * (1 + (old_idx - 1) * 0.20)
    out["selling_price"] = out["selling_price"].clip(lower=out["base_price"] * 0.86, upper=out["base_price"] * 1.14)

    gap = (out["market_price"] - out["selling_price"]).fillna(0)
    gap_pct = (gap / out["selling_price"].replace(0, np.nan)).fillna(0).clip(-0.10, 0.10)
    out["market_price"] = out["selling_price"] * (1 + gap_pct)

    med = out.groupby("sku_id")["quantity_sold"].transform("median").replace(0, np.nan)
    target_median = np.where(out["item_category"].isin(["Snacks", "Instant Food"]), 22, 14)
    scale = (target_median / med).clip(0.001, 0.05)
    out["quantity_sold"] = (out["quantity_sold"] * scale).round().clip(lower=1).astype(int)
    out["stock_on_hand"] = np.maximum((out["quantity_sold"] * 2.3).round(), 20).astype(int)
    out["profit_amt"] = (out["quantity_sold"] * out["selling_price"] * out["target_margin_pct"]).round(2)

    out = out[
        [
            "date",
            "sku_id",
            "item_name",
            "item_category",
            "quantity_sold",
            "selling_price",
            "market_price",
            "stock_on_hand",
            "empty_shelf_flag",
            "profit_amt",
            "festival_impact",
            "target_margin_pct",
        ]
    ]
    return out


def extend_date_range(df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date)

    keys = df[["sku_id", "item_name", "item_category", "target_margin_pct"]].drop_duplicates()
    full = pd.MultiIndex.from_product([pd.date_range(start, end, freq="D"), keys["sku_id"]], names=["date", "sku_id"]).to_frame(index=False)
    full = full.merge(keys, on="sku_id", how="left")

    d = full.merge(df, on=["date", "sku_id", "item_name", "item_category", "target_margin_pct"], how="left")
    d.sort_values(["sku_id", "date"], inplace=True)

    val_cols = ["quantity_sold", "selling_price", "market_price", "stock_on_hand", "empty_shelf_flag", "profit_amt", "festival_impact"]
    src = d[["sku_id", "date"] + val_cols].copy()
    src.rename(columns={"date": "source_date", **{c: f"src_{c}" for c in val_cols}}, inplace=True)

    d["source_date"] = d["date"] - pd.Timedelta(days=364)
    d = d.merge(src, on=["sku_id", "source_date"], how="left")
    for c in val_cols:
        d[c] = d[c].fillna(d[f"src_{c}"])

    d.drop(columns=["source_date"] + [f"src_{c}" for c in val_cols], inplace=True)
    d[val_cols] = d.groupby("sku_id")[val_cols].transform(lambda s: s.ffill().bfill())

    d["quantity_sold"] = d["quantity_sold"].round().clip(lower=0).astype(int)
    d["stock_on_hand"] = d["stock_on_hand"].round().clip(lower=0).astype(int)
    d["empty_shelf_flag"] = d["empty_shelf_flag"].round().clip(lower=0, upper=1).astype(int)
    d["selling_price"] = d["selling_price"].round(2)
    d["market_price"] = d["market_price"].round(2)
    d["profit_amt"] = d["profit_amt"].round(2)
    d["festival_impact"] = d["festival_impact"].round(2)
    return d


def apply_festival_logic(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    fmap = {pd.Timestamp(k): v for k, v in FESTIVALS.items()}

    out["festival_name"] = out["date"].map(fmap).fillna("")
    out["is_festival_day"] = (out["festival_name"] != "").astype(int)

    pre_days = set()
    for d in fmap:
        pre_days.update({d - pd.Timedelta(days=i) for i in range(1, 8)})

    out["is_pre_festival_window"] = out["date"].isin(pre_days).astype(int)
    out.loc[(out["festival_name"] == "") & (out["is_pre_festival_window"] == 1), "festival_name"] = "Pre-Festival"

    mult = np.ones(len(out), dtype=float)
    holi = out["festival_name"].str.contains("Holi|Pre-Festival", regex=True)
    diwali = out["festival_name"].str.contains("Diwali|Pre-Festival", regex=True)

    festive = out["item_category"].eq("Festive")
    premium = out["item_category"].eq("Premium")
    staples = out["item_category"].isin(["Staples", "Oils", "Pulses"])

    mult[holi & festive] = 4.2
    mult[holi & staples] = 1.5
    mult[diwali & premium] = 2.4
    mult[diwali & festive] = 2.1
    mult[diwali & staples] = 1.35

    out["quantity_sold"] = (out["quantity_sold"] * mult).round().astype(int)
    out["festival_impact"] = np.where(out["festival_name"] == "", out["festival_impact"], np.maximum(out["festival_impact"], mult))
    out["profit_amt"] = (out["quantity_sold"] * out["selling_price"] * out["target_margin_pct"]).round(2)

    return out


def season_from_month(month: int) -> str:
    if month in (11, 12, 1, 2):
        return "Winter"
    if month in (3, 4, 5):
        return "Summer"
    if month in (6, 7, 8, 9):
        return "Monsoon"
    return "Post-Monsoon"


def weather_from_month(month: int) -> str:
    if month in (6, 7, 8, 9):
        return "Rainy"
    if month in (4, 5):
        return "Hot"
    if month in (12, 1):
        return "Cold"
    return "Mild"


def tax_pct_for_category(category: str) -> float:
    if category in ("Staples", "Pulses"):
        return 0.0
    if category in ("Spices", "Condiments"):
        return 5.0
    if category in ("Snacks", "Instant Food", "Premium", "Festive"):
        return 12.0
    return 5.0


def supplier_for_sku(sku_id: str) -> str:
    sid = int(sku_id.replace("KR", ""))
    return f"SUP{(sid % 12) + 1:03d}"


def lead_time_days_for_row(row, rng: np.random.Generator) -> int:
    base_by_cat = {
        "Staples": 2,
        "Pulses": 3,
        "Oils": 3,
        "Beverages": 4,
        "Snacks": 2,
        "Instant Food": 3,
        "Cooking": 2,
        "Spices": 4,
        "Condiments": 3,
        "Premium": 6,
        "Festive": 5,
    }
    base = base_by_cat.get(row.item_category, 3)
    jitter = int(rng.integers(0, 3))
    festival_bump = 1 if (row.is_festival_day == 1 or row.is_pre_festival_window == 1) else 0
    return int(base + jitter + festival_bump)


def split_intraday(df: pd.DataFrame) -> pd.DataFrame:
    records = []

    for row in df.itertuples(index=False):
        d = pd.Timestamp(row.date)
        weekend = int(d.weekday() >= 5)

        base_probs = np.array([x[2] for x in TIME_SLOTS], dtype=float)
        if weekend:
            base_probs += np.array([0.00, 0.00, 0.01, 0.01, 0.01, 0.01, 0.02, 0.00])
        if row.is_festival_day == 1:
            base_probs += np.array([0.00, 0.00, 0.00, 0.01, 0.02, 0.02, 0.03, 0.00])
        probs = base_probs / base_probs.sum()

        seed = stable_seed(str(d.date()), row.sku_id)
        rng = np.random.default_rng(seed)

        qty = int(max(0, row.quantity_sold))
        splits = rng.multinomial(qty, probs) if qty > 0 else np.zeros(len(TIME_SLOTS), dtype=int)

        reorder_point = int(max(8, round(row.quantity_sold * 2.2)))
        opening_stock = int(max(row.stock_on_hand, row.quantity_sold + reorder_point))
        running_stock = opening_stock

        for i, (slot_name, start_hour, _) in enumerate(TIME_SLOTS):
            slot_qty = int(splits[i])
            running_stock = max(0, running_stock - slot_qty)

            festival_or_pre = int((row.is_festival_day == 1) or (row.is_pre_festival_window == 1))
            promo_prob = 0.07 + (0.20 if festival_or_pre else 0.0) + (0.03 if weekend else 0.0)
            promo_flag = int(rng.random() < min(0.45, promo_prob))

            discount_pct = 0.0
            if promo_flag:
                discount_pct = float(rng.choice([0.04, 0.06, 0.08, 0.10, 0.12], p=[0.25, 0.30, 0.25, 0.15, 0.05]))

            effective_price = float(round(row.selling_price * (1 - discount_pct), 2))
            revenue = round(slot_qty * effective_price, 2)

            cogs_unit = row.selling_price * (1 - row.target_margin_pct)
            cost_amt = round(slot_qty * cogs_unit, 2)
            profit_amt = round(revenue - cost_amt, 2)
            gross_margin_pct = round((profit_amt / revenue) if revenue > 0 else row.target_margin_pct, 4)
            purchase_cost = round(cogs_unit, 2)
            tax_pct = tax_pct_for_category(row.item_category)
            mrp = round(max(row.selling_price * 1.08, row.selling_price + 1.0), 2)
            lead_time_days = lead_time_days_for_row(row, rng)
            supplier_id = supplier_for_sku(row.sku_id)
            tax_amt = round(revenue * (tax_pct / (100.0 + tax_pct)), 2) if revenue > 0 else 0.0
            net_profit = round(profit_amt - (0.008 * revenue), 2)

            basket = float(round(max(1.1, rng.normal(1.7, 0.35)), 2))
            footfall = int(max(2, round(slot_qty / basket))) if slot_qty > 0 else int(rng.integers(1, 4))

            payment_mode = rng.choice(["UPI", "Cash", "Card"], p=[0.58, 0.32, 0.10])

            ts = pd.Timestamp(year=d.year, month=d.month, day=d.day, hour=start_hour)
            price_gap_pct = round((effective_price - row.market_price) / row.market_price, 4) if row.market_price else 0.0

            records.append(
                {
                    "record_id": f"{d.strftime('%Y%m%d')}-{row.sku_id}-{slot_name}",
                    "date": d.date().isoformat(),
                    "txn_timestamp": ts.isoformat(),
                    "store_id": "IND_RAJU_001",
                    "store_city": "Indore",
                    "sku_id": row.sku_id,
                    "item_name": row.item_name,
                    "item_category": row.item_category,
                    "time_slot": slot_name,
                    "hour_start": start_hour,
                    "quantity_sold": slot_qty,
                    "selling_price": round(row.selling_price, 2),
                    "mrp": mrp,
                    "tax_pct": tax_pct,
                    "purchase_cost": purchase_cost,
                    "discount_pct": round(discount_pct, 4),
                    "effective_price": effective_price,
                    "market_price": round(row.market_price, 2),
                    "price_gap_pct": price_gap_pct,
                    "supplier_id": supplier_id,
                    "lead_time_days": lead_time_days,
                    "opening_stock": opening_stock if i == 0 else None,
                    "stock_on_hand": running_stock,
                    "reorder_point": reorder_point,
                    "needs_reorder": int(running_stock <= reorder_point),
                    "empty_shelf_flag": int((running_stock == 0) or (row.empty_shelf_flag == 1 and slot_qty == 0)),
                    "revenue": revenue,
                    "tax_amt": tax_amt,
                    "cost_amt": cost_amt,
                    "profit_amt": profit_amt,
                    "net_profit": net_profit,
                    "gross_margin_pct": gross_margin_pct,
                    "festival_impact": round(row.festival_impact, 2),
                    "festival_name": row.festival_name,
                    "is_festival_day": int(row.is_festival_day),
                    "is_pre_festival_window": int(row.is_pre_festival_window),
                    "promo_flag": promo_flag,
                    "footfall_est": footfall,
                    "basket_size_est": basket,
                    "payment_mode": payment_mode,
                    "day_of_week": d.day_name(),
                    "week_of_year": int(d.isocalendar().week),
                    "month": d.month,
                    "quarter": int((d.month - 1) // 3 + 1),
                    "is_weekend": weekend,
                    "season": season_from_month(d.month),
                    "weather_tag": weather_from_month(d.month),
                }
            )

    out = pd.DataFrame(records)
    out["opening_stock"] = out["opening_stock"].ffill().fillna(0).astype(int)
    return out


def run(cfg: Config) -> None:
    validate_columns(cfg.input_csv)
    df = ingest_base(cfg)
    df = map_to_kirana_catalog(df, cfg.sku_count)
    df = extend_date_range(df, cfg.start_date, cfg.end_date)
    df = apply_festival_logic(df)
    df = split_intraday(df)

    # Stable ordering for downstream systems.
    df = df.sort_values(["date", "sku_id", "hour_start"]).reset_index(drop=True)

    cols = [
        "record_id",
        "date",
        "txn_timestamp",
        "store_id",
        "store_city",
        "sku_id",
        "item_name",
        "item_category",
        "time_slot",
        "hour_start",
        "quantity_sold",
        "selling_price",
        "mrp",
        "tax_pct",
        "purchase_cost",
        "discount_pct",
        "effective_price",
        "market_price",
        "price_gap_pct",
        "supplier_id",
        "lead_time_days",
        "opening_stock",
        "stock_on_hand",
        "reorder_point",
        "needs_reorder",
        "empty_shelf_flag",
        "revenue",
        "tax_amt",
        "cost_amt",
        "profit_amt",
        "net_profit",
        "gross_margin_pct",
        "festival_impact",
        "festival_name",
        "is_festival_day",
        "is_pre_festival_window",
        "promo_flag",
        "footfall_est",
        "basket_size_est",
        "payment_mode",
        "day_of_week",
        "week_of_year",
        "month",
        "quarter",
        "is_weekend",
        "season",
        "weather_tag",
    ]
    df = df[cols]
    df.to_csv(cfg.output_csv, index=False)

    print(f"Input: {cfg.input_csv}")
    print(f"Output: {cfg.output_csv}")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"SKU count: {df['sku_id'].nunique()}")
    print(f"Item count: {df['item_name'].nunique()}")


def parse_args() -> Config:
    p = argparse.ArgumentParser(description="Build rich 2-year kirana dataset with >=60 SKUs and traceability.")
    p.add_argument("--input-csv", default="gcpl_synthetic_detailed_v2.csv")
    p.add_argument("--output-csv", default="raju_kirana_2yr.csv")
    p.add_argument("--region", default="West")
    p.add_argument("--channel", default="GT")
    p.add_argument("--start-date", default="2024-01-01")
    p.add_argument("--end-date", default="2025-12-31")
    p.add_argument("--chunksize", type=int, default=150_000)
    p.add_argument("--sku-count", type=int, default=60)
    a = p.parse_args()

    if a.sku_count < 60:
        raise ValueError("Use --sku-count >= 60 as requested.")

    return Config(
        input_csv=Path(a.input_csv),
        output_csv=Path(a.output_csv),
        region=a.region,
        channel=a.channel,
        start_date=a.start_date,
        end_date=a.end_date,
        chunksize=a.chunksize,
        sku_count=a.sku_count,
    )


if __name__ == "__main__":
    run(parse_args())
