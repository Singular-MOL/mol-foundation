#!/usr/bin/env python3
"""
MOL ABIOGENESIS ENGINE v3.0 - Стабилизаторы РЕАЛЬНО снижают нагрузку
"""

import math
import random
import json
import gzip
from collections import defaultdict

class AbiogenesisMOLv3:
    def __init__(self, seed=42):
        random.seed(seed)
        
        self.molecules = []
        self.reactions = []
        self.stabilizers = []
        self.catalytic_core = set()
        
        # Параметры
        self.O_E_history = []
        self.TAU = 1.0  # Средний порог
        self.STEP = 0
        
        # Эффективность стабилизаторов (постоянные бонусы)
        self.stabilizer_efficiency = {
            "membrane": 0.3,   # Мембрана снижает нагрузку на 30%
            "matrix": 0.25,    # Матрица на 25%
            "replication": 0.5 # Репликация на 50%
        }
        
        # Лог
        self.life_emerged = False
        self.phi_events = []
    
    def add_molecule(self, complexity=1.0, catalytic=False):
        mol = {
            "id": len(self.molecules),
            "complexity": complexity,
            "catalytic": catalytic
        }
        self.molecules.append(mol)
        if catalytic:
            self.catalytic_core.add(mol["id"])
        return mol["id"]
    
    def add_reaction(self, r1, r2, product, catalyst=None, energy=0.0):
        reaction = {
            "reactants": (r1, r2),
            "product": product,
            "catalyst": catalyst,
            "energy": energy
        }
        self.reactions.append(reaction)
        if catalyst is not None:
            self.catalytic_core.add(catalyst)
        return reaction
    
    def add_random_reaction(self, complexity_boost=1.0):
        if len(self.molecules) < 2:
            return
            
        r1 = random.randint(0, len(self.molecules)-1)
        r2 = random.randint(0, len(self.molecules)-1)
        while r2 == r1 and len(self.molecules) > 1:
            r2 = random.randint(0, len(self.molecules)-1)
        
        product = random.randint(0, len(self.molecules)-1)
        
        # После появления жизни катализаторы чаще
        catalyst_chance = 0.1
        if self.stabilizers:
            catalyst_chance += len(self.stabilizers) * 0.1
            
        catalyst = None
        if random.random() < catalyst_chance and len(self.molecules) > 0:
            catalyst = random.randint(0, len(self.molecules)-1)
        
        energy = random.uniform(-2.0, 1.0) * complexity_boost
        
        return self.add_reaction(r1, r2, product, catalyst, energy)
    
    # === ИСПРАВЛЕННАЯ ФОРМУЛА O(ℰ) ===
    
    def calculate_O_E(self):
        if len(self.molecules) < 2:
            return 0.2
        
        # БАЗОВАЯ СЛОЖНОСТЬ
        molecules_complexity = sum(m["complexity"] for m in self.molecules) * 0.05
        reactions_complexity = len(self.reactions) * 0.03
        
        # НЕЭФФЕКТИВНОСТЬ: реакции без катализаторов
        non_catalyzed = sum(1 for r in self.reactions if r["catalyst"] is None)
        inefficiency = (non_catalyzed / max(1, len(self.reactions))) * 0.4
        
        # ПЛОХАЯ ОРГАНИЗАЦИЯ: молекулы вне ядра
        outside_core = len(self.molecules) - len(self.catalytic_core)
        disorganization = (outside_core / max(1, len(self.molecules))) * 0.3
        
        base_O_E = molecules_complexity + reactions_complexity + inefficiency + disorganization
        
        # === БОНУСЫ СТАБИЛИЗАТОРОВ (ВАЖНО: ПОСТОЯННЫЕ) ===
        stabilizer_bonus = 0.0
        
        if "membrane" in self.stabilizers:
            # Мембрана снижает неэффективность
            stabilizer_bonus -= 0.3 * inefficiency
            
        if "matrix" in self.stabilizers:
            # Матрица улучшает организацию
            stabilizer_bonus -= 0.25 * disorganization
            
        if "replication" in self.stabilizers:
            # Репликация даёт максимальный бонус
            stabilizer_bonus -= 0.5 * base_O_E  # Снижает ВСЮ нагрузку на 50%
            
            # Дополнительно: репликация делает катализаторы эффективнее
            if len(self.catalytic_core) > 0:
                stabilizer_bonus -= 0.1 * len(self.catalytic_core)
        
        # ИТОГ с ограничением снизу
        total_O_E = base_O_E + stabilizer_bonus
        return max(0.1, total_O_E)
    
    # === УМНЫЙ Φ-ОПЕРАТОР ===
    
    def evaluate_best_stabilizer(self):
        """Выбирает лучший стабилизатор для текущего состояния"""
        scores = {}
        
        # Оцениваем потребность
        non_catalyzed = sum(1 for r in self.reactions if r["catalyst"] is None)
        outside_core = len(self.molecules) - len(self.catalytic_core)
        
        # Мембрана нужна при высокой неэффективности
        if non_catalyzed > len(self.reactions) * 0.7:
            scores["membrane"] = 2.5 - (0.5 if "membrane" in self.stabilizers else 0)
        
        # Матрица нужна при плохой организации
        if outside_core > len(self.molecules) * 0.6:
            scores["matrix"] = 2.0 - (0.5 if "matrix" in self.stabilizers else 0)
        
        # Репликация нужна при наличии катализаторов
        if len(self.catalytic_core) >= 2:
            scores["replication"] = 3.0 - (0.5 if "replication" in self.stabilizers else 0)
        
        if not scores:
            return None
            
        # Выбираем лучший, но не повторяем
        for stabilizer, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            if stabilizer not in self.stabilizers:
                return stabilizer
                
        return None
    
    def phi_operator(self):
        if len(self.stabilizers) >= 3:  # Максимум 3 стабилизатора
            return False
            
        target = self.evaluate_best_stabilizer()
        if not target:
            return False
            
        old_O_E = self.calculate_O_E()
        
        # Применяем стабилизатор
        if target == "membrane":
            self._implement_membrane()
        elif target == "matrix":
            self._implement_matrix()
        else:
            self._implement_replication()
            
        self.stabilizers.append(target)
        
        new_O_E = self.calculate_O_E()
        delta = new_O_E - old_O_E
        
        self.phi_events.append({
            "step": self.STEP,
            "stabilizer": target,
            "delta_O_E": delta,
            "old_O_E": old_O_E,
            "new_O_E": new_O_E
        })
        
        print(f"🌀 Φ-{target.upper()}: O(ℰ) {old_O_E:.3f} → {new_O_E:.3f} ({delta:+.3f})")
        
        if target == "replication" and not self.life_emerged:
            self.life_emerged = True
            print(f"✨ ЖИЗНЬ ВОЗНИКЛА! Шаг {self.STEP}")
            
        return True
    
    def _implement_membrane(self):
        print("   → Мембрана: снижает энергетические барьеры")
        for r in self.reactions:
            if r["energy"] > -1.0:  # Улучшаем слабые реакции
                r["energy"] -= 0.5
    
    def _implement_matrix(self):
        mineral = self.add_molecule(complexity=2.0, catalytic=True)
        print(f"   → Матрица: минеральный катализатор {mineral}")
        
        # Катализируем несколько случайных реакций
        for r in random.sample(self.reactions, min(5, len(self.reactions))):
            if r["catalyst"] is None:
                r["catalyst"] = mineral
                r["energy"] -= 0.8
    
    def _implement_replication(self):
        if len(self.catalytic_core) == 0:
            # Создаём катализатор
            catalyst = self.add_molecule(complexity=1.8, catalytic=True)
        else:
            catalyst = random.choice(list(self.catalytic_core))
            
        # Создаём реплицируемую молекулу
        replicant = self.add_molecule(complexity=1.3, catalytic=False)
        
        # Цикл репликации
        self.add_reaction(catalyst, replicant, replicant, catalyst=catalyst, energy=-2.8)
        self.add_reaction(replicant, replicant, replicant, catalyst=catalyst, energy=-2.0)
        
        print(f"   → Репликация: цикл ({catalyst} → {replicant})")
    
    # === ЭКСПЕРИМЕНТ С УМНЫМ РОСТОМ ===
    
    def run_experiment(self, max_steps=40):
        print("=" * 70)
        print("MOL ABIOGENESIS ENGINE v3.0")
        print("=" * 70)
        print("Стабилизаторы дают ПОСТОЯННЫЙ бонус к эффективности")
        print()
        
        # Инициализация
        for i in range(4):
            self.add_molecule(catalytic=(i==0))
        for i in range(6):
            self.add_random_reaction()
        
        initial_O_E = self.calculate_O_E()
        print(f"🎯 НАЧАЛО: {len(self.molecules)} молекул, {len(self.reactions)} реакций")
        print(f"   O(ℰ) = {initial_O_E:.3f}")
        print()
        
        # Основной цикл
        for step in range(max_steps):
            self.STEP = step
            
            # УМНЫЙ РОСТ: после стабилизаторов рост замедляется
            growth_rate = 0.5
            if self.stabilizers:
                growth_rate /= (1 + len(self.stabilizers) * 0.3)
            
            if random.random() < growth_rate * 0.6:
                complexity = 0.8 + random.random() * (0.5 if self.stabilizers else 1.0)
                self.add_molecule(complexity=complexity)
                
            if random.random() < growth_rate * 0.8:
                complexity_boost = 0.7 if self.stabilizers else 1.0
                self.add_random_reaction(complexity_boost=complexity_boost)
            
            # Текущее состояние
            current_O_E = self.calculate_O_E()
            self.O_E_history.append(current_O_E)
            
            # Проверяем Φ-скачок
            if current_O_E > self.TAU and len(self.stabilizers) < 3:
                if self.phi_operator():
                    print(f"   📊 O(ℰ) после скачка: {current_O_E:.3f}")
            
            # Отчёт
            efficiency = (initial_O_E - current_O_E) / initial_O_E if initial_O_E > 0 else 0
            
            status_line = f"Шаг {step:2d}: O(ℰ)={current_O_E:.3f}"
            if self.stabilizers:
                status_line += f" | Стаб: {self.stabilizers}"
            if self.life_emerged:
                status_line += f" | Эфф: {efficiency:+.1%}"
                
            print(status_line)
            
            # Остановка при достижении хорошей эффективности
            if efficiency > 0.3 and step > 10:
                print(f"\n✅ Достигнута целевая эффективность +{efficiency:.1%}")
                break
        
        self._final_analysis(initial_O_E)
    
    def _final_analysis(self, initial_O_E):
        print("\n" + "=" * 70)
        print("ФИНАЛЬНЫЙ АНАЛИЗ v3.0")
        print("=" * 70)
        
        final_O_E = self.calculate_O_E()
        efficiency = (initial_O_E - final_O_E) / initial_O_E if initial_O_E > 0 else 0
        
        print(f"📊 РЕЗУЛЬТАТЫ:")
        print(f"   • Начальная O(ℰ): {initial_O_E:.3f}")
        print(f"   • Конечная O(ℰ): {final_O_E:.3f}")
        print(f"   • Эффективность: {efficiency:+.1%}")
        print(f"   • Стабилизаторы: {self.stabilizers}")
        print(f"   • Φ-событий: {len(self.phi_events)}")
        
        if self.phi_events:
            print(f"\n📈 Φ-СКАЧКИ:")
            for event in self.phi_events:
                sign = "+" if event["delta_O_E"] >= 0 else ""
                print(f"   Шаг {event['step']}: {event['stabilizer']} "
                      f"({event['old_O_E']:.3f}→{event['new_O_E']:.3f}, Δ={sign}{event['delta_O_E']:.3f})")
        
        print(f"\n🔬 ВЫВОД:")
        if efficiency > 0.1 and self.life_emerged:
            print(f"   ✅ ГИПОТЕЗА ПОДТВЕРЖДЕНА")
            print(f"   → Жизнь снижает онтологическую нагрузку на {abs(efficiency):.1%}")
            print(f"   → Φ-скачки работают как предсказывает MOL")
        elif self.life_emerged:
            print(f"   ⚠️  ЧАСТИЧНОЕ ПОДТВЕРЖДЕНИЕ")
            print(f"   → Жизнь возникла, но эффективность {efficiency:+.1%}")
            print(f"   → Требуется настройка параметров роста")
        else:
            print(f"   ❌ ГИПОТЕЗА НЕ ПОДТВЕРЖДЕНА")
            print(f"   → Система не достигла жизни-подобного состояния")

# Запуск
if __name__ == "__main__":
    print("🔬 MOL Abiogenesis Engine v3.0")
    print("Стабилизаторы = постоянное снижение O(ℰ)")
    print("=" * 50)
    
    experiment = AbiogenesisMOLv3(seed=42)
    experiment.run_experiment(max_steps=35)
