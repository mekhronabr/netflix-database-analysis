"""
Встраивание matplotlib-графиков в Tkinter.

Автор: Бободжанова Мехрона Рахимовна
"""

from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def create_chart_frame(parent):
    """Создаёт контейнер для встраивания matplotlib-графика."""
    frame = ttk.Frame(parent)
    frame.pack(fill='both', expand=True, pady=5)
    canvas_holder = {'canvas': None, 'widget': None}
    return frame, canvas_holder


def show_figure(chart_frame, canvas_holder, figure):
    """Отображает matplotlib-фигуру внутри Tkinter-фрейма."""
    if canvas_holder.get('widget'):
        canvas_holder['widget'].destroy()

    canvas = FigureCanvasTkAgg(figure, master=chart_frame)
    canvas.draw_idle()
    widget = canvas.get_tk_widget()
    widget.pack(fill='both', expand=True)
    canvas_holder['canvas'] = canvas
    canvas_holder['widget'] = widget
    canvas.mpl_connect('resize_event', lambda _event: canvas.draw_idle())
