"""
Расширенная аналитика: поиск похожего контента и сетевой анализ.

Автор: Бободжанова Мехрона Рахимовна
"""

import re

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.patches import Patch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import Library.analysis as analysis
import Library.messages as messages
import Library.reports as reports

# Пастельная палитра для графа актёров и режиссёров
DIRECTOR_COLOR = '#0e98c3'
ACTOR_COLOR = '#4bcc63'
EDGE_COLOR = '#0f1624' #'#B0B0B0'
TEXT_COLOR = '#333333'


def _normalize_text(text):
    """Приводит текст описания к нижнему регистру и убирает лишние символы."""
    text = str(text).lower()
    return re.sub(r'[^a-z0-9\s]', ' ', text)


def find_similar_content(title, top_n=10):
    """
    Ищет схожий контент по описаниям с помощью TF-IDF.

    Параметры
    ----------
    title : str
        Название фильма или сериала.
    top_n : int
        Число похожих записей.

    Возвращает
    ----------
    pandas.DataFrame
        Таблица с похожими названиями и коэффициентом сходства.
    """
    df = analysis.get_main_dataframe().copy()
    df['norm_description'] = df['description'].fillna('').apply(_normalize_text)

    title_list = [value.lower() for value in df['title'].values]
    if title.lower() not in title_list:
        raise LookupError(messages.content_not_found(title))

    # Создаём векторизатор TF-IDF: каждое описание превращается в числовой вектор,
    # где важность слова учитывает его частоту в документе и редкость во всём корпусе.
    # stop_words='english' — служебные слова (the, is, and...) не участвуют в сравнении.
    vectorizer = TfidfVectorizer(stop_words='english')

    # fit_transform: обучается на всех описаниях (строит словарь слов) и сразу
    # преобразует их в разреженную матрицу размера (число фильмов × число уникальных слов).
    matrix = vectorizer.fit_transform(df['norm_description'])

    # Находим индекс строки выбранного фильма в матрице по его названию.
    idx = df.index[df['title'] == title][0]

    # Сравниваем вектор выбранного фильма с векторами всех остальных:
    # cosine_similarity возвращает значения от 0 (не похожи) до 1 (идентичны по тексту).
    # flatten() превращает результат из матрицы 1×N в одномерный массив оценок.
    scores = cosine_similarity(matrix[idx], matrix).flatten()

    result = df.copy()
    result['cosine_similarity'] = scores
    result = result[result['title'] != title]
    result = result.sort_values('cosine_similarity', ascending=False).head(top_n)

    return result[['title', 'type', 'country', 'release_year', 'cosine_similarity']]


def _offset_label_positions(pos, offset=0.14):
    """
    Смещает подписи узлов от центра, чтобы они не перекрывали квадраты.

    Параметры
    ----------
    pos : dict
        Координаты узлов.
    offset : float
        Величина смещения подписи от узла.

    Возвращает
    ----------
    dict
        Координаты для размещения текста.
    """
    positions = np.array(list(pos.values()))
    centroid = positions.mean(axis=0)
    label_pos = {}

    for node, (x_pos, y_pos) in pos.items():
        dx = x_pos - centroid[0]
        dy = y_pos - centroid[1]
        length = np.hypot(dx, dy)
        if length < 1e-6:
            dx, dy, length = 1.0, 0.0, 1.0
        label_pos[node] = (
            x_pos + dx / length * offset,
            y_pos + dy / length * offset,
        )

    return label_pos


