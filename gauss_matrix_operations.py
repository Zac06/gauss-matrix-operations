"""
Operazioni Elementari di Gauss
================================
GUI in Python/tkinter — supporta interi, frazioni, complessi ed espressioni simboliche.
Interfaccia bilingue / Bilingual UI: Italiano · English (selettore IT / EN in alto a destra).

Funzionalità:
  • Tre operazioni elementari di riga (manuale)
  • Eliminazione automatica: forma a scala (Gauss) e ridotta (Gauss-Jordan)
  • Pannello info: rango, determinante, traccia
  • Esempi numerici e simbolici
  • Annulla / Storico operazioni

Input validi:  3  ,  -1/2  ,  2+3i  ,  alfa^2+4  ,  sqrt(2)  ,  pi
"""

import re
import copy
import tkinter as tk
from tkinter import ttk, messagebox
import sympy
from sympy import sympify, simplify, I, pi, E, sqrt, SympifyError, Matrix

# ─── palette ─────────────────────────────────────────────────────────────────
BG       = "#1e1e2e"
PANEL    = "#2a2a3e"
CARD     = "#313145"
CARD2    = "#272738"
ACCENT   = "#7c7ff8"
FG       = "#e2e0f0"
FG_DIM   = "#8880a8"
ENTRY_BG = "#25253a"
BORDER   = "#44446a"
HI_BLUE  = "#3a4a7a"
HI_GREEN = "#2a5a3a"
ERR      = "#e05555"
MONO     = ("Courier New", 12)
SANS     = ("Segoe UI", 11)
SANS_SM  = ("Segoe UI", 10)
SANS_LG  = ("Segoe UI", 13, "bold")

_LOCALS = {"i": I, "j": I, "I": I, "pi": pi, "e": E, "E": E, "sqrt": sqrt}
ZERO = sympy.Integer(0)
ONE  = sympy.Integer(1)

# ─── internazionalizzazione / internationalization ───────────────────────────
LANG = "it"          # lingua corrente / current language: "it" | "en"

STRINGS = {
    "it": {
        "title":       "Operazioni Elementari di Gauss",
        "subtitle":    "  Input: interi · frazioni (3/4) · complessi (2+3i) · "
                       "espressioni simboliche (alfa^2+4, sqrt(2), pi, e)",
        "lang_label":  "Lingua:",
        "rows_label":  "Righe:",
        "cols_label":  "Colonne:",
        "btn_new":     "Nuova matrice",
        "btn_ex_num":  "Esempio numerico",
        "btn_ex_sym":  "Esempio simbolico",
        "btn_undo":    "Annulla",
        "rank":        "Rango",
        "det":         "Determinante",
        "trace":       "Traccia",
        "not_square":  "(non quadrata)",
        "history":     "Storico operazioni",
        "op1_title":   "1 · Scambio di righe",
        "op1_btn":     "Applica scambio",
        "op2_title":   "2 · Scala una riga",
        "op2_btn":     "Applica scala",
        "op3_title":   "3 · Somma righe",
        "op3_btn":     "Applica somma",
        "err_rows_diff": "Le righe devono essere diverse.",
        "err_k_zero":    "k non può essere zero.",
        "err_k_noop":    "k = 0 non cambia nulla.",
        "auto_card":   "Riduzione automatica",
        "auto_sub":    "passo per passo, con animazione",
        "btn_gauss":   "▶  Forma a Scala  (Gauss)",
        "btn_gj":      "▶▶  Forma Ridotta  (Gauss-Jordan)",
        "speed":       "Velocità:",
        "auto_title":  "Auto-riduzione",
        "already_reduced": "La matrice è già in forma ridotta.",
        "undo_title":  "Annulla",
        "nothing_to_undo": "Nessuna operazione da annullare.",
        "auto_start":  "[inizio auto-riduzione]",
        "input_err_title": "Errore input",
        "input_err_body":  "Cella ({i},{j}): {ex}\n\n"
                           "Esempi: 3, -1/2, 2+3i, alfa^2+4, sqrt(2), pi",
        "err_expr":    "Espressione non valida: '{s}'",
    },
    "en": {
        "title":       "Elementary Row Operations (Gauss)",
        "subtitle":    "  Input: integers · fractions (3/4) · complex numbers (2+3i) · "
                       "symbolic expressions (alpha^2+4, sqrt(2), pi, e)",
        "lang_label":  "Language:",
        "rows_label":  "Rows:",
        "cols_label":  "Columns:",
        "btn_new":     "New matrix",
        "btn_ex_num":  "Numeric example",
        "btn_ex_sym":  "Symbolic example",
        "btn_undo":    "Undo",
        "rank":        "Rank",
        "det":         "Determinant",
        "trace":       "Trace",
        "not_square":  "(not square)",
        "history":     "Operation history",
        "op1_title":   "1 · Swap rows",
        "op1_btn":     "Apply swap",
        "op2_title":   "2 · Scale a row",
        "op2_btn":     "Apply scaling",
        "op3_title":   "3 · Add rows",
        "op3_btn":     "Apply addition",
        "err_rows_diff": "The rows must be different.",
        "err_k_zero":    "k cannot be zero.",
        "err_k_noop":    "k = 0 changes nothing.",
        "auto_card":   "Automatic reduction",
        "auto_sub":    "step by step, animated",
        "btn_gauss":   "▶  Row Echelon Form  (Gauss)",
        "btn_gj":      "▶▶  Reduced Echelon Form  (Gauss-Jordan)",
        "speed":       "Speed:",
        "auto_title":  "Auto-reduction",
        "already_reduced": "The matrix is already in reduced form.",
        "undo_title":  "Undo",
        "nothing_to_undo": "No operation to undo.",
        "auto_start":  "[auto-reduction start]",
        "input_err_title": "Input error",
        "input_err_body":  "Cell ({i},{j}): {ex}\n\n"
                           "Examples: 3, -1/2, 2+3i, alpha^2+4, sqrt(2), pi",
        "err_expr":    "Invalid expression: '{s}'",
    },
}

