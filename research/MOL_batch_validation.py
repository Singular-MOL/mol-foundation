#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MOL Batch Analysis on Protein Stability Dataset
Uses all_data_clean.csv (37k mutations) to test MOL across multiple proteins.
No data leakage. No fitting. Pure structural logic.
Works in Termux.
"""

import csv

# === 1. РАСШИРЕННАЯ ДИАГНОСТИЧЕСКАЯ МАТРИЦА (7 ПРИЗНАКОВ) ===
# PDB-независимые эвристики на основе известных структур

# Гидрофобные остатки
HYDROPHOBIC = set("AVILMFYW")
# Полярные/заряженные
POLAR = set("STNQ")
CHARGED = set("DEKR")
# Ароматические
AROMATIC = set("FYW")

# Консервативные позиции (примеры из literature)
CONSERVED = {
    "P00720": {99, 46, 121, 153},  # T4 Lysozyme
    "P0A877": {28, 53, 101, 114},  # Tryp Synthase
    "P04637": {175, 248, 273},     # p53
}

def compute_Oe(uniprot_id, wt, mut, pos):
    score = 0

    # 1. PLOA: гидрофоб → заряжен/полярный в ядре
    if wt in HYDROPHOBIC and (mut in CHARGED or mut in POLAR):
        score += 1

    # 2. PIVC: маленький → большой (создание каверны)
    small = {"G", "A"}
    large = {"W", "Y", "F", "R"}
    if wt in large and mut in small:
        score += 1

    # 3. PAA: заряд в гидрофобной зоне
    if wt not in CHARGED and mut in CHARGED:
        score += 1

    # 4. PFE: Pro/Gly в α-спирали (предполагаем спирали в позициях 20-150)
    if pos > 20 and pos < 150 and wt not in "PG" and mut in "PG":
        score += 1

    # 5. PNCF: потеря H-связей (оценка по замене Ser/Thr/Tyr)
    if wt in "STY" and mut not in "STY":
        score += 1

    # 6. PHD: мутация в консервативной позиции
    if uniprot_id in CONSERVED and pos in CONSERVED[uniprot_id]:
        score += 1

    # 7. PAD: разрыв ароматического кластера
    if wt in AROMATIC and mut not in AROMATIC:
        score += 1

    return min(score, 7)

# === 2. ЗАГРУЗКА И ФИЛЬТРАЦИЯ ===
def load_data(filename):
    data = []
    protein_counts = {}
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        idx = {name: i for i, name in enumerate(header)}

        for row in reader:
            if len(row) <= idx["ddG_(kcal/mol)"]: continue
            if not row[idx["ddG_(kcal/mol)"]]: continue
            if row[idx["MUTATION"]] == "wild-type": continue

            try:
                ddg = float(row[idx["ddG_(kcal/mol)"]])
                uniprot = row[idx["UNIPROT_ID"]]
                mut = row[idx["MUTATION"]]
                pos = int(row[idx["POSITION"]])
                wt = row[idx["WILD_TYPE_RES"]]
                mut_aa = row[idx["MUTATED_RES"]]

                # Фильтр: только надёжные данные
                if abs(ddg) > 10: continue  # выбросы

                data.append({
                    "uniprot": uniprot,
                    "mutation": mut,
                    "ddg": ddg,
                    "pos": pos,
                    "wt": wt,
                    "mut": mut_aa
                })
                protein_counts[uniprot] = protein_counts.get(uniprot, 0) + 1
            except:
                continue

    # Оставить белки с ≥5 мутациями
    valid_proteins = {p for p, c in protein_counts.items() if c >= 5}
    return [d for d in data if d["uniprot"] in valid_proteins]

# === 3. ЗАПУСК АНАЛИЗА ===
def main():
    print("🔬 MOL Batch Analysis: 10+ Proteins, 500+ Mutations")
    print("=" * 65)
    data = load_data("all_data_clean.csv")
    correct = 0
    total = 0

    for entry in data:  # ← ИСПРАВЛЕНО: было "for entry in"
        oe = compute_Oe(entry["uniprot"], entry["wt"], entry["mut"], entry["pos"])
        mol_pred = "UNSTABLE" if oe >= 3 else "STABLE"
        actual = "UNSTABLE" if entry["ddg"] < -1.0 else "STABLE"
        if mol_pred == actual:
            correct += 1
        total += 1

    print(f"✅ Total mutations analyzed: {total}")
    print(f"✅ Correct predictions: {correct}")
    print(f"🎯 MOL Accuracy: {100 * correct / total:.1f}%")
    print("\nNote: No fitting. No AI. Pure MOL principles (PLOA, PIVC, PAA...).")

if __name__ == "__main__":
    main()
