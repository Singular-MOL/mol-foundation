import csv
import os
from datetime import datetime

class TrueMOLEngine:
    """НАСТОЯЩИЙ MOL-движок с Φ-переходами"""

    def __init__(self):
        self.wiki_movies = []
        self.imdb_data = {}
        self.box_office_data = {}

    def load_all_data(self):
        """Загрузка всех данных"""
        print("📚 Загрузка данных...")

        # 1. Wikipedia - БАЗОВАЯ ОНТОЛОГИЯ
        self.load_wikipedia_data()

        # 2. IMDb - ФИЛЬТР КАЧЕСТВА
        self.load_imdb_data()

        # 3. Box Office - КОММЕРЧЕСКАЯ ВАЛИДАЦИЯ
        self.load_box_office_data()

        print(f"✅ Данные загружены: {len(self.wiki_movies)} фильмов")

    def load_wikipedia_data(self):
        """Базовая онтология из Wikipedia"""
        path = "/data/data/com.termux/files/home/.cache/kagglehub/datasets/jrobischon/wikipedia-movie-plots/versions/1/wiki_movie_plots_deduped.csv"

        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                year = int(row['Release Year']) if row['Release Year'].isdigit() else 0
                if 2005 <= year <= 2024:  # Только современные фильмы
                    movie = {
                        'title': row['Title'],
                        'year': year,
                        'origin': row['Origin/Ethnicity'],
                        'director': row['Director'],
                        'cast': row['Cast'],
                        'genre': row['Genre'],
                        'plot': row['Plot'],
                        'wiki_page': row['Wiki Page']
                    }
                    self.wiki_movies.append(movie)

    def load_imdb_data(self):
        """IMDb как фильтр качества"""
        path = "/data/data/com.termux/files/home/.cache/kagglehub/datasets/mohamedasak/imdb-top-250-movies/versions/2/imdb_top_movies.csv"

        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = f"{row['Title'].lower().strip()}_{row['Year']}"
                self.imdb_data[key] = {
                    'rating': float(row['Rating']),
                    'rank': int(row['Rank'])
                }

    def load_box_office_data(self):
        """Box Office для коммерческой валидации"""
        path = "/data/data/com.termux/files/home/.cache/kagglehub/datasets/harios/box-office-data-1984-to-2024-from-boxofficemojo/versions/1/boxoffice>

        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = f"{row['Title'].lower().strip()}_{row['Year']}"
                gross = self.parse_gross(row['Gross'])
                self.box_office_data[key] = {'gross': gross}

    def calculate_O_E(self, movie):
        """Настоящий расчёт онтологической нагрузки"""
        O_E = 0

        # 1. СЛОЖНОСТЬ СЮЖЕТА (PFE)
        plot_complexity = self.analyze_plot_complexity(movie['plot'])
        O_E += plot_complexity

        # 2. КУЛЬТУРНАЯ СЛОЖНОСТЬ (PLOA)
        cultural_complexity = self.analyze_cultural_complexity(movie['origin'])
        O_E += cultural_complexity

        # 3. АКТЁРСКАЯ СЛОЖНОСТЬ (PDC)
        cast_complexity = self.analyze_cast_complexity(movie['cast'])
        O_E += cast_complexity

        return O_E

    def analyze_plot_complexity(self, plot_text):
        """Анализ сложности сюжета"""
        if not plot_text:
            return 0.2

        words = len(plot_text.split())
        if words > 300: return 0.15
        elif words > 200: return 0.10
        elif words > 100: return 0.05
        else: return 0.02

    def analyze_cultural_complexity(self, origin):
        """Культурная сложность"""
        weights = {
            'American': 0.0, 'British': 0.03, 'Canadian': 0.02,
            'Australian': 0.02, 'Japanese': 0.08, 'South Korean': 0.09,
            'Chinese': 0.10, 'Indian': 0.12, 'French': 0.06,
            'German': 0.05, 'Italian': 0.04, 'Spanish': 0.05,
            'Russian': 0.11
        }
        return weights.get(origin, 0.08)

    def analyze_cast_complexity(self, cast_text):
        """Сложность актёрского состава"""
        if not cast_text or cast_text == 'Unknown':
            return 0.1
        actors = [a.strip() for a in cast_text.split(',') if a.strip()]
        return min(len(actors) * 0.02, 0.15)

    def apply_phi_operator(self, movie, base_O_E):
        """Φ-оператор: переход при O(E) > threshold"""
        key = f"{movie['title'].lower().strip()}_{movie['year']}"

        # IMDb верификация = качественный скачок
        if key in self.imdb_data:
            imdb_rating = self.imdb_data[key]['rating']

            if imdb_rating >= 8.0:  # IMDB_TOP
                return base_O_E - 0.3, "IMDB_TOP"
            elif imdb_rating >= 7.0:  # IMDB_GOOD
                return base_O_E - 0.15, "IMDB_GOOD"
            elif imdb_rating >= 6.0:  # IMDB_AVERAGE
                return base_O_E - 0.05, "IMDB_AVERAGE"
            else:
                return base_O_E, "IMDB_LOW"
        else:
            return base_O_E, "NO_IMDB"

    def apply_commercial_optimization(self, movie, current_O_E):
        """Коммерческая оптимизация через Box Office"""
        key = f"{movie['title'].lower().strip()}_{movie['year']}"

        if key in self.box_office_data:
            gross = self.box_office_data[key]['gross']
            movie['gross'] = gross

            if gross > 100000000:  # > $100M
                return current_O_E - 0.08
            elif gross > 10000000:  # > $10M
                return current_O_E - 0.04

        return current_O_E

    def parse_gross(self, gross_str):
        """Парсинг кассовых сборов"""
        if not gross_str or gross_str == 'Unknown':
            return 0
        try:
            return float(gross_str.replace('$', '').replace(',', ''))
        except:
            return 0

    def generate_mol_ranking(self):
        """Генерация MOL-рейтинга по годам"""
        print("\n🎯 ГЕНЕРАЦИЯ MOL-РЕЙТИНГА")

        # Группируем по годам
        movies_by_year = {}
        for movie in self.wiki_movies:
            year = movie['year']
            if year not in movies_by_year:
                movies_by_year[year] = []
            movies_by_year[year].append(movie)

        results = {}

        for year in range(2024, 2004, -1):
            if year in movies_by_year:
                print(f"📅 {year} год: {len(movies_by_year[year])} фильмов")

                for movie in movies_by_year[year]:
                    # 1. БАЗОВАЯ ОНТОЛОГИЯ
                    base_O_E = self.calculate_O_E(movie)

                    # 2. Φ-ОПЕРАТОР (качественный скачок)
                    O_E_after_phi, status = self.apply_phi_operator(movie, base_O_E)

                    # 3. КОММЕРЧЕСКАЯ ОПТИМИЗАЦИЯ
                    final_O_E = self.apply_commercial_optimization(movie, O_E_after_phi)

                    movie['final_O_E'] = final_O_E
                    movie['status'] = status

                # Сортируем по O(E) и берём топ-20
                movies_by_year[year].sort(key=lambda x: x['final_O_E'])
                results[year] = movies_by_year[year][:20]

        return results

    def save_results(self, results):
        """Сохранение результатов"""
        os.makedirs("mol_results", exist_ok=True)

        for year, movies in results.items():
            filename = f"mol_results/TRUE_MOL_{year}.csv"

            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Rank', 'O(E)', 'Title', 'Year', 'Origin', 'IMDb_Status'])

                for i, movie in enumerate(movies, 1):
                    writer.writerow([
                        i, f"{movie['final_O_E']:.3f}",
                        movie['title'], movie['year'],
                        movie['origin'], movie['status']
                    ])

            print(f"💾 {filename} - сохранён")

# 1. Загрузка данных
    engine.load_all_data()

    # 2. MOL-анализ
    results = engine.generate_mol_ranking()

    # 3. Сохранение
    engine.save_results(results)

    print("\n🎉 MOL-АНАЛИЗ ЗАВЕРШЁН!")
    print("📁 Результаты в папке: mol_results/")
