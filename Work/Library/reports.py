"""
Модуль формирования отчётов и графиков по датасету Netflix.

Автор: Бободжанова Мехрона Рахимовна
"""

import matplotlib.pyplot as plt
import pandas as pd

import Library.db_loader as db_loader
from Library import db_merge, messages

BRIDGE_MERGES = {
    'genre_name': db_merge.get_merged_by_genre,
    'actor_name': db_merge.get_merged_by_actor,
    'director_name': db_merge.get_merged_by_director,
    'show_type_name': db_merge.get_merged_by_type,
}

BRIDGE_COLUMN_NAMES = (
    'genre_name',
    'actor_name',
    'director_name',
    'show_type_name',
)

CREW_COLUMNS = frozenset({'actor_name', 'director_name'})

COLUMN_LABELS = {
    'show_id': 'Идентификатор',
    'show_type_id': 'Идентификатор типа',
    'title': 'Название',
    'country': 'Страна',
    'date_added': 'Дата добавления',
    'release_year': 'Год выпуска',
    'rating': 'Рейтинг',
    'description': 'Описание',
    'duration_minutes': 'Длительность (мин)',
    'duration_seasons': 'Число сезонов',
    'show_type_name': 'Тип контента',
    'genre_name': 'Жанр',
    'actor_name': 'Актёр',
    'director_name': 'Режиссёр',
}


def get_column_label(column_name):
    """Возвращает понятное пользователю имя столбца."""
    return COLUMN_LABELS.get(column_name, str(column_name).replace('_', ' '))


def resolve_column_name(label, columns):
    """Находит техническое имя столбца по подписи из интерфейса."""
    for column in columns:
        if get_column_label(column) == label:
            return column
    if label in columns:
        return label
    raise KeyError(messages.column_not_found(label))


def format_report_for_display(report):
    """Переименовывает столбцы и индекс отчёта для показа пользователю."""
    display = report.copy()
    display = display.rename(columns={
        column: get_column_label(column) for column in display.columns
    })
    display.index = [
        get_column_label(index) if index in COLUMN_LABELS else index
        for index in display.index
    ]
    return display


def get_all_report_columns():
    """
    Возвращает список столбцов, доступных для текстовых и графических отчётов.

    Включает поля таблицы shows и столбцы из связанных справочников.
    """
    shows_columns = list(db_loader.database['shows'].columns)
    extra = [name for name in BRIDGE_COLUMN_NAMES if name not in shows_columns]
    return shows_columns + extra


def _ensure_columns(df, *column_names):
    """Проверяет наличие столбцов в DataFrame перед построением отчёта."""
    for column_name in column_names:
        if column_name not in df.columns:
            raise KeyError(messages.column_missing_in_data(column_name))


def get_dataframe_for_columns(*columns):
    """Возвращает DataFrame только с нужными merge для указанных столбцов."""
    columns = [col for col in columns if col]
    base = db_loader.database['shows'].copy()
    bridge_cols = [col for col in dict.fromkeys(columns) if col in BRIDGE_MERGES]
    plain_cols = [
        col for col in dict.fromkeys(columns)
        if col not in BRIDGE_MERGES
        and col in base.columns
        and col != 'show_id'
    ]

    if 'actor_name' in columns and 'director_name' in columns:
        df = db_merge.get_merged_by_crew(base)
        for col in bridge_cols:
            if col in CREW_COLUMNS:
                continue
            part = BRIDGE_MERGES[col](base)[['show_id', col]].drop_duplicates()
            df = pd.merge(df, part, on='show_id', how='left')
    elif not bridge_cols:
        df = base
    else:
        merge_funcs = []
        for col in bridge_cols:
            merge_func = BRIDGE_MERGES.get(col)
            if merge_func is not None and merge_func not in merge_funcs:
                merge_funcs.append(merge_func)

        if len(merge_funcs) == 1:
            df = merge_funcs[0](base)
        else:
            parts = []
            for col in bridge_cols:
                part = BRIDGE_MERGES[col](base)[['show_id', col]].drop_duplicates()
                parts.append(part)
            df = parts[0]
            for part in parts[1:]:
                df = pd.merge(df, part, on='show_id', how='inner')
            if plain_cols:
                right = base[['show_id'] + plain_cols].drop_duplicates(subset=['show_id'])
                df = pd.merge(df, right, on='show_id', how='left')

    return df


def get_statistics_report(df, column_name): 
    """
    Формирует статистический отчет для выбранного атрибута.
    """
    if df[column_name].dtype == 'object' or df[column_name].dtype == 'category':
        freq = df[column_name].value_counts().reset_index()
        freq.columns = ['Уровень', 'Частота']
        freq['Процент'] = (freq['Частота'] / freq['Частота'].sum()) * 100
        return freq

    stats = {
        'Мин': df[column_name].min(),
        'Макс': df[column_name].max(),
        'Среднее': df[column_name].mean(),
        'Дисперсия': df[column_name].var(),
        'Ст.Откл': df[column_name].std()
    }

    return pd.DataFrame([stats], index=[column_name])

