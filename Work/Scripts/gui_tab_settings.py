"""
Вкладка настроек интерфейса.

Автор: Бободжанова Мехрона Рахимовна
"""

from tkinter import ttk

from Scripts import gui_widgets as widgets


def setup_settings_tab(notebook, config):
    """Создаёт вкладку «Настройки»."""
    tab = ttk.Frame(notebook, padding=10)
    notebook.add(tab, text='  Настройки  ')

    frame = ttk.LabelFrame(tab, text='Параметры интерфейса', padding=10)
    frame.pack(fill='x')

    width_entry = widgets.add_labeled_entry(
        frame, 'Ширина окна:', config.get('UI', 'window_width')
    )
    height_entry = widgets.add_labeled_entry(
        frame, 'Высота окна:', config.get('UI', 'window_height')
    )
    bg_entry = widgets.add_labeled_entry(frame, 'Цвет фона:', config.get('UI', 'bg_color'))
    font_entry = widgets.add_labeled_entry(frame, 'Шрифт:', config.get('UI', 'font_family'))
    size_entry = widgets.add_labeled_entry(
        frame, 'Размер шрифта:', config.get('UI', 'font_size')
    )
    accent_entry = widgets.add_labeled_entry(
        frame, 'Акцентный цвет:', config.get('UI', 'accent_color')
    )

    btn_save = ttk.Button(frame, text='Сохранить настройки')
    btn_save.pack(anchor='w', pady=10)

    ttk.Label(
        tab,
        text='Настройки сохраняются в settings.ini и применяются при перезапуске.',
    ).pack(anchor='w', pady=10)

    return {
        'width_entry': width_entry,
        'height_entry': height_entry,
        'bg_entry': bg_entry,
        'font_entry': font_entry,
        'size_entry': size_entry,
        'accent_entry': accent_entry,
        'btn_save': btn_save,
    }
