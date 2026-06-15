"""
Вкладка текстовых отчётов.

Автор: Бободжанова Мехрона Рахимовна
"""

from tkinter import ttk

from Scripts import gui_widgets as widgets

TEXT_REPORT_LAYOUT = {
    'Проекция': {
        'fields': ('projection_cols',),
        'labels': {'projection_cols': 'Столбцы (Ctrl+клик — несколько):'},
    },
    'Статистика': {
        'fields': ('col1',),
        'labels': {'col1': 'Атрибут:'},
    },
    'Сводная таблица': {
        'fields': ('col1', 'col2', 'col3', 'agg'),
        'labels': {
            'col1': 'Строки:',
            'col2': 'Столбцы:',
            'col3': 'Значения:',
            'agg': 'Агрегация:',
        },
    },
}


def configure_text_report_fields(text_tab, report_kind=None):
    """
    Показывает только те поля параметров, которые нужны выбранному отчёту.

    Параметры
    ----------
    text_tab : dict
        Виджеты вкладки текстовых отчётов.
    report_kind : str, optional
        Тип отчёта. По умолчанию — текущий выбор в combobox.
    """
    if report_kind is None:
        report_kind = text_tab['report_type'].get()

    layout = TEXT_REPORT_LAYOUT.get(report_kind, TEXT_REPORT_LAYOUT['Проекция'])
    visible_fields = layout['fields']
    labels = layout['labels']

    for field_name in ('col1', 'col2', 'col3', 'agg', 'projection_cols'):
        text_tab['field_frames'][field_name].pack_forget()

    for field_name in visible_fields:
        text_tab['field_frames'][field_name].pack(fill='x')
        if field_name in labels:
            text_tab['field_labels'][field_name].config(text=labels[field_name])


def setup_text_reports_tab(notebook, columns):
    """Создаёт вкладку «Текстовые отчёты»."""
    tab = ttk.Frame(notebook, padding=10)
    notebook.add(tab, text='  Текстовые отчёты  ')

    controls = ttk.LabelFrame(tab, text='Параметры отчёта', padding=8)
    controls.pack(fill='x')

    report_type = widgets.add_labeled_combobox(
        controls,
        'Тип отчёта:',
        ['Проекция', 'Статистика', 'Сводная таблица'],
        'Проекция',
    )

    params_frame = ttk.Frame(controls)
    params_frame.pack(fill='x')

    field_frames = {}
    field_labels = {}

    projection_frame, projection_label, projection_cols = (
        widgets.add_labeled_column_listbox_group(
            params_frame,
            'Столбцы (Ctrl+клик — несколько):',
            columns,
            default=['title', 'show_type_name'],
        )
    )
    field_frames['projection_cols'] = projection_frame
    field_labels['projection_cols'] = projection_label

    col1_frame, col1_label, col1 = widgets.add_labeled_column_combobox_group(
        params_frame, 'Столбец 1:', columns, 'title'
    )
    field_frames['col1'] = col1_frame
    field_labels['col1'] = col1_label

    col2_frame, col2_label, col2 = widgets.add_labeled_column_combobox_group(
        params_frame, 'Столбец 2:', columns, 'show_type_name'
    )
    field_frames['col2'] = col2_frame
    field_labels['col2'] = col2_label

    col3_frame, col3_label, col3 = widgets.add_labeled_column_combobox_group(
        params_frame, 'Значения:', columns, 'show_id'
    )
    field_frames['col3'] = col3_frame
    field_labels['col3'] = col3_label

    agg_frame, agg_label, agg_combo = widgets.add_labeled_combobox_group(
        params_frame, 'Агрегация:', ['count', 'mean', 'sum', 'max', 'min'], 'count'
    )
    field_frames['agg'] = agg_frame
    field_labels['agg'] = agg_label

    btn_build = ttk.Button(controls, text='Построить отчёт')
    btn_build.pack(anchor='w', pady=5)
    btn_export = ttk.Button(controls, text='Сохранить в файл')
    btn_export.pack(anchor='w')

    report_tree = widgets.create_scrollable_tree(tab, height=14)

    text_tab = {
        'report_type': report_type,
        'projection_cols': projection_cols,
        'col1': col1,
        'col2': col2,
        'col3': col3,
        'agg_combo': agg_combo,
        'field_frames': field_frames,
        'field_labels': field_labels,
        'btn_build': btn_build,
        'btn_export': btn_export,
        'report_tree': report_tree,
    }

    configure_text_report_fields(text_tab, 'Проекция')
    return text_tab
