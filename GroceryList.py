import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime

# ── Paleta de cores ──────────────────────────────────────────────────────────
BG        = "#0f0f13"
PANEL     = "#1a1a24"
CARD      = "#22222f"
ACCENT    = "#6c63ff"
ACCENT2   = "#ff6584"
SUCCESS   = "#43e97b"
WARNING   = "#f7971e"
TEXT      = "#e8e8f0"
TEXT_DIM  = "#7a7a99"
BORDER    = "#2e2e45"
WHITE     = "#ffffff"

FONT_TITLE  = ("Segoe UI", 22, "bold")
FONT_HEAD   = ("Segoe UI", 13, "bold")
FONT_BODY   = ("Segoe UI", 11)
FONT_SMALL  = ("Segoe UI", 9)
FONT_MONO   = ("Consolas", 12, "bold")
FONT_BIG    = ("Segoe UI", 28, "bold")


class ListaCompras:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🛒 Lista de Compras Inteligente")
        self.root.configure(bg=BG)
        self.root.minsize(820, 620)
        self.root.geometry("920x680")

        self.orcamento   = tk.DoubleVar(value=0.0)
        self.itens: list = []          # [{"nome", "preco", "qtd"}]
        self.arquivo_atual = None

        self._build_ui()
        self._atualizar_resumo()

    # ── Construção da UI ─────────────────────────────────────────────────────

    def _build_ui(self):
        # Cabeçalho
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=24, pady=(20, 0))

        tk.Label(header, text="🛒 Lista de Compras", font=FONT_TITLE,
                 bg=BG, fg=WHITE).pack(side="left")

        # Botões de arquivo
        btn_frame = tk.Frame(header, bg=BG)
        btn_frame.pack(side="right")
        self._btn(btn_frame, "💾 Salvar", self._salvar, ACCENT).pack(side="left", padx=4)
        self._btn(btn_frame, "📂 Abrir",  self._abrir,  PANEL ).pack(side="left", padx=4)
        self._btn(btn_frame, "🆕 Nova",   self._nova_lista, PANEL).pack(side="left", padx=4)

        sep = tk.Frame(self.root, bg=BORDER, height=1)
        sep.pack(fill="x", padx=24, pady=12)

        # Corpo principal
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=24, pady=0)

        # Coluna esquerda — resumo + formulário
        left = tk.Frame(body, bg=BG, width=280)
        left.pack(side="left", fill="y", padx=(0, 16))
        left.pack_propagate(False)

        self._build_resumo(left)
        self._build_form(left)

        # Coluna direita — lista de itens
        right = tk.Frame(body, bg=BG)
        right.pack(side="left", fill="both", expand=True)
        self._build_lista(right)

    # ── Painel de resumo ─────────────────────────────────────────────────────

    def _build_resumo(self, parent):
        card = tk.Frame(parent, bg=PANEL, padx=16, pady=16)
        card.pack(fill="x", pady=(0, 12))
        self._round_border(card)

        tk.Label(card, text="ORÇAMENTO TOTAL", font=FONT_SMALL,
                 bg=PANEL, fg=TEXT_DIM).pack(anchor="w")

        row = tk.Frame(card, bg=PANEL)
        row.pack(fill="x", pady=(4, 8))

        tk.Label(row, text="R$", font=("Segoe UI", 14), bg=PANEL, fg=TEXT_DIM).pack(side="left")
        self.entry_orc = tk.Entry(row, font=FONT_MONO, bg=CARD, fg=WHITE,
                                  insertbackground=WHITE, relief="flat",
                                  bd=0, width=10)
        self.entry_orc.pack(side="left", padx=6)
        self.entry_orc.insert(0, "0.00")
        self.entry_orc.bind("<FocusOut>", self._atualizar_orcamento)
        self.entry_orc.bind("<Return>",   self._atualizar_orcamento)

        # Barra de progresso
        tk.Label(card, text="CONSUMIDO", font=FONT_SMALL,
                 bg=PANEL, fg=TEXT_DIM).pack(anchor="w")

        self.canvas_bar = tk.Canvas(card, height=10, bg=CARD,
                                    highlightthickness=0)
        self.canvas_bar.pack(fill="x", pady=(4, 8))

        # Valores
        vals = tk.Frame(card, bg=PANEL)
        vals.pack(fill="x")
        vals.columnconfigure(0, weight=1)
        vals.columnconfigure(1, weight=1)

        tk.Label(vals, text="Gasto", font=FONT_SMALL,
                 bg=PANEL, fg=TEXT_DIM).grid(row=0, column=0, sticky="w")
        tk.Label(vals, text="Restante", font=FONT_SMALL,
                 bg=PANEL, fg=TEXT_DIM).grid(row=0, column=1, sticky="e")

        self.lbl_gasto    = tk.Label(vals, text="R$ 0,00", font=FONT_HEAD,
                                     bg=PANEL, fg=ACCENT2)
        self.lbl_gasto.grid(row=1, column=0, sticky="w")

        self.lbl_restante = tk.Label(vals, text="R$ 0,00", font=FONT_HEAD,
                                     bg=PANEL, fg=SUCCESS)
        self.lbl_restante.grid(row=1, column=1, sticky="e")

        # Total de itens
        sep = tk.Frame(card, bg=BORDER, height=1)
        sep.pack(fill="x", pady=10)

        self.lbl_itens = tk.Label(card, text="0 itens  •  0 unidades",
                                  font=FONT_SMALL, bg=PANEL, fg=TEXT_DIM)
        self.lbl_itens.pack(anchor="center")

    # ── Formulário de adição ─────────────────────────────────────────────────

    def _build_form(self, parent):
        card = tk.Frame(parent, bg=PANEL, padx=16, pady=16)
        card.pack(fill="x")

        tk.Label(card, text="ADICIONAR ITEM", font=FONT_SMALL,
                 bg=PANEL, fg=TEXT_DIM).pack(anchor="w", pady=(0, 10))

        # Nome
        tk.Label(card, text="Nome do produto", font=FONT_SMALL,
                 bg=PANEL, fg=TEXT_DIM).pack(anchor="w")
        self.entry_nome = self._entrada(card)
        self.entry_nome.pack(fill="x", pady=(2, 8))

        # Preço e quantidade na mesma linha
        row = tk.Frame(card, bg=PANEL)
        row.pack(fill="x", pady=(0, 8))
        row.columnconfigure(0, weight=3)
        row.columnconfigure(1, weight=1)

        col_preco = tk.Frame(row, bg=PANEL)
        col_preco.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        tk.Label(col_preco, text="Preço (R$)", font=FONT_SMALL,
                 bg=PANEL, fg=TEXT_DIM).pack(anchor="w")
        self.entry_preco = self._entrada(col_preco)
        self.entry_preco.pack(fill="x", pady=(2, 0))

        col_qtd = tk.Frame(row, bg=PANEL)
        col_qtd.grid(row=0, column=1, sticky="ew")
        tk.Label(col_qtd, text="Qtd.", font=FONT_SMALL,
                 bg=PANEL, fg=TEXT_DIM).pack(anchor="w")
        self.entry_qtd = self._entrada(col_qtd)
        self.entry_qtd.insert(0, "1")
        self.entry_qtd.pack(fill="x", pady=(2, 0))

        self._btn(card, "+ Adicionar Item", self._adicionar_item,
                  ACCENT, full=True).pack(fill="x", pady=(6, 0))

        # Bind Enter no nome para adicionar
        self.entry_nome.bind("<Return>",  lambda _: self.entry_preco.focus())
        self.entry_preco.bind("<Return>", lambda _: self.entry_qtd.focus())
        self.entry_qtd.bind("<Return>",   lambda _: self._adicionar_item())

    # ── Lista de itens ────────────────────────────────────────────────────────

    def _build_lista(self, parent):
        header = tk.Frame(parent, bg=BG)
        header.pack(fill="x", pady=(0, 8))

        tk.Label(header, text="ITENS DA LISTA", font=FONT_SMALL,
                 bg=BG, fg=TEXT_DIM).pack(side="left")

        self._btn(header, "🗑 Limpar Tudo", self._limpar_tudo,
                  ACCENT2).pack(side="right")

        # Container com scroll
        container = tk.Frame(parent, bg=PANEL, bd=0)
        container.pack(fill="both", expand=True)

        self.canvas_lista = tk.Canvas(container, bg=PANEL,
                                      highlightthickness=0, bd=0)
        scroll = tk.Scrollbar(container, orient="vertical",
                              command=self.canvas_lista.yview)
        self.canvas_lista.configure(yscrollcommand=scroll.set)

        scroll.pack(side="right", fill="y")
        self.canvas_lista.pack(side="left", fill="both", expand=True)

        self.frame_itens = tk.Frame(self.canvas_lista, bg=PANEL)
        self.canvas_lista.create_window((0, 0), window=self.frame_itens,
                                        anchor="nw", tags="inner")

        self.frame_itens.bind("<Configure>", self._on_frame_configure)
        self.canvas_lista.bind("<Configure>", self._on_canvas_configure)
        self.canvas_lista.bind("<MouseWheel>", self._on_mousewheel)
        self.frame_itens.bind("<MouseWheel>", self._on_mousewheel)

        # Placeholder
        self.lbl_vazio = tk.Label(self.frame_itens,
                                  text="Nenhum item adicionado ainda.\nComece adicionando produtos →",
                                  font=FONT_BODY, bg=PANEL, fg=TEXT_DIM,
                                  justify="center")
        self.lbl_vazio.pack(expand=True, pady=60)

    # ── Lógica principal ──────────────────────────────────────────────────────

    def _adicionar_item(self):
        nome  = self.entry_nome.get().strip()
        preco = self.entry_preco.get().strip().replace(",", ".")
        qtd   = self.entry_qtd.get().strip()

        if not nome:
            self._shake(self.entry_nome)
            return

        try:
            preco_f = float(preco)
            if preco_f < 0:
                raise ValueError
        except ValueError:
            self._shake(self.entry_preco)
            messagebox.showerror("Valor inválido", "Informe um preço válido.")
            return

        try:
            qtd_i = int(qtd)
            if qtd_i < 1:
                raise ValueError
        except ValueError:
            self._shake(self.entry_qtd)
            messagebox.showerror("Quantidade inválida", "A quantidade deve ser ≥ 1.")
            return

        self.itens.append({"nome": nome, "preco": preco_f, "qtd": qtd_i})
        self._renderizar_lista()
        self._atualizar_resumo()

        # Limpar campos
        self.entry_nome.delete(0, "end")
        self.entry_preco.delete(0, "end")
        self.entry_qtd.delete(0, "end")
        self.entry_qtd.insert(0, "1")
        self.entry_nome.focus()

    def _remover_item(self, idx: int):
        del self.itens[idx]
        self._renderizar_lista()
        self._atualizar_resumo()

    def _limpar_tudo(self):
        if not self.itens:
            return
        if messagebox.askyesno("Limpar lista",
                               "Deseja remover todos os itens?"):
            self.itens.clear()
            self._renderizar_lista()
            self._atualizar_resumo()

    def _atualizar_orcamento(self, _event=None):
        val = self.entry_orc.get().replace(",", ".")
        try:
            self.orcamento.set(float(val))
        except ValueError:
            self.orcamento.set(0.0)
            self.entry_orc.delete(0, "end")
            self.entry_orc.insert(0, "0.00")
        self._atualizar_resumo()

    def _total_gasto(self):
        return sum(i["preco"] * i["qtd"] for i in self.itens)

    def _atualizar_resumo(self):
        gasto    = self._total_gasto()
        orc      = self.orcamento.get()
        restante = orc - gasto

        self.lbl_gasto.config(text=f"R$ {gasto:,.2f}".replace(",", "X")
                              .replace(".", ",").replace("X", "."))
        cor_rest = SUCCESS if restante >= 0 else ACCENT2
        self.lbl_restante.config(
            text=f"R$ {abs(restante):,.2f}".replace(",", "X")
                 .replace(".", ",").replace("X", "."),
            fg=cor_rest)

        n_itens = len(self.itens)
        n_unid  = sum(i["qtd"] for i in self.itens)
        self.lbl_itens.config(text=f"{n_itens} iten{'s' if n_itens != 1 else ''}"
                                   f"  •  {n_unid} unidade{'s' if n_unid != 1 else ''}")

        # Barra de progresso
        self.canvas_bar.update_idletasks()
        w = self.canvas_bar.winfo_width()
        if w < 2:
            w = 248
        self.canvas_bar.delete("all")
        self.canvas_bar.create_rectangle(0, 0, w, 10, fill=CARD, outline="")
        if orc > 0:
            pct = min(gasto / orc, 1.0)
            cor = SUCCESS if pct < 0.75 else (WARNING if pct < 1.0 else ACCENT2)
            self.canvas_bar.create_rectangle(0, 0, int(w * pct), 10,
                                             fill=cor, outline="")

    # ── Renderização da lista ─────────────────────────────────────────────────

    def _renderizar_lista(self):
        for w in self.frame_itens.winfo_children():
            w.destroy()

        if not self.itens:
            self.lbl_vazio = tk.Label(
                self.frame_itens,
                text="Nenhum item adicionado ainda.\nComece adicionando produtos →",
                font=FONT_BODY, bg=PANEL, fg=TEXT_DIM, justify="center")
            self.lbl_vazio.pack(expand=True, pady=60)
            return

        for idx, item in enumerate(self.itens):
            self._card_item(self.frame_itens, idx, item)

    def _card_item(self, parent, idx: int, item: dict):
        card = tk.Frame(parent, bg=CARD, padx=14, pady=10)
        card.pack(fill="x", padx=12, pady=(6, 0))

        # Número
        tk.Label(card, text=f"{idx + 1:02d}", font=FONT_SMALL,
                 bg=CARD, fg=TEXT_DIM, width=3).pack(side="left")

        # Info central
        info = tk.Frame(card, bg=CARD)
        info.pack(side="left", fill="x", expand=True, padx=8)

        tk.Label(info, text=item["nome"], font=FONT_HEAD,
                 bg=CARD, fg=TEXT, anchor="w").pack(anchor="w")

        sub = tk.Frame(info, bg=CARD)
        sub.pack(anchor="w")

        preco_fmt = f"R$ {item['preco']:,.2f}".replace(",", "X")\
                                               .replace(".", ",")\
                                               .replace("X", ".")
        tk.Label(sub, text=preco_fmt, font=FONT_SMALL,
                 bg=CARD, fg=ACCENT).pack(side="left")
        tk.Label(sub, text=f"  ×  {item['qtd']}  un.", font=FONT_SMALL,
                 bg=CARD, fg=TEXT_DIM).pack(side="left")

        # Total do item
        total_item = item["preco"] * item["qtd"]
        total_fmt = f"R$ {total_item:,.2f}".replace(",", "X")\
                                            .replace(".", ",")\
                                            .replace("X", ".")
        tk.Label(card, text=total_fmt, font=FONT_HEAD,
                 bg=CARD, fg=WHITE).pack(side="right", padx=(0, 8))

        # Botão remover
        btn_del = tk.Label(card, text="✕", font=("Segoe UI", 12),
                           bg=CARD, fg=TEXT_DIM, cursor="hand2", padx=4)
        btn_del.pack(side="right")
        btn_del.bind("<Button-1>", lambda _, i=idx: self._remover_item(i))
        btn_del.bind("<Enter>", lambda _, b=btn_del: b.config(fg=ACCENT2))
        btn_del.bind("<Leave>", lambda _, b=btn_del: b.config(fg=TEXT_DIM))

        # Hover no card
        for w in [card, info] + list(card.winfo_children()) + list(info.winfo_children()):
            w.bind("<MouseWheel>", self._on_mousewheel)

    # ── Salvar / Abrir ────────────────────────────────────────────────────────

    def _salvar(self):
        path = self.arquivo_atual or filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Lista de Compras", "*.json"), ("Todos", "*.*")],
            initialfile=f"lista_{datetime.now().strftime('%Y%m%d_%H%M')}.json")
        if not path:
            return
        dados = {
            "orcamento": self.orcamento.get(),
            "itens":     self.itens,
            "salvo_em":  datetime.now().isoformat()
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        self.arquivo_atual = path
        self.root.title(f"🛒 Lista de Compras — {os.path.basename(path)}")
        messagebox.showinfo("Salvo!", f"Lista salva com sucesso em:\n{path}")

    def _abrir(self):
        path = filedialog.askopenfilename(
            filetypes=[("Lista de Compras", "*.json"), ("Todos", "*.*")])
        if not path:
            return
        try:
            with open(path, encoding="utf-8") as f:
                dados = json.load(f)
            self.orcamento.set(dados.get("orcamento", 0.0))
            self.entry_orc.delete(0, "end")
            self.entry_orc.insert(0, str(dados.get("orcamento", 0.0)))
            self.itens = dados.get("itens", [])
            self.arquivo_atual = path
            self.root.title(f"🛒 Lista de Compras — {os.path.basename(path)}")
            self._renderizar_lista()
            self._atualizar_resumo()
        except Exception as e:
            messagebox.showerror("Erro ao abrir", str(e))

    def _nova_lista(self):
        if self.itens:
            if not messagebox.askyesno("Nova lista",
                                       "Deseja descartar a lista atual?"):
                return
        self.itens.clear()
        self.orcamento.set(0.0)
        self.entry_orc.delete(0, "end")
        self.entry_orc.insert(0, "0.00")
        self.arquivo_atual = None
        self.root.title("🛒 Lista de Compras Inteligente")
        self._renderizar_lista()
        self._atualizar_resumo()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _btn(self, parent, text, cmd, color=ACCENT, full=False):
        btn = tk.Label(parent, text=text, font=FONT_SMALL, bg=color,
                       fg=WHITE, cursor="hand2", padx=12, pady=7,
                       relief="flat")
        btn.bind("<Button-1>", lambda _: cmd())
        btn.bind("<Enter>",    lambda _, b=btn, c=color: b.config(bg=self._lighten(c)))
        btn.bind("<Leave>",    lambda _, b=btn, c=color: b.config(bg=c))
        return btn

    def _entrada(self, parent):
        e = tk.Entry(parent, font=FONT_BODY, bg=CARD, fg=WHITE,
                     insertbackground=WHITE, relief="flat", bd=0,
                     highlightthickness=1, highlightbackground=BORDER,
                     highlightcolor=ACCENT)
        return e

    def _round_border(self, widget):
        pass  # tkinter não suporta border-radius nativamente

    def _lighten(self, hex_color: str) -> str:
        """Clareia levemente a cor para efeito hover."""
        hex_color = hex_color.lstrip("#")
        r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r, g, b = min(255, r + 20), min(255, g + 20), min(255, b + 20)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _shake(self, widget):
        """Animação de shake para indicar erro."""
        orig_x = widget.winfo_x()
        for dx in [5, -5, 5, -5, 0]:
            widget.place_configure(x=orig_x + dx)
            widget.update()

    def _on_frame_configure(self, _event=None):
        self.canvas_lista.configure(
            scrollregion=self.canvas_lista.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas_lista.itemconfig("inner", width=event.width)

    def _on_mousewheel(self, event):
        self.canvas_lista.yview_scroll(-1 * (event.delta // 120), "units")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    root.tk_setPalette(background=BG)
    try:
        root.iconbitmap(default="")  # remove ícone padrão se possível
    except Exception:
        pass
    app = ListaCompras(root)
    root.mainloop()