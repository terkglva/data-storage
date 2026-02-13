"""
Анализ данных успеваемости студентов
Dataset: StudentsPerformance.csv
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ============================================================================
# 1. ЗАГРУЗКА И ИССЛЕДОВАНИЕ ДАННЫХ
# ============================================================================

print("=" * 80)
print("ЗАГРУЗКА И ИССЛЕДОВАНИЕ ДАТАСЕТА")
print("=" * 80)

# Загружаем данные
df = pd.read_csv(r'StudentsPerformance 1.csv')


# Базовая информация
print(f"\n📊 Размер датасета: {df.shape[0]} строк, {df.shape[1]} столбцов\n")

print("Первые 5 строк:")
print(df.head())

print("\n" + "=" * 80)
print("ТИПЫ ДАННЫХ")
print("=" * 80)
print(df.dtypes)

print("\n" + "=" * 80)
print("ОПИСАТЕЛЬНАЯ СТАТИСТИКА")
print("=" * 80)
print(df.describe())

print("\n" + "=" * 80)
print("ПРОПУЩЕННЫЕ ЗНАЧЕНИЯ")
print("=" * 80)
print(df.isnull().sum())

# ============================================================================
# 2. АНАЛИЗ КОРРЕЛЯЦИЙ
# ============================================================================

print("\n" + "=" * 80)
print("АНАЛИЗ КОРРЕЛЯЦИЙ МЕЖДУ ОЦЕНКАМИ")
print("=" * 80)

# Вычисляем корреляцию между числовыми колонками
numeric_cols = ['math score', 'reading score', 'writing score']
correlation_matrix = df[numeric_cols].corr()

print("\nМатрица корреляции:")
print(correlation_matrix)

# Находим наиболее коррелированные пары
print("\n" + "-" * 80)
print("НАИБОЛЕЕ КОРРЕЛИРОВАННЫЕ КОЛОНКИ")
print("-" * 80)

correlations = []
for i in range(len(numeric_cols)):
    for j in range(i+1, len(numeric_cols)):
        col1 = numeric_cols[i]
        col2 = numeric_cols[j]
        corr_value = correlation_matrix.loc[col1, col2]
        correlations.append((col1, col2, corr_value))

# Сортируем по убыванию корреляции
correlations.sort(key=lambda x: abs(x[2]), reverse=True)

for col1, col2, corr in correlations:
    print(f"  • {col1} <-> {col2}: {corr:.4f}")

print(f"\n🔍 ГЛАВНЫЙ ВЫВОД:")
print(f"   Самая высокая корреляция между '{correlations[0][0]}' и '{correlations[0][1]}'")
print(f"   Коэффициент корреляции: {correlations[0][2]:.4f}")
print(f"   Это означает очень сильную взаимосвязь между этими навыками!")

# ============================================================================
# 3. СОЗДАНИЕ ВИЗУАЛИЗАЦИИ
# ============================================================================

print("\n" + "=" * 80)
print("СОЗДАНИЕ ВИЗУАЛИЗАЦИИ")
print("=" * 80)

# Настройка стиля
sns.set_style("whitegrid")
plt.rcParams['figure.facecolor'] = 'white'

# Создаём фигуру с двумя графиками
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# ---- График 1: Scatter plot с регрессией ----
ax1 = axes[0]

# Точечный график
sns.scatterplot(data=df, x='reading score', y='writing score', 
                alpha=0.6, color='#2E86AB', s=50, ax=ax1)

# Линия регрессии
z = np.polyfit(df['reading score'], df['writing score'], 1)
p = np.poly1d(z)
x_line = df['reading score'].sort_values()
ax1.plot(x_line, p(x_line), "r--", linewidth=2, 
         label=f'Регрессия: y = {z[0]:.2f}x + {z[1]:.2f}')

ax1.set_xlabel('Reading Score (баллы по чтению)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Writing Score (баллы по письму)', fontsize=12, fontweight='bold')
ax1.set_title('Связь между баллами по чтению и письму\nКорреляция: r = 0.9546', 
              fontsize=14, fontweight='bold', pad=20)
ax1.legend(fontsize=10, loc='lower right')
ax1.grid(True, alpha=0.3)

# ---- График 2: Тепловая карта корреляций ----
ax2 = axes[1]

sns.heatmap(correlation_matrix, annot=True, cmap='RdYlGn', center=0.85, 
            square=True, linewidths=2, cbar_kws={"shrink": 0.8}, 
            fmt='.3f', ax=ax2, vmin=0.7, vmax=1.0, 
            annot_kws={'size': 12, 'weight': 'bold'})

ax2.set_title('Матрица корреляции между оценками по предметам', 
              fontsize=14, fontweight='bold', pad=20)
ax2.set_xticklabels(['Математика', 'Чтение', 'Письмо'], rotation=45, ha='right')
ax2.set_yticklabels(['Математика', 'Чтение', 'Письмо'], rotation=0)

# Сохраняем
plt.tight_layout()
plt.savefig('visualization.png', dpi=300, bbox_inches='tight')
print("\n✅ Визуализация сохранена в файл 'visualization.png'")

# ============================================================================
# 4. АНАЛИТИЧЕСКИЙ ИНСАЙТ
# ============================================================================

print("\n" + "=" * 80)
print("АНАЛИТИЧЕСКИЙ ИНСАЙТ")
print("=" * 80)

insight = """
 КЛЮЧЕВОЙ ВЫВОД:

Анализ данных о 1000 студентах выявил ИСКЛЮЧИТЕЛЬНО СИЛЬНУЮ взаимосвязь 
между баллами по чтению и письму (корреляция r = 0.9546). 

Это означает, что студенты, которые хорошо справляются с чтением, почти 
всегда демонстрируют высокие результаты и в письме, и наоборот. 

ПРАКТИЧЕСКОЕ ЗНАЧЕНИЕ:

Такая тесная связь указывает на то, что эти два навыка развиваются 
совместно и поддерживают друг друга. Вместо того чтобы отдельно развивать 
навыки чтения и письма, преподавателям следует применять ИНТЕГРИРОВАННЫЙ 
ПОДХОД, объединяющий эти компетенции в единый учебный процесс.

Примеры:
  • Анализ прочитанных текстов с последующим написанием эссе
  • Критическое чтение с письменной рефлексией
  • Совместные проекты, требующие чтения исследований и создания текстов

ДОПОЛНИТЕЛЬНО:

Также заметна умеренно-сильная корреляция между математикой и языковыми 
дисциплинами (r ≈ 0.81), что предполагает наличие общих когнитивных 
способностей или учебных привычек, влияющих на успеваемость в целом.
"""

print(insight)

print("\n" + "=" * 80)
print("АНАЛИЗ ЗАВЕРШЁН!")
print("=" * 80)