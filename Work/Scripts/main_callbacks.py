"""
Обработчики данных и справочников графического интерфейса.

Автор: Бободжанова Мехрона Рахимовна
"""

from tkinter import messagebox

import pandas as pd
import tkinter as tk

from Library import analysis, db_loader
from Scripts import gui_widgets as widgets
from Scripts.gui_tab_text_reports import configure_text_report_fields
from Scripts.main_callbacks_analysis import (
    on_export_analysis_chart,
    on_export_analysis_table,
    on_find_similar,
    on_show_countries,
    on_show_dynamics,
    on_show_network,
)
from Scripts.main_callbacks_reports import (
    on_build_chart_report,
    on_build_text_report,
    on_export_chart_report,
    on_export_text_report,
    on_save_settings,
)


def bind_callbacks(ctx):
    """Привязывает обработчики к виджетам интерфейса."""
    data_tab = ctx['data_tab']
    ref_tab = ctx['ref_tab']
    text_tab = ctx['text_tab']
    chart_tab = ctx['chart_tab']
    analysis_tab = ctx['analysis_tab']
    settings_tab = ctx['settings_tab']

    data_tab['btn_apply'].config(command=lambda: on_apply_filter(ctx))
    data_tab['btn_reset'].config(command=lambda: on_reset_filter(ctx))

    ref_tab['btn_refresh'].config(command=lambda: on_reference_refresh(ctx))
    ref_tab['btn_save'].config(command=on_reference_save)
    ref_tab['btn_form'].config(command=lambda: on_generate_form(ctx))
    ref_tab['btn_add'].config(command=lambda: on_add_reference_row(ctx))
    ref_tab['btn_delete'].config(command=lambda: on_delete_reference_row(ctx))
    widgets.make_treeview_editable(
        ref_tab['ref_tree'],
        on_cell_save=lambda col_index, values, new_val: on_reference_cell_edit(
            ctx, col_index, values, new_val
        ),
    )
    ref_tab['table_combo'].bind(
        '<<ComboboxSelected>>',
        lambda _e: on_reference_refresh(ctx),
    )

    text_tab['report_type'].bind(
        '<<ComboboxSelected>>',
        lambda _e: configure_text_report_fields(text_tab),
    )
    text_tab['btn_build'].config(command=lambda: on_build_text_report(ctx))
    text_tab['btn_export'].config(command=lambda: on_export_text_report(ctx))

    chart_tab['btn_build'].config(command=lambda: on_build_chart_report(ctx))
    chart_tab['btn_export'].config(command=lambda: on_export_chart_report(ctx))

    analysis_tab['btn_countries'].config(command=lambda: on_show_countries(ctx))
    analysis_tab['btn_dynamics'].config(command=lambda: on_show_dynamics(ctx))
    analysis_tab['btn_similar'].config(command=lambda: on_find_similar(ctx))
    analysis_tab['btn_network'].config(command=lambda: on_show_network(ctx))
    analysis_tab['btn_export_table'].config(
        command=lambda: on_export_analysis_table(ctx)
    )
    analysis_tab['btn_export_chart'].config(
        command=lambda: on_export_analysis_chart(ctx)
    )

    settings_tab['btn_save'].config(command=lambda: on_save_settings(ctx))


def refresh_data_view(ctx, dataframe=None):
    """Обновляет таблицу и статистику на вкладке данных."""
    if dataframe is not None:
        ctx['current_data'] = dataframe
    else:
        ctx['current_data'] = analysis.get_main_dataframe()

    data_tab = ctx['data_tab']
    widgets.update_treeview(data_tab['data_tree'], ctx['current_data'])
    widgets.update_treeview(
        data_tab['stats_tree'],
        analysis.get_summary_statistics(ctx['current_data']),
    )


def on_apply_filter(ctx):
    """Применяет фильтры к датасету."""
    data_tab = ctx['data_tab']
    try:
        filtered = analysis.filter_content(
            show_type=data_tab['type_combo'].get(),
            country=data_tab['country_entry'].get(),
            year_from=data_tab['year_from'].get(),
            year_to=data_tab['year_to'].get(),
        )
        refresh_data_view(ctx, filtered)
    except (ValueError, TypeError) as error:
        messagebox.showerror('Ошибка фильтра', str(error))


def on_reset_filter(ctx):
    """Сбрасывает фильтры."""
    data_tab = ctx['data_tab']
    data_tab['type_combo'].set('Все')
    data_tab['country_entry'].delete(0, tk.END)
    data_tab['country_entry'].insert(0, 'United States')
    data_tab['year_from'].delete(0, tk.END)
    data_tab['year_from'].insert(0, '2010')
    data_tab['year_to'].delete(0, tk.END)
    data_tab['year_to'].insert(0, '2021')
    refresh_data_view(ctx)


def on_reference_refresh(ctx, select_value=None):
    """Обновляет таблицу справочника из памяти (после сохранения на диск)."""
    ref_tab = ctx['ref_tab']
    table_name = ref_tab['table_combo'].get()
    if table_name not in db_loader.database:
        return

    dataframe = db_loader.database[table_name]
    id_column = dataframe.columns[0]
    widgets.update_treeview(
        ref_tab['ref_tree'],
        dataframe,
        max_rows=500,
        sort_by=id_column,
        select_value=select_value,
    )


