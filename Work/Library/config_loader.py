"""
Модуль загрузки и сохранения параметров приложения из файла settings.ini.

Автор: Бободжанова Мехрона Рахимовна
"""

from configparser import ConfigParser
from pathlib import Path

# Путь к файлу настроек рядом с главным скриптом
SETTINGS_PATH = Path(__file__).resolve().parent.parent / 'Scripts' / 'settings.ini'

# Значения по умолчанию, если секция или ключ отсутствуют в .ini
DEFAULTS = {
    'Paths': {
        'data_path': '../Data',
        'output_path': '../Output',
        'graphics_path': '../Graphics',
    },
    'UI': {
        'window_width': '1100',
        'window_height': '700',
        'bg_color': '#f0f0f0',
        'font_family': 'Arial',
        'font_size': '11',
        'accent_color': '#e50914',
    },
}


def load_settings(path=None):
    """
    Загружает настройки из .ini-файла.

    Параметры
    ----------
    path : str или Path, optional
        Путь к файлу настроек. По умолчанию — settings.ini в Scripts.

    Возвращает
    ----------
    ConfigParser
        Объект с прочитанными параметрами.
    """
    config = ConfigParser()
    config.read_dict(DEFAULTS)

    settings_file = Path(path) if path else SETTINGS_PATH
    if settings_file.exists():
        config.read(settings_file, encoding='utf-8')

    return config


def save_settings(config, path=None):
    """
    Сохраняет настройки в .ini-файл.

    Параметры
    ----------
    config : ConfigParser
        Объект конфигурации для записи.
    path : str или Path, optional
        Путь к файлу настроек.

    Возвращает
    ----------
    Path
        Путь к сохранённому файлу.
    """
    settings_file = Path(path) if path else SETTINGS_PATH
    settings_file.parent.mkdir(parents=True, exist_ok=True)

    with open(settings_file, 'w', encoding='utf-8') as ini_file:
        config.write(ini_file)

    return settings_file


def resolve_path(relative_path, base=None):
    """
    Преобразует относительный путь из .ini в абсолютный.

    Параметры
    ----------
    relative_path : str
        Относительный путь из конфигурации.
    base : Path, optional
        Базовая директория. По умолчанию — каталог Work.

    Возвращает
    ----------
    Path
        Абсолютный путь к каталогу или файлу.
    """
    work_dir = base or Path(__file__).resolve().parent
    return (work_dir / relative_path).resolve()
