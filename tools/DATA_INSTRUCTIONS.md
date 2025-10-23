# MOL Real Analyzer - Data Instructions

## 📊 Required Dataset

**Dataset:** GDP by Country 1975-2025  
**Source:** Kaggle - https://www.kaggle.com/datasets/codebynadiia/gdp-1975-2025  
**File:** `GDP_1975_2025_uploaded.csv`

## 🚀 Setup Instructions

### 1. Download Dataset
```bash
# Option 1: Kaggle CLI
kaggle datasets download -d codebynadiia/gdp-1975-2025

# Option 2: Manual download
# Visit: https://www.kaggle.com/datasets/codebynadiia/gdp-1975-2025
# Click "Download" and extract CSV file
2. File Structure

```
/mol-foundation/
├── /tools/
│   ├── mol_demo.py              # Demo version (works immediately)
│   ├── mol_real_analyzer.py     # Full version (requires data)
│   └── DATA_INSTRUCTIONS.md     # This file
└── /data/                       # Create this folder
    └── GDP_1975_2025_uploaded.csv  # Place dataset here
    3. Run Analysis
    # Demo version (immediate results)
python tools/mol_demo.py

# Full version (requires dataset)
python tools/mol_real_analyzer.py
🔍 Dataset Description

· 208 countries and territories
· 1975-2025 annual GDP data (billions USD)
· Includes historical states (USSR, Yugoslavia, etc.)
· IMF and World Bank sources
· Missing data handled appropriately

📈 What MOL Analyzer Does

1. Loads real GDP data for accurate O(ℰ) calculation
2. Calculates economic metrics: volatility, growth patterns, crisis detection
3. Integrates World Bank data for FDI analysis
4. Predicts system stability based on ontological load thresholds

🎯 Quick Start

For immediate demonstration, use mol_demo.py.
For real economic analysis, download dataset and use mol_real_analyzer.py.
