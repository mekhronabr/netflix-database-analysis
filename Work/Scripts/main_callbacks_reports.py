"""
Обработчики отчётов графического интерфейса.

Автор: Бободжанова Мехрона Рахимовна
"""

from tkinter import filedialog, messagebox

from Library import config_loader, messages, reports
from Scripts import gui_widgets as widgets


def _parse_positive_int(raw_value, field_name):
    """Проверяет и преобразует ввод в целое положительное число."""
    text = raw_value.strip()
    if not text.isdigit() or int(text) <= 0:
        raise ValueError(messages.positive_integer(field_name, text))
    return int(text)


def on_build_text_report(ctx):
    """Формирует текстовый отчёт."""
    text_tab = ctx['text_tab']
    report_kind = text_tab['report_type'].get()

    try:
        if report_kind == 'Проекция':
            selected = widgets.get_listbox_column_selection(text_tab['projection_cols'])
            if not selected:
                raise ValueError(messages.no_projection_columns())
            merged = reports.get_dataframe_for_columns(*selected)
            selected = [col for col in selected if col in merged.columns]
            result = merged[selected].drop_duplicates().head(300)
        elif report_kind == 'Статистика':
            column = widgets.get_combobox_column(text_tab['col1'])
            result = reports.get_statistics_report(
                reports.get_dataframe_for_columns(column),
                column,
            )
        else:
            result = reports.get_pivot_table_report(
                widgets.get_combobox_column(text_tab['col1']),
                widgets.get_combobox_column(text_tab['col2']),
                widgets.get_combobox_column(text_tab['col3']),
                text_tab['agg_combo'].get(),
            ).reset_index()

        ctx['current_text_report']['df'] = result
        widgets.update_treeview(
            text_tab['report_tree'],
            reports.format_report_for_display(result),
        )
    except (KeyError, ValueError) as error:
        messagebox.showerror('Ошибка отчёта', str(error))


def on_export_text_report(ctx):
    """Экспортирует текстовый отчёт в CSV."""
    if ctx['current_text_report']['df'] is None:
        messagebox.showwarning('Экспорт', 'Сначала постройте отчёт.')
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension='.csv',
        initialdir=ctx['output_dir'],
        filetypes=[('CSV', '*.csv')],
    )
    if not file_path:
        return

    try:
        reports.save_report_to_csv(ctx['current_text_report']['df'], file_path)
        messagebox.showinfo('Экспорт', f'Отчёт сохранён:\n{file_path}')
    except IOError as error:
        messagebox.showerror('Ошибка экспорта', str(error))


def on_build_chart_report(ctx):
    """Строит графический отчёт."""
    chart_tab = ctx['chart_tab']
    chart_kind = chart_tab['chart_kind'].get()

    try:
        if chart_kind == 'Кластеризованная гистограмма':
            tab = chart_tab['clustered_bar_tab']
            top_n = _parse_positive_int(tab['top_n'].get(), 'Топ связей')
            figure = reports.plot_clustered_bar(
                cat_col1=widgets.get_combobox_column(tab['qual1']),
                cat_col2=widgets.get_combobox_column(tab['qual2']),
                top_n=top_n,
            )
        elif chart_kind == 'Категоризированная гистограмма':
            tab = chart_tab['categorized_hist_tab']
            top_n = _parse_positive_int(tab['top_n'].get(), 'Топ категорий')
            bins = _parse_positive_int(tab['bins'].get(), 'Число интервалов')
            figure = reports.plot_categorized_hist(
                quant_col=widgets.get_combobox_column(tab['quant']),
                cat_col=widgets.get_combobox_column(tab['qual']),
                top_n=top_n,
                bins=bins,
            )
        elif chart_kind == 'Диаграмма Бокса-Вискера':
            tab = chart_tab['categorized_boxplot_tab']
            top_n = _parse_positive_int(tab['top_n'].get(), 'Топ категорий')
            figure = reports.plot_categorized_boxplot(
                quant_col=widgets.get_combobox_column(tab['quant']),
                cat_col=widgets.get_combobox_column(tab['qual']),
                top_n=top_n,
            )
        else:
            tab = chart_tab['categorized_scatter_tab']
            top_n = _parse_positive_int(tab['top_n'].get(), 'Топ категорий')
            max_points = _parse_positive_int(tab['max_points'].get(), 'Макс. точек')
            figure = reports.plot_categorized_scatter(
                x_col=widgets.get_combobox_column(tab['quant1']),
                y_col=widgets.get_combobox_column(tab['quant2']),
                cat_col=widgets.get_combobox_column(tab['qual']),
                top_n=top_n,
                max_points=max_points,
            )

        chart_tab['current_figure']['fig'] = figure
        widgets.show_figure(
            chart_tab['chart_frame'], chart_tab['canvas_holder'], figure
        )
    except (KeyError, ValueError) as error:
        messagebox.showerror('Ошибка графика', str(error))


def on_export_chart_report(ctx):
    """Экспортирует графический отчёт."""
    figure = ctx['chart_tab']['current_figure']['fig']
    if figure is None:
        messagebox.showwarning('Экспорт', 'Сначала постройте график.')
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension='.png',
        initialdir=ctx['graphics_dir'],
        filetypes=[('PNG', '*.png'), ('PDF', '*.pdf')],
    )
    if not file_path:
        return

    try:
        reports.save_chart_to_file(figure, file_path)
        messagebox.showinfo('Экспорт', f'График сохранён:\n{file_path}')
    except IOError as error:
        messagebox.showerror('Ошибка экспорта', str(error))


def on_save_settings(ctx):
    """Сохраняет настройки интерфейса в settings.ini."""
    settings_tab = ctx['settings_tab']
    config = ctx['config']

    config.set('UI', 'window_width', settings_tab['width_entry'].get())
    config.set('UI', 'window_height', settings_tab['height_entry'].get())
    config.set('UI', 'bg_color', settings_tab['bg_entry'].get())
    config.set('UI', 'font_family', settings_tab['font_entry'].get())
    config.set('UI', 'font_size', settings_tab['size_entry'].get())
    config.set('UI', 'accent_color', settings_tab['accent_entry'].get())

    saved_path = config_loader.save_settings(config)
    messagebox.showinfo(
        'Настройки',
        f'Параметры сохранены в:\n{saved_path}\n\n'
        'Перезапустите приложение для применения.',
    )
