import tkinter as tk
from tkinter import messagebox, ttk
import sys, os, threading

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT_DIR, 'source'))

from database import init_db
from form_1d import Form1D
from form_2d import Form2D

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


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('HMM — Вариант 13')
        self.configure(bg=BG)
        self.geometry('900x540')
        self.minsize(720, 460)

        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TCombobox', fieldbackground=CARD, background=CARD,
                        foreground=FG, selectbackground=ACC, bordercolor=BRD, arrowcolor=DIM)

        self._build_menu()
        self._build_header()
        self._build_cards()
        self._build_statusbar()

        self.status_var.set('Инициализация базы данных...')
        threading.Thread(target=self._init_db_bg, daemon=True).start()

        self.bind('<F1>', lambda e: self._show_help())
        self.protocol('WM_DELETE_WINDOW', self.quit)

    def _build_menu(self):
        mb = tk.Menu(self, bg=PAN, fg=FG, activebackground=ACC, activeforeground='white',
                     relief='flat', bd=0)
        self.config(menu=mb)

        def menu(label, items):
            m = tk.Menu(mb, tearoff=0, bg=PAN, fg=FG,
                        activebackground=ACC, activeforeground='white')
            for item in items:
                if item is None:
                    m.add_separator()
                else:
                    m.add_command(label=item[0], command=item[1])
            mb.add_cascade(label=label, menu=m)

        menu('Данные', [
            ('Открыть БД            Ctrl+O', self._open_db_info),
            ('Пересоздать БД        Ctrl+N', self._recreate_db),
            None,
            ('Выход                 Ctrl+X', self.quit),
        ])
        menu('Визуализация', [
            ('Объект 1D — Последовательность Гулда   F4', self._open_1d),
            ('Объект 2D — Ker(A·cos(X·Y))             F5', self._open_2d),
        ])
        menu('Справка', [
            ('Содержание            F1',      self._show_help),
            ('О программе           Ctrl+F1', self._show_about),
        ])

        self.bind('<F4>', lambda e: self._open_1d())
        self.bind('<F5>', lambda e: self._open_2d())
        self.bind('<Control-x>', lambda e: self.quit())
        self.bind('<Control-o>', lambda e: self._open_db_info())
        self.bind('<Control-n>', lambda e: self._recreate_db())
        self.bind('<Control-F1>', lambda e: self._show_about())

    def _build_header(self):
        hdr = tk.Frame(self, bg='#0d2045')
        hdr.pack(fill='x')
        inn = tk.Frame(hdr, bg='#0d2045')
        inn.pack(fill='x', padx=24, pady=14)
        tk.Label(inn, text='Хромоматематическое моделирование',
                 font=('Segoe UI', 17, 'bold'), fg='#cdd9fb', bg='#0d2045').pack(anchor='w')
        tk.Label(inn,
                 text='Вариант 13  ·  Объект 1D: Последовательность Гулда'
                      '  ·  Объект 2D: Ker(A·cos(X·Y))',
                 font=('Segoe UI', 9), fg='#7899d4', bg='#0d2045').pack(anchor='w', pady=(2, 0))
        tk.Frame(self, bg=BRD, height=1).pack(fill='x')

    def _build_cards(self):
        outer = tk.Frame(self, bg=BG)
        outer.pack(fill='both', expand=True, padx=20, pady=14)

        self._make_card(outer, side='left',
            title='Объект 1D', subtitle='Последовательность Гулда',
            formula='a(n) = 2^popcount(n)',
            sample='1, 2, 2, 4, 2, 4, 4, 8, 2, 4, …',
            desc='Линейная полоса · Спираль · Замощение\nСтолбчатая диаграмма · Треугольник Серпинского',
            btn_text='Открыть  (F4)', btn_bg=ACC, btn_hover=ACC2,
            draw_fn=self._preview_1d, open_fn=self._open_1d)

        tk.Frame(outer, bg=BRD, width=1).pack(side='left', fill='y', padx=10)

        self._make_card(outer, side='left',
            title='Объект 2D', subtitle='Ker(A·cos(X·Y))',
            formula='Z = Ker(|round(A·cos(X·Y))|)',
            sample='Z ∈ {1…9}  (цифровой корень)',
            desc='Цветовая карта · Контуры · Полосы по X\nПсевдо-3D · Полярная карта',
            btn_text='Открыть  (F5)', btn_bg=GRN, btn_hover=GRN2,
            draw_fn=self._preview_2d, open_fn=self._open_2d)

    def _make_card(self, parent, side, title, subtitle, formula, sample,
                   desc, btn_text, btn_bg, btn_hover, draw_fn, open_fn):
        card = tk.Frame(parent, bg=PAN)
        card.pack(side=side, fill='both', expand=True)
        tk.Frame(card, bg=btn_bg, height=3).pack(fill='x')
        body = tk.Frame(card, bg=PAN)
        body.pack(fill='both', expand=True, padx=16, pady=10)
        tk.Label(body, text=title, font=('Segoe UI', 13, 'bold'), fg=FG, bg=PAN).pack(anchor='w')
        tk.Label(body, text=subtitle, font=('Consolas', 10), fg=ACC2, bg=PAN).pack(anchor='w', pady=(1, 0))
        tk.Frame(body, bg=BRD, height=1).pack(fill='x', pady=7)
        pf = tk.Frame(body, bg=BG, highlightthickness=1, highlightbackground=BRD)
        pf.pack(fill='x')
        cnv = tk.Canvas(pf, bg=BG, height=68, highlightthickness=0)
        cnv.pack(fill='x', expand=True)
        cnv.bind('<Configure>', lambda e, c=cnv, f=draw_fn: f(c))
        draw_fn(cnv)
        tk.Frame(body, bg=BRD, height=1).pack(fill='x', pady=7)
        tk.Label(body, text=formula, font=('Consolas', 9), fg='#f0c27a', bg=PAN, anchor='w').pack(fill='x')
        tk.Label(body, text=sample, font=('Consolas', 8), fg=DIM, bg=PAN, anchor='w').pack(fill='x', pady=(2, 4))
        tk.Label(body, text=desc, font=('Segoe UI', 8), fg=DIM, bg=PAN, anchor='w', justify='left').pack(fill='x')
        tk.Frame(body, bg=BG).pack(fill='both', expand=True)
        tk.Button(body, text=btn_text, command=open_fn, bg=btn_bg, fg='white', relief='flat',
                  font=('Segoe UI', 10, 'bold'), cursor='hand2', pady=6,
                  activebackground=btn_hover, activeforeground='white').pack(fill='x', pady=(8, 0))

    def _preview_1d(self, cnv):
        from hmm import gould, get_color
        cnv.delete('all')
        w = cnv.winfo_width() or 360
        cell = 9
        cols = max(1, w // cell)
        for i in range(min(cols * 7, 400)):
            v = gould(i)
            col, row = i % cols, i // cols
            clr = get_color('HMM_R', v, N=9, vmin=1, vmax=8)
            cnv.create_rectangle(col * cell, row * cell,
                                 (col + 1) * cell, (row + 1) * cell, fill=clr, outline='')

    def _preview_2d(self, cnv):
        from hmm import ker_cos, get_color
        cnv.delete('all')
        w = cnv.winfo_width() or 360
        cell = 9
        cols = max(1, w // cell)
        A = 10.0
        for i in range(min(cols * 7, 400)):
            x = (i % 50) + 1
            y = (i // 50) + 1
            v = ker_cos(x, y, A)
            col, row = i % cols, i // cols
            clr = get_color('HMM_DN', v, N=9, vmin=1, vmax=9)
            cnv.create_rectangle(col * cell, row * cell,
                                 (col + 1) * cell, (row + 1) * cell, fill=clr, outline='')

    def _build_statusbar(self):
        tk.Frame(self, bg=BRD, height=1).pack(fill='x')
        bar = tk.Frame(self, bg=PAN)
        bar.pack(fill='x')
        self.status_var = tk.StringVar(value='Готово')
        tk.Label(bar, textvariable=self.status_var, anchor='w',
                 bg=PAN, fg=DIM, font=('Consolas', 8), padx=10, pady=4).pack(side='left')
        tk.Label(bar, text='Python 3  ·  tkinter  ·  SQLite',
                 anchor='e', bg=PAN, fg=BRD, font=('Segoe UI', 8), padx=10).pack(side='right')

    def _init_db_bg(self):
        try:
            init_db()
            self.after(0, lambda: self.status_var.set(
                'База данных готова.   F4 — Объект 1D   F5 — Объект 2D   F1 — Справка'))
        except Exception as e:
            self.after(0, lambda: self.status_var.set(f'Ошибка БД: {e}'))

    def _open_1d(self):
        Form1D(self)

    def _open_2d(self):
        Form2D(self)

    def _open_db_info(self):
        from database import DB_PATH, get_connection
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM gould_1d');  n1 = cur.fetchone()[0]
        cur.execute('SELECT COUNT(*) FROM ker_cos_2d'); n2 = cur.fetchone()[0]
        conn.close()
        messagebox.showinfo('База данных',
                            f'Путь: {DB_PATH}\n\n'
                            f'gould_1d:    {n1} записей\n'
                            f'ker_cos_2d:  {n2} записей')

    def _recreate_db(self):
        from database import DB_PATH
        if messagebox.askyesno('Пересоздать БД', 'Удалить и пересоздать базу данных?'):
            if os.path.exists(DB_PATH):
                os.remove(DB_PATH)
            self.status_var.set('Пересоздание базы данных...')
            threading.Thread(target=self._init_db_bg, daemon=True).start()

    def _show_help(self):
        win = tk.Toplevel(self)
        win.title('Справка — HMM Вариант 13')
        win.configure(bg=BG)
        win.resizable(False, False)
        tk.Label(win, text='Справка — HMM Вариант 13',
                 bg=BG, fg=ACC2, font=('Segoe UI', 12, 'bold')).pack(anchor='w', padx=16, pady=(14, 4))
        text = (
            "Хромоматематическое моделирование числовых закономерностей.\n\n"
            "Объект 1D — Последовательность Гулда:\n"
            "  a(n) = 2^popcount(n),  n = 0, 1, 2, ...\n"
            "  Значения: 1, 2, 2, 4, 2, 4, 4, 8, ...\n\n"
            "Объект 2D — Ker(A·cos(X·Y)):\n"
            "  Z = Ker(|round(A·cos(X·Y))|),  Z ∈ {1…9}\n\n"
            "HMM-модели:\n"
            "  HMM_N  — монохромная (оттенки серого)\n"
            "  HMM_N2 — двухцветный градиент\n"
            "  HMM_B  — биградиентная\n"
            "  HMM_R  — мультиградиентная (радуга)\n"
            "  HMM_DN — дискретная (10 цветов)\n"
            "  HMM_T  — тепловая карта\n\n"
            "Клавиши:\n"
            "  F1        — эта справка\n"
            "  F4        — Объект 1D\n"
            "  F5        — Объект 2D\n"
            "  Ctrl+O    — информация о базе данных\n"
            "  Ctrl+N    — пересоздать базу данных\n"
            "  Ctrl+X    — выход\n"
            "  Ctrl+F1   — о программе\n"
        )
        t = tk.Text(win, bg=CARD, fg=FG, font=('Consolas', 9), relief='flat',
                    padx=14, pady=10, width=58, height=22, highlightthickness=0)
        t.insert('end', text)
        t.configure(state='disabled')
        t.pack(padx=16, pady=4)
        tk.Button(win, text='Закрыть', command=win.destroy, bg=ACC, fg='white',
                  relief='flat', padx=20, pady=5, font=('Segoe UI', 9),
                  cursor='hand2').pack(pady=(4, 14))

    def _show_about(self):
        win = tk.Toplevel(self)
        win.title('О программе')
        win.configure(bg=BG)
        win.resizable(False, False)
        tk.Label(win, text='HMM — Вариант 13', bg=BG, fg=ACC2,
                 font=('Segoe UI', 13, 'bold')).pack(pady=(18, 2))
        tk.Label(win, text='Хромоматематическое моделирование',
                 bg=BG, fg=FG, font=('Segoe UI', 10)).pack()
        tk.Frame(win, bg=BRD, height=1).pack(fill='x', padx=20, pady=12)
        for k, v in [
            ('Объект 1D', 'Последовательность Гулда'),
            ('Объект 2D', 'Ker(A·cos(X·Y))'),
            ('Студент',   'Жуков Ярослав Юрьевич'),
            ('Группа',    'БСБО-22-24'),
            ('Год',       '2026'),
            ('Язык',      'Python 3 / tkinter / SQLite'),
        ]:
            row = tk.Frame(win, bg=BG); row.pack(fill='x', padx=24, pady=1)
            tk.Label(row, text=f'{k}:', width=14, anchor='e', bg=BG, fg=DIM,
                     font=('Segoe UI', 9)).pack(side='left')
            tk.Label(row, text=v, anchor='w', bg=BG, fg=FG,
                     font=('Segoe UI', 9)).pack(side='left', padx=6)
        tk.Frame(win, bg=BRD, height=1).pack(fill='x', padx=20, pady=12)
        tk.Button(win, text='OK', command=win.destroy, bg=ACC, fg='white', relief='flat',
                  padx=24, pady=5, font=('Segoe UI', 9), cursor='hand2').pack(pady=(0, 16))


if __name__ == '__main__':
    app = MainApp()
    app.mainloop()
