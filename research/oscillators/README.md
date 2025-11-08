
---
title: "MOL Oscillator Experiments – Full Sweep Analysis"
description: "Scientific experiments on oscillator networks using the Law of Minimal Ontological Load (MOL). Full sweep over K, alpha, sigma, and omega_spread for transparency and reproducibility."
tags:
  - oscillators
  - kuramoto-model
  - mol-law
  - complex-systems
  - phase-coherence
license: "CC-BY-4.0"
doi: "10.5281/zenodo.17445023"
---

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17445023.svg)](https://doi.org/10.5281/zenodo.17445023)

# MOL Oscillator Scientific Experiments
**Full sweep of parameters for Kuramoto-like oscillator networks**

This project demonstrates **MOL-based modeling** of coupled oscillators with:

- Sweep over **K, alpha, sigma, omega_spread**  
- Multi-run statistical validation  
- Full MOL O(ℰ) computation  
- Energy, coherence, and O(ℰ) saved for analysis  
- JSON/CSV outputs for heatmaps and correlation studies  

## 🧪 Experimental Code

- [mol_oscillators_full_sweep.py](./mol_oscillators_full_sweep.py) – main simulation script implementing the full sweep and MOL calculations

## 📊 Outputs

- Each run saves a **JSON file** with phases, coherence, O(ℰ), energy  
- A **summary JSON/CSV** file contains all runs for plotting heatmaps and analyzing correlations

## 🔹 Features

1. **Parameter sweep** across physically justified ranges  
2. **MOL transparency** – no magic numbers; all constants documented with references  
3. **Statistical significance** via multiple runs (repeats)  
4. **JSON + CSV outputs** for downstream analysis  
5. **Phase coherence, O(ℰ), and energy** saved per run

## 📚 References

- MOL Whitepaper v1.0: [DOI: 10.5281/zenodo.17445023](https://doi.org/10.5281/zenodo.17445023)  
- Kuramoto, Y. 1975, *International Symposium on Mathematical Problems in Theoretical Physics*  
- Wu et al., Sci Rep 2018  
- Zou et al., Phys Rev E 2019  

## 🚀 Usage

```bash
python mol_oscillators_full_sweep.py
````

Outputs will be saved in a timestamped folder like `mol_osc_experiments_YYYYMMDD/` with all JSON/CSV files.

```
