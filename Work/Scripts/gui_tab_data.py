"""
Вкладка просмотра и фильтрации датасета.

Автор: Бободжанова Мехрона Рахимовна
"""

from tkinter import ttk

from Scripts import gui_widgets as widgets


def setup_data_tab(notebook):
    """Создаёт вкладку «Данные»."""
    tab = ttk.Frame(notebook, padding=10)
    notebook.add(tab, text='  Данные  ')

    filter_frame = ttk.LabelFrame(tab, text='Фильтры', padding=10)
    filter_frame.pack(fill='x', pady=(0, 8))

    type_combo = widgets.add_labeled_combobox(
        filter_frame, 'Тип контента:', ['Все', 'Movie', 'TV Show'], 'Все'
    )
    country_entry = widgets.add_labeled_entry(
        filter_frame, 'Страна (часть названия):', 'United States'
    )
    year_from = widgets.add_labeled_entry(filter_frame, 'Год от:', '2010')
    year_to = widgets.add_labeled_entry(filter_frame, 'Год до:', '2021')

    btn_row = ttk.Frame(filter_frame)
    btn_row.pack(fill='x', pady=5)
    btn_apply = ttk.Button(btn_row, text='Применить фильтр')
    btn_apply.pack(side='left', padx=(0, 5))
    btn_reset = ttk.Button(btn_row, text='Сбросить')
    btn_reset.pack(side='left')

    ttk.Label(tab, text='Таблица контента:').pack(anchor='w')
    data_tree = widgets.create_scrollable_tree(tab, height=10)

    stats_frame = ttk.LabelFrame(tab, text='Сводная статистика', padding=8)
    stats_frame.pack(fill='both', expand=True, pady=8)
    stats_tree = widgets.create_scrollable_tree(stats_frame, height=6)

    return {
        'type_combo': type_combo,
        'country_entry': country_entry,
        'year_from': year_from,
        'year_to': year_to,
        'btn_apply': btn_apply,
        'btn_reset': btn_reset,
        'data_tree': data_tree,
        'stats_tree': stats_tree,
    }
