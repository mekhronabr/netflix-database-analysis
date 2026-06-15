"""
Модуль загрузки и изменения данных датасета Netflix.

Автор: Бободжанова Мехрона Рахимовна
"""

from pathlib import Path
import pandas as pd
import pickle

from Library import messages

DATA_PATH = Path(__file__).resolve().parent.parent / 'Data'
DEFAULT_TABLES = ['directors', 'actors', 'show_crew', 'shows', 'show_types', 'genres', 'show_genre']
database = {}


def convert_csv_to_binary(table_names=None):
    """
    Конвертирует CSV-файлы в двоичный формат pickle.

    Параметры
    ----------
    table_names : list, optional
        Имена таблиц без расширения. Если не задано — все .csv в DATA_PATH.
    """
    if table_names is None:
        table_names = [
            path.stem for path in DATA_PATH.glob('*.csv')
        ]

    for name in table_names:
        csv_path = DATA_PATH / f'{name}.csv'
        if not csv_path.exists():
            continue

        df = pd.read_csv(csv_path)
        if 'Unnamed: 0' in df.columns:
            df = df.drop(columns=['Unnamed: 0'])
        with open(DATA_PATH / f'{name}.pkl', 'wb') as pkl_file:
            pickle.dump(df, pkl_file)


def load_data(table_names=None):
    """Загружает справочники из двоичных файлов, при необходимости создаёт их из CSV."""
    global database
    if not table_names:
        table_names = DEFAULT_TABLES

    for name in table_names:
        pkl_path = DATA_PATH / f'{name}.pkl'
        csv_path = DATA_PATH / f'{name}.csv'

        if not pkl_path.exists():
            if not csv_path.exists():
                raise FileNotFoundError(
                    messages.data_file_not_found(csv_path, name)
                )
            convert_csv_to_binary([name])

        try:
            with open(pkl_path, 'rb') as pkl_file:
                database[name] = pickle.load(pkl_file)
        except (TypeError, EOFError, pickle.UnpicklingError):
            # Пересоздаём pickle при несовместимости версий pandas
            if not csv_path.exists():
                raise FileNotFoundError(
                    messages.data_file_not_found(csv_path, name)
                )
            convert_csv_to_binary([name])
            with open(pkl_path, 'rb') as pkl_file:
                database[name] = pickle.load(pkl_file)

    return database


def save_table_data(table_name):
    global database
    if table_name not in database:
        raise KeyError(messages.table_not_found(table_name))

    with open(DATA_PATH / f'{table_name}.pkl', 'wb') as pkl_file:
        pickle.dump(database[table_name], pkl_file)

def save_data():
    global database
    for table_name in database.keys():
        save_table_data(table_name)


def _column_values_equal(series, value):
    """Сравнивает столбец таблицы с одним значением с учётом NaN и строк."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return series.isna()
    if isinstance(value, str) and series.dtype == object:
        return series.fillna('').str.lower() == value.lower()
    return series == value


def row_exists(table_name, row_data):
    """
    Проверяет, есть ли в таблице дублирующая запись.

    Дубликатом считается:
    - полное совпадение всех столбцов;
    - совпадение первичного ключа (первый столбец);
    - совпадение остальных столбцов (без учёта id).

    Параметры
    ----------
    table_name : str
        Имя таблицы.
    row_data : dict
        Проверяемая запись.

    Возвращает
    ----------
    bool
        True, если такая запись уже есть.
    """
    if table_name not in database:
        raise KeyError(messages.table_not_found(table_name))

    df = database[table_name]
    columns = list(df.columns)

    # Полное совпадение всех столбцов
    mask = pd.Series(True, index=df.index)
    for column in columns:
        mask &= _column_values_equal(df[column], row_data.get(column))
    if mask.any():
        return True

    # Совпадение первичного ключа
    primary_key = columns[0]
    pk_value = row_data.get(primary_key)
    if pk_value is not None and (df[primary_key] == pk_value).any():
        return True

    # Совпадение по содержимому без учёта id-столбцов
    content_columns = [col for col in columns if not col.endswith('_id')]
    if content_columns:
        mask = pd.Series(True, index=df.index)
        for column in content_columns:
            mask &= _column_values_equal(df[column], row_data.get(column))
        if mask.any():
            return True

    return False


def get_indices_by_value(table_name, column_names, values):
    global database
    if table_name not in database:
        raise KeyError(messages.table_not_found(table_name))
    
    df = database[table_name]
    indices_cnt = {}
    for column, value in zip(column_names, values):
        if column not in df.columns:
            raise ValueError(messages.column_not_found(column, table_name))

        for index in df[_column_values_equal(df[column], value)].index.tolist():
            indices_cnt[index] = indices_cnt.get(index, 0) + 1
    
    return [index for index, cnt in indices_cnt.items() if cnt == len(column_names)] 

def delete_rows_by_value(table_name, column_names, values):
    global database
    if len(column_names) != len(values):
        raise ValueError(messages.mismatch_columns_count())
    
    indices = get_indices_by_value(table_name, column_names, values)

    if not indices:
        raise LookupError(
            messages.rows_not_found(
                table_name,
                dict(zip(column_names, values)),
            )
        )
    
    database[table_name] = database[table_name].drop(indices)
    save_table_data(table_name)

def edit_table_column(table_name, condition_column, condition_value, target_column, new_value):
    global database
    if table_name not in database:
        raise KeyError(messages.table_not_found(table_name))

    df = database[table_name]
    mask = _column_values_equal(df[condition_column], condition_value)

    if not mask.any():
        raise LookupError(messages.record_not_found(condition_column, condition_value))

    df.loc[mask, target_column] = new_value
    database[table_name] = df
    save_table_data(table_name)
