#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O_ℰ_calculator.py
Part of the MOL Dialogic Intelligence Architecture (Astra Core)
Calculates ontological load O(ℰ) from DeepDDG mutation data.

Usage:
    python O_ℰ_calculator.py --csv 1L63.ddg.csv
"""

import argparse
import pandas as pd

# --- аминокислотные классы ---
hydrophobic = set("AILMFWVY")
polar = set("STNQCH")
charged = set("KRDE")

def infer_ontological_load(wt, mut, ddg):
    """Эвристическая функция оценки O(ℰ)"""
    score = 0

    # 1. Грубое нарушение гидрофобности
    if (wt in hydrophobic and mut in charged) or (wt in charged and mut in hydrophobic):
        score += 1

    # 2. Потеря объёма (пример: Leu → Ala)
    volume_loss = ["LVIMFWY", "A", "G"]
    if wt in "LVIMFWY" and mut in "AG":
        score += 1

    # 3. Резкая дестабилизация по ΔΔG
    if ddg < -1.5:
        score += 1

    # 4. Консервативность (снижение балла)
    if (wt in hydrophobic and mut in hydrophobic) or (wt in charged and mut in charged):
        score -= 1

    return max(0, score)

def main():
    parser = argparse.ArgumentParser(description="Compute Ontological Load O(ℰ)")
    parser.add_argument("--csv", required=True, help="DeepDDG output file (e.g. 1L63.ddg.csv)")
    args = parser.parse_args()

    # Загрузка
    df = pd.read_csv(args.csv, comment="#", delim_whitespace=True,
                     names=["chain", "WT", "ResID", "Mut", "ddG"])

    # Расчёт O(ℰ)
    df["O_E"] = df.apply(lambda row: infer_ontological_load(row["WT"], row["Mut"], row["ddG"]), axis=1)

    # Категоризация
    df["Category"] = df["O_E"].map({0:"Natural", 1:"Mild", 2:"Heavy", 3:"Critical"})

    # Сводная статистика
    summary = df.groupby("O_E")["ddG"].mean().reset_index()
    summary.columns = ["O(ℰ)", "Mean ΔΔG"]

    print("\n==============================")
    print(" Ontological Load Analysis (E = ℰ(∑I))")
    print("==============================\n")
    print(df.head(10))
    print("\n--- Summary ---")
    print(summary)
    print("\nTotal mutations analyzed:", len(df))

    # Сохранение результатов
    out_file = args.csv.replace(".csv", "_O_E_results.csv")
    df.to_csv(out_file, index=False)
    print(f"\nResults saved to: {out_file}")

if __name__ == "__main__":
    main()
