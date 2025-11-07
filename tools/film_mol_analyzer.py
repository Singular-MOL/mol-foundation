import csv
import re
import math
from collections import Counter
from datetime import datetime
import os

class TemporalMOLAnalyzer:
    def __init__(self):
        self.wikipedia_movies = []
        self.imdb_movies = {}
        self.box_office_movies = {}
        self.final_temporal_ranking = {}
        
    def load_all_datasets(self):
        """Загружаем данные с НОВОЙ иерархией: Wikipedia -> IMDb -> Box Office"""
        print("📚 ЗАГРУЗКА ДАННЫХ (НОВАЯ ИЕРАРХИЯ)...")
        print("=" * 60)
        
        # 1. ОСНОВНАЯ БАЗА: Wikipedia (самый полный источник)
        print("🌍 Загрузка Wikipedia данных...")
        self.wikipedia_movies = self.load_wikipedia_data()
        print(f"📊 Wikipedia фильмов: {len(self.wikipedia_movies)}")
        
        # 2. ФИЛЬТР: IMDb данные (для верификации качества)
        print("🎬 Загрузка IMDb данных...")
        self.imdb_movies = self.load_imdb_data()
        print(f"⭐ IMDb фильмов: {len(self.imdb_movies)}")
        
        # 3. ДОПОЛНИТЕЛЬНЫЕ ДАННЫЕ: Box Office (коммерческий успех)
        print("💰 Загрузка Box Office данных...")
        self.box_office_movies = self.load_box_office_data()
        print(f"💵 Box Office фильмов: {len(self.box_office_movies)}")

    def load_wikipedia_data(self):
        """Загружаем Wikipedia как ОСНОВНУЮ базу"""
        movies = []
        wiki_path = "/data/data/com.termux/files/home/.cache/kagglehub/datasets/jrobischon/wikipedia-movie-plots/versions/1/wiki_movie_plots_deduped.csv"

        with open(wiki_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i % 20000 == 0:
                    print(f"   Обработано {i} строк...")
                
                year = int(row['Release Year']) if row['Release Year'].isdigit() else 0
                # Фильтруем по году: 2005-2024
                if 2005 <= year <= 2024:
                    movie = {
                        'title': row['Title'],
                        'year': year,
                        'origin': row['Origin/Ethnicity'],
                        'director': row['Director'],
                        'cast': row['Cast'],
                        'genre': row['Genre'],
                        'plot': row['Plot'],
                        'wiki_page': row['Wiki Page'],
                        'source': 'wikipedia',
                        'data_quality': 1
                    }
                    movies.append(movie)
        return movies

    def load_imdb_data(self):
        """Загружаем IMDb как ФИЛЬТР качества"""
        movies = {}
        imdb_path = "/data/data/com.termux/files/home/.cache/kagglehub/datasets/mohamedasak/imdb-top-250-movies/versions/2/imdb_top_movies.csv"

        with open(imdb_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = self.create_movie_key(row['Title'], row['Year'])
                movies[key] = {
                    'imdb_rating': float(row['Rating']),
                    'imdb_rank': int(row['Rank']),
                    'duration': row['Duration'],
                    'certificate': row['Certificate']
                }
        return movies

    def load_box_office_data(self):
        """Загружаем Box Office как ДОПОЛНИТЕЛЬНЫЕ данные"""
        movies = {}
        box_office_path = "/data/data/com.termux/files/home/.cache/kagglehub/datasets/harios/box-office-data-1984-to-2024-from-boxofficemojo/versions/1/boxoffice_data_2024.csv"

        with open(box_office_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = self.create_movie_key(row['Title'], row['Year'])
                gross = self.parse_gross(row['Gross'])
                movies[key] = {
                    'gross': gross,
                    'title': row['Title']
                }
        return movies

    def calculate_wikipedia_O_E(self, movie):
        """Расчет O(E) на основе Wikipedia данных"""
        O_E = 0
        
        # 1. СЛОЖНОСТЬ СЮЖЕТА (PFE)
        plot_complexity = self.calculate_plot_complexity(movie.get('plot', ''))
        O_E += plot_complexity
        
        # 2. КУЛЬТУРНАЯ СЛОЖНОСТЬ (PLOA)
        cultural_complexity = self.calculate_cultural_complexity(movie)
        O_E += cultural_complexity
        
        # 3. АКТЕРСКАЯ СЛОЖНОСТЬ (PDC)
        cast_complexity = self.calculate_cast_complexity(movie.get('cast', ''))
        O_E += cast_complexity
        
        # 4. ЖАНРОВАЯ СЛОЖНОСТЬ
        genre_complexity = self.calculate_genre_complexity(movie.get('genre', ''))
        O_E += genre_complexity
        
        return round(O_E, 4)

    def calculate_plot_complexity(self, plot_text):
        """Сложность сюжета based on text analysis"""
        if not plot_text:
            return 0.2
            
        text_length = len(plot_text)
        if text_length > 1500:
            return 0.15
        elif text_length > 1000:
            return 0.10
        elif text_length > 500:
            return 0.05
        else:
            return 0.02

    def calculate_cultural_complexity(self, movie):
        """Культурная сложность based on origin"""
        origin = movie.get('origin', 'Unknown')
        
        cultural_weights = {
            'American': 0.0,
            'British': 0.03,
            'Canadian': 0.02,
            'Australian': 0.02,
            'Japanese': 0.08,
            'South Korean': 0.09,
            'Chinese': 0.10,
            'Indian': 0.12,
            'French': 0.06,
            'German': 0.05,
            'Italian': 0.04,
            'Spanish': 0.05,
            'Russian': 0.11
        }
        
        return cultural_weights.get(origin, 0.08)

    def calculate_cast_complexity(self, cast_text):
        """Сложность актерского состава"""
        if not cast_text or cast_text == 'Unknown':
            return 0.1
            
        actors = [actor.strip() for actor in cast_text.split(',') if actor.strip()]
        complexity = min(len(actors) * 0.02, 0.15)
        return complexity

    def calculate_genre_complexity(self, genre_text):
        """Сложность жанров"""
        if not genre_text or genre_text == 'Unknown':
            return 0.1
            
        genres = [genre.strip() for genre in genre_text.split(',') if genre.strip()]
        complexity = min(len(genres) * 0.03, 0.12)
        return complexity

    def apply_imdb_filter(self, movie):
        """Применяем IMDb как ФИЛЬТР качества"""
        key = self.create_movie_key(movie['title'], str(movie['year']))
        imdb_data = self.imdb_movies.get(key, {})
        
        quality_bonus = 0
        verification_status = "WIKI_ONLY"
        
        if imdb_data:
            rating = imdb_data.get('imdb_rating', 0)
            rank = imdb_data.get('imdb_rank', 1000)
            
            # IMDb рейтинг сильно улучшает качество
            if rating >= 8.0:
                quality_bonus = -0.3
                verification_status = "IMDB_TOP"
            elif rating >= 7.0:
                quality_bonus = -0.15
                verification_status = "IMDB_GOOD"
            elif rating >= 6.0:
                quality_bonus = -0.05
                verification_status = "IMDB_AVERAGE"
            else:
                verification_status = "IMDB_LOW"
                
            movie['imdb_rating'] = rating
            movie['imdb_rank'] = rank
        else:
            verification_status = "NO_IMDB"
            
        movie['verification_status'] = verification_status
        return quality_bonus

    def apply_box_office_data(self, movie):
        """Добавляем Box Office данные"""
        key = self.create_movie_key(movie['title'], str(movie['year']))
        box_office_data = self.box_office_movies.get(key, {})
        
        if box_office_data:
            gross = box_office_data.get('gross', 0)
            movie['gross'] = gross
            
            # Коммерческий успех немного снижает O(E)
            if gross > 100000000:  # > $100M
                return -0.08
            elif gross > 10000000:  # > $10M
                return -0.04
                
        return 0

    def generate_temporal_top50_per_year(self):
        """Генерируем топ-50 фильмов для каждого года (2024 → 2005)"""
        print("\n🎯 ГЕНЕРАЦИЯ ВРЕМЕННОГО ТОП-50 ПО ГОДАМ")
        print("=" * 60)
        
        # Группируем фильмы по годам
        movies_by_year = {}
        for movie in self.wikipedia_movies:
            year = movie['year']
            if year not in movies_by_year:
                movies_by_year[year] = []
            movies_by_year[year].append(movie)
        
        # Для каждого года рассчитываем O(E) и выбираем топ-50
        current_year = 2024  # Фиксируем текущий год
        for year in range(current_year, 2004, -1):
            if year in movies_by_year:
                print(f"📅 Обработка {year} года...")
                
                year_movies = movies_by_year[year]
                print(f"   Найдено фильмов: {len(year_movies)}")
                
                # Рассчитываем O(E) для всех фильмов года
                for movie in year_movies:
                    base_O_E = self.calculate_wikipedia_O_E(movie)
                    
                    # Применяем IMDb фильтр
                    imdb_bonus = self.apply_imdb_filter(movie)
                    
                    # Добавляем Box Office данные
                    box_office_bonus = self.apply_box_office_data(movie)
                    
                    # Финальный O(E)
                    movie['final_O_E'] = base_O_E + imdb_bonus + box_office_bonus
                
                # Сортируем и берем топ-50
                year_movies.sort(key=lambda x: x['final_O_E'])
                self.final_temporal_ranking[year] = year_movies[:50]
                
                print(f"   ✅ Топ-50 сгенерирован для {year} года")
            else:
                print(f"   ⚠️ Нет данных за {year} год")
        
        return self.final_temporal_ranking

    def save_results_to_files(self):
        """Сохраняем результаты в CSV файлы для каждого года"""
        print(f"\n💾 СОХРАНЕНИЕ РЕЗУЛЬТАТОВ В ФАЙЛЫ...")
        
        # Создаем папку для результатов
        results_dir = "temporal_mol_results"
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
            print(f"📁 Создана папка: {results_dir}")
        
        # Сохраняем общий файл со всеми годами
        all_years_file = os.path.join(results_dir, "ALL_YEARS_TOP50.csv")
        with open(all_years_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Year', 'Rank', 'O(E)', 'Title', 'IMDb_Rating', 'Gross', 'Origin', 'Status'])
            
            for year in sorted(self.final_temporal_ranking.keys(), reverse=True):
                movies = self.final_temporal_ranking[year]
                for i, movie in enumerate(movies, 1):
                    gross_str = f"${movie.get('gross', 0)/1000000:.1f}M" if movie.get('gross', 0) > 0 else "No data"
                    rating_str = movie.get('imdb_rating', 'N/A')
                    
                    writer.writerow([
                        year, i, movie['final_O_E'], movie['title'],
                        rating_str, gross_str, movie.get('origin', 'Unknown'),
                        movie.get('verification_status', 'UNKNOWN')
                    ])
        
        print(f"📄 Общий файл создан: {all_years_file}")
        
        # Сохраняем отдельные файлы для каждого года
        for year in self.final_temporal_ranking.keys():
            year_file = os.path.join(results_dir, f"TOP50_{year}.csv")
            with open(year_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Rank', 'O(E)', 'Title', 'IMDb_Rating', 'Gross', 'Origin', 'Director', 'Status'])
                
                movies = self.final_temporal_ranking[year]
                for i, movie in enumerate(movies, 1):
                    gross_str = f"${movie.get('gross', 0)/1000000:.1f}M" if movie.get('gross', 0) > 0 else "No data"
                    rating_str = movie.get('imdb_rating', 'N/A')
                    
                    writer.writerow([
                        i, movie['final_O_E'], movie['title'], rating_str,
                        gross_str, movie.get('origin', 'Unknown'),
                        movie.get('director', 'Unknown'), 
                        movie.get('verification_status', 'UNKNOWN')
                    ])
            
            print(f"📅 Файл для {year} года: {year_file}")
        
        return results_dir

    def print_sample_results(self, max_years=3):
        """Показываем примеры результатов (первые 3 года)"""
        print(f"\n🎬 ПРИМЕРЫ РЕЗУЛЬТАТОВ (первые {max_years} года)")
        print("=" * 70)
        
        years_shown = 0
        for year in sorted(self.final_temporal_ranking.keys(), reverse=True):
            if years_shown >= max_years:
                break
                
            movies = self.final_temporal_ranking[year]
            print(f"\n📅 ТОП-5 ФИЛЬМОВ {year} ГОДА")
            print("=" * 50)
            print("Рейт | O(E)    | Статус       | Название")
            print("-" * 50)
            
            for i, movie in enumerate(movies[:5], 1):
                status_icons = {
                    "IMDB_TOP": "✅",
                    "IMDB_GOOD": "☑️", 
                    "IMDB_AVERAGE": "⚠️",
                    "IMDB_LOW": "🔻",
                    "NO_IMDB": "🌍",
                    "WIKI_ONLY": "📚"
                }
                
                status_icon = status_icons.get(movie.get('verification_status', 'WIKI_ONLY'), '❓')
                gross_str = f"${movie.get('gross', 0)/1000000:.1f}M" if movie.get('gross', 0) > 0 else "No data"
                rating_str = f"{movie.get('imdb_rating', 'N/A')}" if movie.get('imdb_rating') else "N/A"
                
                print(f"#{i:2} | {movie['final_O_E']:7.4f} | {status_icon:2} | {movie['title'][:35]:35} | {gross_str:8} | IMDb: {rating_str}")
            
            years_shown += 1

    def print_year_statistics(self):
        """Общая статистика по годам"""
        print(f"\n📈 ОБЩАЯ СТАТИСТИКА ПО ГОДАМ (2005-2024)")
        print("=" * 60)
        
        years = sorted(self.final_temporal_ranking.keys(), reverse=True)
        
        print("Год | Фильмов | Лучший O(E) | Худший O(E) | IMDb_TOP%")
        print("-" * 60)
        
        for year in years:
            movies = self.final_temporal_ranking[year]
            if movies:
                best_O_E = min(m['final_O_E'] for m in movies)
                worst_O_E = max(m['final_O_E'] for m in movies)
                imdb_top_count = sum(1 for m in movies if m.get('verification_status') == 'IMDB_TOP')
                imdb_top_pct = (imdb_top_count / len(movies)) * 100
                
                print(f"{year} | {len(movies):7} | {best_O_E:11.4f} | {worst_O_E:11.4f} | {imdb_top_pct:7.1f}%")

    def create_movie_key(self, title, year):
        """Создаем ключ для идентификации фильма"""
        clean_title = re.sub(r'[^\w\s]', '', title.lower().strip())
        clean_year = int(year) if year.isdigit() else 0
        return f"{clean_title}_{clean_year}"

    def parse_gross(self, gross_str):
        """Парсинг финансовых данных"""
        if not gross_str or gross_str == 'Unknown':
            return 0
        try:
            clean = gross_str.replace('$', '').replace(',', '')
            return float(clean)
        except:
            return 0

# Запуск анализа
if __name__ == "__main__":
    print("🎬 TEMPORAL MOL АНАЛИЗ: ТОП-50 ПО ГОДАМ (2005-2024)")
    print("Иерархия: Wikipedia → IMDb фильтр → Box Office")
    print("=" * 70)
    
    analyzer = TemporalMOLAnalyzer()
    
    # Загружаем данные
    analyzer.load_all_datasets()
    
    # Генерируем временной топ
    temporal_ranking = analyzer.generate_temporal_top50_per_year()
    
    # Сохраняем результаты в файлы
    results_dir = analyzer.save_results_to_files()
    
    # Показываем примеры
    analyzer.print_sample_results(max_years=3)
    
    # Общая статистика
    analyzer.print_year_statistics()
    
    print(f"\n🎉 TEMPORAL АНАЛИЗ ЗАВЕРШЕН!")
    print(f"📁 Все результаты сохранены в папку: {results_dir}")
    print("📄 Файлы CSV можно открыть в Excel или любом редакторе!")
