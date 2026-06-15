"""
Главный модуль приложения для анализа датасета Netflix.

Запуск: python main.py (из каталога Work/Scripts)
Автор: Бободжанова Мехрона Рахимовна
"""

import sys
from pathlib import Path

import pandas as pd

# Добавляем каталог Work в путь поиска модулей
WORK_DIR = Path(__file__).resolve().parent.parent
if str(WORK_DIR) not in sys.path:
    sys.path.insert(0, str(WORK_DIR))

from Library import analysis, config_loader, db_loader, reports
from Scripts import (
    gui,
    gui_tab_analysis,
    gui_tab_chart_reports,
    gui_tab_data,
    gui_tab_reference,
    gui_tab_settings,
    gui_tab_text_reports,
)
from Scripts.main_callbacks import bind_callbacks, refresh_data_view, on_reference_refresh


def main():
    """Запускает графический интерфейс приложения."""
    config = config_loader.load_settings()
    db_loader.load_data()

    output_dir = config_loader.resolve_path(config.get('Paths', 'output_path'))
    graphics_dir = config_loader.resolve_path(config.get('Paths', 'graphics_path'))
    output_dir.mkdir(parents=True, exist_ok=True)
    graphics_dir.mkdir(parents=True, exist_ok=True)

    root = gui.create_main_window(config)
    notebook = gui.create_notebook(root)

    merged_df = reports.get_dataframe_for_columns(*reports.get_all_report_columns())
    report_columns = reports.get_all_report_columns()
    qual_columns = [
        col for col in report_columns
        if col in merged_df.columns and merged_df[col].dtype == 'object'
    ]
    quant_columns = [
        col for col in report_columns
        if col in merged_df.columns
        and pd.api.types.is_numeric_dtype(merged_df[col])
        and col not in ('show_id',)
        and not col.startswith('Unnamed')
    ]

    ctx = {
        'config': config,
        'output_dir': output_dir,
        'graphics_dir': graphics_dir,
        'current_data': analysis.get_main_dataframe(),
        'current_text_report': {'df': None},
        'data_tab': gui_tab_data.setup_data_tab(notebook),
        'ref_tab': gui_tab_reference.setup_reference_tab(
            notebook, list(db_loader.database.keys())
        ),
        'text_tab': gui_tab_text_reports.setup_text_reports_tab(
            notebook, report_columns
        ),
        'chart_tab': gui_tab_chart_reports.setup_chart_reports_tab(
            notebook, qual_columns, quant_columns
        ),
        'analysis_tab': gui_tab_analysis.setup_analysis_tab(
            notebook,
            analysis.get_main_dataframe()['title'].tolist(),
        ),
        'settings_tab': gui_tab_settings.setup_settings_tab(notebook, config),
    }

    bind_callbacks(ctx)
    refresh_data_view(ctx)
    on_reference_refresh(ctx)

    root.mainloop()


if __name__ == '__main__':
    main()
