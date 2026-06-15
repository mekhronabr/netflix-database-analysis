"""
Функции объединения таблиц датасета Netflix.

Автор: Бободжанова Мехрона Рахимовна
"""

import pandas as pd

import Library.db_loader as db_loader


def get_merged_by_genre(df):
    """Добавляет к таблице названия жанров."""
    df = pd.merge(df, db_loader.database['show_genre'], on='show_id')
    df = pd.merge(df, db_loader.database['genres'], on='genre_id')
    return df.drop(columns=['genre_id'])


def get_merged_by_actor(df):
    """Добавляет к таблице имена актёров."""
    df = pd.merge(df, db_loader.database['show_crew'], on='show_id')
    df = pd.merge(df, db_loader.database['actors'], on='actor_id')
    df = df.drop(columns=['director_id', 'actor_id'])
    return df.drop_duplicates()


def get_merged_by_director(df):
    """Добавляет к таблице имена режиссёров."""
    df = pd.merge(df, db_loader.database['show_crew'], on='show_id')
    df = pd.merge(df, db_loader.database['directors'], on='director_id')
    df = df.drop(columns=['director_id', 'actor_id'])
    return df.drop_duplicates()


def get_merged_by_crew(df):
    """Добавляет пару актёр–режиссёр из одной строки show_crew."""
    df = pd.merge(df, db_loader.database['show_crew'], on='show_id')
    df = pd.merge(df, db_loader.database['actors'], on='actor_id')
    df = pd.merge(df, db_loader.database['directors'], on='director_id')
    return df.drop(columns=['director_id', 'actor_id']).drop_duplicates()


def get_merged_by_type(df):
    """Добавляет к таблице названия типов контента."""
    df = pd.merge(df, db_loader.database['show_types'], on='show_type_id')
    return df.drop(columns=['show_type_id'])
