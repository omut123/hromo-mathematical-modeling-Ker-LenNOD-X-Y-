import tkinter as tk
from tkinter import ttk
import math
import sys, os

sys.path.insert(0, os.path.dirname(__file__))
from hmm import MODELS, get_color, ker_cos
from database import fetch_ker_cos

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

VIZ = ['Цветовая карта', 'Контурный анализ', 'Полосы по X', 'Псевдо-3D', 'Полярная карта']


class Form2D(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title('Объект 2D — Ker(A·cos(X·Y))')
        self.configure(bg=BG)
        self.minsize(900, 600)
        try:
            self.state('zoomed')
        except Exception:
            pass

        self._resize_id = None
        self._last_w = 0
        self._last_h = 0

        self._build_ui()
        self.after(100, self.draw)
        self.bind('<F5>', lambda e: self.draw())
        self.bind('<F1>', lambda e: self._show_help())
        self.bind('<Configure>', self._on_window_configure)

    def _build_ui(self):
        panel = tk.Frame(self, bg=PAN, width=185)
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
        self.status_var = tk.StringVar(value='Нажмите «Расчёт» или F5')
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

        tk.Label(p, text='ОБЪЕКТ 2D', bg=PAN, fg=ACC2,
                 font=('Segoe UI', 9, 'bold'), anchor='w').pack(fill='x', padx=10, pady=(12, 2))
        sep()

        lbl('Модель HMM')
        self.model_var = tk.StringVar(value='HMM_DN')
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

        self.n_var    = tk.IntVar(value=9)
        self.a_var    = tk.DoubleVar(value=10.0)
        self.xmin_var = tk.IntVar(value=1)
        self.xmax_var = tk.IntVar(value=40)
        self.ymin_var = tk.IntVar(value=1)
        self.ymax_var = tk.IntVar(value=40)
        self.cell_var = tk.IntVar(value=14)

        lbl('Параметр N');    spn(self.n_var,    from_=2,   to=50)
        lbl('Коэфф. A');      spn(self.a_var,    from_=0.1, to=100.0, increment=0.5, format='%.1f')
        lbl('X от — до')
        fr = tk.Frame(p, bg=PAN); fr.pack(fill='x', padx=10, pady=(0, 4))
        for var, lim in [(self.xmin_var, (1, 200)), (self.xmax_var, (2, 200))]:
            tk.Spinbox(fr, textvariable=var, from_=lim[0], to=lim[1],
                       bg=CARD, fg=FG, insertbackground=FG, buttonbackground=CARD,
                       relief='flat', highlightthickness=1, highlightbackground=BRD,
                       highlightcolor=ACC2, font=('Consolas', 9), width=5
                       ).pack(side='left', padx=(0, 4))
        lbl('Y от — до')
        fr2 = tk.Frame(p, bg=PAN); fr2.pack(fill='x', padx=10, pady=(0, 4))
        for var, lim in [(self.ymin_var, (1, 200)), (self.ymax_var, (2, 200))]:
            tk.Spinbox(fr2, textvariable=var, from_=lim[0], to=lim[1],
                       bg=CARD, fg=FG, insertbackground=FG, buttonbackground=CARD,
                       relief='flat', highlightthickness=1, highlightbackground=BRD,
                       highlightcolor=ACC2, font=('Consolas', 9), width=5
                       ).pack(side='left', padx=(0, 4))
        lbl('Размер ячейки'); spn(self.cell_var, from_=4, to=40)

        tk.Frame(p, bg=BG).pack(fill='both', expand=True)

        def btn(text, cmd, bg_c, fg_c='white', hover=None):
            b = tk.Button(p, text=text, command=cmd, bg=bg_c, fg=fg_c, relief='flat',
                          font=('Segoe UI', 9, 'bold'), cursor='hand2', pady=5,
                          activebackground=hover or bg_c, activeforeground=fg_c)
            b.pack(fill='x', padx=10, pady=2)

        btn('⟳  Расчёт',  self.draw,        ACC, hover=ACC2)
        btn('?  Справка', self._show_help,  CARD, fg_c=FG, hover=BRD)
        btn('✕  Закрыть', self.destroy,     CARD, fg_c=DIM, hover='#3d1a1a')
        tk.Frame(p, bg=PAN, height=10).pack()

    def _on_window_configure(self, event):
        if event.widget is not self:
            return
        if event.width == self._last_w and event.height == self._last_h:
            return
        self._last_w = event.width
        self._last_h = event.height
        viz = self.viz_var.get()
        if viz in ('Полосы по X', 'Полярная карта'):
            if self._resize_id:
                self.after_cancel(self._resize_id)
            self._resize_id = self.after(200, self.draw)

    def _get_data(self):
        xmin = self.xmin_var.get()
        xmax = max(xmin + 1, self.xmax_var.get())
        ymin = self.ymin_var.get()
        ymax = max(ymin + 1, self.ymax_var.get())
        A    = self.a_var.get()
        return fetch_ker_cos(xmin, xmax, ymin, ymax, A), xmin, xmax, ymin, ymax, A

    def draw(self, *_):
        self.canvas.delete('all')
        self.update_idletasks()
        N     = self.n_var.get()
        model = self.model_var.get()
        cell  = self.cell_var.get()
        viz   = self.viz_var.get()
        data, xmin, xmax, ymin, ymax, A = self._get_data()
        if not data:
            return
        vals = list(data.values())
        vmin, vmax = min(vals), max(vals)
        dispatch = {
            'Цветовая карта':  self._draw_heatmap,
            'Контурный анализ': self._draw_contour,
            'Полосы по X':     self._draw_strips_x,
            'Псевдо-3D':       self._draw_pseudo3d,
            'Полярная карта':  self._draw_polar,
        }
        dispatch.get(viz, self._draw_heatmap)(data, xmin, xmax, ymin, ymax, N, model, cell, vmin, vmax)

    def _cw(self):
        w = self.canvas.winfo_width()
        return w if w > 1 else 700

    def _ch(self):
        h = self.canvas.winfo_height()
        return h if h > 1 else 500

    def _draw_heatmap(self, data, xmin, xmax, ymin, ymax, N, model, cell, vmin, vmax):
        W = (xmax - xmin + 1) * cell
        H = (ymax - ymin + 1) * cell
        for (x, y), v in data.items():
            x0 = (x - xmin) * cell
            y0 = (y - ymin) * cell
            clr = get_color(model, v, N, vmin, vmax)
            self.canvas.create_rectangle(x0, y0, x0 + cell, y0 + cell, fill=clr, outline='')
            if cell >= 20:
                self.canvas.create_text(x0 + cell // 2, y0 + cell // 2,
                                        text=str(v), font=('Consolas', 7), fill='white')
        step = max(1, (xmax - xmin) // 8)
        for xi in range(xmin, xmax + 1, step):
            px = (xi - xmin) * cell + cell // 2
            self.canvas.create_text(px, H + 9, text=str(xi), font=('Consolas', 7), fill=DIM)
        step = max(1, (ymax - ymin) // 8)
        for yi in range(ymin, ymax + 1, step):
            py = (yi - ymin) * cell + cell // 2
            self.canvas.create_text(W + 12, py, text=str(yi), font=('Consolas', 7), fill=DIM)
        self.canvas.configure(scrollregion=(0, 0, W + 28, H + 22))

    def _draw_contour(self, data, xmin, xmax, ymin, ymax, N, model, cell, vmin, vmax):
        W = (xmax - xmin + 1) * cell
        H = (ymax - ymin + 1) * cell
        for (x, y), v in data.items():
            x0 = (x - xmin) * cell
            y0 = (y - ymin) * cell
            clr = get_color(model, v, N, vmin, vmax)
            self.canvas.create_rectangle(x0, y0, x0 + cell, y0 + cell, fill=clr, outline='')
            for dx, dy in [(1, 0), (0, 1)]:
                nb = data.get((x + dx, y + dy))
                if nb is not None and nb != v:
                    if dx == 1:
                        self.canvas.create_line(x0 + cell, y0, x0 + cell, y0 + cell,
                                                fill='white', width=1)
                    else:
                        self.canvas.create_line(x0, y0 + cell, x0 + cell, y0 + cell,
                                                fill='white', width=1)
        self.canvas.configure(scrollregion=(0, 0, W + 4, H + 4))

    def _draw_strips_x(self, data, xmin, xmax, ymin, ymax, N, model, cell, vmin, vmax):
        W, H = self._cw(), self._ch()
        xs    = sorted(set(x for x, _ in data))
        if not xs:
            return
        bar_w = max(2, (W - 20) // len(xs))
        pad   = 28
        for i, x in enumerate(xs):
            ys = [data[(x, y)] for y in range(ymin, ymax + 1) if (x, y) in data]
            if not ys:
                continue
            avg = sum(ys) / len(ys)
            clr = get_color(model, avg, N, vmin, vmax)
            bh  = int((avg / (vmax or 1)) * (H - pad - 4))
            x0  = 10 + i * bar_w
            self.canvas.create_rectangle(x0, H - pad - bh, x0 + bar_w - 1, H - pad,
                                         fill=clr, outline='')
            if bar_w >= 22:
                self.canvas.create_text(x0 + bar_w // 2, H - 14,
                                        text=str(x), font=('Consolas', 7), fill=DIM)
        self.canvas.create_line(8, H - pad, W - 8, H - pad, fill=BRD, width=1)
        self.canvas.configure(scrollregion=(0, 0, W, H))

    def _draw_pseudo3d(self, data, xmin, xmax, ymin, ymax, N, model, cell, vmin, vmax):
        OX = cell // 2
        OY = cell // 3
        cols = sorted(set(x for x, _ in data))
        rows = sorted(set(y for _, y in data))
        for ri, y in enumerate(rows):
            for ci, x in enumerate(cols):
                v   = data.get((x, y), 0)
                clr = get_color(model, v, N, vmin, vmax)
                bx  = ci * cell + ri * OX
                by  = ri * (cell - OY)
                self.canvas.create_rectangle(bx, by, bx + cell, by + cell,
                                             fill=clr, outline='#1c2128')
        W = len(cols) * cell + len(rows) * OX + cell
        H = len(rows) * (cell - OY) + cell
        self.canvas.configure(scrollregion=(0, 0, W, H))

    def _draw_polar(self, data, xmin, xmax, ymin, ymax, N, model, cell, vmin, vmax):
        W, H = self._cw(), self._ch()
        cx, cy = W // 2, H // 2
        R_max  = min(cx, cy) - 10

        xs = sorted(set(x for x, _ in data))
        ys = sorted(set(y for _, y in data))
        if not xs or not ys:
            return

        rings  = len(ys)
        slices = len(xs)
        if rings == 0 or slices == 0:
            return

        ring_w  = R_max / rings
        slice_a = 2 * math.pi / slices

        for si, x in enumerate(xs):
            for ri, y in enumerate(ys):
                v = data.get((x, y))
                if v is None:
                    continue
                clr   = get_color(model, v, N, vmin, vmax)
                r0    = ri * ring_w
                r1    = (ri + 1) * ring_w
                a0    = si * slice_a - math.pi / 2
                a1    = (si + 1) * slice_a - math.pi / 2
                steps = max(3, int(r1 * (a1 - a0) / 2))
                pts   = []
                for k in range(steps + 1):
                    ang = a0 + (a1 - a0) * k / steps
                    pts.append((cx + r1 * math.cos(ang), cy + r1 * math.sin(ang)))
                for k in range(steps, -1, -1):
                    ang = a0 + (a1 - a0) * k / steps
                    pts.append((cx + r0 * math.cos(ang), cy + r0 * math.sin(ang)))
                flat = [c for pt in pts for c in pt]
                self.canvas.create_polygon(flat, fill=clr, outline='')

        for xi, x in enumerate(xs[::max(1, slices // 8)]):
            a   = xi * (slices // max(1, slices // 8)) * slice_a - math.pi / 2
            tx  = cx + (R_max + 14) * math.cos(a)
            ty  = cy + (R_max + 14) * math.sin(a)
            self.canvas.create_text(tx, ty, text=str(x), font=('Consolas', 7), fill=DIM)

        self.canvas.configure(scrollregion=(0, 0, W, H))

    def _show_help(self):
        win = tk.Toplevel(self)
        win.title('Справка — Объект 2D')
        win.configure(bg=BG)
        win.resizable(False, False)
        tk.Label(win, text='Объект 2D — Ker(A·cos(X·Y))',
                 bg=BG, fg=ACC2, font=('Segoe UI', 11, 'bold')).pack(anchor='w', padx=16, pady=(14, 4))
        text = (
            "Формула:  Z = Ker( |round( A · cos(X·Y) )| )\n\n"
            "Ker(n) — цифровой корень (рекурсивная сумма цифр).\n"
            "Значения Z всегда от 1 до 9.\n\n"
            "Параметры:\n"
            "  A — коэффициент масштабирования косинуса\n"
            "  N — нормирующий параметр HMM-модели\n"
            "  X, Y — диапазоны целых чисел\n\n"
            "Визуализации:\n"
            "  Цветовая карта    — матрица Z(X,Y)\n"
            "  Контурный анализ  — границы зон\n"
            "  Полосы по X       — средние Z по каждому X\n"
            "  Псевдо-3D         — изометрия\n"
            "  Полярная карта    — круговая диаграмма-матрица\n\n"
            "F5 — пересчитать   F1 — справка"
        )
        t = tk.Text(win, bg=CARD, fg=FG, font=('Consolas', 9), relief='flat',
                    padx=12, pady=8, width=56, height=16, highlightthickness=0)
        t.insert('end', text)
        t.configure(state='disabled')
        t.pack(padx=16, pady=4)
        tk.Button(win, text='Закрыть', command=win.destroy, bg=ACC, fg='white',
                  relief='flat', padx=16, pady=4, font=('Segoe UI', 9),
                  cursor='hand2').pack(pady=(4, 14))
