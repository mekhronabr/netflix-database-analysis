"""
Вкладка специализированной аналитики Netflix.

Автор: Бободжанова Мехрона Рахимовна
"""

from tkinter import ttk

from Scripts import gui_charts, gui_widgets as widgets


def setup_analysis_tab(notebook, titles):
    """Создаёт вкладку «Аналитика Netflix»."""
    tab = ttk.Frame(notebook, padding=10)
    notebook.add(tab, text='  Аналитика Netflix  ')

    left = ttk.Frame(tab)
    left.pack(side='left', fill='both', expand=True, padx=(0, 8))
    right = ttk.Frame(tab)
    right.pack(side='right', fill='both', expand=True)

    ttk.Label(left, text='Анализ по странам и динамике').pack(anchor='w')
    btn_countries = ttk.Button(left, text='Распределение по странам')
    entry_countries = widgets.add_labeled_entry(left, 'Количество стран:', '15')
    btn_countries.pack(anchor='w', pady=3)
    btn_dynamics = ttk.Button(left, text='Динамика выпуска')
    entry_dynamics_year_from = widgets.add_labeled_entry(left, 'Год от:', '2018')
    entry_dynamics_year_to = widgets.add_labeled_entry(left, 'Год до:', '2021')
    btn_dynamics.pack(anchor='w', pady=3)

    ttk.Separator(left, orient='horizontal').pack(fill='x', pady=8)
    ttk.Label(left, text='Поиск похожего контента').pack(anchor='w')
    title_combo = widgets.add_labeled_combobox(
        left, 'Название:', titles[:200], titles[0] if titles else '',
    )
    entry_similar = widgets.add_labeled_entry(left, 'Число похожих:', '10')
    btn_similar = ttk.Button(left, text='Найти похожие')
    btn_similar.pack(anchor='w', pady=3)

    ttk.Separator(left, orient='horizontal').pack(fill='x', pady=8)
    ttk.Label(left, text='Сеть актёров и режиссёров').pack(anchor='w')
    entry_network = widgets.add_labeled_entry(left, 'Число связей:', '20')
    btn_network = ttk.Button(left, text='Построить граф')
    btn_network.pack(anchor='w', pady=3)

    btn_export_table = ttk.Button(left, text='Экспорт таблицы')
    btn_export_table.pack(anchor='w', pady=8)
    btn_export_chart = ttk.Button(left, text='Экспорт графика')
    btn_export_chart.pack(anchor='w')

    analysis_tree = widgets.create_scrollable_tree(right, height=10)
    chart_frame, canvas_holder = gui_charts.create_chart_frame(right)

    return {
        'btn_countries': btn_countries,
        'entry_countries': entry_countries,
        'btn_dynamics': btn_dynamics,
        'entry_dynamics_year_from': entry_dynamics_year_from,
        'entry_dynamics_year_to': entry_dynamics_year_to,
        'title_combo': title_combo,
        'entry_similar': entry_similar,
        'btn_similar': btn_similar,
        'entry_network': entry_network,
        'btn_network': btn_network,
        'btn_export_table': btn_export_table,
        'btn_export_chart': btn_export_chart,
        'analysis_tree': analysis_tree,
        'chart_frame': chart_frame,
        'canvas_holder': canvas_holder,
        'current_figure': {'fig': None},
        'current_table': {'df': None},
    }
