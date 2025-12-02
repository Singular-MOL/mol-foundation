#!/usr/bin/env python3
"""
MOL ABIOGENESIS ENGINE - From Chemical Chaos to Life
Структурный аналог mol_genesis_engine.py для абиогенеза
"""

import math
import random
import json
import gzip
from collections import defaultdict, Counter
import numpy as np

class AbiogenesisMOL:
    def __init__(self, seed=42):
        random.seed(seed)
        np.random.seed(seed)
        
        # Основные структуры (аналог космогенеза)
        self.molecules = []           # Аналог nodes
        self.reactions = []           # Аналог relations
        self.stabilizers = []         # Аналог dimensions: ['replication','membrane','matrix']
        self.catalytic_core = set()   # Автокаталитическое ядро
        
        # MOL параметры
        self.O_E_history = []
        self.TAU = 0.70               # Порог из белковых экспериментов
        self.ATTRACTOR_DEPTH_THRESHOLD = 0.3
        
        # Диагностика
        self.phase_log = []
        self.step = 0
        
    # === БАЗОВАЯ ХИМИЯ ===
    
    def add_molecule(self, complexity=1.0, catalytic_potential=0.1):
        """Добавить молекулу в систему"""
        mol = {
            "id": len(self.molecules),
            "complexity": complexity,
            "catalytic_potential": catalytic_potential,
            "type": random.choice(["acid", "base", "hydrocarbon", "polymer_fragment"])
        }
        self.molecules.append(mol)
        return mol["id"]
    
    def add_random_reaction(self):
        """Добавить случайную реакцию между молекулами"""
        if len(self.molecules) < 2:
            return
            
        # Выбираем реагенты
        r1 = random.randint(0, len(self.molecules)-1)
        r2 = random.randint(0, len(self.molecules)-1)
        while r2 == r1 and len(self.molecules) > 1:
            r2 = random.randint(0, len(self.molecules)-1)
            
        # Продукт - либо существующая, либо новая молекула
        if random.random() < 0.3 and len(self.molecules) < 20:
            # Создаём новую молекулу как продукт
            p = self.add_molecule(complexity=1.2)
        else:
            # Используем существующую
            p = random.randint(0, len(self.molecules)-1)
            
        # Катализатор (может быть None)
        catalyst = None
        if random.random() < 0.2 and len(self.molecules) > 0:
            catalyst = random.randint(0, len(self.molecules)-1)
            
        reaction = {
            "reactants": (r1, r2),
            "product": p,
            "catalyst": catalyst,
            "energy": random.uniform(-5.0, 2.0)  # Энергетика реакции
        }
        self.reactions.append(reaction)
        
        # Обновляем каталитическое ядро если нужно
        if catalyst is not None:
            self.catalytic_core.add(catalyst)
            # Если продукт катализируется, добавляем его тоже
            if random.random() < 0.1:
                self.catalytic_core.add(p)
    
    def _detect_catalytic_core_raf(self):
        """RAF-подобное обнаружение каталитического ядра"""
        if not self.reactions:
            return set()
            
        # Начальное ядро - все катализаторы
        core = set()
        for r in self.reactions:
            if r["catalyst"] is not None:
                core.add(r["catalyst"])
                
        # Простая замыкающая процедура
        changed = True
        while changed:
            changed = False
            for r in self.reactions:
                # Если все реагенты в ядре и есть катализатор из ядра
                if (r["reactants"][0] in core and r["reactants"][1] in core and
                    r["catalyst"] in core):
                    if r["product"] not in core:
                        core.add(r["product"])
                        changed = True
        return core
    
    # === MOL МЕТРИКИ ===
    
    def calculate_O_E(self):
        """Вычисление онтологической нагрузки (3 компоненты)"""
        if not self.molecules:
            return 0.0
            
        # 1. Core term (главный компонент)
        core = self._detect_catalytic_core_raf()
        core_size = len(core)
        total_mols = len(self.molecules)
        core_term = 1.0 - (core_size / total_mols) if total_mols > 0 else 1.0
        
        # 2. Graph entropy (энтропия реакционного графа)
        entropy_term = self._calculate_graph_entropy()
        
        # 3. MDL proxy через gzip-сжатие (идея от GPT-5)
        mdl_term = self._calculate_mdl_proxy()
        
        # Комбинируем с весами из калибровки GPT-5
        O_E = core_term + 0.45 * entropy_term + 0.30 * mdl_term
        
        # Добавляем штраф за нестабильность если нужно
        if len(self.reactions) > 10:
            instability = self._calculate_instability_penalty()
            O_E += 0.25 * instability
            
        return min(3.0, O_E)
    
    def _calculate_graph_entropy(self):
        """Энтропия распределения степеней в графе реакций"""
        if not self.reactions:
            return 0.3
            
        # Считаем исходящие степени (сколько раз молекула - продукт)
        out_degrees = defaultdict(int)
        for r in self.reactions:
            out_degrees[r["product"]] += 1
            
        if not out_degrees:
            return 0.3
            
        # Нормализованная энтропия Шеннона
        total = sum(out_degrees.values())
        entropy = 0.0
        for count in out_degrees.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)
                
        # Нормализуем к [0,1]
        max_entropy = math.log2(len(out_degrees)) if len(out_degrees) > 0 else 1.0
        return entropy / max_entropy if max_entropy > 0 else 0.0
    
    def _calculate_mdl_proxy(self):
        """MDL proxy через сжатие gzip (практическая реализация)"""
        if not self.molecules and not self.reactions:
            return 0.5
            
        # Сериализуем состояние в JSON
        state = {
            "molecules": len(self.molecules),
            "reactions": len(self.reactions),
            "core_size": len(self.catalytic_core),
            "reaction_patterns": [f"{r['reactants']}->{r['product']}" for r in self.reactions[:10]]
        }
        
        try:
            json_str = json.dumps(state, sort_keys=True)
            compressed = gzip.compress(json_str.encode())
            original_len = len(json_str)
            compressed_len = len(compressed)
            
            # Коэффициент сжатия как proxy для описательной сложности
            compression_ratio = compressed_len / max(original_len, 1)
            return min(1.0, compression_ratio * 2)  # Нормализуем
        except:
            return 0.5
    
    def _calculate_instability_penalty(self):
        """Штраф за нестабильность сети"""
        if len(self.reactions) < 5:
            return 0.0
            
        # Считаем степени всех молекул
        degrees = defaultdict(int)
        for r in self.reactions:
            for reactant in r["reactants"]:
                degrees[reactant] += 1
            degrees[r["product"]] += 1
            
        if not degrees:
            return 0.0
            
        values = list(degrees.values())
        mean = np.mean(values)
        std = np.std(values)
        
        if mean == 0:
            return 1.0
            
        # Коэффициент вариации
        cv = std / mean
        return min(1.0, cv)
    
    # === ПРИНЦИПЫ MOL (аналоги космогенезу) ===
    
    def diagnose_phase(self):
        """PDP: Диагностика фазы системы"""
        V = self._calculate_velocity_of_change()
        Var = self._calculate_response_variability()
        C = self._calculate_structural_coherence()
        
        if V < 0.1 and Var < 0.2 and C > 0.7:
            return "STABILIZATION", "Химическое равновесие"
        elif V > 0.3 and Var > 0.5 and C < 0.5:
            return "RECONFIGURATION", "Готовность к Φ-скачку"
        else:
            return "DECOMPRESSION", "Нарастание онтологической нагрузки"
    
    def _calculate_velocity_of_change(self):
        """Скорость изменения O(E)"""
        if len(self.O_E_history) < 2:
            return 0.1
        return abs(self.O_E_history[-1] - self.O_E_history[-2])
    
    def _calculate_response_variability(self):
        """Вариабельность отклика системы"""
        if len(self.O_E_history) < 5:
            return 0.3
        return np.std(self.O_E_history[-5:]) / (np.mean(self.O_E_history[-5:]) + 0.001)
    
    def _calculate_structural_coherence(self):
        """Структурная когерентность"""
        if not self.reactions:
            return 0.5
            
        # Простая мера: доля реакций с катализаторами
        catalyzed = sum(1 for r in self.reactions if r["catalyst"] is not None)
        return catalyzed / len(self.reactions)
    
    def evaluate_attractors(self):
        """PAD: Оценка аттракторов (аналог 1D/2D/3D в космогенезе)"""
        attractors = []
        
        # 1. Репликационный аттрактор (PDC - дискретное кодирование)
        rep_depth = 2.0 - len(self.stabilizers) * 0.5
        rep_width = 0.8
        attractors.append(("replication", rep_depth, rep_width))
        
        # 2. Мембранный аттрактор (PLOA - локальная автономия)
        mem_depth = 1.5 - (0 if "membrane" in self.stabilizers else 0.8)
        mem_width = 0.7
        attractors.append(("membrane", mem_depth, mem_width))
        
        # 3. Минеральный аттрактор (PIVC - невидимое ядро)
        min_depth = 1.2 - (0 if "matrix" in self.stabilizers else 0.6)
        min_width = 0.6
        attractors.append(("matrix", min_depth, min_width))
        
        if attractors:
            best = max(attractors, key=lambda x: x[1] * x[2])
            return best[0] if best[1] > self.ATTRACTOR_DEPTH_THRESHOLD else None
        return None
    
    def check_collapse_threshold(self):
        """PIC: Проверка порога коллапса"""
        current_O_E = self.calculate_O_E()
        return current_O_E > self.TAU and len(self.molecules) >= 5
    
    # === Φ-ОПЕРАТОР ДЛЯ АБИОГЕНЕЗА ===
    
    def phi_operator_abiogenesis(self):
        """Φ-оператор для перехода к жизни"""
        phase, recommendation = self.diagnose_phase()
        print(f"📊 PDP: {phase} - {recommendation}")
        
        if not self.check_collapse_threshold():
            print("⏸️  PIC: Ниже порога коллапса")
            return False
            
        target_stabilizer = self.evaluate_attractors()
        if not target_stabilizer:
            print("❌ PAD: Нет доминирующего аттрактора")
            return False
            
        print(f"🎯 PAD: Целевой стабилизатор → {target_stabilizer}")
        
        old_O_E = self.calculate_O_E()
        
        # Применяем стабилизатор
        if target_stabilizer == "replication":
            self._implement_replication_kernel()
        elif target_stabilizer == "membrane":
            self._implement_membrane_compartment()
        else:  # matrix
            self._implement_mineral_matrix()
            
        self.stabilizers.append(target_stabilizer)
        
        new_O_E = self.calculate_O_E()
        delta_O_E = new_O_E - old_O_E
        
        print(f"🌀 Φ-OPERATOR: Применён {target_stabilizer}")
        print(f"   O(ℰ) изменилась: {old_O_E:.3f} → {new_O_E:.3f} ({delta_O_E:+.3f})")
        
        # PAA: Анализ эффективности
        if delta_O_E < 0:
            print(f"✅ PAA: Стабилизация снизила нагрузку на {-delta_O_E:.3f}")
            return True
        else:
            print(f"⚠️  PAA: Стоимость перехода: {delta_O_E:.3f}")
            return False
    
    def _implement_replication_kernel(self):
        """Внедрение репликационного ядра (PDC)"""
        # Создаём автокаталитический цикл
        if len(self.molecules) >= 3:
            # Выбираем молекулу как "шаблон"
            template = random.randint(0, len(self.molecules)-1)
            
            # Добавляем реакцию самовоспроизведения
            reaction = {
                "reactants": (template, template),
                "product": template,  # Та же молекула
                "catalyst": template,  # Автокатализ!
                "energy": -2.0  # Выгодная реакция
            }
            self.reactions.append(reaction)
            self.catalytic_core.add(template)
            
            # Добавляем "комплементарную" молекулу
            complement = self.add_molecule(complexity=1.3, catalytic_potential=0.8)
            reaction2 = {
                "reactants": (template, complement),
                "product": complement,
                "catalyst": template,
                "energy": -1.5
            }
            self.reactions.append(reaction2)
            self.catalytic_core.add(complement)
            
            print(f"   → Создан автокаталитический цикл (молекулы {template}, {complement})")
    
    def _implement_membrane_compartment(self):
        """Внедрение мембранной компартментализации (PLOA)"""
        # Создаём "липидные" молекулы
        lipid1 = self.add_molecule(complexity=1.5, catalytic_potential=0.2)
        lipid2 = self.add_molecule(complexity=1.5, catalytic_potential=0.2)
        
        # Реакция образования мембраны
        membrane_reaction = {
            "reactants": (lipid1, lipid2),
            "product": lipid1,  # Упрощённо
            "catalyst": None,
            "energy": -3.0
        }
        self.reactions.append(membrane_reaction)
        
        # Внутренние реакции становятся более эффективными
        for r in self.reactions[:min(5, len(self.reactions))]:
            if r["energy"] < 0:  # Уже выгодные реакции
                r["energy"] *= 1.5  # Делаем ещё выгоднее
        
        print(f"   → Создана мембранная структура (молекулы {lipid1}, {lipid2})")
    
    def _implement_mineral_matrix(self):
        """Внедрение минеральной матрицы (PIVC)"""
        # Минерал как внешний катализатор
        mineral = self.add_molecule(complexity=2.0, catalytic_potential=0.9)
        
        # Минерал катализирует множество реакций
        for r in self.reactions[:min(10, len(self.reactions))]:
            if r["catalyst"] is None and random.random() < 0.4:
                r["catalyst"] = mineral
                r["energy"] -= 0.5  # Снижаем энергетический барьер
        
        self.catalytic_core.add(mineral)
        print(f"   → Добавлен минеральный катализатор (молекула {mineral})")
    
    # === ЭКСПЕРИМЕНТ ===
    
    def run_experiment(self, max_steps=100):
        """Основной эксперимент"""
        print("=" * 70)
        print("MOL ABIOGENESIS ENGINE")
        print("=" * 70)
        print("Гипотеза: жизнь возникает при превышении порога O(ℰ)")
        print(f"Порог τ = {self.TAU}")
        print()
        
        # Инициализация: случайная химия
        for i in range(6):
            self.add_molecule()
        for i in range(10):
            self.add_random_reaction()
        
        initial_O_E = self.calculate_O_E()
        print(f"🎯 НАЧАЛЬНОЕ СОСТОЯНИЕ:")
        print(f"   Молекулы: {len(self.molecules)}, Реакции: {len(self.reactions)}")
        print(f"   O(ℰ) = {initial_O_E:.3f}")
        print()
        
        # Эволюционный цикл
        life_emerged = False
        for step in range(max_steps):
            self.step = step
            print(f"\n🔄 ШАГ {step}:")
            
            # Добавляем немного сложности
            if random.random() < 0.3:
                self.add_molecule(complexity=1.0 + random.random())
            if random.random() < 0.4:
                self.add_random_reaction()
            
            # Рассчитываем O(E)
            current_O_E = self.calculate_O_E()
            self.O_E_history.append(current_O_E)
            
            print(f"   Молекулы: {len(self.molecules)}, Реакции: {len(self.reactions)}")
            print(f"   O(ℰ) = {current_O_E:.3f}")
            
            # Проверяем Φ-скачок
            if current_O_E > self.TAU and not life_emerged:
                print(f"   ⚠️  O(ℰ) > τ ({self.TAU}) → активация Φ-оператора")
                if self.phi_operator_abiogenesis():
                    life_emerged = True
                    print(f"   ✨ ЖИЗНЬ ВОЗНИКЛА на шаге {step}")
            
            # Если жизнь возникла, продолжаем оптимизацию
            elif life_emerged:
                print(f"   ✅ Режим жизни: {self.stabilizers}")
                # Иногда добавляем ещё стабилизаторов
                if random.random() < 0.1 and len(self.stabilizers) < 3:
                    additional = self.evaluate_attractors()
                    if additional and additional not in self.stabilizers:
                        self.stabilizers.append(additional)
                        print(f"   → Добавлен дополнительный стабилизатор: {additional}")
            
            # Остановка если достигли стабильности
            if life_emerged and current_O_E < self.TAU * 0.7 and step > 20:
                print(f"\n✅ Достигнута стабильная жизнь-подобная система")
                break
        
        self._scientific_analysis(initial_O_E)
    
    def _scientific_analysis(self, initial_O_E):
        """Научный анализ результатов"""
        print("\n" + "=" * 70)
        print("НАУЧНЫЙ АНАЛИЗ")
        print("=" * 70)
        
        final_O_E = self.calculate_O_E()
        efficiency = (initial_O_E - final_O_E) / initial_O_E if initial_O_E > 0 else 0
        
        print(f"📊 РЕЗУЛЬТАТЫ:")
        print(f"   • Начальная O(ℰ): {initial_O_E:.3f} (хаотическая химия)")
        print(f"   • Конечная O(ℰ): {final_O_E:.3f} ({', '.join(self.stabilizers) if self.stabilizers else 'нет стабилизаторов'})")
        print(f"   • Эффективность: {efficiency:+.1%}")
        print(f"   • Размер каталитического ядра: {len(self.catalytic_core)}/{len(self.molecules)}")
        
        print(f"\n🔬 ТЕСТ ГИПОТЕЗЫ MOL:")
        if final_O_E < initial_O_E and self.stabilizers:
            print(f"   ✅ ПОДТВЕРЖДЕНО: Стабилизаторы {self.stabilizers} снизили O(ℰ) на {-efficiency:.1%}")
            print(f"   → Жизнь возникает как онтологическая оптимизация")
        else:
            print(f"   ❌ ОПРОВЕРГНУТО: Система не нашла онтологически эффективного состояния")
            print(f"   → Требуется пересмотр параметров или механизмов")
        
        print(f"\n🎯 ПРИНЦИПЫ MOL В ДЕЙСТВИИ:")
        print(f"   • PDP: {self.diagnose_phase()[0]}")
        print(f"   • PAD: {self.evaluate_attractors()}")
        print(f"   • PIC: Сработал при O(ℰ) > {self.TAU}")

# Запуск
if __name__ == "__main__":
    print("🔬 MOL Abiogenesis Engine v1.0")
    print("DOI: 10.5281/zenodo.17445099")
    print()
    
    experiment = AbiogenesisMOL(seed=42)
    experiment.run_experiment(max_steps=80)
