#!/usr/bin/env python3
"""
MOL-АНАЛИЗ 6.2 — Полная версия для Termux / локального запуска
Реализует:
 - mol_score и явный O(E)
 - фрактальную нормализацию (PFE) при калибровке
 - Φ-оператор через трейлер (apply_trailer_phi) с сохранением источников и DOI MOL
 - собственную кросс-валидацию без sklearn
 - стресс-тесты, детальный разбор вкладов
 - экспорт JSON-отчёта с phi_sources
Автор: интеграция по запросу пользователя
Дата: автоматически
"""
import json
import math
import random
from datetime import datetime

class FullMOLAnalyzer:
    def __init__(self):
        self.analysis_date = datetime.now().strftime("%Y-%m-%d")
        self.historical_films = self.load_extended_historical_data()
        self.calibrated_weights = self.simple_calibration()
        self.validate_calibration()
        self.last_phi_sources = {}

    # === ДАННЫЕ ===
    def load_extended_historical_data(self):
        return [
            {'title':'Марсианин','budget':108_000_000,'box_office':630_200_000,'imdb_score':8.0,'success':1.0,
             'principles':{'PIVC':0.85,'PLOA':0.80,'PAA':0.75,'PDC':0.70}},
            {'title':'Интерстеллар','budget':165_000_000,'box_office':677_500_000,'imdb_score':8.6,'success':1.0,
             'principles':{'PIVC':0.90,'PLOA':0.85,'PAA':0.80,'PDC':0.75}},
            {'title':'Гравитация','budget':100_000_000,'box_office':723_200_000,'imdb_score':7.7,'success':1.0,
             'principles':{'PIVC':0.88,'PLOA':0.82,'PAA':0.78,'PDC':0.72}},
            {'title':'Прибытие','budget':47_000_000,'box_office':203_400_000,'imdb_score':7.9,'success':0.8,
             'principles':{'PIVC':0.82,'PLOA':0.75,'PAA':0.85,'PDC':0.68}},
            {'title':'Изгой-один','budget':200_000_000,'box_office':1_056_100_000,'imdb_score':7.8,'success':1.0,
             'principles':{'PIVC':0.78,'PLOA':0.72,'PAA':0.70,'PDC':0.82}},
            {'title':'Первый человек','budget':70_000_000,'box_office':105_800_000,'imdb_score':7.3,'success':0.4,
             'principles':{'PIVC':0.75,'PLOA':0.70,'PAA':0.65,'PDC':0.60}},
            {'title':'Артемис Фаул','budget':125_000_000,'box_office':167_800_000,'imdb_score':6.2,'success':0.3,
             'principles':{'PIVC':0.60,'PLOA':0.55,'PAA':0.58,'PDC':0.52}},
            {'title':'Сфера','budget':80_000_000,'box_office':37_300_000,'imdb_score':6.6,'success':0.1,
             'principles':{'PIVC':0.45,'PLOA':0.50,'PAA':0.40,'PDC':0.35}},
            {'title':'Время','budget':40_000_000,'box_office':18_000_000,'imdb_score':5.7,'success':0.1,
             'principles':{'PIVC':0.38,'PLOA':0.42,'PAA':0.35,'PDC':0.30}},
            {'title':'Джонни-мнемоник','budget':28_000_000,'box_office':52_400_000,'imdb_score':5.6,'success':0.2,
             'principles':{'PIVC':0.42,'PLOA':0.38,'PAA':0.45,'PDC':0.40}}
        ]

    # === КАЛИБРОВКА ===
    def simple_calibration(self):
        principles = ['PIVC','PLOA','PAA','PDC']
        correlations = {}
        for p in principles:
            corr = self.calculate_correlation(
                [f['principles'][p] for f in self.historical_films],
                [f['success'] for f in self.historical_films]
            )
            level = {'PIVC':1,'PLOA':2,'PAA':2,'PDC':1}[p]
            correlations[p] = abs(corr) / (level if level > 0 else 1)
        total = sum(correlations.values()) or 1.0
        weights = {p: correlations[p]/total for p in correlations}
        print("🔧 Калибровка (PFE-normalized):")
        for p,w in weights.items():
            print(f"   {p}: {w:.3f}")
        return weights

    def calculate_correlation(self,x,y):
        n=len(x)
        if n<2: return 0.0
        sx,sumx2,sy,sumy2,sumxy=0,0,0,0,0
        for i in range(n):
            sx+=x[i]; sy+=y[i]
            sumx2+=x[i]*x[i]; sumy2+=y[i]*y[i]
            sumxy+=x[i]*y[i]
        num = n*sumxy - sx*sy
        den_sq = (n*sumx2 - sx*sx)*(n*sumy2 - sy*sy)
        if den_sq <= 0: return 0.0
        return num / math.sqrt(den_sq)

    def validate_calibration(self):
        total = sum(self.calibrated_weights.values())
        if total == 0:
            n = len(self.calibrated_weights)
            for p in self.calibrated_weights:
                self.calibrated_weights[p] = 1.0/n
            total = 1.0
        else:
            for p in self.calibrated_weights:
                self.calibrated_weights[p] /= total
        print("✅ Калибровка проверена")

    # === АНАЛИЗ ===
    def analyze_hail_mary(self):
        hail_mary = {'PIVC':0.85,'PLOA':0.78,'PAA':0.80,'PDC':0.76}
        mol_score = sum(hail_mary[p]*self.calibrated_weights[p] for p in self.calibrated_weights)
        ontological_load = 1.0 - mol_score
        asymmetry_index = 1.0 - (min(hail_mary.values())/max(hail_mary.values()))

        print(f"\n📊 MOL-показатель: {mol_score:.3f}")
        print(f"🧠 O(E) = {ontological_load:.3f} | Индекс асимметрии = {asymmetry_index:.3f}")

        CRITICAL_LOAD = 0.7
        phi_activated=False
        if ontological_load > CRITICAL_LOAD:
            print(f"⚠️ O(E) > {CRITICAL_LOAD} → активация Φ-оператора")
            self.recalibrate_phi()
            phi_activated=True

        box_pred=self.simple_box_office_prediction(mol_score)
        val=self.custom_cross_validation()

        return {
            'date': self.analysis_date,
            'film':'Project Hail Mary (Проект "Конец света")',
            'mol_score': mol_score,
            'ontological_load': ontological_load,
            'asymmetry_index': asymmetry_index,
            'phi_activated': phi_activated,
            'box_office_prediction': box_pred,
            'validation': val,
            'weights': self.calibrated_weights,
            'principles_breakdown': hail_mary,
            'phi_sources': self.last_phi_sources
        }

    def recalibrate_phi(self):
        print("🔄 Перекалибровка на новых данных (Φ-оператор активирован)...")
        self.calibrated_weights=self.simple_calibration()
        self.validate_calibration()
        print("✅ Φ-сдвиг завершен")

    def apply_trailer_phi(self,trailer_metrics,sources=None):
        print("\n🎞️ Активация Φ через трейлерное возмущение δ...")
        views=float(trailer_metrics.get('views',0))
        like_ratio=float(trailer_metrics.get('like_ratio',0.8))
        sentiment=float(trailer_metrics.get('sentiment',0.8))

        delta_energy=(views/100_000_000.0)*sentiment*max(0.5,like_ratio)
        delta_energy=max(0.0,min(delta_energy,5.0))
        print(f"   ⚙️ Энергия возмущения δ = {delta_energy:.3f} (views={int(views)}, like_ratio={like_ratio:.2f}, sentiment={sentiment:.2f})")

        adjustment=min(0.20,0.04*delta_energy)
        print(f"   🔧 Коррекция весов: базовый коэффициент = {adjustment:.4f}")

        new_weights={}
        for p,w in self.calibrated_weights.items():
            if p in ['PIVC','PDC']:
                new_w=w*(1.0+adjustment)
            else:
                new_w=w*(1.0-adjustment*0.5)
            new_weights[p]=new_w

        total=sum(new_weights.values()) or 1.0
        for p in new_weights: new_weights[p]/=total
        self.calibrated_weights=new_weights
        print(f"   ✅ Веса обновлены: { {p:round(w,3) for p,w in self.calibrated_weights.items()} }")

        self.last_phi_sources=sources or {"unknown":"no sources provided"}
        print(f"   📚 Источники сохранены: {list(self.last_phi_sources.keys()) if isinstance(self.last_phi_sources,dict) else self.last_phi_sources}")
        print("✅ Φ-сдвиг по трейлеру завершен — модель обновлена на основе реакции аудитории.")

    # === ПРОГНОЗ ===
    def simple_box_office_prediction(self,mol_score):
        x=[]; y=[]
        for f in self.historical_films:
            s=sum(f['principles'][p]*self.calibrated_weights[p] for p in self.calibrated_weights)
            x.append(s); y.append(f['box_office'])
        n=len(x)
        if n<3: avg=sum(y)/n if n>0 else 0; return {'point_estimate':avg,'millions':avg/1e6}
        sx=sum(x); sy=sum(y)
        sumx2=sum(xi*xi for xi in x); sumxy=sum(x[i]*y[i] for i in range(n))
        den=n*sumx2 - sx*sx
        if abs(den)<1e-12: avg=sy/n; return {'point_estimate':avg,'millions':avg/1e6}
        b=(n*sumxy - sx*sy)/den
        a=(sy - b*sx)/n
        pred=a+b*mol_score

        predictions=[a+b*xi for xi in x]
        errors=[y[i]-predictions[i] for i in range(n)]
        std_error=math.sqrt(sum(e*e for e in errors)/(n-2)) if n>2 else 0.0
        conf_lower=max(0.0,pred-1.96*std_error)
        conf_upper=pred+1.96*std_error
        return {'point_estimate':pred,'millions':pred/1e6,'confidence_range_millions':[conf_lower/1e6,conf_upper/1e6]}

    # === ВАЛИДАЦИЯ ===
    def custom_cross_validation(self):
        data=self.historical_films.copy()
        random.seed(42)
        random.shuffle(data)
        n_folds=5
        fold_size=max(1,len(data)//n_folds)
        mae_list=[]
        for fold in range(n_folds):
            test_start=fold*fold_size
            test_end=test_start+fold_size if fold<n_folds-1 else len(data)
            test_set=data[test_start:test_end]
            train_set=data[:test_start]+data[test_end:]
            if len(train_set)<2: continue
            train_weights=self.calibrate_on_subset(train_set)
            preds=[]; acts=[]
            for film in test_set:
                score=sum(film['principles'][p]*train_weights[p] for p in train_weights)
                preds.append(score)
                acts.append(film['success'])
            if not preds: continue
            mae=sum(abs(preds[i]-acts[i]) for i in range(len(preds)))/len(preds)
            mae_list.append(mae)
        mean_mae=sum(mae_list)/len(mae_list) if mae_list else 0.0
        stability='Высокая' if mean_mae<0.2 else 'Умеренная'
        return {'mean_MAE':mean_mae,'folds':len(mae_list),'stability':stability}

    def calibrate_on_subset(self,films_subset):
        principles=['PIVC','PLOA','PAA','PDC']
        correlations={}
        for p in principles:
            corr=self.calculate_correlation(
                [f['principles'][p] for f in films_subset],
                [f['success'] for f in films_subset]
            )
            level={'PIVC':1,'PLOA':2,'PAA':2,'PDC':1}[p]
            correlations[p]=abs(corr)/(level if level>0 else 1)
        total=sum(correlations.values()) or 1.0
        return {p: correlations[p]/total for p in correlations}

    # === СТРЕСС-ТЕСТЫ ===
    def stress_tests(self):
        cases=[
            {'name':'Идеальный фильм','principles':{'PIVC':1.0,'PLOA':1.0,'PAA':1.0,'PDC':1.0}},
            {'name':'Антифильм','principles':{'PIVC':0.0,'PLOA':0.0,'PAA':0.0,'PDC':0.0}},
            {'name':'Асимметричный','principles':{'PIVC':0.9,'PLOA':0.2,'PAA':0.2,'PDC':0.9}},
            {'name':'Только PIVC','principles':{'PIVC':0.9,'PLOA':0.1,'PAA':0.1,'PDC':0.1}}
        ]
        results=[]
        for c in cases:
            principles=c['principles']
            score=sum(principles[p]*self.calibrated_weights[p] for p in self.calibrated_weights)
            Oe=1.0-score
            values=list(principles.values())
            asymmetry=1.0-(min(values)/max(values)) if max(values)>0 else 1.0
            results.append({'case':c['name'],'mol_score':score,'O(E)':Oe,'asymmetry':asymmetry})
        return results

    # === ДЕТАЛЬНЫЙ РАЗБОР ===
    def get_detailed_breakdown(self):
        hail_mary={'PIVC':0.85,'PLOA':0.78,'PAA':0.80,'PDC':0.76}
        breakdown={}
        total_score=sum(hail_mary[p]*self.calibrated_weights[p] for p in hail_mary)
        for p,score in hail_mary.items():
            weight=self.calibrated_weights[p]
            contribution=score*weight
            percentage=(contribution/total_score*100) if total_score>0 else 0.0
            breakdown[p]={'score':score,'weight':weight,'contribution':contribution,'percentage':percentage}
        return breakdown

# === MAIN ===
def main():
    print("🧬 MOL-АНАЛИЗ 6.2 — реализация закона минимальной онтологической нагрузки (Termux-ready)")
    print("="*72)
    analyzer=FullMOLAnalyzer()

    trailer_data={
        'views':400_000_000,
        'like_ratio':0.96,
        'sentiment':0.87
    }
    trailer_sources={
        'ScreenRant':'https://screenrant.com/project-hail-mary-ryan-gosling-box-office-fall-guy-redemption/',
        'YouTube (official trailer)':'https://www.youtube.com/watch?v=---',
        'Wikipedia':'https://en.wikipedia.org/wiki/Project_Hail_Mary_(film)',
        'MOL Law DOI':'https://doi.org/10.5281/zenodo.17445023'
    }

    analyzer.apply_trailer_phi(trailer_data,trailer_sources)
    res=analyzer.analyze_hail_mary()

    bo=res['box_office_prediction']
    print(f"\n💰 ПРОГНОЗ СБОРОВ (точечная оценка): ${bo['millions']:.1f}M")
    if 'confidence_range_millions' in bo:
        low,high=bo['confidence_range_millions']
        print(f"   Доверительный интервал: ${low:.1f}M - ${high:.1f}M")

    val=res['validation']
    print(f"\n📈 ВАЛИДАЦИЯ: mean_MAE = {val['mean_MAE']:.3f} (folds={val['folds']})")
    print(f"   Стабильность модели: {val['stability']}")

    print("\n🔍 Детальный разбор принципов и вкладов:")
    breakdown=analyzer.get_detailed_breakdown()
    for p,d in breakdown.items():
        print(f"   {p}: score={d['score']:.2f} × weight={d['weight']:.3f} => contribution={d['contribution']:.3f} ({d['percentage']:.1f}%)")

    print("\n🧩 Стресс-тесты:")
    stress=analyzer.stress_tests()
    for s in stress:
        print(f"   {s['case']}: MOL={s['mol_score']:.3f}, O(E)={s['O(E)']:.3f}, Asymmetry={s['asymmetry']:.3f}")

    mol_score=res['mol_score']
    print("\n🎯 ИНТЕРПРЕТАЦИЯ:")
    if mol_score>0.7:
        print("   ✅ ВЫСОКИЙ ПОТЕНЦИАЛ УСПЕХА — фильм хорошо сбалансирован по MOL-принципам.")
    elif mol_score>0.5:
        print("   ⚠️ УМЕРЕННЫЙ ПОТЕНЦИАЛ — есть возможности для оптимизации (маркетинг/прайсинг/распространение).")
    else:
        print("   ❌ НИЗКИЙ ПОТЕНЦИАЛ — рекомендуем пересмотреть концепцию или маркетинг.")

    out_filename=f"mol_analysis6_2_{res['date']}.json"
    res['phi_sources']=analyzer.last_phi_sources
    with open(out_filename,'w',encoding='utf-8') as f:
        json.dump(res,f,ensure_ascii=False,indent=2)
    print(f"\n💾 Отчёт сохранён: {out_filename}")

if __name__=="__main__":
    main()
