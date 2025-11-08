#!/usr/bin/env python3
"""
MOL OSCILLATOR SCIENTIFIC EXPERIMENT
-------------------------------------
Обновлённая версия для максимальной научной прозрачности

Особенности:
- Sweep по K, alpha, sigma для устранения "магических чисел"
- Полная формула O(ℰ) (MOL Whitepaper v1.0)
- Многократные прогоны для статистической значимости
- Сохранение всех результатов для визуализации (JSON + CSV)
- Обоснование параметров с ссылками на литературу

Whitepaper: DOI:10.5281/zenodo.17445023
Kuramoto model reference: Kuramoto, Y. 1975, International Symposium on Mathematical Problems in Theoretical Physics
Clustered extension: Wu et al., Sci Rep 2018; Zou et al., Phys Rev E 2019
"""
import math
import random
import json
import os
import csv
from datetime import datetime

# ---------------------------
# Папка для результатов
# ---------------------------
folder = f"mol_osc_experiments_{datetime.now().strftime('%Y%m%d')}"
os.makedirs(folder, exist_ok=True)
print(f"📁 Результаты будут сохранены в папке: {folder}")

# ---------------------------
# Полная формула O(ℰ)
# ---------------------------
def compute_OE(phases, bins=4, energies=None):
    """
    Онтологическая нагрузка O(ℰ) (MOL Whitepaper v1.0)
    phases: список фаз осцилляторов [-π, π]
    bins: число фазовых бинов
    energies: список энергий осцилляторов для взвешивания (опционально)
    """
    N = len(phases)
    hist = [0.0]*bins
    for i, p in enumerate(phases):
        idx = int((p + math.pi)/(2*math.pi) * bins) % bins
        w = energies[i] if energies else 1.0
        hist[idx] += w
    total = sum(hist) or 1.0
    p_bins = [h/total for h in hist if h>0]
    Oe = -sum(pi * math.log(pi + 1e-12) for pi in p_bins)
    # Нормировка на max энтропию (log(bins))
    Oe /= math.log(bins)
    return Oe

# ---------------------------
# Модель осцилляторов
# ---------------------------
def run_simulation(params, run_id, use_full_OE=True):
    """
    params: dict с ключами
        N, T, dt, K, alpha, sigma, omega_spread, seed
    """
    N = params['N']
    T = params['T']
    dt = params['dt']
    K = params['K']
    alpha = params['alpha']
    sigma = params['sigma']
    omega_spread = params['omega_spread']
    omega_base = 1.0
    seed = params['seed']

    random.seed(seed)
    omega = [random.uniform(omega_base - omega_spread/2, omega_base + omega_spread/2) for _ in range(N)]
    theta = [random.uniform(0, 2*math.pi) for _ in range(N)]

    for step in range(T):
        dtheta = [0.0]*N
        for i in range(N):
            interaction = 0.0
            for j in range(N):
                if i != j:
                    delta = theta[j] - theta[i]
                    delta = (delta + math.pi) % (2*math.pi) - math.pi
                    interaction += math.sin(delta) * (1.0 - alpha*math.cos(2*delta))
            interaction *= K/N
            noise = sigma * random.gauss(0,1)
            dtheta[i] = omega[i] + interaction + noise
        for i in range(N):
            theta[i] = (theta[i] + dtheta[i]*dt) % (2*math.pi)

    # Центрируем фазы [-π, π]
    phases_centered = [(t + math.pi) % (2*math.pi) - math.pi for t in theta]

    # Коэрентность
    real = sum(math.cos(t) for t in theta)/N
    imag = sum(math.sin(t) for t in theta)/N
    coherence = math.sqrt(real*real + imag*imag)

    # Энергия осцилляторов
    energies = [(omega[i] - sum(math.sin(theta[j]-theta[i]) for j in range(N) if j!=i)*K/N)**2 for i in range(N)]

    # Онтологическая нагрузка O(ℰ)
    Oe = compute_OE(phases_centered, bins=4, energies=energies) if use_full_OE else compute_OE(phases_centered, bins=4, energies=None)

    report = {
        "run_id": run_id,
        "parameters": params,
        "results": {
            "phases_centered": [round(p,4) for p in phases_centered],
            "coherence": round(coherence,4),
            "O_epsilon": round(Oe,4),
            "energy_mean": round(sum(energies)/N,4)
        }
    }

    # Сохраняем JSON
    filename = os.path.join(folder, f"run_{run_id}.json")
    with open(filename,'w') as f:
        json.dump(report,f,indent=2)
    return coherence, Oe, sum(energies)/N

# ---------------------------
# Параметры sweep
# ---------------------------
base_params = {
    'N': 10,
    'T': 4000,
    'dt': 0.01,
    'K': 0.5,
    'alpha': 0.6,
    'seed': 42
}

K_list = [0.3, 0.5, 0.7]              # Сила связи
alpha_list = [0.4, 0.6, 0.8]          # Модификация нелинейности
sigma_list = [0.02, 0.06, 0.12, 0.20, 0.30]  # Шум
omega_spread_list = [0.1, 0.3, 0.5, 0.8, 1.0]
repeats = 5                            # Многократные прогоны для статистики

results_summary = []

print("🚀 Запуск сеточного sweep по K, alpha, sigma, omega_spread...")
run_counter = 0
for K in K_list:
    for alpha in alpha_list:
        for sigma in sigma_list:
            for omega_spread in omega_spread_list:
                for r in range(repeats):
                    run_id = f"K{K}_A{alpha}_σ{sigma}_Δω{omega_spread}_r{r+1}"
                    params = base_params.copy()
                    params.update({'K':K, 'alpha':alpha, 'sigma':sigma, 'omega_spread':omega_spread, 'seed':r+100})
                    coh, Oe, energy_mean = run_simulation(params, run_id, use_full_OE=True)
                    results_summary.append({
                        "run": run_id,
                        "K":K, "alpha":alpha, "sigma":sigma, "omega_spread":omega_spread,
                        "coherence": coh, "O_epsilon": Oe, "energy_mean": energy_mean
                    })
                    run_counter += 1
                    if run_counter % 10 == 0:
                        print(f"  ✅ Выполнено {run_counter} прогонов...")

# ---------------------------
# Сохраняем JSON
# ---------------------------
summary_file = os.path.join(folder,"summary.json")
with open(summary_file,'w') as f:
    json.dump({
        "experiment_series": "MOL Oscillator Full Sweep",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "whitepaper_doi": "10.5281/zenodo.17445023",
        "runs": results_summary
    }, f, indent=2)

# ---------------------------
# Сохраняем CSV для визуализации heatmaps
# ---------------------------
csv_file = os.path.join(folder,"summary.csv")
with open(csv_file,'w',newline='') as f:
    writer = csv.DictWriter(f, fieldnames=list(results_summary[0].keys()))
    writer.writeheader()
    for row in results_summary:
        writer.writerow(row)

print(f"\n✅ Все эксперименты завершены! JSON и CSV сохранены в папке {folder}")
print(f"📊 JSON: {summary_file}")
print(f"📊 CSV: {csv_file}")
