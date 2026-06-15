"""
Обработчики вкладки аналитики Netflix.

Автор: Бободжанова Мехрона Рахимовна
"""

from datetime import datetime
from tkinter import messagebox

from Library import analysis, analysis_advanced, messages, reports
from Scripts import gui_widgets as widgets


def _parse_positive_int(raw_value, field_name):
    """Проверяет и преобразует ввод в целое положительное число."""
    text = raw_value.strip()
    if not text.isdigit() or int(text) <= 0:
        raise ValueError(messages.positive_integer(field_name, text))
    return int(text)


def _parse_year(raw_value, field_name):
    """Проверяет и преобразует ввод в год."""
    text = raw_value.strip()
    if not text.isdigit():
        raise ValueError(messages.year_integer(field_name, text))
    return int(text)


def on_show_countries(ctx):
    """Показывает распределение контента по странам."""
    analysis_tab = ctx['analysis_tab']
    try:
        top_n = _parse_positive_int(
            analysis_tab['entry_countries'].get(),
            'Количество стран',
        )
        table = analysis.get_country_distribution(
            df=ctx['current_data'],
            top_n=top_n,
        )
        analysis_tab['current_table']['df'] = table
        widgets.update_treeview(analysis_tab['analysis_tree'], table)

        figure = analysis.plot_country_distribution(counts=table)
        analysis_tab['current_figure']['fig'] = figure
        widgets.show_figure(
            analysis_tab['chart_frame'],
            analysis_tab['canvas_holder'],
            figure,
        )
    except ValueError as error:
        messagebox.showerror('Ошибка аналитики', str(error))


def on_show_dynamics(ctx):
    """Показывает динамику выпуска фильмов и сериалов."""
    analysis_tab = ctx['analysis_tab']
    try:
        year_from = _parse_year(
            analysis_tab['entry_dynamics_year_from'].get(),
            'Год от',
        )
        year_to = _parse_year(
            analysis_tab['entry_dynamics_year_to'].get(),
            'Год до',
        )
        if year_from > year_to:
            raise ValueError(messages.year_range_invalid(year_from, year_to))

        table = analysis.get_release_dynamics(
            df=ctx['current_data'],
            year_to=year_to,
            year_from=year_from,
        )
        if table.empty:
            raise ValueError(messages.no_release_data(year_from, year_to))

        analysis_tab['current_table']['df'] = table
        widgets.update_treeview(analysis_tab['analysis_tree'], table)

        figure = analysis.plot_release_dynamics(dynamics=table)
        analysis_tab['current_figure']['fig'] = figure
        widgets.show_figure(
            analysis_tab['chart_frame'],
            analysis_tab['canvas_holder'],
            figure,
        )
    except ValueError as error:
        messagebox.showerror('Ошибка аналитики', str(error))


def on_find_similar(ctx):
    """Ищет контент, похожий по описанию."""
    analysis_tab = ctx['analysis_tab']
    title = analysis_tab['title_combo'].get().strip()
    if not title:
        messagebox.showwarning('Поиск', 'Выберите название контента.')
        return

    try:
        top_n = _parse_positive_int(
            analysis_tab['entry_similar'].get(),
            'Количество похожих',
        )
        table = analysis_advanced.find_similar_content(title, top_n=top_n)
        analysis_tab['current_table']['df'] = table

        if analysis_tab['current_figure']['fig']:
            analysis_tab['canvas_holder']['widget'].destroy()
            analysis_tab['canvas_holder']['widget'] = None
            analysis_tab['canvas_holder']['canvas'] = None
            analysis_tab['current_figure']['fig'] = None

        widgets.update_treeview(analysis_tab['analysis_tree'], table)
    except LookupError as error:
        messagebox.showerror('Ошибка поиска', str(error))


def on_show_network(ctx):
    """Строит граф связей актёров и режиссёров."""
    analysis_tab = ctx['analysis_tab']

    try:
        text = analysis_tab['entry_network'].get().strip()
        max_edges = 20 if not text else _parse_positive_int(text, 'Число связей')

        graph, edges = analysis_advanced.build_actor_director_graph(
            max_edges=max_edges,
        )
        analysis_tab['current_table']['df'] = edges
        widgets.update_treeview(analysis_tab['analysis_tree'], edges)

        figure = analysis_advanced.plot_actor_director_network(
            graph=graph,
            max_edges=max_edges,
        )
        analysis_tab['current_figure']['fig'] = figure
        widgets.show_figure(
            analysis_tab['chart_frame'],
            analysis_tab['canvas_holder'],
            figure,
        )
    except ValueError as error:
        messagebox.showerror('Ошибка графа', str(error))


def on_export_analysis_table(ctx):
    """Экспортирует таблицу аналитики в CSV."""
    dataframe = ctx['analysis_tab']['current_table']['df']
    if dataframe is None:
        messagebox.showwarning('Экспорт', 'Нет данных для экспорта.')
        return

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_path = ctx['output_dir'] / f'analysis_{timestamp}.csv'
    try:
        reports.save_report_to_csv(dataframe, file_path)
        messagebox.showinfo('Экспорт', f'Таблица сохранена:\n{file_path}')
    except IOError as error:
        messagebox.showerror('Ошибка экспорта', str(error))


def on_export_analysis_chart(ctx):
    """Экспортирует график аналитики в PNG."""
    figure = ctx['analysis_tab']['current_figure']['fig']
    if figure is None:
        messagebox.showwarning('Экспорт', 'Нет графика для экспорта.')
        return

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_path = ctx['graphics_dir'] / f'analysis_{timestamp}.png'
    try:
        reports.save_chart_to_file(figure, file_path)
        messagebox.showinfo('Экспорт', f'График сохранён:\n{file_path}')
    except IOError as error:
        messagebox.showerror('Ошибка экспорта', str(error))
