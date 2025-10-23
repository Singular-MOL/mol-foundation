#!/usr/bin/env python3
"""
MOL Demo - Historical Systems Analysis
Law of Minimal Ontological Load - Principle Demonstration
Official tool for MOL Foundation
"""

print("🧪 MOL DEMO: Historical Systems Analysis")
print("Law of Minimal Ontological Load - Principle Demonstration") 
print("=" * 60)

def run_demo_analysis():
    """Run MOL demonstration with historical cases"""
    
    historical_systems = [
        {"name": "Venetian Republic 1797", "territory": 6, "complexity": 7, "comm_time": 3, "centralization": 0.7},
        {"name": "Ottoman Empire 1922", "territory": 8, "complexity": 9, "comm_time": 5, "centralization": 0.9},
        {"name": "Austro-Hungary 1918", "territory": 7, "complexity": 10, "comm_time": 4, "centralization": 0.8},
        {"name": "Japanese Empire 1945", "territory": 7, "complexity": 8, "comm_time": 4, "centralization": 0.85},
    ]

    def calculate_O_E(territory, complexity, comm_time, centralization):
        """Calculate Ontological Load (simplified demo formula)"""
        size_complexity = territory * complexity * 0.1
        communication_load = comm_time ** 2 
        centralization_risk = (centralization - 0.8) * 10 if centralization > 0.8 else 0
        return size_complexity + communication_load + centralization_risk

    print("\n📊 MOL PREDICTION VS HISTORICAL OUTCOMES")
    print("System                | O(ℰ) | MOL Prediction | Actual Outcome | Status")
    print("-" * 75)

    correct = 0
    for system in historical_systems:
        O_E = calculate_O_E(
            system["territory"],
            system["complexity"],
            system["comm_time"], 
            system["centralization"]
        )

        # MOL prediction
        if O_E > 25:
            prediction = "COLLAPSE"
        elif O_E > 20:
            prediction = "CRISIS"
        else:
            prediction = "STABLE"

        # Historical reality
        reality = {
            "Venetian Republic 1797": "COLLAPSE",  # Napoleon invasion
            "Ottoman Empire 1922": "COLLAPSE",     # Official dissolution
            "Austro-Hungary 1918": "COLLAPSE",     # WWI dissolution  
            "Japanese Empire 1945": "CRISIS"       # Lost empire, state survived
        }

        actual = reality[system["name"]]
        status = "✅" if prediction == actual else "❌"
        if prediction == actual:
            correct += 1

        print(f"{system['name']:22} | {O_E:4.1f} | {prediction:13} | {actual:13} | {status}")

    accuracy = correct / len(historical_systems)
    
    print(f"\n🎯 DEMO ACCURACY: {correct}/{len(historical_systems)} = {accuracy:.0%}")
    print("💡 MOL Principle: Systems collapse when O(ℰ) > 25")
    
    print("\n⚠️  DEMO LIMITATIONS:")
    print("• Simplified O(ℰ) formula for demonstration")
    print("• External factors (wars, leaders) not included") 
    print("• Real analysis requires comprehensive data")
    print("• See real implementation for full accuracy")

def main():
    print("\n🔬 MOL FOUNDATION - PRINCIPLE DEMONSTRATION")
    print("Repository: https://github.com/Singular-MOL/mol-foundation")
    
    run_demo_analysis()
    
    print(f"\n🚀 For real analysis with GDP data:")
    print("   Run: python tools/mol_real_analyzer.py")
    print("   Requires: GDP dataset from Kaggle")

if __name__ == "__main__":
    main()
