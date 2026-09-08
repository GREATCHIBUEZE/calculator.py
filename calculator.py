import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
import math


DEFAULT_THEME = {
    "bg":          "#1a1a2e",
    "display_bg":  "#16213e",
    "display_fg":  "#e0e0ff",
    "btn_num_bg":  "#0f3460",
    "btn_num_fg":  "#e0e0ff",
    "btn_op_bg":   "#533483",
    "btn_op_fg":   "#ffffff",
    "btn_eq_bg":   "#e94560",
    "btn_eq_fg":   "#ffffff",
    "btn_clr_bg":  "#2d2d44",
    "btn_clr_fg":  "#ff6b6b",
    "btn_hover":   "#7b52ab",
    "font_display": ("Courier New", 28, "bold"),
    "font_btn":     ("Courier New", 16, "bold"),
    "font_small":   ("Courier New", 10),
}

theme = DEFAULT_THEME.copy()


class Calculator:
    def __init__(self):
        self.reset()

    def reset(self):
        self.current   = "0"
        self.stored    = None
        self.operator  = None
        self.new_num   = True
        self.history   = []

    def input_digit(self, digit):
        if self.new_num:
            self.current  = str(digit)
            self.new_num  = False
        else:
            if self.current == "0" and digit != ".":
                self.current = str(digit)
            elif digit == "." and "." in self.current:
                return
            else:
                self.current += str(digit)

    def set_operator(self, op):
        if self.stored is not None and not self.new_num:
            self.calculate()
        self.stored   = float(self.current)
        self.operator = op
        self.new_num  = True

    def calculate(self):
        if self.stored is None or self.operator is None:
            return
        b = float(self.current)
        a = self.stored
        op = self.operator
        try:
            if op == "+":   result = a + b
            elif op == "−": result = a - b
            elif op == "×": result = a * b
            elif op == "÷":
                if b == 0:
                    messagebox.showerror("Error", "Cannot divide by zero!")
                    self.reset(); return
                result = a / b
            elif op == "%": result = a % b
            elif op == "^": result = a ** b
            else: return
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.reset(); return

        expr = f"{self._fmt(a)} {op} {self._fmt(b)} = {self._fmt(result)}"
        self.history.append(expr)
        self.current  = self._fmt(result)
        self.stored   = None
        self.operator = None
        self.new_num  = True

    def toggle_sign(self):
        val = float(self.current)
        self.current = self._fmt(-val)

    def sqrt(self):
        val = float(self.current)
        if val < 0:
            messagebox.showerror("Error", "Cannot √ a negative number")
            return
        self.current = self._fmt(math.sqrt(val))
        self.new_num = True

    def backspace(self):
        if not self.new_num and len(self.current) > 1:
            self.current = self.current[:-1]
        else:
            self.current = "0"
            self.new_num = True

    @staticmethod
    def _fmt(val):
        if val == int(val):
            return str(int(val))
        s = f"{val:.10f}".rstrip("0")
        return s