def get_pivot_table_report(index_col, columns_col, values_col, agg_func='count'):
    """
    Создает сводную таблицу.
    - index_col: Атрибут для строк
    - columns_col: Атрибут для столбцов
    - values_col: Атрибут для вычислений (например, ID)
    - agg_func: Метод агрегации ('count', 'mean', 'sum' и т.д.)
    """
    return pd.pivot_table(
        get_dataframe_for_columns(index_col, columns_col, values_col),
        values=values_col,
        index=index_col,
        columns=columns_col,
        aggfunc=agg_func,
        fill_value=0,
    )

def plot_clustered_bar(cat_col1, cat_col2, top_n=10):
    """Строит кластеризованную столбчатую диаграмму по двум категориям."""
    df = get_dataframe_for_columns(cat_col1, cat_col2)
    _ensure_columns(df, cat_col1, cat_col2)

    counts = pd.crosstab(df[cat_col1], df[cat_col2])
    counts = counts.stack().sort_values(ascending=False).head(top_n)
    counts = counts.unstack(fill_value=0)

    ax = counts.plot(kind='bar', figsize=(10, 6), rot=0)
    ax.legend(
        title=get_column_label(cat_col2),
        loc='upper left',
        bbox_to_anchor=(1.02, 1),
        borderaxespad=0,
    )

    plt.xticks(rotation=45, ha='right')
    plt.title(
        f'Распределение: {get_column_label(cat_col1)} по {get_column_label(cat_col2)}'
    )
    plt.xlabel(get_column_label(cat_col1))
    plt.ylabel('Количество')
    plt.gcf().subplots_adjust(left=0.10, bottom=0.22, right=0.72, top=0.90)

    return plt.gcf()

def plot_categorized_hist(quant_col, cat_col, bins=10, top_n=10):
    """Строит категоризированную гистограмму."""
    df = get_dataframe_for_columns(quant_col, cat_col)
    _ensure_columns(df, quant_col, cat_col)
    categories = df[cat_col].value_counts().head(top_n).index
    fig, ax = plt.subplots(figsize=(10, 6))

    for cat in categories:
        data = df.loc[df[cat_col] == cat, quant_col].dropna()
        ax.hist(data, bins=bins, alpha=0.5, label=str(cat), edgecolor='black')
    
    ax.set_title(
        f'Распределение {get_column_label(quant_col)} по {get_column_label(cat_col)}'
    )
    ax.set_xlabel(get_column_label(quant_col))
    ax.set_ylabel('Частота')
    ax.legend(title=get_column_label(cat_col))
    fig.subplots_adjust(left=0.10, bottom=0.14, right=0.96, top=0.90)

    return fig

def plot_categorized_boxplot(quant_col, cat_col, top_n=10):
    """Строит диаграмму Бокса-Вискера по категориям."""
    df = get_dataframe_for_columns(quant_col, cat_col)
    _ensure_columns(df, quant_col, cat_col)

    categories = df[cat_col].value_counts().head(top_n).index
    data_to_plot = [
        df.loc[df[cat_col] == cat, quant_col].dropna()
        for cat in categories
    ]

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.boxplot(
        data_to_plot,
        labels=[str(cat) for cat in categories],
        patch_artist=True,
    )

    ax.set_title(
        'Диаграмма Бокса-Вискера: '
        f'{get_column_label(quant_col)} по {get_column_label(cat_col)}'
    )
    ax.set_xlabel(get_column_label(cat_col))
    ax.set_ylabel(get_column_label(quant_col))
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    fig.subplots_adjust(left=0.10, bottom=0.22, right=0.96, top=0.90)

    return fig


def plot_categorized_scatter(x_col, y_col, cat_col, top_n=10, max_points=500):
    """Строит диаграмму рассеивания с группировкой по категории."""
    df = get_dataframe_for_columns(x_col, y_col, cat_col)
    _ensure_columns(df, x_col, y_col, cat_col)

    categories = df[cat_col].value_counts().head(top_n).index
    fig, ax = plt.subplots(figsize=(10, 7))

    for cat in categories:
        subset = df.loc[df[cat_col] == cat, [x_col, y_col]].dropna()
        if len(subset) > max_points:
            subset = subset.sample(n=max_points, random_state=42)
        ax.scatter(subset[x_col], subset[y_col], label=str(cat), alpha=0.7)

    ax.set_title(
        'Диаграмма рассеивания: '
        f'{get_column_label(x_col)} и {get_column_label(y_col)} '
        f'(по {get_column_label(cat_col)})'
    )
    ax.set_xlabel(get_column_label(x_col))
    ax.set_ylabel(get_column_label(y_col))
    ax.legend(
        title=get_column_label(cat_col),
        loc='upper left',
        bbox_to_anchor=(1.02, 1),
        borderaxespad=0,
    )
    ax.grid(True, linestyle='--', alpha=0.6)
    fig.subplots_adjust(left=0.10, bottom=0.14, right=0.72, top=0.90)

    return fig

def save_report_to_csv(report, file_path):
    """Сохраняет табличный отчёт в CSV."""
    try:
        report.to_csv(file_path, index=False, encoding='utf-8-sig')
    except OSError as error:
        raise IOError(messages.save_csv_error(error)) from error


def save_chart_to_file(fig, file_path):
    """Экспортирует график в файл PNG или PDF."""
    try:
        fig.savefig(file_path, dpi=300, bbox_inches='tight', pad_inches=0.25)
    except OSError as error:
        raise IOError(messages.save_chart_error(error)) from error