def build_actor_director_graph(min_collaborations=1, max_edges=100):
    """
    Строит граф связей между актёрами и режиссёрами.

    Параметры
    ----------
    min_collaborations : int
        Минимальное число совместных проектов.
    max_nodes : int
        Максимальное число узлов.

    Возвращает
    ----------
    tuple
        (networkx.Graph, pandas.DataFrame).
    """
    crew = (
        reports.get_dataframe_for_columns('actor_name', 'director_name')
        [['actor_name', 'director_name']]
        .drop_duplicates()
    )
    # Группируем по паре (режиссёр, актёр) и считаем, сколько раз они встречались
    # вместе — это число совместных проектов (рёбра будущего графа).
    edges = (
        crew.groupby(['director_name', 'actor_name'])
        .size()
        .reset_index(name='projects')
    )

    edges = edges[edges['projects'] >= min_collaborations]
    
    # Берём самые «сильные» связи, чтобы граф не перегружался узлами.
    edges = edges.sort_values('projects', ascending=False).head(max_edges)

    # Создаём неориентированный граф: узлы — люди, рёбра — совместные проекты.
    graph = nx.Graph()
    for _, row in edges.iterrows():
        graph.add_edge(
            # Префиксы «Р:» и «А:» различают режиссёров и актёров на визуализации.
            f"Р: {row['director_name']}",
            f"А: {row['actor_name']}",
            weight=row['projects'],  # толщина/важность ребра = число совместных проектов
        )

    # Возвращаем граф для отрисовки и таблицу рёбер для вывода в интерфейсе.
    return graph, edges.rename(columns={
        'director_name': 'Режиссёр',
        'actor_name': 'Актёр',
        'projects': 'Совместных проектов',
    })


def plot_actor_director_network(graph=None, min_collaborations=1, max_edges=20):
    """
    Визуализирует сеть взаимосвязей актёров и режиссёров.

    Параметры
    ----------
    min_collaborations : int
        Минимальное число совместных проектов.
    max_nodes : int
        Ограничение числа узлов.

    Возвращает
    ----------
    matplotlib.figure.Figure
        Объект графика.
    """
    if not graph:
        graph = build_actor_director_graph(min_collaborations, max_edges) 

    if graph.number_of_nodes() == 0:
        raise ValueError(messages.graph_not_enough_data())

    fig, ax = plt.subplots(figsize=(13, 9))
    fig.patch.set_facecolor('#FAFAFA')
    ax.set_facecolor('#FAFAFA')

    # Увеличенное k раздвигает вершины друг от друга
    pos = nx.spring_layout(graph, seed=42, k=1.6, iterations=100, scale=1.6)

    node_colors = [
        DIRECTOR_COLOR if node.startswith('Р:') else ACTOR_COLOR
        for node in graph.nodes()
    ]

    # Квадратные узлы с пастельной заливкой и тонкой обводкой
    nx.draw_networkx_nodes(
        graph,
        pos,
        node_color=node_colors,
        node_size=200,
        # edgecolors='#888888',
        linewidths=0.8,
        ax=ax,
    )

    # Рёбра одинаковой толщины
    nx.draw_networkx_edges(
        graph,
        pos,
        edge_color=EDGE_COLOR,
        width=1.4,
        alpha=0.65,
        ax=ax,
    )

    edge_labels = {
        (u, v): d['weight']
        for u, v, d in graph.edges(data=True)
    }
    nx.draw_networkx_edge_labels(
        graph,
        pos,
        edge_labels=edge_labels,
        font_size=7,
        font_color=TEXT_COLOR,
        bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none', alpha=0.8),
        ax=ax,
    )

    # Подписи без префиксов, смещены от узлов для читаемости
    labels = {node: node.split(': ', 1)[1] for node in graph.nodes()}
    label_pos = _offset_label_positions(pos, offset=0.16)
    nx.draw_networkx_labels(
        graph,
        label_pos,
        labels=labels,
        font_size=7,
        font_color=TEXT_COLOR,
        font_weight='bold',
        bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='none', alpha=0.85),
        ax=ax,
    )

    ax.set_title(
        'Сеть взаимосвязей актёров и режиссёров',
        fontsize=13,
        color=TEXT_COLOR,
        pad=14,
    )
    ax.legend(
        handles=[
            Patch(facecolor=DIRECTOR_COLOR, edgecolor='#888888', label='Режиссёр'),
            Patch(facecolor=ACTOR_COLOR, edgecolor='#888888', label='Актёр'),
        ],
        loc='upper left',
        framealpha=0.9,
        fontsize=9,
    )
    fig.text(
        0.5,
        0.02,
        'Число на ребре — количество совместных проектов',
        ha='center',
        fontsize=9,
        color='#555555',
    )

    ax.axis('off')
    fig.subplots_adjust(left=0.10, bottom=0.20, right=0.96, top=0.90)
    return fig
