"""
Виджеты Treeview: таблицы и редактирование ячеек.

Автор: Бободжанова Мехрона Рахимовна
"""

import tkinter as tk
from tkinter import ttk


def update_treeview(tree, dataframe, max_rows=500, sort_by=None, select_value=None):
    """Заполняет Treeview данными из DataFrame."""
    close_tree_edit_entry(tree)
    tree.delete(*tree.get_children())
    columns = list(dataframe.columns)
    tree['columns'] = columns
    tree['show'] = 'headings'

    for column in columns:
        title = str(column).replace('_', ' ').capitalize()
        tree.heading(column, text=title)
        tree.column(column, width=120, anchor='w')

    display_df = dataframe
    if sort_by and sort_by in display_df.columns:
        display_df = display_df.sort_values(sort_by, ascending=False)
    if max_rows is not None:
        display_df = display_df.head(max_rows)

    selected_item = None
    first_column = columns[0] if columns else None
    for _, row in display_df.iterrows():
        values = [str(value) if value == value else '' for value in row]
        item_id = tree.insert('', 'end', values=values)
        if (
            select_value is not None
            and first_column
            and str(row[first_column]) == str(select_value)
        ):
            selected_item = item_id

    if selected_item:
        tree.selection_set(selected_item)
        tree.focus(selected_item)
        tree.see(selected_item)


def create_scrollable_tree(parent, height=12):
    """Создаёт Treeview со скроллбаром."""
    frame = ttk.Frame(parent)
    frame.pack(fill='both', expand=True)
    scrollbar = ttk.Scrollbar(frame, orient='vertical')
    tree = ttk.Treeview(frame, height=height, yscrollcommand=scrollbar.set)
    scrollbar.config(command=tree.yview)
    tree.pack(side='left', fill='both', expand=True)
    scrollbar.pack(side='right', fill='y')
    return tree


def close_tree_edit_entry(tree):
    """Закрывает активное поле редактирования ячейки."""
    entry = getattr(tree, '_edit_entry', None)
    if entry is not None and entry.winfo_exists():
        entry.destroy()
    tree._edit_entry = None
    tree._edit_row_id = None


def make_treeview_editable(tree, on_cell_save=None):
    """Включает редактирование ячеек Treeview по двойному клику."""
    tree._on_cell_save = on_cell_save
    tree.bind('<Double-1>', lambda event: _on_double_click(event, tree))


def _on_double_click(event, tree):
    """Открывает поле ввода поверх выбранной ячейки."""
    column = tree.identify_column(event.x)
    row_id = tree.identify_row(event.y)
    if not row_id or not column:
        return

    bbox = tree.bbox(row_id, column)
    if not bbox:
        return

    close_tree_edit_entry(tree)
    x_pos, y_pos, width, height = bbox
    entry = tk.Entry(tree)
    entry.place(x=x_pos, y=y_pos, width=width, height=height)

    col_index = int(column[1:]) - 1
    try:
        current_val = tree.item(row_id, 'values')[col_index]
    except tk.TclError:
        return

    entry.insert(0, current_val)
    tree._edit_entry = entry
    tree._edit_row_id = row_id

    def save_edit(_event=None):
        if not entry.winfo_exists():
            return
        new_val = entry.get()
        entry.destroy()
        tree._edit_entry = None
        tree._edit_row_id = None
        if row_id not in tree.get_children():
            return
        try:
            values = list(tree.item(row_id, 'values'))
            if callable(getattr(tree, '_on_cell_save', None)):
                tree._on_cell_save(col_index, values, new_val)
            else:
                values[col_index] = new_val
                tree.item(row_id, values=values)
        except tk.TclError:
            return

    entry.bind('<Return>', save_edit)
    entry.bind('<Escape>', lambda _e: close_tree_edit_entry(tree))
    entry.focus_set()
