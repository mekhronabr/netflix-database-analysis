"""
Модуль аналитических функций для датасета Netflix.

Автор: Бободжанова Мехрона Рахимовна
"""

import matplotlib.pyplot as plt
import pandas as pd

import Library.messages as messages
import Library.reports as reports


def _parse_year(value, field_name='Год'):
    """
    Преобразует значение года в int или None, если поле пустое/NaN/некорректное.

    Параметры
    ----------
    value : str, int, float, optional
        Значение из поля ввода или таблицы.

    Возвращает
    ----------
    int or None
        Год или None, если фильтр по году не задан.
    """
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None

    text = str(value).strip()
    if not text or text.lower() == 'nan':
        return None

    try:
        return int(float(text))
    except (ValueError, TypeError) as error:
        raise ValueError(messages.year_integer(field_name, text)) from error


def get_main_dataframe():
    """
    Возвращает объединённую таблицу контента Netflix с типами.

    Возвращает
    ----------
    pandas.DataFrame
        Основные данные о фильмах и сериалах.
    """
    main_columns = [
        'title', 'show_type_name', 'country', 'date_added',
        'release_year', 'rating', 'duration_minutes', 'duration_seasons',
        'description',
    ]
    df = reports.get_dataframe_for_columns(*main_columns)
    return df.rename(columns={'show_type_name': 'type'})[
        [
            'title', 'type', 'country', 'date_added',
            'release_year', 'rating', 'duration_minutes', 'duration_seasons',
            'description',
        ]
    ]


def filter_content(show_type=None, country=None, year_from=None, year_to=None):
    """
    Фильтрует контент по типу, стране и году выпуска.

    Параметры
    ----------
    show_type : str, optional
        Тип контента (Movie / TV Show).
    country : str, optional
        Подстрока для поиска в поле страны.
    year_from : int, optional
        Минимальный год выпуска.
    year_to : int, optional
        Максимальный год выпуска.

    Возвращает
    ----------
    pandas.DataFrame
        Отфильтрованная таблица.
    """
    df = get_main_dataframe().copy()

    if show_type and show_type != 'Все':
        df = df[df['type'] == show_type]

    if country and country.strip():
        mask = df['country'].fillna('').str.contains(country.strip(), case=False)
        df = df[mask]

    year_from = _parse_year(year_from, 'Год от')
    year_to = _parse_year(year_to, 'Год до')

    if year_from is not None and year_to is not None and year_from > year_to:
        raise ValueError(messages.year_range_invalid(year_from, year_to))

    if year_from is not None:
        df = df[df['release_year'] >= year_from]

    if year_to is not None:
        df = df[df['release_year'] <= year_to]

    return df


def get_summary_statistics(df=None):
    """
    Формирует сводную статистику по датасету.

    Параметры
    ----------
    df : pandas.DataFrame, optional
        Таблица для анализа. По умолчанию — все данные.

    Возвращает
    ----------
    pandas.DataFrame
        Таблица с ключевыми показателями.
    """
    data = df if df is not None else get_main_dataframe()
    years = data['release_year'].dropna()

    if years.empty:
        mean_year = '—'
        min_year = '—'
        max_year = '—'
    else:
        mean_year = round(years.mean(), 1)
        min_year = int(years.min())
        max_year = int(years.max())

    stats = {
        'Показатель': [
            'Всего записей',
            'Фильмы',
            'Сериалы',
            'Уникальных стран',
            'Средний год выпуска',
            'Мин. год выпуска',
            'Макс. год выпуска',
        ],
        'Значение': [
            len(data),
            len(data[data['type'] == 'Movie']),
            len(data[data['type'] == 'TV Show']),
            data['country'].fillna('Не указано').nunique(),
            mean_year,
            min_year,
            max_year,
        ],
    }
    return pd.DataFrame(stats)


def get_country_distribution(df=None, top_n=15):
    """
    Считает распределение контента по странам.

    Параметры
    ----------
    df : pandas.DataFrame, optional
        Исходная таблица.
    top_n : int
        Число стран в топе.

    Возвращает
    ----------
    pandas.DataFrame
        Страна и количество записей.
    """
    data = get_main_dataframe() if df is None else df
    countries = (
        data['country']
        .fillna('Не указано')
        .str.split(',')
        .explode()
        .str.strip()
    )
    counts = countries.value_counts().head(top_n).reset_index()
    counts.columns = ['Страна', 'Количество']
    return counts


def plot_country_distribution(counts=None, df=None, top_n=15):
    """
    Строит столбчатую диаграмму распределения по странам.

    Параметры
    ----------
    df : pandas.DataFrame, optional
        Исходная таблица.
    top_n : int
        Число стран на графике.

    Возвращает
    ----------
    matplotlib.figure.Figure
        Объект графика.
    """
    if counts is None:
        counts = get_country_distribution(top_n=top_n)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(counts['Страна'], counts['Количество'], color='#e50914')
    ax.set_title('Распределение контента по странам')
    ax.set_xlabel('Страна')
    ax.set_ylabel('Количество')
    plt.xticks(rotation=45, ha='right')
    fig.subplots_adjust(left=0.10, bottom=0.22, right=0.96, top=0.90)
    return fig


def get_release_dynamics(df=None, year_from=2000, year_to=2020):
    """
    Возвращает динамику выпуска фильмов и сериалов по годам.

    Параметры
    ----------
    year_from : int
        Начальный год для отчёта.

    Возвращает
    ----------
    pandas.DataFrame
        Год, тип контента и количество.
    """
    if df is None:
        df = get_main_dataframe()

    df = df[(df['release_year'] >= year_from) & (df['release_year'] <= year_to)]
    return (
        df.groupby(['release_year', 'type'])
        .size().reset_index(name='Количество')
    )


def plot_release_dynamics(dynamics=None, source_df=None, year_from=2018, year_to=2021):
    """
    Строит график динамики выпуска фильмов и сериалов.

    Параметры
    ----------
    year_from : int
        Начальный год.

    Возвращает
    ----------
    matplotlib.figure.Figure
        Объект графика.
    """
    if dynamics is None:
        dynamics = get_release_dynamics(df=source_df, year_from=year_from, year_to=year_to)

    fig, ax = plt.subplots(figsize=(10, 6))

    for show_type in dynamics['type'].unique():
        subset = dynamics[dynamics['type'] == show_type]
        ax.plot(
            subset['release_year'],
            subset['Количество'],
            marker='o',
            label=show_type,
        )

    years = sorted(dynamics['release_year'].unique())
    ax.set_xticks(years)
    ax.set_xticklabels([str(y) for y in years], rotation=45, ha='right')
    ax.tick_params(axis='x', labelsize=8)
    ax.set_title('Динамика выпуска фильмов и сериалов')
    ax.set_xlabel('Год выпуска')
    ax.set_ylabel('Количество')
    ax.legend(title='Тип')
    ax.grid(True, linestyle='--', alpha=1)
    fig.subplots_adjust(left=0.10, bottom=0.22, right=0.96, top=0.90)
    return fig