def on_reference_save():
    """Сохраняет справочники в двоичные файлы."""
    try:
        db_loader.save_data()
        messagebox.showinfo('Сохранение', 'Справочники сохранены в двоичном формате.')
    except (KeyError, IOError) as error:
        messagebox.showerror('Ошибка сохранения', str(error))


def on_generate_form(ctx):
    """Создаёт форму ввода для справочника."""
    ref_tab = ctx['ref_tab']
    table_name = ref_tab['table_combo'].get()
    dataframe = db_loader.database[table_name]

    widgets.close_tree_edit_entry(ref_tab['edit_tree'])
    ref_tab['edit_tree'].delete(*ref_tab['edit_tree'].get_children())
    ref_tab['edit_tree']['columns'] = list(dataframe.columns)
    ref_tab['edit_tree']['show'] = 'headings'

    for column in dataframe.columns:
        ref_tab['edit_tree'].heading(column, text=column)
        ref_tab['edit_tree'].column(column, width=90)

    id_columns = [col for col in dataframe.columns if col.endswith('_id')]
    if id_columns:
        stats = [f'{col}: {int(dataframe[col].max())}' for col in id_columns]
        ref_tab['max_id_label'].config(text=f'Макс. ID: {" | ".join(stats)}')
    else:
        ref_tab['max_id_label'].config(text='ID-колонок не найдено')

    ref_tab['edit_tree'].insert('', 'end', values=['' for _ in dataframe.columns])


def on_add_reference_row(ctx):
    """Добавляет запись в справочник."""
    ref_tab = ctx['ref_tab']
    table_name = ref_tab['table_combo'].get()
    children = ref_tab['edit_tree'].get_children()
    if not children:
        messagebox.showwarning('Справочники', 'Сначала создайте форму ввода.')
        return

    values = ref_tab['edit_tree'].item(children[0])['values']
    columns = list(db_loader.database[table_name].columns)

    try:
        dataframe = db_loader.database[table_name]
        row = {}

        for column, value in zip(columns, values):
            text = str(value).strip()
            if column.endswith('_id'):
                row[column] = int(text) if text else int(dataframe[column].max()) + 1
            elif column in ('release_year', 'duration_minutes', 'duration_seasons'):
                row[column] = int(text) if text else None
            else:
                row[column] = value

        if db_loader.row_exists(table_name, row):
            messagebox.showwarning(
                'Дубликат',
                'Такая запись уже есть в справочнике. Добавление отменено.',
            )
            return

        new_id = row[columns[0]]
        new_row = pd.DataFrame([row])
        db_loader.database[table_name] = pd.concat(
            [dataframe, new_row],
            ignore_index=True,
        )
        db_loader.save_table_data(table_name)
        on_reference_refresh(ctx, select_value=new_id)
        on_generate_form(ctx)
        messagebox.showinfo('Успех', 'Запись добавлена.')
    except (ValueError, KeyError, TypeError) as error:
        messagebox.showerror('Ошибка добавления', str(error))


def _cast_tree_value(value, column_name, dataframe):
    """Приводит значение из Treeview к типу столбца таблицы."""
    if value == '' or value is None:
        return None

    dtype = dataframe[column_name].dtype
    if column_name.endswith('_id') or column_name in (
        'release_year', 'duration_minutes', 'duration_seasons',
    ):
        return int(value)
    if pd.api.types.is_integer_dtype(dtype):
        return int(value)
    if pd.api.types.is_float_dtype(dtype):
        return float(value)
    return value


def on_reference_cell_edit(ctx, col_index, values, new_value):
    """Сохраняет изменение ячейки справочника через edit_table_column."""
    ref_tab = ctx['ref_tab']
    table_name = ref_tab['table_combo'].get()
    dataframe = db_loader.database[table_name]
    columns = list(dataframe.columns)
    id_column = columns[0]
    target_column = columns[col_index]

    try:
        id_value = _cast_tree_value(values[0], id_column, dataframe)
        parsed_value = _cast_tree_value(new_value, target_column, dataframe)
        old_display = str(values[col_index]).strip()
        new_display = str(new_value).strip()
        if old_display == new_display:
            return

        db_loader.edit_table_column(
            table_name,
            id_column,
            id_value,
            target_column,
            parsed_value,
        )
        select_value = parsed_value if target_column == id_column else id_value
        on_reference_refresh(ctx, select_value=select_value)
    except (LookupError, ValueError, KeyError, TypeError) as error:
        messagebox.showerror('Ошибка редактирования', str(error))


def on_delete_reference_row(ctx):
    """Удаляет выбранную запись справочника."""
    ref_tab = ctx['ref_tab']
    table_name = ref_tab['table_combo'].get()
    selected = ref_tab['ref_tree'].selection()
    if not selected:
        messagebox.showwarning('Справочники', 'Выберите строку для удаления.')
        return

    if not messagebox.askyesno('Подтверждение', 'Удалить выбранную запись?'):
        return

    values = ref_tab['ref_tree'].item(selected[0])['values']
    dataframe = db_loader.database[table_name]
    columns = list(dataframe.columns)
    id_column = columns[0]

    try:
        id_value = _cast_tree_value(values[0], id_column, dataframe)
        db_loader.delete_rows_by_value(table_name, [id_column], [id_value])
        widgets.close_tree_edit_entry(ref_tab['edit_tree'])
        on_reference_refresh(ctx, select_value=None)
        messagebox.showinfo('Успех', 'Запись удалена.')
    except (LookupError, ValueError, KeyError, TypeError) as error:
        messagebox.showerror('Ошибка', str(error))
