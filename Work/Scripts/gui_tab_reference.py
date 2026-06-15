"""
Вкладка управления справочниками.

Автор: Бободжанова Мехрона Рахимовна
"""

from tkinter import ttk

from Scripts import gui_widgets as widgets


def setup_reference_tab(notebook, table_names):
    """Создаёт вкладку «Справочники»."""
    tab = ttk.Frame(notebook, padding=10)
    notebook.add(tab, text='  Справочники  ')

    table_combo = widgets.add_labeled_combobox(tab, 'Справочник:', table_names, 'shows')

    btn_row = ttk.Frame(tab)
    btn_row.pack(fill='x', pady=5)
    btn_refresh = ttk.Button(btn_row, text='Обновить')
    btn_refresh.pack(side='left', padx=(0, 5))
    btn_save = ttk.Button(btn_row, text='Сохранить в файл')
    btn_save.pack(side='left')

    ref_tree = widgets.create_scrollable_tree(tab, height=12)

    edit_frame = ttk.LabelFrame(tab, text='Добавление записи', padding=8)
    edit_frame.pack(fill='x', pady=8)

    edit_tree = ttk.Treeview(edit_frame, height=2)
    edit_tree.pack(fill='x', pady=5)

    btn_form = ttk.Button(edit_frame, text='Создать форму ввода')
    btn_form.pack(side='left', padx=2)
    btn_add = ttk.Button(edit_frame, text='Добавить запись')
    btn_add.pack(side='left', padx=2)
    btn_delete = ttk.Button(edit_frame, text='Удалить выбранную')
    btn_delete.pack(side='left', padx=2)

    max_id_label = ttk.Label(edit_frame, text='Макс. ID: —')
    max_id_label.pack(anchor='w', pady=5)
    widgets.make_treeview_editable(edit_tree)

    return {
        'table_combo': table_combo,
        'btn_refresh': btn_refresh,
        'btn_save': btn_save,
        'ref_tree': ref_tree,
        'edit_tree': edit_tree,
        'btn_form': btn_form,
        'btn_add': btn_add,
        'btn_delete': btn_delete,
        'max_id_label': max_id_label,
    }
