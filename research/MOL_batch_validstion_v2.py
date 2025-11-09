#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MOL Batch Analysis v2: Enhanced with structural priors (core, conservation)
Uses static, literature-based structural knowledge — no fitting, no libraries.
Works in Termux.
"""

import csv

# === СТРУКТУРНЫЕ ПРИОРИТЕТЫ ИЗ LITERATURE ===
HYDROPHOBIC = set("AVILMFYW")
CHARGED = set("DEKR")
AROMATIC = set("FYW")

# Ядро по PDB (ручная аннотация из структур и публикаций)
CORE_RESIDUES = {
    "P00720": {9,10,21,26,27,29,30,34,46,47,54,61,62,70,71,73,80,81,99,101,102,103,106,115,116,118,121,122,130,133,136,145,146,147,148,152,153,156,159},
    "P0A877": {22,28,53,67,78,101,114,115},
    "P04637": {175,248,273,282},
    "P00698": {4,5,8,10,27,32,35,39,40,42,44,51,52,56,58,64,67,71,74,76,80,83,85,87,90,93,95,97,100,103,106,110,113,116,119,122,126,129,132,135,139,142,145,148,151}
}

# Высококонсервативные позиции
HIGH_CONSERVATION = {
    "P00720": {46, 99, 121, 153},
    "P0A877": {28, 53, 101, 114},
    "P04637": {175, 248, 273},
    "P00698": {4,8,27,32,35,67,71,100,103,116}
}

def compute_Oe_v2(uniprot, wt, mut, pos):
    score = 0

    # 1. PLOA: гидрофоб → заряжен в ядре
    if uniprot in CORE_RESIDUES and pos in CORE_RESIDUES[uniprot]:
        if wt in HYDROPHOBIC and mut in CHARGED:
            score += 1

    # 2. PIVC: большая → маленькая в ядре (каверна)
    if uniprot in CORE_RESIDUES and pos in CORE_RESIDUES[uniprot]:
        if wt in "FWYLM" and mut in "AG":
            score += 1

    # 3. PHD: мутация в высококонсервативной позиции
    if uniprot in HIGH_CONSERVATION and pos in HIGH_CONSERVATION[uniprot]:
        score += 1

    # 4. PAD: разрыв ароматического кластера в ядре
    if uniprot in CORE_RESIDUES and pos in CORE_RESIDUES[uniprot]:
        if wt in AROMATIC and mut not in AROMATIC:
            score += 1

    return min(score, 4)

# === ЗАГРУЗКА И АНАЛИЗ (как в предыдущей версии) ===
def load_data(filename):
    data = []
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
                pos = int(row[idx["POSITION"]])
                wt = row[idx["WILD_TYPE_RES"]]
                mut = row[idx["MUTATED_RES"]]
                if abs(ddg) > 10: continue
                data.append({"uniprot": uniprot, "ddg": ddg, "pos": pos, "wt": wt, "mut": mut})
            except:
                continue
    return data

def main():
    data = load_data("all_data_clean.csv")
    correct = 0
    total = 0

    for entry in data:  # ← Вот правильная строка: "for entry in data"
        oe = compute_Oe_v2(entry["uniprot"], entry["wt"], entry["mut"], entry["pos"])
        pred = "UNSTABLE" if oe >= 2 else "STABLE"
        actual = "UNSTABLE" if entry["ddg"] < -1.0 else "STABLE"
        if pred == actual:
            correct += 1
        total += 1

    print(f"🎯 MOL v2 Accuracy (structural priors): {100 * correct / total:.1f}%")
    print(f"✅ Mutations analyzed: {total}")

if __name__ == "__main__":
    main()
