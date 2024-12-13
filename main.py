# Lucas Ribeiro Nunes 1.0
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from tarefas import Tarefa, calcular_mmc_lista
from escalonadores import (atribuir_prioridades_dm, atribuir_prioridades_rm, gerar_instancias,
                           escalonamento_edf, escalonamento_dm, escalonamento_rm)
from plotagem import plotar_simulacao

class EditorTarefas(tk.Toplevel):
    def __init__(self, master, tarefas):
        super().__init__(master)
        self.title("Editor de Tarefas")
        self.tarefas = tarefas

        # Cores e fontes do tema
        bg_color = "#1E1E1E"
        fg_color = "#EEE"
        fonte_padrao = ("Arial", 14)

        self.configure(bg=bg_color)
        self.option_add("*Font", fonte_padrao)
        self.option_add("*Background", bg_color)
        self.option_add("*Foreground", fg_color)
        self.option_add("*Button.Background", "#3A3D41")
        self.option_add("*Button.Foreground", fg_color)
        self.option_add("*Entry.Background", "#252526")
        self.option_add("*Entry.Foreground", fg_color)
        self.option_add("*Entry.BorderWidth", 1)

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#252526",
                        foreground=fg_color,
                        fieldbackground="#252526",
                        rowheight=30)
        style.configure("Treeview.Heading",
                        background="#3A3D41",
                        foreground=fg_color)
        style.map("Treeview.Heading",
                  background=[("active", "#3A3D41")])

        style.configure("Vertical.TScrollbar",
                        background="#252526",
                        troughcolor="#1E1E1E",
                        arrowcolor=fg_color)
        style.configure("TButton",
                        background="#3A3D41",
                        foreground=fg_color)

        style.configure("TCombobox",
                        fieldbackground="#252526",
                        background="#252526",
                        foreground=fg_color)
        style.map("TCombobox",
                  fieldbackground=[("readonly", "#252526")],
                  background=[("readonly", "#252526")],
                  foreground=[("readonly", fg_color)])

        # Texto explicativo conciso
        info_frame = tk.Frame(self, bg=bg_color, padx=10, pady=10)
        info_frame.pack(side=tk.TOP, fill=tk.X)
        info_label_title = tk.Label(info_frame, text="Instruções", bg=bg_color, fg=fg_color, font=("Arial", 16, "bold"))
        info_label_title.pack(side=tk.TOP, anchor="w", pady=(0,5))

        info_texto = (
            "Escolha um algoritmo de escalonamento:\n"
            "- EDF: Prioridade pelo deadline mais próximo.\n"
            "- DM: Prioridade fixa pelo menor deadline relativo.\n"
            "- RM: Prioridade fixa pelo menor período (deadline não interfere em RM).\n\n"
            "Após ajustar as tarefas (adicionar/editar/remover) e escolher o algoritmo na janela principal, clique em Executar."
        )

        txt_info = tk.Label(info_frame, text=info_texto, bg=bg_color, fg=fg_color, justify="left")
        txt_info.pack(fill=tk.X, expand=False)

        # Frame da lista de tarefas
        table_frame = tk.Frame(self, bg=bg_color, padx=10, pady=10)
        table_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        title_label = tk.Label(table_frame, text="Lista de Tarefas", bg=bg_color, fg=fg_color, font=("Arial", 16, "bold"))
        title_label.pack(side=tk.TOP, anchor="w", pady=(0,10))

        columns = ("nome", "periodo", "deadline", "tempo")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
        self.tree.heading("nome", text="Nome")
        self.tree.heading("periodo", text="Período (ms)")
        self.tree.heading("deadline", text="Deadline (ms)")
        self.tree.heading("tempo", text="Tempo de Computação (ms)")

        for col in columns:
            self.tree.column(col, width=150, anchor="center")

        tree_frame = tk.Frame(table_frame, bg=bg_color)
        tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview, style="Vertical.TScrollbar")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscroll=scrollbar.set)

        btn_frame = tk.Frame(self, bg=bg_color, padx=10, pady=10)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X)
        tk.Button(btn_frame, text="Adicionar", command=self.adicionar_tarefa, bg="#3A3D41", fg=fg_color).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Remover", command=self.remover_tarefa, bg="#3A3D41", fg=fg_color).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Editar", command=self.editar_tarefa, bg="#3A3D41", fg=fg_color).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Salvar", command=self.salvar_fechar, bg="#3A3D41", fg=fg_color).pack(side=tk.RIGHT, padx=5)

        self.carregar_tarefas_iniciais()

    def carregar_tarefas_iniciais(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for t in self.tarefas:
            self.tree.insert("", tk.END, values=(t.nome, t.periodo, t.deadline, t.tempo_computacao))

    def adicionar_tarefa(self):
        self.janela_edicao(None)

    def remover_tarefa(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma tarefa para remover.")
            return
        for sel in selected:
            self.tree.delete(sel)

    def editar_tarefa(self):
        selected = self.tree.selection()
        if len(selected) != 1:
            messagebox.showwarning("Aviso", "Selecione exatamente uma tarefa para editar.")
            return
        item = self.tree.item(selected[0])
        self.janela_edicao(selected[0], item["values"])

    def janela_edicao(self, item_id, valores=None):
        edit_window = tk.Toplevel(self)
        edit_window.title("Editar Tarefa" if item_id else "Adicionar Tarefa")

        bg_color = "#1E1E1E"
        fg_color = "#EEE"
        fonte_padrao = ("Arial", 14)
        edit_window.configure(bg=bg_color)
        edit_window.option_add("*Font", fonte_padrao)
        edit_window.option_add("*Background", bg_color)
        edit_window.option_add("*Foreground", fg_color)

        tk.Label(edit_window, text="Nome:", bg=bg_color, fg=fg_color).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        tk.Label(edit_window, text="Período (ms):", bg=bg_color, fg=fg_color).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        tk.Label(edit_window, text="Deadline (ms):", bg=bg_color, fg=fg_color).grid(row=2, column=0, padx=5, pady=5, sticky="e")
        tk.Label(edit_window, text="Tempo de Computação (ms):", bg=bg_color, fg=fg_color).grid(row=3, column=0, padx=5, pady=5, sticky="e")

        nome_var = tk.StringVar(value=valores[0] if valores else "")
        periodo_var = tk.StringVar(value=valores[1] if valores else "")
        deadline_var = tk.StringVar(value=valores[2] if valores else "")
        tempo_var = tk.StringVar(value=valores[3] if valores else "")

        entry_bg = "#252526"
        tk.Entry(edit_window, textvariable=nome_var, bg=entry_bg, fg=fg_color).grid(row=0, column=1, padx=5, pady=5)
        tk.Entry(edit_window, textvariable=periodo_var, bg=entry_bg, fg=fg_color).grid(row=1, column=1, padx=5, pady=5)
        tk.Entry(edit_window, textvariable=deadline_var, bg=entry_bg, fg=fg_color).grid(row=2, column=1, padx=5, pady=5)
        tk.Entry(edit_window, textvariable=tempo_var, bg=entry_bg, fg=fg_color).grid(row=3, column=1, padx=5, pady=5)

        def salvar():
            try:
                p = int(periodo_var.get())
                d = int(deadline_var.get())
                c = int(tempo_var.get())
                n = nome_var.get().strip()
                if not n:
                    raise ValueError("Nome vazio")
            except ValueError:
                messagebox.showerror("Erro", "Dados inválidos. Verifique os valores inseridos.")
                return
            if item_id:
                self.tree.item(item_id, values=(n, p, d, c))
            else:
                self.tree.insert("", tk.END, values=(n, p, d, c))
            edit_window.destroy()

        tk.Button(edit_window, text="Salvar", command=salvar, bg="#3A3D41", fg=fg_color).grid(row=4, column=0, columnspan=2, pady=10)

    def salvar_fechar(self):
        self.tarefas.clear()
        for item_id in self.tree.get_children():
            vals = self.tree.item(item_id, "values")
            self.tarefas.append(Tarefa(vals[0], int(vals[1]), int(vals[2]), int(vals[3])))
        self.destroy()

class App:
    def __init__(self, master):
        self.master = master
        self.master.title("Simulador de Escalonamento")

        bg_color = "#1E1E1E"
        fg_color = "#EEE"
        fonte_padrao = ("Arial", 14)

        self.master.configure(bg=bg_color)
        self.master.option_add("*Font", fonte_padrao)
        self.master.option_add("*Background", bg_color)
        self.master.option_add("*Foreground", fg_color)
        self.master.option_add("*Button.Background", "#3A3D41")
        self.master.option_add("*Button.Foreground", fg_color)
        self.master.option_add("*Label.Foreground", fg_color)

        style = ttk.Style(self.master)
        style.theme_use("clam")
        style.configure(".", background=bg_color, foreground=fg_color)
        style.configure("TLabel", background=bg_color, foreground=fg_color)
        style.configure("TButton", background="#3A3D41", foreground=fg_color)
        style.configure("TCombobox", fieldbackground="#252526", background="#252526", foreground=fg_color)

        self.tarefas = [
            Tarefa("tarefa1", 20, 5, 3),
            Tarefa("tarefa2", 15, 7, 3),
            Tarefa("tarefa3", 10, 10, 4),
            Tarefa("tarefa4", 20, 20, 3)
        ]

        top_frame = tk.Frame(master, bg=bg_color, padx=10, pady=10)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        tk.Label(top_frame, text="Tipo de Análise:", bg=bg_color, fg=fg_color).pack(side=tk.LEFT, padx=5)
        self.tipo_analise_var = tk.StringVar(value="EDF")
        tipo_combobox = ttk.Combobox(top_frame, textvariable=self.tipo_analise_var, values=["EDF", "DM", "RM"], width=5)
        tipo_combobox.pack(side=tk.LEFT, padx=5)

        tk.Button(top_frame, text="Editar Tarefas", command=self.abrir_editor_tarefas, bg="#3A3D41", fg=fg_color).pack(side=tk.LEFT, padx=10)
        tk.Button(top_frame, text="Executar", command=self.executar, bg="#3A3D41", fg=fg_color).pack(side=tk.LEFT, padx=10)

        self.fig_frame = tk.Frame(master, bg=bg_color, padx=10, pady=10)
        self.fig_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def abrir_editor_tarefas(self):
        EditorTarefas(self.master, self.tarefas)

    def executar(self):
        tipo = self.tipo_analise_var.get()
        if not self.tarefas:
            messagebox.showwarning("Aviso", "Não há tarefas para escalonar.")
            return
        periodos = [t.periodo for t in self.tarefas]
        hiper_periodo = calcular_mmc_lista(periodos)

        if tipo == "DM" or tipo == "dm":
            atribuir_prioridades_dm(self.tarefas)
        elif tipo == "RM" or tipo == "rm":
            atribuir_prioridades_rm(self.tarefas)
        else:
            for t in self.tarefas:
                t.prioridade = None

        instancias = gerar_instancias(self.tarefas, hiper_periodo)

        tipo_lower = tipo.lower()
        if tipo_lower == "edf":
            linha_do_tempo = escalonamento_edf(instancias, hiper_periodo)
        elif tipo_lower == "dm":
            linha_do_tempo = escalonamento_dm(instancias, hiper_periodo)
        else:
            linha_do_tempo = escalonamento_rm(instancias, hiper_periodo)

        fig = plotar_simulacao(self.tarefas, linha_do_tempo, instancias, tipo_lower)

        for widget in self.fig_frame.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=self.fig_frame)
        canvas.draw()

        # Adicionar barra de ferramentas para zoom/pan
        toolbar = NavigationToolbar2Tk(canvas, self.fig_frame)
        toolbar.update()

        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
