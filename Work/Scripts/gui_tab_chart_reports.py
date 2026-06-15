"""
Вкладка графических отчётов.

Автор: Бободжанова Мехрона Рахимовна
"""

from tkinter import ttk

from Scripts import gui, gui_charts, gui_widgets as widgets


def setup_chart_reports_tab(notebook, qual_columns, quant_columns):
    """Создаёт вкладку «Графические отчёты»."""
    tab = ttk.Frame(notebook, padding=10)
    notebook.add(tab, text='  Графические отчёты  ')

    controls = ttk.Frame(tab, padding=10)
    reports_tab = gui.create_notebook(controls)

    clustered_bar_tab = setup_clastered_bar_tab(reports_tab, qual_columns)
    categorized_hist_tab = setup_categorized_hist_tab(
        reports_tab, qual_columns, quant_columns
    )
    categorized_boxplot_tab = setup_categorized_boxplot_tab(
        reports_tab, qual_columns, quant_columns
    )
    categorized_scatter_tab = setup_categorized_scatter_tab(
        reports_tab, qual_columns, quant_columns
    )
    controls.pack()

    chart_types = [
        'Кластеризованная гистограмма',
        'Категоризированная гистограмма',
        'Диаграмма Бокса-Вискера',
        'Диаграмма рассеивания',
    ]
    chart_kind = widgets.add_labeled_combobox(
        tab,
        label_text='Выберите тип графика',
        values=chart_types,
        default=chart_types[0],
    )

    btn_build = ttk.Button(tab, text='Построить отчёт')
    btn_build.pack(anchor='w', pady=5)
    btn_export = ttk.Button(tab, text='Сохранить в файл')
    btn_export.pack(anchor='w')

    chart_frame, canvas_holder = gui_charts.create_chart_frame(tab)

    return {
        'clustered_bar_tab': clustered_bar_tab,
        'categorized_hist_tab': categorized_hist_tab,
        'categorized_boxplot_tab': categorized_boxplot_tab,
        'categorized_scatter_tab': categorized_scatter_tab,
        'chart_frame': chart_frame,
        'chart_kind': chart_kind,
        'canvas_holder': canvas_holder,
        'current_figure': {'fig': None},
        'btn_build': btn_build,
        'btn_export': btn_export,
    }


def setup_clastered_bar_tab(notebook, qual_columns):
    """Параметры кластеризованной гистограммы."""
    tab = ttk.Frame(notebook)
    notebook.add(tab, text='  Кластеризованная гистограмма  ', padding=10)
    qual1 = widgets.add_labeled_column_combobox(
        tab, 'Качественный 1:', qual_columns, 'show_type_name'
    )
    qual2 = widgets.add_labeled_column_combobox(
        tab, 'Качественный 2:', qual_columns, 'rating'
    )
    top_n = widgets.add_labeled_entry(tab, 'Топ наиболее частых связей:', '10')
    return {'qual1': qual1, 'qual2': qual2, 'top_n': top_n}


def setup_categorized_hist_tab(notebook, qual_columns, quant_columns):
    """Параметры категоризированной гистограммы."""
    tab = ttk.Frame(notebook)
    notebook.add(tab, text='  Категоризированная гистограмма  ', padding=10)
    quant = widgets.add_labeled_column_combobox(
        tab, 'Количественный:', quant_columns, 'release_year'
    )
    qual = widgets.add_labeled_column_combobox(
        tab, 'Качественный:', qual_columns, 'show_type_name'
    )
    bins = widgets.add_labeled_entry(tab, 'Число интервалов:', '10')
    top_n = widgets.add_labeled_entry(tab, 'Топ категорий:', '10')
    return {'qual': qual, 'quant': quant, 'bins': bins, 'top_n': top_n}


def setup_categorized_boxplot_tab(notebook, qual_columns, quant_columns):
    """Параметры диаграммы Бокса-Вискера."""
    tab = ttk.Frame(notebook)
    notebook.add(tab, text='  Диаграмма Бокса-Вискера  ', padding=10)
    quant = widgets.add_labeled_column_combobox(
        tab, 'Количественный:', quant_columns, 'release_year'
    )
    qual = widgets.add_labeled_column_combobox(
        tab, 'Качественный:', qual_columns, 'show_type_name'
    )
    top_n = widgets.add_labeled_entry(tab, 'Топ категорий:', '10')
    return {'qual': qual, 'quant': quant, 'top_n': top_n}


def setup_categorized_scatter_tab(notebook, qual_columns, quant_columns):
    """Параметры диаграммы рассеивания."""
    tab = ttk.Frame(notebook)
    notebook.add(tab, text='  Диаграмма рассеивания  ', padding=10)
    quant1 = widgets.add_labeled_column_combobox(
        tab, 'Количественный 1:', quant_columns, 'release_year'
    )
    quant2 = widgets.add_labeled_column_combobox(
        tab, 'Количественный 2:', quant_columns, 'duration_minutes'
    )
    qual = widgets.add_labeled_column_combobox(
        tab, 'Качественный:', qual_columns, 'show_type_name'
    )
    top_n = widgets.add_labeled_entry(tab, 'Топ категорий:', '10')
    max_points = widgets.add_labeled_entry(tab, 'Макс. точек на группу:', '500')
    return {
        'quant1': quant1,
        'quant2': quant2,
        'qual': qual,
        'top_n': top_n,
        'max_points': max_points,
    }
