"""
Вспомогательные виджеты графического интерфейса.

Автор: Бободжанова Мехрона Рахимовна
"""

import tkinter as tk
from tkinter import ttk

from Scripts.gui_charts import create_chart_frame, show_figure
from Scripts.gui_tree import (
    close_tree_edit_entry,
    create_scrollable_tree,
    make_treeview_editable,
    update_treeview,
)

from Library import reports

__all__ = [
    'add_labeled_column_combobox',
    'add_labeled_column_combobox_group',
    'add_labeled_column_listbox_group',
    'add_labeled_combobox',
    'add_labeled_combobox_group',
    'add_labeled_entry',
    'add_labeled_listbox_group',
    'close_tree_edit_entry',
    'create_chart_frame',
    'create_scrollable_tree',
    'get_combobox_column',
    'get_listbox_column_selection',
    'get_listbox_selection',
    'make_treeview_editable',
    'show_figure',
    'update_treeview',
]


def _column_labels(columns):
    """Возвращает подписи столбцов для отображения в интерфейсе."""
    return [reports.get_column_label(column) for column in columns]


def _column_label_map(columns):
    """Сопоставляет подписи столбцов с их техническими именами."""
    return {
        reports.get_column_label(column): column
        for column in columns
    }


def add_labeled_column_combobox(parent, label_text, columns, default_col=None):
    """Добавляет combobox с понятными именами столбцов."""
    _, _, combo = add_labeled_column_combobox_group(
        parent, label_text, columns, default_col
    )
    return combo


def add_labeled_column_combobox_group(parent, label_text, columns, default_col=None):
    """Добавляет combobox с понятными именами столбцов в отдельном фрейме."""
    labels = _column_labels(columns)
    default = reports.get_column_label(default_col) if default_col else None
    frame, label, combo = add_labeled_combobox_group(parent, label_text, labels, default)
    combo.column_map = _column_label_map(columns)
    return frame, label, combo


def add_labeled_column_listbox_group(
    parent, label_text, columns, default=None, height=6,
):
    """Добавляет listbox с понятными именами столбцов."""
    labels = _column_labels(columns)
    default_labels = [
        reports.get_column_label(column)
        for column in (default or [])
    ]
    frame, label, listbox = add_labeled_listbox_group(
        parent, label_text, labels, default_labels, height
    )
    listbox.column_map = _column_label_map(columns)
    return frame, label, listbox


def get_combobox_column(combo):
    """Возвращает техническое имя столбца, выбранного в combobox."""
    return combo.column_map[combo.get()]


def get_listbox_column_selection(listbox):
    """Возвращает технические имена столбцов, выбранных в listbox."""
    return [
        listbox.column_map[listbox.get(index)]
        for index in listbox.curselection()
    ]


def add_labeled_combobox(parent, label_text, values, default=None):
    """Добавляет подпись и выпадающий список."""
    _, _, combo = add_labeled_combobox_group(parent, label_text, values, default)
    return combo


def add_labeled_combobox_group(parent, label_text, values, default=None):
    """Добавляет подпись и combobox в отдельном фрейме."""
    frame = ttk.Frame(parent)
    frame.pack(fill='x')
    label = ttk.Label(frame, text=label_text)
    label.pack(anchor='w', pady=(5, 0))
    combo = ttk.Combobox(frame, values=values, state='readonly')
    if default:
        combo.set(default)
    elif values:
        combo.set(values[0])
    combo.pack(fill='x', pady=2)
    return frame, label, combo


def add_labeled_listbox_group(parent, label_text, values, default=None, height=6):
    """Добавляет подпись и список с множественным выбором."""
    frame = ttk.Frame(parent)
    frame.pack(fill='x')
    label = ttk.Label(frame, text=label_text)
    label.pack(anchor='w', pady=(5, 0))
    list_frame = ttk.Frame(frame)
    list_frame.pack(fill='x', pady=2)
    scrollbar = ttk.Scrollbar(list_frame, orient='vertical')
    listbox = tk.Listbox(
        list_frame, selectmode='extended', height=height, yscrollcommand=scrollbar.set,
    )
    scrollbar.config(command=listbox.yview)
    for value in values:
        listbox.insert('end', value)
    if default:
        for item in default:
            if item in values:
                listbox.selection_set(values.index(item))
    listbox.pack(side='left', fill='x', expand=True)
    scrollbar.pack(side='right', fill='y')
    return frame, label, listbox


def get_listbox_selection(listbox):
    """Возвращает список выбранных значений из Listbox."""
    return [listbox.get(index) for index in listbox.curselection()]


def add_labeled_entry(parent, label_text, default=''):
    """Добавляет подпись и поле ввода."""
    ttk.Label(parent, text=label_text).pack(anchor='w', pady=(5, 0))
    entry = ttk.Entry(parent)
    entry.insert(0, default)
    entry.pack(fill='x', pady=2)
    return entry
