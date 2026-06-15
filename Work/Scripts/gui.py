"""
Модуль создания главного окна приложения.

Автор: Бободжанова Мехрона Рахимовна
"""

import tkinter as tk
from tkinter import ttk


def create_main_window(config):
    """
    Создаёт главное окно приложения с параметрами из .ini.

    Параметры
    ----------
    config : ConfigParser
        Настройки интерфейса.

    Возвращает
    ----------
    tk.Tk
        Корневое окно.
    """
    root = tk.Tk()
    root.title('Анализ датасета Netflix')
    root.geometry(
        f"{config.get('UI', 'window_width')}x{config.get('UI', 'window_height')}"
    )
    root.configure(bg=config.get('UI', 'bg_color'))

    style = ttk.Style()
    style.configure(
        'TLabel',
        font=(config.get('UI', 'font_family'), int(config.get('UI', 'font_size'))),
    )
    style.configure(
        'TButton',
        font=(config.get('UI', 'font_family'), int(config.get('UI', 'font_size'))),
    )
    return root


def create_notebook(root):
    """
    Создаёт вкладки главного окна.

    Параметры
    ----------
    root : tk.Tk
        Корневое окно.

    Возвращает
    ----------
    ttk.Notebook
        Виджет вкладок.
    """
    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both', padx=8, pady=8)
    return notebook
