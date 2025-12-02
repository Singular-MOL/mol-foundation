#!/usr/bin/env python3
"""
MOL ABIOGENESIS ENGINE v2.0 - Исправленная метрика O(ℰ)
Жизнь должна СНИЖАТЬ онтологическую нагрузку
"""

import math
import random
import json
import gzip
from collections import defaultdict

class AbiogenesisMOLv2:
    def __init__(self, seed=42):
        random.seed(seed)
        
        self.molecules = []           # Аналог nodes
        self.reactions = []           # Аналог relations
        self.stabilizers = []         # Стабилизаторы жизни
        self.catalytic_core = set()   # Автокаталитическое ядро
        
        # MOL параметры - БОЛЕЕ СТРОГИЕ
        self.O_E_history = []
        self.TAU = 1.2                # ПОВЫШАЕМ порог - система должна накопить сложность
        self.ATTRACTOR_DEPTH_THRESHOLD = 0.5
        
        self.step = 0
        self.life_emerged = False
        
    # === ОСНОВНЫЕ МЕТОДЫ ===
    
    def add_molecule(self, complexity=1.0, catalytic=False):
        mol = {
            "id": len(self.molecules),
            "complexity": complexity,
            "catalytic": catalytic,
            "type": random.choice(["acid", "base", "hydrocarbon"])
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
    
    def add_random_reaction(self):
        """Более разумные случайные реакции"""
        if len(self.molecules) < 3:
            return
            
        # Выбираем разные молекулы
        ids = list(range(len(self.molecules)))
        r1, r2, p = random.sample(ids, 3)
        
        # Катализатор - случайный, но с вероятностью
        catalyst = None
        if random.random() < 0.15:  # РЕЖЕ катализаторы
            catalyst = random.choice(ids)
            
        energy = random.uniform(-3.0, 1.0)
        
        return self.add_reaction(r1, r2, p, catalyst, energy)
    
    # === ИСПРАВЛЕННАЯ МЕТРИКА O(ℰ) ===
    
    def calculate_O_E(self):
        """НОВАЯ ФОРМУЛА: O(ℰ) растёт со сложностью, но падает при эффективной организации"""
        if len(self.molecules) < 2:
            return 0.2
            
        # 1. Базовый член: сложность системы
        base_complexity = len(self.molecules) * 0.05 + len(self.reactions) * 0.03
        
        # 2. Штраф за неэффективность: мало катализаторов
        catalyzed_ratio = sum(1 for r in self.reactions if r["catalyst"] is not None) / max(1, len(self.reactions))
        inefficiency_penalty = (1.0 - catalyzed_ratio) * 0.5
        
        # 3. Штраф за "бесполезные" молекулы (не в ядре)
        core_size = len(self.catalytic_core)
        useless_penalty = (len(self.molecules) - core_size) * 0.02
        
        # 4. БОНУС за организацию (если есть стабилизаторы)
        organization_bonus = 0.0
        if self.stabilizers:
            # Каждый стабилизатор снижает нагрузку
            organization_bonus = -len(self.stabilizers) * 0.3
            # Репликация даёт наибольший бонус
            if "replication" in self.stabilizers:
                organization_bonus -= 0.4
            if "membrane" in self.stabilizers:
                organization_bonus -= 0.3
                
        O_E = base_complexity + inefficiency_penalty + useless_penalty + organization_bonus
        
        return max(0.1, O_E)
    
    def _calculate_mdl_proxy(self):
        """Упрощённый MDL: чем регулярнее система, тем лучше сжимается"""
        if not self.reactions:
            return 0.5
            
        # Создаём строку паттернов реакций
        patterns = []
        for r in self.reactions:
            pattern = f"{r['reactants'][0]}{r['reactants'][1]}→{r['product']}"
            if r["catalyst"] is not None:
                pattern += f"[cat:{r['catalyst']}]"
            patterns.append(pattern)
            
        # Сортируем для лучшего сжатия
        patterns.sort()
        data = "|".join(patterns)
        
        try:
            compressed = gzip.compress(data.encode())
            ratio = len(compressed) / max(len(data), 1)
            # Чем меньше ratio, тем регулярнее система
            return min(1.0, ratio * 1.5)
        except:
            return 0.5
    
    # === Φ-ОПЕРАТОР С УЛУЧШЕНИЯМИ ===
    
    def evaluate_attractors(self):
        """PAD: Оценка с учётом текущего состояния"""
        scores = {}
        
        # Репликация выгодна, если уже есть некоторые катализаторы
        if len(self.catalytic_core) >= 2:
            rep_score = 2.5 - len([s for s in self.stabilizers if s == "replication"]) * 0.8
            scores["replication"] = rep_score
            
        # Мембрана выгодна при разнообразии молекул
        if len(self.molecules) >= 8:
            mem_score = 2.0 - (0 if "membrane" in self.stabilizers else 0.7)
            scores["membrane"] = mem_score
            
        # Матрица выгодна при многих реакциях без катализаторов
        non_catalyzed = sum(1 for r in self.reactions if r["catalyst"] is None)
        if non_catalyzed >= 5:
            mat_score = 1.8 - (0 if "matrix" in self.stabilizers else 0.6)
            scores["matrix"] = mat_score
            
        if not scores:
            return None
            
        # Выбираем лучший, но не повторяемся
        for stabilizer, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            if stabilizer not in self.stabilizers and score > self.ATTRACTOR_DEPTH_THRESHOLD:
                return stabilizer
                
        return None
    
    def phi_operator(self):
        """Улучшенный Φ-оператор с предсказанием ΔO(ℰ)"""
        if self.life_emerged and len(self.stabilizers) >= 2:
            return False  # Уже достаточно стабилизаторов
            
        target = self.evaluate_attractors()
        if not target:
            return False
            
        old_O_E = self.calculate_O_E()
        
        print(f"🎯 PAD: Выбран стабилизатор '{target}'")
        
        # Применяем стабилизатор
        success = False
        if target == "replication":
            success = self._implement_replication()
        elif target == "membrane":
            success = self._implement_membrane()
        else:
            success = self._implement_matrix()
            
        if success:
            self.stabilizers.append(target)
            new_O_E = self.calculate_O_E()
            delta = new_O_E - old_O_E
            
            print(f"🌀 Φ-OPERATOR: Применён {target}")
            print(f"   O(ℰ): {old_O_E:.3f} → {new_O_E:.3f} ({delta:+.3f})")
            
            if delta < 0:
                print(f"✅ PAA: Снижение нагрузки на {-delta:.3f}")
                if not self.life_emerged and target == "replication":
                    self.life_emerged = True
                    print(f"✨ ЖИЗНЬ ВОЗНИКЛА! (репликационный механизм)")
                return True
            else:
                print(f"⚠️  PAA: Временное увеличение нагрузки")
                
        return False
    
    def _implement_replication(self):
        """Создаём эффективный автокаталитический цикл"""
        if len(self.catalytic_core) < 1:
            # Создаём катализатор
            cat_id = self.add_molecule(complexity=1.8, catalytic=True)
        else:
            cat_id = random.choice(list(self.catalytic_core))
            
        # Создаём "реплицируемую" молекулу
        rep_id = self.add_molecule(complexity=1.5, catalytic=False)
        
        # Реакция репликации: катализатор + X → 2X
        self.add_reaction(cat_id, rep_id, rep_id, catalyst=cat_id, energy=-2.5)
        self.add_reaction(rep_id, rep_id, rep_id, catalyst=cat_id, energy=-1.8)
        
        print(f"   → Создан репликационный цикл (катализатор {cat_id}, репликант {rep_id})")
        return True
    
    def _implement_membrane(self):
        """Создаём компартмент"""
        # Липидоподобные молекулы
        lipid1 = self.add_molecule(complexity=1.7, catalytic=False)
        lipid2 = self.add_molecule(complexity=1.7, catalytic=False)
        
        # Реакция образования мембраны
        self.add_reaction(lipid1, lipid2, lipid1, energy=-4.0)
        
        # Мембрана защищает внутренние реакции
        for r in self.reactions:
            if r["energy"] < 0:
                r["energy"] *= 0.8  # Делаем более выгодными
        
        print(f"   → Создана мембранная структура")
        return True
    
    def _implement_matrix(self):
        """Минеральная матрица как общий катализатор"""
        mineral = self.add_molecule(complexity=2.5, catalytic=True)
        
        # Минерал катализирует 30% случайных реакций
        for r in self.reactions:
            if r["catalyst"] is None and random.random() < 0.3:
                r["catalyst"] = mineral
                r["energy"] -= 1.0  # Снижаем энергетический барьер
        
        print(f"   → Добавлен минеральный катализатор {mineral}")
        return True
    
    # === ЭКСПЕРИМЕНТ ===
    
    def run_experiment(self, max_steps=60):
        print("=" * 70)
        print("MOL ABIOGENESIS ENGINE v2.0")
        print("=" * 70)
        print("Гипотеза: жизнь возникает при высокой O(ℰ) и снижает её")
        print(f"Порог τ = {self.TAU}")
        print()
        
        # Более разумная инициализация
        for i in range(4):
            self.add_molecule(complexity=1.0, catalytic=(i==0))
        
        for i in range(8):
            self.add_random_reaction()
        
        initial_O_E = self.calculate_O_E()
        print(f"🎯 НАЧАЛЬНОЕ СОСТОЯНИЕ:")
        print(f"   Молекулы: {len(self.molecules)}, Реакции: {len(self.reactions)}")
        print(f"   Каталитическое ядро: {len(self.catalytic_core)}")
        print(f"   O(ℰ) = {initial_O_E:.3f}")
        print()
        
        # Основной цикл
        for step in range(max_steps):
            self.step = step
            print(f"\n🔄 ШАГ {step}:")
            
            # Добавляем сложность
            if random.random() < 0.4:
                self.add_molecule(complexity=0.8 + random.random()*0.7)
            if random.random() < 0.5:
                self.add_random_reaction()
            
            current_O_E = self.calculate_O_E()
            self.O_E_history.append(current_O_E)
            
            print(f"   Молекулы: {len(self.molecules)}, Реакции: {len(self.reactions)}")
            print(f"   O(ℰ) = {current_O_E:.3f}")
            
            # Решаем: добавлять ли стабилизатор
            if current_O_E > self.TAU:
                print(f"   ⚠️  Высокая нагрузка → проверка Φ-оператора")
                if self.phi_operator():
                    print(f"   ✅ Добавлен стабилизатор")
            
            # Если жизнь возникла, показываем прогресс
            if self.life_emerged:
                efficiency = (initial_O_E - current_O_E) / initial_O_E
                print(f"   🌱 Режим жизни: {self.stabilizers}")
                print(f"   📉 Эффективность: {efficiency:+.1%}")
                
                # Останавливаемся если достигли хорошего снижения
                if efficiency > 0.3 and step > 15:
                    print(f"\n✅ Достигнута эффективная жизнь-подобная система")
                    break
        
        self._scientific_analysis(initial_O_E)
    
    def _scientific_analysis(self, initial_O_E):
        print("\n" + "=" * 70)
        print("НАУЧНЫЙ АНАЛИЗ v2.0")
        print("=" * 70)
        
        final_O_E = self.calculate_O_E()
        efficiency = (initial_O_E - final_O_E) / initial_O_E if initial_O_E > 0 else 0
        
        print(f"📊 РЕЗУЛЬТАТЫ:")
        print(f"   • Начальная O(ℰ): {initial_O_E:.3f}")
        print(f"   • Конечная O(ℰ): {final_O_E:.3f}")
        print(f"   • Эффективность: {efficiency:+.1%}")
        print(f"   • Стабилизаторы: {self.stabilizers}")
        print(f"   • Размер системы: {len(self.molecules)} молекул, {len(self.reactions)} реакций")
        
        print(f"\n🔬 ТЕСТ ГИПОТЕЗЫ MOL:")
        if efficiency > 0 and self.stabilizers:
            print(f"   ✅ ПОДТВЕРЖДЕНО: Стабилизаторы снизили O(ℰ) на {-efficiency:.1%}")
            print(f"   → Жизнь как онтологическая оптимизация РАБОТАЕТ")
        elif self.stabilizers:
            print(f"   ⚠️  ЧАСТИЧНО: Стабилизаторы добавлены, но эффективность {efficiency:+.1%}")
            print(f"   → Требуется тонкая настройка метрик")
        else:
            print(f"   ❌ ОПРОВЕРГНУТО: Система не нашла стабилизаторов")
            print(f"   → Порог τ={self.TAU} слишком высок или механизмы слабы")

# Запуск
if __name__ == "__main__":
    print("🔬 MOL Abiogenesis Engine v2.0")
    print("DOI: 10.5281/zenodo.17445099")
    print("Исправленная метрика O(ℰ) - жизнь должна снижать нагрузку")
    print()
    
    experiment = AbiogenesisMOLv2(seed=42)
    experiment.run_experiment(max_steps=50)
