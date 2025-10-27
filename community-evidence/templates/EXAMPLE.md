# Пример: Анализ транспортной сети Берлина

**Исследователь:** The MOL Foundation
**Домен:** Городские системы

## Методология
- **Система:** 19,758 остановок Берлина
- **Расчет O(ℰ):** Отношение соединений к линиям
- **Метрика стабильности:** Эффективность транспортного узла
- **Инструменты:** Python, stations.csv

## Результаты
- **MOL-оптимальные узлы:** O(ℰ) ≈ 0.300 (Bhf. Zoo)
- **Проблемные узлы:** O(ℰ) ≥ 0.700 (Alexanderplatz)
- **Вывод:** 34% сети требует оптимизации

## Файлы
- Данные: [tools/DATA_INSTRUCTIONS_TRANSPORT.md](../tools/DATA_INSTRUCTIONS_TRANSPORT.md)
- Код: [tools/transport_mol_analyzer.py](../tools/transport_mol_analyzer.py)
