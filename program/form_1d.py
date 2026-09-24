import tkinter as tk
from tkinter import ttk
import math
import sys, os

sys.path.insert(0, os.path.dirname(__file__))
from hmm import MODELS, get_color
from database import fetch_gould

BG   = '#ffffff'
PAN  = '#f6f8fa'
CARD = '#ffffff'
FG   = '#1f2328'
DIM  = '#656d76'
ACC  = '#0969da'
ACC2 = '#0550ae'
GRN  = '#1a7f37'
GRN2 = '#116329'
BRD  = '#d0d7de'

VIZ = ['Линейная полоса', 'Спираль Архимеда', 'Замощение плоскости',
       'Столбчатая диаграмма', 'Треугольник Серпинского']


class Form1D(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title('Объект 1D — Последовательность Гулда')
        self.configure(bg=BG)
        self.minsize(900, 600)
        try:
            self.state('zoomed')
        except Exception:
            pass

        self._resize_id = None
        self._last_w = 0
        self._last_h = 0

        self.data = fetch_gould(1000)
        self._build_ui()
        self.after(100, self.draw)
        self.bind('<F1>', lambda e: self._show_help())
        self.bind('<Configure>', self._on_window_configure)

    def _build_ui(self):
        panel = tk.Frame(self, bg=PAN, width=175)
        panel.pack(side='left', fill='y')
        panel.pack_propagate(False)
        self._build_panel(panel)

        tk.Frame(self, bg=BRD, width=1).pack(side='left', fill='y')

        right = tk.Frame(self, bg=BG)
        right.pack(side='left', fill='both', expand=True)

        self.canvas = tk.Canvas(right, bg=BG, highlightthickness=0, cursor='crosshair')
        sby = tk.Scrollbar(right, orient='vertical',   command=self.canvas.yview, bg=PAN, troughcolor=BG)
        sbx = tk.Scrollbar(right, orient='horizontal', command=self.canvas.xview, bg=PAN, troughcolor=BG)
        self.canvas.configure(xscrollcommand=sbx.set, yscrollcommand=sby.set)
        sbx.pack(side='bottom', fill='x')
        sby.pack(side='right',  fill='y')
        self.canvas.pack(fill='both', expand=True)
        self.canvas.bind('<Motion>', self._on_mouse_move)

        tk.Frame(self, bg=BRD, height=1).pack(side='bottom', fill='x')
        self.status_var = tk.StringVar(value='Готово')
        tk.Label(self, textvariable=self.status_var, anchor='w',
                 bg=PAN, fg=DIM, font=('Consolas', 8), padx=8, pady=3, height = 1, wraplength=0
                 ).pack(side='bottom', fill='x')

    def _build_panel(self, p):
        def sep():
            tk.Frame(p, bg=BRD, height=1).pack(fill='x', padx=8, pady=5)

        def lbl(text):
            tk.Label(p, text=text, fg=DIM, bg=PAN, font=('Segoe UI', 8), anchor='w'
                     ).pack(fill='x', padx=10, pady=(4, 1))

        def spn(var, **kw):
            tk.Spinbox(p, textvariable=var, bg=CARD, fg=FG, insertbackground=FG,
                       buttonbackground=CARD, relief='flat', highlightthickness=1,
                       highlightbackground=BRD, highlightcolor=ACC2,
                       font=('Consolas', 9), width=9, **kw
                       ).pack(padx=10, pady=(0, 4), fill='x')

        tk.Label(p, text='ОБЪЕКТ 1D', bg=PAN, fg=ACC2,
                 font=('Segoe UI', 9, 'bold'), anchor='w').pack(fill='x', padx=10, pady=(12, 2))
        sep()

        lbl('Модель HMM')
        self.model_var = tk.StringVar(value='HMM_R')
        cb = ttk.Combobox(p, textvariable=self.model_var, values=list(MODELS.keys()),
                          state='readonly', width=13, font=('Consolas', 9))
        cb.pack(padx=10, pady=(0, 6), fill='x')
        cb.bind('<<ComboboxSelected>>', lambda e: self.draw())
        sep()

        lbl('Визуализация')
        self.viz_var = tk.StringVar(value=VIZ[0])
        for v in VIZ:
            tk.Radiobutton(p, text=v, variable=self.viz_var, value=v, command=self.draw,
                           bg=PAN, fg=FG, selectcolor=CARD,
                           activebackground=PAN, activeforeground=ACC2,
                           font=('Segoe UI', 8), anchor='w').pack(fill='x', padx=10)
        sep()

        lbl('Параметр N')
        self.n_var = tk.IntVar(value=9)
        spn(self.n_var, from_=2, to=50, command=self.draw)

        lbl('Кол-во элементов')
        self.count_var = tk.IntVar(value=300)
        spn(self.count_var, from_=50, to=1000, increment=50, command=self.draw)

        lbl('Размер ячейки')
        self.cell_var = tk.IntVar(value=14)
        spn(self.cell_var, from_=4, to=40, command=self.draw)

        tk.Frame(p, bg=BG).pack(fill='both', expand=True)

        def btn(text, cmd, bg_c, fg_c='white', hover=None):
            b = tk.Button(p, text=text, command=cmd, bg=bg_c, fg=fg_c, relief='flat',
                          font=('Segoe UI', 9, 'bold'), cursor='hand2', pady=5,
                          activebackground=hover or bg_c, activeforeground=fg_c)
            b.pack(fill='x', padx=10, pady=2)

        btn('⟳  Обновить', self.draw, ACC, hover=ACC2)
        btn('?  Справка',  self._show_help, CARD, fg_c=FG, hover=BRD)
        btn('✕  Закрыть',  self.destroy,    CARD, fg_c=DIM, hover='#3d1a1a')
        tk.Frame(p, bg=PAN, height=10).pack()


    def _on_window_configure(self, event):
        if event.widget is not self:
            return
        if event.width == self._last_w and event.height == self._last_h:
            return
        self._last_w = event.width
        self._last_h = event.height
        if self._resize_id:
            self.after_cancel(self._resize_id)
        self._resize_id = self.after(200, self.draw)

    def draw(self, *_):
        self.canvas.delete('all')
        self.update_idletasks()

        viz   = self.viz_var.get()
        N     = self.n_var.get()
        model = self.model_var.get()
        cell  = self.cell_var.get()
        data  = self.data[:self.count_var.get()]

        if not data:
            return

        vals = [v for _, v in data]
        vmin, vmax = min(vals), max(vals)

        dispatch = {
            'Линейная полоса':       self._draw_strip,
            'Спираль Архимеда':      self._draw_spiral,
            'Замощение плоскости':   self._draw_tile,
            'Столбчатая диаграмма':  self._draw_bar,
            'Треугольник Серпинского': self._draw_sierpinski,
        }
        dispatch.get(viz, self._draw_strip)(data, N, model, cell, vmin, vmax)

    def _cw(self):
        w = self.canvas.winfo_width()
        return w if w > 1 else 800

    def _ch(self):
        h = self.canvas.winfo_height()
        return h if h > 1 else 600

    def _draw_strip(self, data, N, model, cell, vmin, vmax):
        w = self._cw()
        cols = max(1, w // cell)
        for i, (_, v) in enumerate(data):
            c = i % cols
            r = i // cols
            x0, y0 = c * cell, r * cell
            clr = get_color(model, v, N, vmin, vmax)
            self.canvas.create_rectangle(x0, y0, x0 + cell, y0 + cell, fill=clr, outline='')
        rows = (len(data) - 1) // cols + 1
        self.canvas.configure(scrollregion=(0, 0, cols * cell, rows * cell))

    def _draw_spiral(self, data, N, model, cell, vmin, vmax):
        w, h = self._cw(), self._ch()
        cx, cy = w // 2, h // 2
        step = 0.18
        for i, (_, v) in enumerate(data):
            angle = i * step
            r = cell * 0.35 * angle
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            clr = get_color(model, v, N, vmin, vmax)
            half = max(2, cell // 2)
            self.canvas.create_rectangle(x - half, y - half, x + half, y + half, fill=clr, outline='')
        self.canvas.configure(scrollregion=(0, 0, w, h))

    def _draw_tile(self, data, N, model, cell, vmin, vmax):
        w = self._cw()
        cols = max(1, w // cell)
        for i, (_, v) in enumerate(data):
            c = i % cols
            r = i // cols
            x0, y0 = c * cell, r * cell
            clr = get_color(model, v, N, vmin, vmax)
            self.canvas.create_rectangle(x0, y0, x0 + cell, y0 + cell, fill=clr, outline='#1c2128')
            if cell >= 18:
                self.canvas.create_text(x0 + cell // 2, y0 + cell // 2,
                                        text=str(v), font=('Consolas', 7), fill='white')
        rows = (len(data) - 1) // cols + 1
        self.canvas.configure(scrollregion=(0, 0, cols * cell, rows * cell))

    def _draw_bar(self, data, N, model, cell, vmin, vmax):
        w, h = self._cw(), self._ch()
        count  = len(data)
        bar_w  = max(1, w // count)
        max_v  = max(v for _, v in data) or 1
        pad    = 24
        for i, (_, v) in enumerate(data):
            clr = get_color(model, v, N, vmin, vmax)
            bh  = int((v / max_v) * (h - pad - 4))
            x0  = i * bar_w
            self.canvas.create_rectangle(x0, h - pad - bh, x0 + bar_w - 1, h - pad,
                                         fill=clr, outline='')
        self.canvas.create_line(0, h - pad, w, h - pad, fill=BRD, width=1)
        self.canvas.create_text(6, h - 12, text='0',      anchor='w', font=('Consolas', 7), fill=DIM)
        self.canvas.create_text(6, 6,      text=str(max_v), anchor='nw', font=('Consolas', 7), fill=DIM)
        self.canvas.configure(scrollregion=(0, 0, w, h))

    def _draw_sierpinski(self, data, N, model, cell, vmin, vmax):
        w, h = self._cw(), self._ch()
        n = self.count_var.get()
        side = max(1, int(math.sqrt(n)))
        c = min(cell, max(4, min(w, h) // side))
        offset_x = (w - side * c) // 2
        offset_y = (h - side * c) // 2
        idx = 0
        for row in range(side):
            for col in range(side):
                if idx >= len(data):
                    break
                _, v = data[idx]
                idx += 1
                x0 = offset_x + col * c
                y0 = offset_y + row * c
                clr = get_color(model, v, N, vmin, vmax)
                if v == 1:
                    self.canvas.create_rectangle(x0, y0, x0 + c, y0 + c, fill=BG, outline='')
                else:
                    self.canvas.create_rectangle(x0, y0, x0 + c, y0 + c, fill=clr, outline='')
        self.canvas.configure(scrollregion=(0, 0, w, h))

    def _show_help(self):
        win = tk.Toplevel(self)
        win.title('Справка — Объект 1D')
        win.configure(bg=BG)
        win.resizable(False, False)
        tk.Label(win, text='Объект 1D — Последовательность Гулда',
                 bg=BG, fg=ACC2, font=('Segoe UI', 11, 'bold')).pack(anchor='w', padx=16, pady=(14, 4))
        text = (
            "Формула:  a(n) = 2^popcount(n)\n"
            "          popcount(n) — число единиц в двоичном представлении n\n\n"
            "Первые значения: 1, 2, 2, 4, 2, 4, 4, 8, 2, 4, 4, 8, ...\n\n"
            "Визуализации:\n"
            "  Линейная полоса         — элементы строками\n"
            "  Спираль Архимеда        — элементы по спирали\n"
            "  Замощение плоскости     — сетка с числами\n"
            "  Столбчатая диаграмма    — высота = значение\n"
            "  Треугольник Серпинского — чёрные клетки = a(n)=1\n\n"
            "F1 — справка"
        )
        t = tk.Text(win, bg=CARD, fg=FG, font=('Consolas', 9), relief='flat',
                    padx=12, pady=8, width=56, height=14, highlightthickness=0)
        t.insert('end', text)
        t.configure(state='disabled')
        t.pack(padx=16, pady=4)
        tk.Button(win, text='Закрыть', command=win.destroy, bg=ACC, fg='white',
                  relief='flat', padx=16, pady=4, font=('Segoe UI', 9),
                  cursor='hand2').pack(pady=(4, 14))