#  GUI
class CalcApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.calc = Calculator()
        self.title("🧮  Python Calculator")
        self.resizable(False, False)
        self._build_ui()
        self._apply_theme()

    # ── Layout ────────────────────────────────
    def _build_ui(self):
        bar = tk.Frame(self, pady=4)
        bar.pack(fill="x")
        tk.Button(bar, text="🎨  Customize Theme",
                  command=self._open_theme_editor,
                  relief="flat", cursor="hand2",
                  font=theme["font_small"]).pack(side="right", padx=8)

        self.expr_var = tk.StringVar(value="")
        self.expr_lbl = tk.Label(self, textvariable=self.expr_var,
                                 anchor="e", padx=12, height=1)
        self.expr_lbl.pack(fill="x")

        self.display_var = tk.StringVar(value="0")
        self.display = tk.Entry(self, textvariable=self.display_var,
                                justify="right", state="readonly",
                                bd=0, relief="flat", readonlybackground="#16213e")
        self.display.pack(fill="x", ipady=12, padx=8)

        btn_frame = tk.Frame(self)
        btn_frame.pack(padx=8, pady=8)


        buttons = [
    
            ("C",   0, 0, "clr"),  ("⌫",  1, 0, "clr"),
            ("%",   2, 0, "op"),   ("÷",  3, 0, "op"),
            # Row 1
            ("7",   0, 1, "num"),  ("8",  1, 1, "num"),
            ("9",   2, 1, "num"),  ("×",  3, 1, "op"),
            # Row 2
            ("4",   0, 2, "num"),  ("5",  1, 2, "num"),
            ("6",   2, 2, "num"),  ("−",  3, 2, "op"),
            # Row 3
            ("1",   0, 3, "num"),  ("2",  1, 3, "num"),
            ("3",   2, 3, "num"),  ("+",  3, 3, "op"),
            # Row 4
            ("±",   0, 4, "clr"),  ("0",  1, 4, "num"),
            (".",   2, 4, "num"),  ("=",  3, 4, "eq"),
            # Row 5 – extras
            ("√",   0, 5, "op"),   ("x²", 1, 5, "op"),
            ("^",   2, 5, "op"),   ("H",  3, 5, "clr"),
        ]

        self.buttons = {}
        for (lbl, col, row, kind) in buttons:
            b = tk.Button(btn_frame, text=lbl, width=5, height=2,
                          relief="flat", cursor="hand2",
                          font=theme["font_btn"],
                          command=lambda l=lbl: self._press(l))
            b.grid(row=row, column=col, padx=4, pady=4)
            self.buttons[lbl] = (b, kind)

            b.bind("<Enter>", lambda e, w=b: w.config(bg=theme["btn_hover"]))
            b.bind("<Leave>", lambda e, w=b, k=kind: self._reset_btn_color(w, k))

        self.bind("<Key>", self._key_press)

    def _press(self, label):
        c = self.calc
        if   label in "0123456789": c.input_digit(label)
        elif label == ".":          c.input_digit(".")
        elif label in ("+", "−", "×", "÷", "%", "^"):
            c.set_operator(label)
        elif label == "=":          c.calculate()
        elif label == "C":          c.reset()
        elif label == "⌫":         c.backspace()
        elif label == "±":          c.toggle_sign()
        elif label == "√":          c.sqrt()
        elif label == "x²":
            c.input_digit(c.current)
            c.set_operator("^")
            c.input_digit("2")
            c.calculate()
        elif label == "H":          self._show_history()
        self._refresh()

    def _key_press(self, event):
        k = event.char
        key_map = {
            "0":"0","1":"1","2":"2","3":"3","4":"4",
            "5":"5","6":"6","7":"7","8":"8","9":"9",
            ".":".", "+":"+", "-":"−", "*":"×", "/":"÷",
            "%":"%", "^":"^", "\r":"=", "\x08":"⌫",
        }
        if k in key_map:
            self._press(key_map[k])
        elif event.keysym == "Escape":
            self._press("C")

    def _refresh(self):
        c = self.calc
        self.display_var.set(c.current)
        if c.stored is not None and c.operator:
            self.expr_var.set(f"{c._fmt(c.stored)} {c.operator}")
        else:
            self.expr_var.set("")
    
    def _apply_theme(self):
        t = theme
        self.config(bg=t["bg"])
        for widget in self.winfo_children():
            self._style_widget(widget, t)

        for lbl, (btn, kind) in self.buttons.items():
            if   kind == "num": bg, fg = t["btn_num_bg"], t["btn_num_fg"]
            elif kind == "op":  bg, fg = t["btn_op_bg"],  t["btn_op_fg"]
            elif kind == "eq":  bg, fg = t["btn_eq_bg"],  t["btn_eq_fg"]
            else:               bg, fg = t["btn_clr_bg"], t["btn_clr_fg"]
            btn.config(bg=bg, fg=fg, activebackground=t["btn_hover"],
                       activeforeground=fg, font=t["font_btn"])

        self.display.config(
            font=t["font_display"],
            fg=t["display_fg"],
            readonlybackground=t["display_bg"],
            insertbackground=t["display_fg"])
        self.expr_lbl.config(
            bg=t["display_bg"], fg=t["btn_op_fg"],
            font=t["font_small"])

    def _style_widget(self, w, t):
        try: w.config(bg=t["bg"])
        except: pass
        for child in w.winfo_children():
            self._style_widget(child, t)

    def _reset_btn_color(self, btn, kind):
        t = theme
        if   kind == "num": bg = t["btn_num_bg"]
        elif kind == "op":  bg = t["btn_op_bg"]
        elif kind == "eq":  bg = t["btn_eq_bg"]
        else:               bg = t["btn_clr_bg"]
        btn.config(bg=bg)


    def _open_theme_editor(self):
        win = tk.Toplevel(self)
        win.title("🎨 Theme Editor")
        win.resizable(False, False)
        win.config(bg=theme["bg"])

        color_keys = [
            ("bg",         "Window Background"),
            ("display_bg", "Display Background"),
            ("display_fg", "Display Text"),
            ("btn_num_bg", "Number Button BG"),
            ("btn_num_fg", "Number Button Text"),
            ("btn_op_bg",  "Operator Button BG"),
            ("btn_op_fg",  "Operator Button Text"),
            ("btn_eq_bg",  "Equals Button BG"),
            ("btn_eq_fg",  "Equals Button Text"),
            ("btn_clr_bg", "Clear Button BG"),
            ("btn_clr_fg", "Clear Button Text"),
            ("btn_hover",  "Hover Highlight"),
        ]

        previews = {}

        for i, (key, label) in enumerate(color_keys):
            tk.Label(win, text=label, bg=theme["bg"], fg="#ccc",
                     font=("Courier New", 11)).grid(
                         row=i, column=0, sticky="w", padx=12, pady=3)
            preview = tk.Label(win, width=4, bg=theme[key], relief="groove")
            preview.grid(row=i, column=1, padx=4)
            previews[key] = preview

            def pick(k=key, p=preview):
                color = colorchooser.askcolor(color=theme[k],
                                              title=f"Choose color for {k}")
                if color[1]:
                    theme[k] = color[1]
                    p.config(bg=color[1])

            tk.Button(win, text="Pick", command=pick,
                      bg=theme["btn_op_bg"], fg="#fff",
                      relief="flat", font=("Courier New", 10),
                      cursor="hand2").grid(row=i, column=2, padx=6, pady=3)

        presets_frame = tk.LabelFrame(win, text=" Presets ",
                                      bg=theme["bg"], fg="#aaa",
                                      font=("Courier New", 10))
        presets_frame.grid(row=len(color_keys), column=0,
                           columnspan=3, padx=12, pady=8, sticky="ew")

        presets = {
            "🌙 Dark Blue (Default)": DEFAULT_THEME.copy(),
            "☀️  Light Mint": {
                "bg": "#f0faf4", "display_bg": "#e0f5ea",
                "display_fg": "#1a3c2a",
                "btn_num_bg": "#b2dfdb", "btn_num_fg": "#1a3c2a",
                "btn_op_bg":  "#4caf7d", "btn_op_fg": "#ffffff",
                "btn_eq_bg":  "#00796b", "btn_eq_fg": "#ffffff",
                "btn_clr_bg": "#cfd8dc", "btn_clr_fg": "#b71c1c",
                "btn_hover":  "#80cbc4",
                "font_display": ("Courier New", 28, "bold"),
                "font_btn":     ("Courier New", 16, "bold"),
                "font_small":   ("Courier New", 10),
            },
            "🔥 Fire Red": {
                "bg": "#1c0a00", "display_bg": "#2d1000",
                "display_fg": "#ffccaa",
                "btn_num_bg": "#3d1a00", "btn_num_fg": "#ffccaa",
                "btn_op_bg":  "#b34700", "btn_op_fg": "#fff",
                "btn_eq_bg":  "#ff3300", "btn_eq_fg": "#fff",
                "btn_clr_bg": "#2a1200", "btn_clr_fg": "#ff8800",
                "btn_hover":  "#c45c00",
                "font_display": ("Courier New", 28, "bold"),
                "font_btn":     ("Courier New", 16, "bold"),
                "font_small":   ("Courier New", 10),
            },
        }

        for name, preset in presets.items():
            def apply_preset(p=preset, pv=previews):
                theme.update(p)
                for k, prev in pv.items():
                    prev.config(bg=theme[k])
                self._apply_theme()

            tk.Button(presets_frame, text=name, command=apply_preset,
                      bg=theme["btn_op_bg"], fg="#fff", relief="flat",
                      font=("Courier New", 10), cursor="hand2",
                      padx=8, pady=4).pack(side="left", padx=6, pady=6)


        def apply_and_close():
            self._apply_theme()
            win.destroy()

        tk.Button(win, text="✅  Apply & Close",
                  command=apply_and_close,
                  bg=theme["btn_eq_bg"], fg=theme["btn_eq_fg"],
                  relief="flat", font=("Courier New", 12, "bold"),
                  cursor="hand2", pady=6).grid(
                      row=len(color_keys)+1, column=0, columnspan=3,
                      padx=12, pady=10, sticky="ew")

    def _show_history(self):
        win = tk.Toplevel(self)
        win.title("📜 Calculation History")
        win.config(bg=theme["bg"])
        win.resizable(False, False)

        tk.Label(win, text="History", bg=theme["bg"],
                 fg=theme["display_fg"],
                 font=("Courier New", 14, "bold")).pack(pady=(10, 4))

        if not self.calc.history:
            tk.Label(win, text="No calculations yet.",
                     bg=theme["bg"], fg="#888",
                     font=("Courier New", 11)).pack(pady=20, padx=20)
        else:
            listbox = tk.Listbox(win, bg=theme["display_bg"],
                                 fg=theme["display_fg"],
                                 font=("Courier New", 12),
                                 width=36, height=min(15, len(self.calc.history)),
                                 bd=0, relief="flat", selectbackground=theme["btn_hover"])
            listbox.pack(padx=14, pady=10)
            for item in reversed(self.calc.history):
                listbox.insert("end", "  " + item)

        def clear_h():
            self.calc.history.clear()
            win.destroy()

        tk.Button(win, text="🗑  Clear History",
                  command=clear_h,
                  bg=theme["btn_clr_bg"], fg=theme["btn_clr_fg"],
                  relief="flat", font=("Courier New", 11),
                  cursor="hand2").pack(pady=(0, 10))


#  ENTRY POINT
if __name__ == "__main__":
    app = CalcApp()
    app.mainloop()