def tr(key, **kw):
    s = STRINGS[LANG].get(key, STRINGS["it"][key])
    return s.format(**kw) if kw else s

# ─── helpers ──────────────────────────────────────────────────────────────────
def parse_expr(s):
    s = s.strip().replace(",", ".").replace("^", "**")
    s = re.sub(r'(\d)([ij])\b', r'\1*I', s)
    s = re.sub(r'\b([ij])\b', 'I', s)
    try:
        return sympify(s, locals=_LOCALS, evaluate=True)
    except (SympifyError, SyntaxError, TypeError) as exc:
        raise ValueError(tr("err_expr", s=s)) from exc

def fmt(expr):
    expr = simplify(expr)
    s = str(expr)
    s = s.replace("**", "^")
    s = re.sub(r'\*I\b', 'i', s)
    s = re.sub(r'\bI\b', 'i', s)
    return s

# ─── algoritmi di riduzione ───────────────────────────────────────────────────
def gauss_steps(m):
    """Restituisce lista di (matrix_snapshot, op_text, hi_rows) per forma a scala."""
    m = [[simplify(v) for v in row] for row in m]
    r, c = len(m), len(m[0])
    steps = []
    pivot_row = 0
    for col in range(c):
        if pivot_row >= r:
            break
        # cerca pivot
        found = next((row for row in range(pivot_row, r)
                      if simplify(m[row][col]) != ZERO), None)
        if found is None:
            continue
        # scambio righe
        if found != pivot_row:
            m[pivot_row], m[found] = m[found], m[pivot_row]
            steps.append((copy.deepcopy(m),
                          f"R{pivot_row+1} ↔ R{found+1}",
                          (pivot_row, found)))
        # normalizza pivot a 1
        piv = simplify(m[pivot_row][col])
        if piv != ONE:
            inv = simplify(ONE / piv)
            m[pivot_row] = [simplify(inv * v) for v in m[pivot_row]]
            steps.append((copy.deepcopy(m),
                          f"R{pivot_row+1} → ({fmt(inv)}) · R{pivot_row+1}",
                          (pivot_row,)))
        # elimina righe sotto
        for row in range(pivot_row + 1, r):
            factor = simplify(m[row][col])
            if factor == ZERO:
                continue
            neg = simplify(-factor)
            m[row] = [simplify(m[row][k] + neg * m[pivot_row][k]) for k in range(c)]
            steps.append((copy.deepcopy(m),
                          f"R{row+1} → R{row+1} + ({fmt(neg)}) · R{pivot_row+1}",
                          (row, pivot_row)))
        pivot_row += 1
    return steps

