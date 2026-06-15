"""
Тексты сообщений об ошибках для пользовательского интерфейса.

Автор: Бободжанова Мехрона Рахимовна
"""


def table_not_found(table_name):
    """Сообщение об отсутствии таблицы в базе данных."""
    return f'Таблица «{table_name}» не найдена в базе данных.'


def column_not_found(column_name, table_name=None):
    """Сообщение об отсутствии столбца."""
    if table_name:
        return f'Столбец «{column_name}» отсутствует в таблице «{table_name}».'
    return f'Столбец «{column_name}» недоступен для построения отчёта.'


def column_missing_in_data(column_name):
    """Сообщение, если столбец не попал в подготовленные данные."""
    return f'Столбец «{column_name}» не найден в подготовленных данных.'


def rows_not_found(table_name, criteria):
    """Сообщение, если строки по условию не найдены."""
    return f'В таблице «{table_name}» нет записей по условию: {criteria}.'


def record_not_found(column_name, value):
    """Сообщение об отсутствии одной записи."""
    return f'Запись с «{column_name}» = «{value}» не найдена.'


def mismatch_columns_count():
    """Сообщение о несовпадении числа столбцов и значений."""
    return 'Число столбцов и значений для поиска не совпадает.'


def positive_integer(field_name, value=None):
    """Сообщение о неверном целом положительном числе."""
    if value is None:
        return f'Поле «{field_name}»: укажите целое положительное число.'
    return (
        f'Поле «{field_name}»: укажите целое положительное число '
        f'(введено: «{value}»).'
    )


def year_integer(field_name, value=None):
    """Сообщение о неверном формате года."""
    if value is None:
        return f'Поле «{field_name}»: год должен быть целым числом.'
    return (
        f'Поле «{field_name}»: год должен быть целым числом '
        f'(введено: «{value}»).'
    )


def year_range_invalid(year_from, year_to):
    """Сообщение о неверном диапазоне лет."""
    return (
        f'Начальный год ({year_from}) не может быть больше конечного ({year_to}).'
    )


def no_projection_columns():
    """Сообщение, если для проекции не выбраны столбцы."""
    return 'Выберите хотя бы один столбец для проекции.'


def no_release_data(year_from, year_to):
    """Сообщение об отсутствии данных за период."""
    return (
        f'Нет записей с годом выпуска в диапазоне {year_from}–{year_to}. '
        'Проверьте фильтры на вкладке «Данные».'
    )


def data_file_not_found(path, table_name):
    """Сообщение об отсутствии файла данных."""
    return f'Не найден файл данных {path} для таблицы «{table_name}».'


def save_csv_error(details):
    """Сообщение об ошибке сохранения CSV."""
    return f'Не удалось сохранить отчёт в CSV: {details}'


def save_chart_error(details):
    """Сообщение об ошибке сохранения графика."""
    return f'Не удалось сохранить график: {details}'


def graph_not_enough_data():
    """Сообщение при недостатке данных для сетевого графа."""
    return 'Недостаточно связей актёр–режиссёр для построения графа.'


def content_not_found(title):
    """Сообщение, если контент по названию не найден."""
    return f'Контент с названием «{title}» не найден в базе.'
