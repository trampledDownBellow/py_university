import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np 
import pandas as pd

def load_data(csv_path: Path) -> pd.DataFrame:
    return pd.read_csv(csv_path)

def cbs(df: pd.DataFrame) -> tuple[float, float, float]:
    mean_price = float(np.mean(df["price_per_unit"]))
    median_quantity = float(np.median(df["quantity"]))
    price_std = float(np.std(df["price_per_unit"]))
    return mean_price, median_quantity, price_std

def e_totoal(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["total_price"] = df["quantity"] * df["price_per_unit"]
    return df

def find_top_supplier(df: pd.DataFrame) -> tuple[str, float]:
    supplier_revenue = df.groupby("supplier")["total_price"].sum()
    top_supplier = supplier_revenue.idxmax()
    return top_supplier, float(supplier_revenue.loc[top_supplier])

def category_quantities(df: pd.DataFrame) -> pd.Series:
    return df.groupby("category")["quantity"].sum()

def save_low_supply(df: pd.DataFrame, output_path: Path) -> pd.DataFrame:
    low_supply = df[df["quantity"] < 100]
    low_supply.to_csv(output_path, index=False)
    return low_supply


def save_report(
    report_path: Path,
    mean_price: float,
    median_quantity: float,
    price_std: float,
    top_supplier: str,
    low_supply_filename: str,
) -> None:
    report_lines = [
        "Звіт про аналіз поставок",
        "======================",
        f"Середня ціна за одиницю: {mean_price:.2f}",
        f"Середня кількість: {median_quantity:.2f}",
        f"Стандартне відхилення ціни: {price_std:.2f}",
        "",
        f"Топ постачальник за виручкою: {top_supplier}",
        f"Файл із низьким запасом: {low_supply_filename}",
    ]
    report_path.write_text("\n".join(report_lines))

def plot_category_distribution(category_totals: pd.Series, output_path: Path) -> None:
    plt.figure(figsize=(8, 5))
    category_totals.sort_values(ascending=False).plot(kind="bar", color="steelblue")
    plt.title("Quantity Distribution by Category")
    plt.xlabel("Category")
    plt.ylabel("Total Quantity")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze supply data.")
    parser.add_argument(
        "csv",
        nargs="?",
        default="supplies.csv",
        help="Шлях до CSV-файлу з інформацією про витратні матеріали (default: supplies.csv)",
    )
    args = parser.parse_args()

    csv_path = Path(args.csv)
    df = load_data(csv_path)
    mean_price, median_quantity, price_std = cbs(df)

    enriched_df = e_totoal(df)
    top_supplier, _ = find_top_supplier(enriched_df)
    category_totals = category_quantities(enriched_df)

    low_supply_path = csv_path.with_name("low_supply.csv")
    save_low_supply(enriched_df, low_supply_path)

    report_path = csv_path.with_name("report.txt")
    save_report(
        report_path,
        mean_price,
        median_quantity,
        price_std,
        top_supplier,
        low_supply_path.name,
    )

    plot_path = csv_path.with_name("category_distribution.png")
    plot_category_distribution(category_totals, plot_path)

    sorted_df = enriched_df.sort_values("total_price", ascending=False)
    print(sorted_df.head(3))

if __name__ == "__main__":
    main()