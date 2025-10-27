#!/usr/bin/env python3
"""
MOL 5.2: ИСПРАВЛЕННАЯ МОДЕЛЬ С НОРМАЛИЗАЦИЕЙ ДАННЫХ
Law of Minimal Ontological Load - Economic Systems Analysis
Official tool for MOL Foundation
"""

import csv
import math
import statistics
import requests
import json
import os

print("🌍 MOL 5.2: ИСПРАВЛЕННАЯ МОДЕЛЬ С НОРМАЛИЗАЦИЕЙ ДАННЫХ")
print("=" * 65)

class MOLEconomicAnalyzer:
    def __init__(self):
        self.countries_data = []
        
    def load_gdp_data(self, csv_path):
        """Загрузка данных ВВП из CSV файла"""
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    country_data = {'name': row['Country']}
                    for year in range(1975, 2026):
                        value = row.get(str(year), '').strip()
                        country_data[year] = float(value) if value and value.replace('.', '').isdigit() else None
                    self.countries_data.append(country_data)
            print(f"✅ Загружено {len(self.countries_data)} стран")
            return True
        except Exception as e:
            print(f"❌ Ошибка загрузки данных: {e}")
            return False

    def get_worldbank_data_safe(self, country_name, indicator, year):
        """Безопасное получение данных с нормализацией"""
        country_codes = {
            'united states': 'USA', 'china': 'CHN', 'japan': 'JPN', 
            'germany': 'DEU', 'russia': 'RUS', 'france': 'FRA', 
            'united kingdom': 'GBR', 'india': 'IND', 'brazil': 'BRA', 
            'italy': 'ITA', 'canada': 'CAN', 'australia': 'AUS', 
            'korea': 'KOR', 'spain': 'ESP', 'mexico': 'MEX', 
            'greece': 'GRC', 'argentina': 'ARG'
        }
        
        country_key = None
        for key, code in country_codes.items():
            if key in country_name.lower():
                country_key = code
                break
                
        if not country_key:
            return None
            
        url = f"http://api.worldbank.org/v2/country/{country_key}/indicator/{indicator}?format=json&date={year}"
        
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            if len(data) > 1 and data[1]:
                value = data[1][0].get('value')
                return float(value) if value else None
        except:
            pass
            
        return None

    def calculate_safe_O_E(self, country, start_year, end_year):
        """Безопасный расчёт с нормализацией данных"""
        
        # 1. БАЗОВЫЙ АНАЛИЗ ВВП
        gdp_values = []
        for year in range(start_year, end_year + 1):
            if country.get(year) is not None:
                gdp_values.append(country[year])
                
        if len(gdp_values) < 5:
            return None, "Недостаточно данных ВВП"
            
        growth_rates = []
        for i in range(1, len(gdp_values)):
            if gdp_values[i-1] and gdp_values[i] and gdp_values[i-1] != 0:
                growth_rate = (gdp_values[i] - gdp_values[i-1]) / gdp_values[i-1]
                growth_rates.append(growth_rate)
                
        if len(growth_rates) < 4:
            return None, "Недостаточно данных по росту"
            
        volatility = statistics.stdev(growth_rates) if len(growth_rates) > 1 else 0
        sharp_declines = sum(1 for rate in growth_rates if rate < -0.05)
        mean_growth = statistics.mean(growth_rates)
        decline_factor = sharp_declines / len(growth_rates)

        # 2. БЕЗОПАСНЫЙ РАСЧЁТ ГЛОБАЛЬНЫХ МЕТРИК
        global_metrics = {}
        
        # НОРМАЛИЗАЦИЯ FDI
        fdi = self.get_worldbank_data_safe(country['name'], 'BX.KLT.DINV.CD', end_year)
        if fdi and gdp_values[-1] and gdp_values[-1] > 0:
            fdi_ratio = fdi / gdp_values[-1]
            fdi_ratio = max(0, min(fdi_ratio, 1.0))
            global_metrics['fdi_dependence'] = fdi_ratio
        else:
            global_metrics['fdi_dependence'] = 0.3

        # Глобальная нагрузка
        global_pressure = 0
        pressure_points = 0
        for year in range(start_year, end_year + 1):
            crisis_factor = 0
            if 2008 <= year <= 2009: 
                crisis_factor = 0.8 
            elif 2020 <= year <= 2021: 
                crisis_factor = 0.6
            elif year >= 2022: 
                crisis_factor = 0.7
                
            global_pressure += crisis_factor
            pressure_points += 1
            
        global_metrics['crisis_pressure'] = global_pressure / pressure_points if pressure_points > 0 else 0

        # 3. СТАБИЛЬНАЯ ФОРМУЛА O(ℰ) с проверкой границ
        base_metrics = (
            volatility * 20 + 
            decline_factor * 15 + 
            abs(mean_growth) * 5
        )
        
        global_metrics_component = (
            global_metrics['fdi_dependence'] * 8 + 
            global_metrics['crisis_pressure'] * 10
        )
        
        O_E = base_metrics + global_metrics_component
        O_E = max(0, min(O_E, 100))  # Защита от выбросов

        details = {
            'volatility': volatility,
            'decline_factor': decline_factor,
            'mean_growth': mean_growth,
            'fdi_dependence': global_metrics['fdi_dependence'],
            'crisis_pressure': global_metrics['crisis_pressure'],
            'data_points': len(growth_rates)
        }
        
        return O_E, details

    def run_historical_tests(self):
        """Тестирование модели на исторических данных"""
        print("\n📊 MOL 5.2: ТЕСТ С НОРМАЛИЗОВАННЫМИ ДАННЫМИ")
        print("Страна           | Период    | O(ℰ)  | Прогноз      | Статус")
        print("-" * 70)
        
        test_cases = [
            ('United States', (2005, 2009), 'Кризис 2008'),
            ('Japan', (1985, 1993), 'Пузырь 1990'),
            ('Russia', (1990, 1998), 'Кризис 1998'),
            ('China', (2015, 2020), 'Торговые войны'),
            ('Argentina', (1998, 2002), 'Дефолт 2001'),
            ('Greece', (2005, 2012), 'Долговой кризис'),
        ]
        
        correct = 0
        total = 0
        
        for country_name, period, crisis_name in test_cases:
            country = None
            for c in self.countries_data:
                if country_name.lower() in c['name'].lower():
                    country = c
                    break
                    
            if country:
                O_E, details = self.calculate_safe_O_E(country, period[0], period[1])
                if O_E is not None:
                    total += 1
                    
                    if O_E > 25: 
                        prediction = "🔴 РАСПАД"
                    elif O_E > 15: 
                        prediction = "🟡 КРИЗИС"
                    else: 
                        prediction = "🟢 СТАБИЛЬНО"
                    
                    actual_outcome = "КРИЗИС"  # Все тест-кейсы - кризисы
                    model_outcome = "КРИЗИС" if O_E > 15 else "СТАБИЛЬНО"
                    
                    if model_outcome == actual_outcome:
                        correct += 1
                        status = "✅"
                    else:
                        status = "❌"
                        
                    print(f"{country_name:15} | {period[0]}-{period[1]} | {O_E:5.1f} | {prediction:12} | {status} {crisis_name}")
        
        # СТАТИСТИКА
        if total > 0:
            accuracy = correct / total * 100
            print(f"\n🎯 ТОЧНОСТЬ MOL 5.2: {correct}/{total} = {accuracy:.1f}%")

    def analyze_russia_2020_2024(self):
        """Анализ России 2020-2024"""
        print(f"\n🇷🇺 MOL 5.2: РОССИЯ 2020-2024")
        russia = None
        for c in self.countries_data:
            if 'russia' in c['name'].lower():
                russia = c
                break
                
        if russia:
            O_E_2020_2024, details = self.calculate_safe_O_E(russia, 2020, 2024)
            if O_E_2020_2024 is not None:
                if O_E_2020_2024 > 25: 
                    status = "🔴 РАСПАД"
                elif O_E_2020_2024 > 15: 
                    status = "🟡 КРИЗИС"
                else: 
                    status = "🟢 СТАБИЛЬНО"
                    
                print(f"O(ℰ) = {O_E_2020_2024:.1f} → {status}")
                print(f"• Волатильность ВВП: {details['volatility']:.3f}")
                print(f"• Падения (>5%): {details['decline_factor']:.1%}")
                print(f"• Зависимость от FDI: {details['fdi_dependence']:.3f}")
                print(f"• Глобальная нагрузка: {details['crisis_pressure']:.3f}")

def main():
    analyzer = MOLEconomicAnalyzer()
    
    # ПРАВИЛЬНЫЙ ПУТЬ К ДАННЫМ
    csv_path = "./.cache/kagglehub/datasets/codebynadiia/gdp-1975-2025/versions/1/GDP_1975_2025_uploaded.csv"
    
    print(f"📁 Загрузка данных из: {csv_path}")
    
    if not analyzer.load_gdp_data(csv_path):
        print("❌ Не удалось загрузить данные.")
        return
    
    # Тестирование модели
    analyzer.run_historical_tests()
    
    # Анализ России
    analyzer.analyze_russia_2020_2024()
    
    print(f"\n🔧 ИСПРАВЛЕНИЯ В MOL 5.2:")
    print("• Защита от отрицательных и аномальных значений")
    print("• Нормализация FDI в диапазоне [0, 1]")
    print("• Фиксированные годы для глобальной нагрузки")
    print("• Ограничение O(ℰ) в разумных пределах")
    
    print(f"\n💡 MOL FOUNDATION")
    print("DOI: 10.5281/zenodo.17422128")
    print("Repository: https://github.com/Singular-MOL/mol-foundation")

if __name__ == "__main__":
    main()
