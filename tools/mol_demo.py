#!/usr/bin/env python3
"""
MOL Demo - Historical Systems Analysis
Law of Minimal Ontological Load - Principle Demonstration
Official tool for MOL Foundation
"""

print("🧪 MOL DEMO: Historical Systems Validation")
print("Law of Minimal Ontological Load - Principle Demonstration") 
print("=" * 65)

def run_demo():
    """Run MOL demonstration with historical cases"""
    
    historical_systems = [
        {"name": "Venetian Republic 1797", "territory": 6, "complexity": 7, "comm_time": 3, "centralization": 0.7},
        {"name": "Ottoman Empire 1922", "territory": 8, "complexity": 9, "comm_time": 5, "centralization": 0.9},
        {"name": "Austro-Hungary 1918", "territory": 7, "complexity": 10, "comm_time": 4, "centralization": 0.8},
        {"name": "Japanese Empire 1945", "territory": 7, "complexity": 8, "comm_time": 4, "centralization": 0.85},
    ]

    def calculate_O_E(territory, complexity, comm_time, centralization):
        size_complexity = territory * complexity * 0.1
        communication_load = comm_time ** 2 
        centralization_risk = (centralization - 0.8) * 10 if centralization > 0.8 else 0
        return size_complexity + communication_load + centralization_risk

    print("\n📊 MOL PREDICTION VS HISTORICAL REALITY")
    print("System                | O(ℰ) | Prediction  | Actual Outcome | Status")
    print("-" * 75)

    for system in historical_systems:
        O_E = calculate_O_E(
            system["territory"], system["complexity"], 
            system["comm_time"], system["centralization"]
        )

        if O_E > 25: prediction = "COLLAPSE"
        elif O_E > 20: prediction = "CRISIS"
        else: prediction = "STABLE"

        real_outcomes = {
            "Venetian Republic 1797": "COLLAPSE",  # External factor: Napoleon
            "Ottoman Empire 1922": "COLLAPSE",     # Systemic collapse  
            "Austro-Hungary 1918": "COLLAPSE",     # WWI dissolution
            "Japanese Empire 1945": "CRISIS"       # Lost empire, state survived
        }

        actual = real_outcomes[system["name"]]
        status = "✅" if prediction == actual else "❌"

        print(f"{system['name']:22} | {O_E:4.1f} | {prediction:10} | {actual:14} | {status}")

    print(f"\n💡 DEMONSTRATION NOTES:")
    print("• O(ℰ) > 25 predicts system collapse")
    print("• Venetian Republic: External factor (Napoleon) not captured in model")
    print("• Austro-Hungary: Close to threshold (23.0), WWI accelerated collapse")
    print("• Demonstrates MOL principle - real implementation uses economic data")

def main():
    print("\n🔬 MOL FOUNDATION - PRINCIPLE DEMONSTRATION")
    print("This demo shows the CORE MOL principle using simplified parameters")
    print("For REAL economic analysis with GDP data, use: mol_real_analyzer.py")
    print("DOI: 10.5281/zenodo.17422128")
    
    run_demo()
    
    print(f"\n🚀 Real implementation uses:")
    print("• GDP data from Kaggle: 'GDP by Country 1975-2025'")
    print("• World Bank FDI statistics") 
    print("• Historical volatility analysis")
    print("• Download dataset: https://www.kaggle.com/datasets/codebynadiia/gdp-1975-2025")

if __name__ == "__main__":
    main()