def gauss_jordan_steps(m):
    """Restituisce lista di passi per RREF (Gauss-Jordan)."""
    steps = gauss_steps(copy.deepcopy(m))
    m = copy.deepcopy(steps[-1][0]) if steps else [[simplify(v) for v in row] for row in m]
    r, c = len(m), len(m[0])
    # individua righe pivot
    pivot_pairs = []
    for i in range(r):
        for j in range(c):
            if simplify(m[i][j]) == ONE and all(
                    simplify(m[k][j]) == ZERO for k in range(r) if k != i):
                pivot_pairs.append((i, j))
                break
    # back-substitution
    for (pr, pc) in reversed(pivot_pairs):
        for row in range(pr):
            factor = simplify(m[row][pc])
            if factor == ZERO:
                continue
            neg = simplify(-factor)
            m[row] = [simplify(m[row][k] + neg * m[pr][k]) for k in range(c)]
            steps.append((copy.deepcopy(m),
                          f"R{row+1} → R{row+1} + ({fmt(neg)}) · R{pr+1}",
                          (row, pr)))
    return steps

# ─── applicazione principale ──────────────────────────────────────────────────
class GaussApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(tr("title"))
        self.configure(bg=BG)
        self.resizable(True, True)
        self.rows = tk.IntVar(master=self, value=3)
        self.cols = tk.IntVar(master=self, value=4)
        self.matrix = []
        self.history = []
        self.hist_lines = []      # (numero, testo | "@chiave") per il listbox
        self._hi_rows = ()
        self.auto_delay = tk.IntVar(master=self, value=600)
        self.cell_vars = []
        self.cell_entries = []
        self._build_ui()
        self._load_example()

    # ── interfaccia ──────────────────────────────────────────────────────────
    def _build_ui(self):
        top = tk.Frame(self, bg=BG, pady=14)
        top.pack(fill="x", padx=24)
        self.title(tr("title"))
        tk.Label(top, text=tr("title"),
                 font=("Segoe UI", 17, "bold"), bg=BG, fg=FG).pack(side="left")
        lang_box = tk.Frame(top, bg=BG)
        lang_box.pack(side="right")
        tk.Label(lang_box, text=tr("lang_label"), font=SANS_SM,
                 bg=BG, fg=FG_DIM).pack(side="left", padx=(0, 6))
        for code in ("it", "en"):
            self._btn(lang_box, code.upper(),
                      lambda c=code: self._set_language(c),
                      dim=(code != LANG)).pack(side="left", padx=2)

        tk.Label(self,
                 text=tr("subtitle"),
                 font=("Segoe UI", 9), bg=BG, fg=FG_DIM
                 ).pack(anchor="w", padx=24, pady=(0, 4))

        ctrl = tk.Frame(self, bg=BG)
        ctrl.pack(fill="x", padx=24, pady=(0, 10))
        tk.Label(ctrl, text=tr("rows_label"), font=SANS_SM, bg=BG, fg=FG_DIM).pack(side="left")
        ttk.Spinbox(ctrl, from_=1, to=8, textvariable=self.rows, width=4,
                    command=self._rebuild_matrix).pack(side="left", padx=(4, 12))
        tk.Label(ctrl, text=tr("cols_label"), font=SANS_SM, bg=BG, fg=FG_DIM).pack(side="left")
        ttk.Spinbox(ctrl, from_=1, to=10, textvariable=self.cols, width=4,
                    command=self._rebuild_matrix).pack(side="left", padx=(4, 18))
        for label, cmd in [
            (tr("btn_new"),    self._new_matrix),
            (tr("btn_ex_num"), self._load_example),
            (tr("btn_ex_sym"), self._load_example_sym),
            (tr("btn_undo"),   self._undo),
        ]:
            self._btn(ctrl, label, cmd, dim=True).pack(side="left", padx=3)

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=24, pady=(0, 12))

        # ── colonna sinistra ──
        left = tk.Frame(body, bg=BG)
        left.pack(side="left", fill="both", expand=True)

        self.matrix_frame = tk.Frame(left, bg=BG)
        self.matrix_frame.pack(fill="x", pady=(0, 10))

        # pannello info
        info_outer = tk.Frame(left, bg=CARD2, highlightbackground=BORDER, highlightthickness=1)
        info_outer.pack(fill="x", pady=(0, 10))
        self.info_labels = {}
        row_info = tk.Frame(info_outer, bg=CARD2)
        row_info.pack(padx=12, pady=7, anchor="w")
        for key, lbl in [("rank", tr("rank")), ("det", tr("det")), ("trace", tr("trace"))]:
            tk.Label(row_info, text=lbl + ":", font=SANS_SM,
                     bg=CARD2, fg=FG_DIM).pack(side="left")
            v = tk.Label(row_info, text="—", font=("Courier New", 11),
                         bg=CARD2, fg=ACCENT, width=20, anchor="w")
            v.pack(side="left", padx=(3, 20))
            self.info_labels[key] = v

        # storico
        tk.Label(left, text=tr("history"), font=SANS_SM,
                 bg=BG, fg=FG_DIM).pack(anchor="w", pady=(0, 4))
        hist_outer = tk.Frame(left, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        hist_outer.pack(fill="both", expand=True)
        sb = tk.Scrollbar(hist_outer, bg=PANEL)
        sb.pack(side="right", fill="y")
        self.hist_box = tk.Listbox(
            hist_outer, font=("Courier New", 11), bg=PANEL, fg=FG_DIM,
            selectbackground=HI_BLUE, selectforeground=FG,
            bd=0, highlightthickness=0, activestyle="none",
            yscrollcommand=sb.set, height=9)
        self.hist_box.pack(fill="both", expand=True, padx=6, pady=6)
        sb.config(command=self.hist_box.yview)

        # ── colonna destra ──
        right = tk.Frame(body, bg=BG, padx=18)
        right.pack(side="right", fill="y")
        self._build_op1(right)
        self._build_op2(right)
        self._build_op3(right)
        self._build_auto(right)

    # ── rendering matrice ─────────────────────────────────────────────────────
    def _rebuild_matrix(self, *_):
        r, c = self.rows.get(), self.cols.get()
        old = [[self.matrix[i][j] if i < len(self.matrix) and j < len(self.matrix[i])
                else ZERO for j in range(c)] for i in range(r)]
        self.matrix = old
        self._render_matrix()
        self._refresh_row_selects()

    def _render_matrix(self, hi_rows=()):
        self._hi_rows = tuple(hi_rows)
        for w in self.matrix_frame.winfo_children():
            w.destroy()
        r = len(self.matrix)
        c = len(self.matrix[0]) if self.matrix else 0
        self.cell_vars, self.cell_entries = [], []

        outer = tk.Frame(self.matrix_frame, bg=BG)
        outer.pack(anchor="w")
        BSIZE = 22 + r * 6

        for side, chars in [("left",  ("⎡","⎢","⎣")),
                             ("right", ("⎤","⎥","⎦"))]:
            bf = tk.Frame(outer, bg=BG)
            bf.pack(side=side)
            tk.Label(bf, text=chars[0], font=("Courier New", BSIZE),
                     bg=BG, fg=FG_DIM).grid(row=0, column=0, sticky="n")
            for i in range(1, r-1):
                tk.Label(bf, text=chars[1], font=("Courier New", BSIZE),
                         bg=BG, fg=FG_DIM).grid(row=i, column=0)
            if r > 1:
                tk.Label(bf, text=chars[2], font=("Courier New", BSIZE),
                         bg=BG, fg=FG_DIM).grid(row=r-1, column=0, sticky="s")

        gf = tk.Frame(outer, bg=BG)
        gf.pack(side="left", padx=4)

        hi_list = list(hi_rows)
        for i in range(r):
            rv, re_ = [], []
            for j in range(c):
                var = tk.StringVar(master=self, value=fmt(self.matrix[i][j]))
                if hi_list and i == hi_list[0]:
                    bg = HI_BLUE
                elif len(hi_list) > 1 and i == hi_list[1]:
                    bg = HI_GREEN
                else:
                    bg = ENTRY_BG
                e = tk.Entry(gf, textvariable=var, width=14,
                             font=MONO, bg=bg, fg=FG,
                             insertbackground=FG, relief="flat",
                             highlightthickness=1, highlightbackground=BORDER,
                             highlightcolor=ACCENT, justify="center")
                e.grid(row=i, column=j, padx=3, pady=3, ipady=5)
                rv.append(var); re_.append(e)
            self.cell_vars.append(rv)
            self.cell_entries.append(re_)

        lf = tk.Frame(outer, bg=BG)
        lf.pack(side="left", padx=(6, 0))
        for i in range(r):
            col = ACCENT if i in hi_list else FG_DIM
            tk.Label(lf, text=f"R{i+1}", font=("Courier New", 10),
                     bg=BG, fg=col).grid(row=i, column=0, pady=3, sticky="w")

        self._update_info()

    def _update_info(self):
        try:
            M = Matrix([[simplify(v) for v in row] for row in self.matrix])
            r, c = M.shape
            self.info_labels["rank"].config(text=str(M.rank()))
            if r == c:
                self.info_labels["det"].config(text=fmt(M.det()))
                self.info_labels["trace"].config(text=fmt(M.trace()))
            else:
                self.info_labels["det"].config(text=tr("not_square"))
                self.info_labels["trace"].config(text=tr("not_square"))
        except Exception:
            for k in self.info_labels:
                self.info_labels[k].config(text="—")

    # ── lettura/scrittura celle ───────────────────────────────────────────────
    def _read_matrix(self):
        r = len(self.cell_vars)
        c = len(self.cell_vars[0]) if self.cell_vars else 0
        m = []
        for i in range(r):
            row = []
            for j in range(c):
                try:
                    row.append(parse_expr(self.cell_vars[i][j].get()))
                except Exception as ex:
                    messagebox.showerror(
                        tr("input_err_title"),
                        tr("input_err_body", i=i+1, j=j+1, ex=ex))
                    return False
            m.append(row)
        self.matrix = m
        return True

    def _write_matrix(self, m):
        for i, row in enumerate(m):
            for j, val in enumerate(row):
                self.cell_vars[i][j].set(fmt(val))

    # ── costruzione card ──────────────────────────────────────────────────────
    def _card(self, parent, title, formula):
        f = tk.Frame(parent, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        f.pack(fill="x", pady=(0, 10), ipady=8)
        tk.Label(f, text=title, font=SANS_LG, bg=CARD, fg=FG
                 ).pack(anchor="w", padx=14, pady=(10, 0))
        tk.Label(f, text=formula, font=("Courier New", 11), bg=CARD, fg=ACCENT
                 ).pack(anchor="w", padx=14, pady=(2, 6))
        return f

    def _row_select(self, parent, label):
        row = tk.Frame(parent, bg=CARD)
        row.pack(fill="x", padx=14, pady=2)
        tk.Label(row, text=label, width=5, anchor="w",
                 font=SANS_SM, bg=CARD, fg=FG_DIM).pack(side="left")
        cb = ttk.Combobox(row, state="readonly", width=8)
        cb.pack(side="left")
        return cb

    def _num_entry(self, parent, label, default="2"):
        row = tk.Frame(parent, bg=CARD)
        row.pack(fill="x", padx=14, pady=2)
        tk.Label(row, text=label, width=5, anchor="w",
                 font=SANS_SM, bg=CARD, fg=FG_DIM).pack(side="left")
        e = tk.Entry(row, font=SANS, width=16, bg=ENTRY_BG, fg=FG,
                     insertbackground=FG, relief="flat",
                     highlightthickness=1, highlightbackground=BORDER,
                     highlightcolor=ACCENT)
        e.insert(0, default)
        e.pack(side="left")
        return e

    def _btn(self, parent, text, cmd, dim=False, bg=None):
        bg_ = bg if bg else (PANEL if dim else ACCENT)
        fg = FG_DIM if dim else FG
        return tk.Button(parent, text=text, command=cmd,
                         font=SANS_SM, bg=bg_, fg=fg,
                         activebackground=BORDER, activeforeground=FG,
                         relief="flat", padx=10, pady=5, cursor="hand2",
                         bd=0, highlightthickness=1, highlightbackground=BORDER)

    def _err_label(self, parent):
        lbl = tk.Label(parent, text="", font=SANS_SM, bg=CARD, fg=ERR)
        lbl.pack(anchor="w", padx=14, pady=(0, 4))
        return lbl

    def _build_op1(self, parent):
        card = self._card(parent, tr("op1_title"), "Rᵢ  ↔  Rⱼ")
        self.op1_i = self._row_select(card, "Rᵢ :")
        self.op1_j = self._row_select(card, "Rⱼ :")
        self._btn(card, tr("op1_btn"), self._apply_swap
                  ).pack(fill="x", padx=14, pady=(6, 2))
        self.err1 = self._err_label(card)

    def _build_op2(self, parent):
        card = self._card(parent, tr("op2_title"), "Rᵢ  →  k · Rᵢ")
        self.op2_i = self._row_select(card, "Rᵢ :")
        self.op2_k = self._num_entry(card, "k  :", "2")
        self._btn(card, tr("op2_btn"), self._apply_scale
                  ).pack(fill="x", padx=14, pady=(6, 2))
        self.err2 = self._err_label(card)

    def _build_op3(self, parent):
        card = self._card(parent, tr("op3_title"), "Rᵢ  →  Rᵢ + k · Rⱼ")
        self.op3_i = self._row_select(card, "Rᵢ :")
        self.op3_j = self._row_select(card, "Rⱼ :")
        self.op3_k = self._num_entry(card, "k  :", "1")
        self._btn(card, tr("op3_btn"), self._apply_add
                  ).pack(fill="x", padx=14, pady=(6, 2))
        self.err3 = self._err_label(card)

    def _build_auto(self, parent):
        card = self._card(parent, tr("auto_card"), tr("auto_sub"))
        self._btn(card, tr("btn_gauss"),
                  self._auto_gauss, bg="#3a3a60"
                  ).pack(fill="x", padx=14, pady=(4, 4))
        self._btn(card, tr("btn_gj"),
                  self._auto_gauss_jordan, bg="#2a4a3a"
                  ).pack(fill="x", padx=14, pady=(0, 8))
        # slider velocità
        speed_row = tk.Frame(card, bg=CARD)
        speed_row.pack(fill="x", padx=14, pady=(0, 10))
        tk.Label(speed_row, text=tr("speed"), font=SANS_SM,
                 bg=CARD, fg=FG_DIM).pack(side="left")
        tk.Scale(speed_row, from_=100, to=2000, resolution=100,
                 variable=self.auto_delay, orient="horizontal",
                 bg=CARD, fg=FG, troughcolor=ENTRY_BG, highlightthickness=0,
                 sliderrelief="flat", length=110, showvalue=False
                 ).pack(side="left", padx=6)
        self.delay_lbl = tk.Label(speed_row, text=f"{self.auto_delay.get()} ms",
                                  font=SANS_SM, bg=CARD, fg=FG_DIM, width=7)
        self.delay_lbl.pack(side="left")
        self._delay_trace = self.auto_delay.trace_add(
            "write",
            lambda *_: self.delay_lbl.config(text=f"{self.auto_delay.get()} ms"))

    # ── selezione righe ───────────────────────────────────────────────────────
    def _refresh_row_selects(self):
        r = len(self.matrix)
        values = [f"R{i+1}" for i in range(r)]
        for cb in (self.op1_i, self.op1_j, self.op2_i, self.op3_i, self.op3_j):
            cb["values"] = values
            cb.set(values[0] if values else "")
        if r > 1:
            self.op1_j.set(values[1])
            self.op3_j.set(values[1])

    def _get_row(self, cb):
        s = cb.get()
        return int(s[1:]) - 1 if s else 0

    # ── operazioni manuali ────────────────────────────────────────────────────
    def _apply_swap(self):
        self.err1.config(text="")
        if not self._read_matrix(): return
        i, j = self._get_row(self.op1_i), self._get_row(self.op1_j)
        if i == j:
            self.err1.config(text=tr("err_rows_diff")); return
        snap = copy.deepcopy(self.matrix)
        self.matrix[i], self.matrix[j] = self.matrix[j], self.matrix[i]
        self._commit(snap, f"R{i+1} ↔ R{j+1}", hi_rows=(i, j))

    def _apply_scale(self):
        self.err2.config(text="")
        if not self._read_matrix(): return
        i = self._get_row(self.op2_i)
        try:
            k = parse_expr(self.op2_k.get())
        except Exception as ex:
            self.err2.config(text=str(ex)[:60]); return
        if simplify(k) == ZERO:
            self.err2.config(text=tr("err_k_zero")); return
        snap = copy.deepcopy(self.matrix)
        self.matrix[i] = [simplify(k * v) for v in self.matrix[i]]
        self._commit(snap, f"R{i+1} → ({fmt(k)}) · R{i+1}", hi_rows=(i,))

    def _apply_add(self):
        self.err3.config(text="")
        if not self._read_matrix(): return
        i, j = self._get_row(self.op3_i), self._get_row(self.op3_j)
        try:
            k = parse_expr(self.op3_k.get())
        except Exception as ex:
            self.err3.config(text=str(ex)[:60]); return
        if simplify(k) == ZERO:
            self.err3.config(text=tr("err_k_noop")); return
        snap = copy.deepcopy(self.matrix)
        cols = len(self.matrix[i])
        self.matrix[i] = [simplify(self.matrix[i][col] + k * self.matrix[j][col])
                          for col in range(cols)]
        self._commit(snap, f"R{i+1} → R{i+1} + ({fmt(k)}) · R{j+1}",
                     hi_rows=(i, j))

    # ── riduzione automatica ──────────────────────────────────────────────────
    def _run_steps(self, steps):
        if not steps:
            messagebox.showinfo(tr("auto_title"), tr("already_reduced")); return
        snap0 = copy.deepcopy(self.matrix)
        self.history.append((snap0, "[auto]"))
        self._hist_add(len(self.history), "@auto_start")

        def _next(idx):
            if idx >= len(steps): return
            new_m, op_text, hi = steps[idx]
            self.matrix = new_m
            self._render_matrix(hi_rows=hi)
            self._write_matrix(self.matrix)
            self._hist_add(len(self.history) + idx + 1, op_text)
            self.after(self.auto_delay.get(), lambda: _next(idx + 1))

        _next(0)

    def _auto_gauss(self):
        if not self._read_matrix(): return
        self._run_steps(gauss_steps(copy.deepcopy(self.matrix)))

    def _auto_gauss_jordan(self):
        if not self._read_matrix(): return
        self._run_steps(gauss_jordan_steps(copy.deepcopy(self.matrix)))

    # ── storico testuale (rigenerabile al cambio lingua) ──────────────────────
    @staticmethod
    def _hist_fmt(n, text):
        if text.startswith("@"):              # chiave di traduzione
            text = tr(text[1:])
        return f"  {n:02d}.  {text}"

    def _hist_add(self, n, text):
        self.hist_lines.append((n, text))
        self.hist_box.insert(0, self._hist_fmt(n, text))
        self.hist_box.see(0)

    def _hist_clear(self):
        self.hist_lines.clear()
        self.hist_box.delete(0, tk.END)

    def _hist_render(self):
        self.hist_box.delete(0, tk.END)
        for n, text in self.hist_lines:
            self.hist_box.insert(0, self._hist_fmt(n, text))

    # ── cambio lingua ─────────────────────────────────────────────────────────
    def _set_language(self, code):
        global LANG
        if code == LANG:
            return
        combos = (self.op1_i, self.op1_j, self.op2_i, self.op3_i, self.op3_j)
        # stato modificabile dall'utente: testo grezzo delle celle, k, selezioni
        raw = [[v.get() for v in row] for row in self.cell_vars]
        k2, k3 = self.op2_k.get(), self.op3_k.get()
        sel = [cb.get() for cb in combos]
        try:
            self.auto_delay.trace_remove("write", self._delay_trace)
        except Exception:
            pass

        LANG = code
        for w in self.winfo_children():
            w.destroy()
        self._build_ui()
        self._render_matrix(hi_rows=self._hi_rows)
        self._refresh_row_selects()

        combos = (self.op1_i, self.op1_j, self.op2_i, self.op3_i, self.op3_j)
        for cb, val in zip(combos, sel):
            if val in cb["values"]:
                cb.set(val)
        for i, row in enumerate(raw):
            for j, txt in enumerate(row):
                self.cell_vars[i][j].set(txt)
        for entry, txt in ((self.op2_k, k2), (self.op3_k, k3)):
            entry.delete(0, tk.END)
            entry.insert(0, txt)
        self._hist_render()

    # ── commit / annulla ──────────────────────────────────────────────────────
    def _commit(self, snapshot, op_text, hi_rows=()):
        self.history.append((snapshot, op_text))
        self._render_matrix(hi_rows=hi_rows)
        self._write_matrix(self.matrix)
        self._hist_add(len(self.history), op_text)

    def _undo(self):
        if not self.history:
            messagebox.showinfo(tr("undo_title"), tr("nothing_to_undo")); return
        snap, _ = self.history.pop()
        self.matrix = snap
        self._render_matrix()
        self._write_matrix(self.matrix)
        if self.hist_lines:
            self.hist_lines.pop()
            self.hist_box.delete(0)

    # ── esempi ────────────────────────────────────────────────────────────────
    def _new_matrix(self):
        r, c = self.rows.get(), self.cols.get()
        self.matrix = [[ZERO] * c for _ in range(r)]
        self.history.clear(); self._hist_clear()
        self._render_matrix(); self._refresh_row_selects()

    def _load_example(self):
        self.rows.set(3); self.cols.set(4)
        S = sympy.Integer
        self.matrix = [
            [S(2),  S(1),  S(-1), S(8)],
            [S(-3), S(-1), S(2),  S(-11)],
            [S(-2), S(1),  S(2),  S(-3)],
        ]
        self.history.clear(); self._hist_clear()
        self._render_matrix(); self._refresh_row_selects()

    def _load_example_sym(self):
        """Esempio con parametro simbolico 'a' (il blocco 3×3 ha det = a^3 - 2a)."""
        self.rows.set(3); self.cols.set(4)
        a = sympy.Symbol("a")
        S = sympy.Integer
        self.matrix = [
            [a,    S(1),  S(0),  S(1)],
            [S(1), a,     S(1),  S(0)],
            [S(0), S(1),  a,     S(1)],
        ]
        self.history.clear(); self._hist_clear()
        self._render_matrix(); self._refresh_row_selects()


# ─── avvio ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = GaussApp()
    style = ttk.Style(app)
    style.theme_use("default")
    style.configure("TCombobox",
                    fieldbackground=ENTRY_BG, background=PANEL,
                    foreground=FG, selectbackground=HI_BLUE,
                    selectforeground=FG, arrowcolor=FG_DIM)
    style.configure("TSpinbox",
                    fieldbackground=ENTRY_BG, background=PANEL,
                    foreground=FG, arrowcolor=FG_DIM)
    style.map("TCombobox", fieldbackground=[("readonly", ENTRY_BG)],
              selectbackground=[("readonly", HI_BLUE)])
    app.geometry("1150x750")
    app.mainloop()
