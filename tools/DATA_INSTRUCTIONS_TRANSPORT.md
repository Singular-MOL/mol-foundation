# 🚆 MOL Transport Network Analysis

## 📊 Required Dataset

**Dataset:** Berlin Public Transport Network 1946-1989  
**Source:** Zenodo - https://doi.org/10.5281/zenodo.17444654  
**File:** `stations.csv` (1.7 MB)

## 🚀 Setup Instructions

### 1. Download Dataset

```bash
# Option 1: Direct download
wget https://zenodo.org/record/17444654/files/stations.csv

# Option 2: Manual download
# Visit: https://doi.org/10.5281/zenodo.17444654  
# Download "stations.csv" (1.7 MB)
```
🔍 Dataset Description

· 19,758 transport stops in Berlin
· 1946-1989 historical data from divided Berlin
· All transport types: S-Bahn, U-Bahn, tram, bus
· Geographic coordinates for spatial analysis
· Line information for network topology

📈 What MOL Transport Analyzer Does

· Calculates ontological load O(ℰ) for each stop
· Identifies MOL-optimal systems (O(ℰ) ≈ 0.3)
· Detects problematic nodes with high ontological load
· Analyzes network efficiency across transport types
· Provides urban planning recommendations

🎯 Quick Start

For immediate demonstration, use transport_mol_demo.py.
For real transport network analysis, download dataset and use transport_mol_analyzer.py.

📊 Expected Results

With real data, you'll discover:

· MOL-Optimal stops: Bhf. Zoo, Ostkreuz (O(ℰ)=0.300)
· Problematic stops: Alexanderplatz (O(ℰ)=0.800)
· Network efficiency: S-Bahn outperforms U-Bahn ontologically
· Optimality ratio: Only 1.9% of stops are MOL-optimal

Cross-scale system analysis - transport_mol_demo.py
Reall MOL Transport Network Analysis - transport_mol_analyzer.py
