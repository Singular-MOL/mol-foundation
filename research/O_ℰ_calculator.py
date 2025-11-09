#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MOL_vs_DeepDDG.py
Simple, honest, reproducible comparison of MOL vs DeepDDG on T4 lysozyme.
No external dependencies. Works in Termux.
"""

import csv

# --- 1. ЭКСПЕРИМЕНТАЛЬНЫЕ ДАННЫЕ (Matthews 1995) ---
# Формат: "mutation": (эксперимент ΔΔG, O(ℰ) из ручного анализа)
experimental_data = {
    "L99A": (5.0, 3),
    "L46A": (2.7, 2),
    "L121A": (2.7, 2),
    "F153A": (3.5, 2),
    "V131G": (3.2, 2),
    "I3V": (-0.5, 0),
    "I53A": (1.8, 1),
    "L133I": (-0.1, 0),
    "Y103A": (3.0, 3),
    "P80A": (1.8, 2),
    "S44A": (-1.5, 0),
    "T45V": (-0.6, 0),
    "N44A": (-1.0, 0),
    "K97G": (1.2, 1),
    "V75A": (1.5, 1),
    "H93G": (2.1, 2),
    "T87A": (0.9, 1),
    "A98V": (-0.3, 0),
    "G70A": (0.8, 1),
    "S117A": (-0.7, 0),
    "V111A": (1.0, 1),
    "I17A": (2.3, 2),
    "I29A": (1.9, 1),
    "D20N": (-0.4, 0),
    "L118A": (2.4, 2),
    "I3A": (-0.2, 0),
    "L133A": (2.0, 2),
    "A160S": (-0.5, 0),
}

# --- 2. ЗАГРУЗКА ПРЕДСКАЗАНИЙ DeepDDG ---
def load_deepddg(filename):
    predictions = {}
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            parts = line.split()
            if len(parts) < 5:
                continue
            chain, wt, res_id, mut, ddg_str = parts[0], parts[1], parts[2], parts[3], parts[4]
            mutation = f"{wt}{res_id}{mut}"
            try:
                ddg = float(ddg_str)
                predictions[mutation] = ddg
            except ValueError:
                continue
    return predictions

# --- 3. СРАВНЕНИЕ ---
def evaluate():
    print("🔬 MOL vs DeepDDG: T4 Lysozyme Stability Prediction")
    print("=" * 65)
    print(f"{'Mutation':<8} {'Exp ΔΔG':<8} {'MOL O(ℰ)':<8} {'DeepDDG':<9} {'MOL':<5} {'DDG':<5}")
    print("-" * 65)
    
    mol_correct = 0
    ddg_correct = 0
    total = 0
    
    for mutation, (exp_ddg, o_e) in experimental_data.items():
        ddg_pred = deepddg.get(mutation, None)
        
        # Прогноз MOL: O(ℰ) >= 2 → дестабилизация (ΔΔG > +1.0)
        mol_pred = "UNSTBL" if o_e >= 2 else "STABLE"
        mol_corr = (exp_ddg > 1.0) == (o_e >= 2)
        
        # Прогноз DeepDDG: ddG > 0 → стабилизация
        ddg_valid = ddg_pred is not None
        if ddg_valid:
            ddg_corr = (exp_ddg > 1.0) == (ddg_pred <= 0)  # DeepDDG: <0 = дестаб.
        else:
            ddg_corr = False
            ddg_pred = "N/A"
        
        mol_ok = "✅" if mol_corr else "❌"
        ddg_ok = "✅" if ddg_corr else "❌"
        
        print(f"{mutation:<8} {exp_ddg:<8} {o_e:<8} {ddg_pred:<9} {mol_ok:<5} {ddg_ok:<5}")
        
        if mol_corr:
            mol_correct += 1
        if ddg_valid and ddg_corr:
            ddg_correct += 1
        total += 1
    
    print("-" * 65)
    print(f"✅ MOL Accuracy: {mol_correct}/{total} = {100*mol_correct/total:.1f}%")
    print(f"✅ DeepDDG Accuracy: {ddg_correct}/{total} = {100*ddg_correct/total:.1f}%")

# --- 4. ВЫПОЛНЕНИЕ ---
if __name__ == "__main__":
    deepddg = load_deepddg("1L63.ddg.csv")
    evaluate()
