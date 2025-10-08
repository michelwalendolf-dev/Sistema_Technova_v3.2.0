import customtkinter as ctk
from tkinter import colorchooser, messagebox, Toplevel, Text, END
import tkinter as tk
import calendar
import json
import os
from datetime import datetime

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class Agenda(ctk.CTk):
    def __init__(self):
        super().__init__()
        calendar.setfirstweekday(calendar.SUNDAY)
        
        self.title("Agenda")
        self.geometry("950x720")
        self.configure(bg="#f0f2f5")
        self.resizable(False, False)

        self.ano = datetime.now().year
        self.mes = datetime.now().month

        self.datas_marcadas = {}
        self.anotacoes = {}

        self.data_ultima_selecionada = None
        self.frame_dia_selecionado = None
        self.frames_dias = {}
        self.widgets_cache = []  # Cache de widgets para reutilização

        self.carregar_dados()
        self.criar_widgets()
        self.atualizar_calendario()

    def salvar_dados(self):
        try:
            with open("datas_marcadas.json", "w", encoding="utf-8") as f:
                json.dump(self.datas_marcadas, f, ensure_ascii=False, indent=2)
            with open("anotacoes.json", "w", encoding="utf-8") as f:
                json.dump(self.anotacoes, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar dados: {e}")

    def carregar_dados(self):
        try:
            with open("datas_marcadas.json", "r", encoding="utf-8") as f:
                self.datas_marcadas = json.load(f)
        except FileNotFoundError:
            self.datas_marcadas = {}
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar cores: {e}")
            self.datas_marcadas = {}

        try:
            with open("anotacoes.json", "r", encoding="utf-8") as f:
                self.anotacoes = json.load(f)
        except FileNotFoundError:
            self.anotacoes = {}
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar anotações: {e}")
            self.anotacoes = {}

    def abrir_janela_marcacao(self):
        if not self.data_ultima_selecionada:
            messagebox.showwarning("Aviso", "Selecione uma data primeiro!")
            return

        janela = Toplevel(self)
        janela.title("Agendamento")
        janela.geometry("520x380")
        janela.configure(bg="#f0f2f5")
        janela.grab_set()
        janela.transient(self)
        janela.focus_set()

        if self.data_ultima_selecionada in self.datas_marcadas:
            janela.cor_temp = self.datas_marcadas[self.data_ultima_selecionada]
        else:
            janela.cor_temp = "#1a73e8"

        main_frame = ctk.CTkFrame(janela, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=25, pady=15)

        # Título com gradiente visual
        header_frame = ctk.CTkFrame(main_frame, fg_color="#1a73e8", corner_radius=10, height=60)
        header_frame.pack(fill="x", pady=(0, 15))
        header_frame.pack_propagate(False)
        
        label_info = ctk.CTkLabel(
            header_frame, 
            text=f"📅 Agendamento para: {self.data_ultima_selecionada}", 
            font=("Roboto", 16, "bold"),
            text_color="white"
        )
        label_info.pack(expand=True)

        # Frame para descrição
        frame_descricao = ctk.CTkFrame(main_frame, fg_color="transparent")
        frame_descricao.pack(fill="x", pady=(0, 10))
        
        lbl_descricao = ctk.CTkLabel(frame_descricao, text="Descrição:", font=("Roboto", 13, "bold"))
        lbl_descricao.pack(side="left", padx=(0, 10))
        
        self.entry_descricao = ctk.CTkEntry(
            frame_descricao,
            height=35,
            font=("Roboto", 11),
            corner_radius=8
        )
        self.entry_descricao.pack(side="left", fill="x", expand=True)

        anotacao = self.anotacoes.get(self.data_ultima_selecionada, {})
        descricao = ""
        observacao = ""
        if isinstance(anotacao, dict):
            descricao = anotacao.get("descricao", "")
            observacao = anotacao.get("observacao", "")
        elif isinstance(anotacao, str):
            observacao = anotacao

        self.entry_descricao.insert(0, descricao)

        lbl_observacao = ctk.CTkLabel(main_frame, text="Observação:", font=("Roboto", 13, "bold"))
        lbl_observacao.pack(pady=(10, 5), anchor="w")
        
        frame_texto = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=8, border_width=2, border_color="#e0e0e0")
        frame_texto.pack(fill="x", pady=(0, 15))
        
        self.text_observacao = Text(
            frame_texto, 
            height=6, 
            width=45, 
            font=("Roboto", 10),
            relief="flat",
            padx=10,
            pady=10
        )
        self.text_observacao.pack(fill="x", padx=2, pady=2)
        
        frame_contador = ctk.CTkFrame(
            frame_texto, 
            width=70, 
            height=22,
            fg_color="white",
            corner_radius=5
        )
        frame_contador.pack_propagate(False)
        frame_contador.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        
        self.contador_caracteres = ctk.CTkLabel(
            frame_contador, 
            text="0/200", 
            text_color="#666666",
            font=("Roboto", 10, "bold")
        )
        self.contador_caracteres.pack(expand=True)
        
        self.text_observacao.insert("1.0", observacao)
        self.atualizar_contador()
        self.text_observacao.bind("<KeyRelease>", lambda e: self.atualizar_contador())

        # Frame para controles inferiores
        frame_controles = ctk.CTkFrame(main_frame, fg_color="transparent")
        frame_controles.pack(fill="x")
        
        center_container = ctk.CTkFrame(frame_controles, fg_color="transparent")
        center_container.pack(expand=True)

        # Seletor de cor melhorado
        frame_cor = ctk.CTkFrame(center_container, fg_color="transparent")
        frame_cor.pack(side="left", padx=(0, 15))
        
        lbl_cor = ctk.CTkLabel(frame_cor, text="Cor:", font=("Roboto", 13, "bold"))
        lbl_cor.pack(side="left", padx=(0, 8))
        
        self.cor_indicator = ctk.CTkButton(
            frame_cor,
            text="",
            width=35,
            height=35,
            corner_radius=8,
            fg_color=janela.cor_temp,
            hover_color=janela.cor_temp,
            border_width=3,
            border_color="#dadce0"
        )
        self.cor_indicator.pack(side="left", padx=(0, 10))
        
        btn_cor = ctk.CTkButton(
            frame_cor, 
            text="🖌️Selecionar", 
            width=90,
            height=35,
            font=("Segoe UI Emoji", 12, "bold"),
            fg_color="#1a73e8",
            hover_color="#1557b0",
            border_width=0,
            corner_radius=8,
            command=lambda: self.adicionar_cor_modal(janela)
        )
        btn_cor.pack(side="left")

        # Botão Salvar melhorado
        btn_salvar = ctk.CTkButton(
            center_container, 
            text="✔️Salvar", 
            width=100,
            height=35,
            font=("Segoe UI Emoji", 13, "bold"),
            fg_color="#34a853",
            hover_color="#2d8e47",
            border_width=0,
            corner_radius=8,
            command=lambda: self.salvar_agendamento(janela)
        )
        btn_salvar.pack(side="left")

    def adicionar_cor_modal(self, janela):
        cor = colorchooser.askcolor(title="Escolher cor da marcação")
        if cor and cor[1]:
            janela.cor_temp = cor[1]
            self.cor_indicator.configure(fg_color=cor[1], hover_color=cor[1])

    def atualizar_contador(self):
        texto = self.text_observacao.get("1.0", "end-1c")
        num_caracteres = len(texto)
        
        self.contador_caracteres.configure(text=f"{num_caracteres}/200")
        
        if num_caracteres > 180:
            self.contador_caracteres.configure(text_color="#ea4335")
        else:
            self.contador_caracteres.configure(text_color="#666666")
        
        if num_caracteres > 200:
            texto = texto[:200]
            self.text_observacao.delete("1.0", "end")
            self.text_observacao.insert("1.0", texto)
            self.contador_caracteres.configure(text="200/200", text_color="#ea4335")

    def salvar_agendamento(self, janela):
        descricao = self.entry_descricao.get().strip()
        observacao = self.text_observacao.get("1.0", END).strip()
        
        if not descricao:
            messagebox.showwarning("Aviso", "A descrição não pode ser vazia.")
            return

        if len(observacao) > 200:
            observacao = observacao[:200]
            
        self.anotacoes[self.data_ultima_selecionada] = {
            "descricao": descricao,
            "observacao": observacao
        }

        self.datas_marcadas[self.data_ultima_selecionada] = janela.cor_temp

        self.salvar_dados()
        self.atualizar_calendario_rapido()
        janela.destroy()

    def limpar_data_selecionada(self):
        if not self.data_ultima_selecionada:
            return

        confirmar = messagebox.askyesno("Confirmar", f"Deseja realmente limpar a marcação da data?")
        if not confirmar:
            return

        if self.data_ultima_selecionada in self.anotacoes:
            del self.anotacoes[self.data_ultima_selecionada]
        if self.data_ultima_selecionada in self.datas_marcadas:
            del self.datas_marcadas[self.data_ultima_selecionada]

        self.salvar_dados()
        self.atualizar_calendario_rapido()
        self.data_ultima_selecionada = None
        self.btn_agendamento.configure(state="disabled")
        self.btn_limpar_data.configure(state="disabled")
        self.label_info.configure(text="Selecione uma data")

    def criar_widgets(self):
        # Frame superior com gradiente
        self.frame_topo = ctk.CTkFrame(self, height=70, fg_color="#ffffff", corner_radius=12)
        self.frame_topo.pack(fill="x", padx=15, pady=(15, 10))

        self.label_mes_ano = ctk.CTkLabel(
            self.frame_topo, 
            text="", 
            font=("Roboto", 24, "bold"),
            text_color="#202124"
        )
        self.label_mes_ano.pack(side="left", padx=20)

        # Botões melhorados
        self.btn_agendamento = ctk.CTkButton(
            self.frame_topo,
            text="➕Agendamento",
            text_color="white",
            font=("Segoe UI Emoji", 13, "bold"),
            width=130,
            height=38,
            state="disabled",
            fg_color="#1a73e8",
            border_width=0,
            hover_color="#1557b0",
            corner_radius=10,
            command=self.abrir_janela_marcacao
        )
        self.btn_agendamento.pack(side="right", padx=15)

        self.btn_limpar_data = ctk.CTkButton(
            self.frame_topo,
            text="❌Limpar",
            text_color="white",
            font=("Roboto", 13, "bold"),
            width=100,
            height=38,
            state="disabled",
            fg_color="#ea4335",
            border_width=0,
            hover_color="#c5372c",
            corner_radius=10,
            command=self.limpar_data_selecionada
        )
        self.btn_limpar_data.pack(side="right", padx=(0, 10))

        # Frame de navegação melhorado
        self.frame_nav = ctk.CTkFrame(self, height=50, fg_color="#ffffff", corner_radius=12)
        self.frame_nav.pack(fill="x", padx=15, pady=(0, 10))

        self.btn_mes_anterior = ctk.CTkButton(
            self.frame_nav, 
            text="◀", 
            font=("Roboto", 22, "bold"), 
            text_color="#1a73e8", 
            fg_color="transparent", 
            hover_color="#e8f0fe",
            width=45,
            height=45,
            corner_radius=10,
            command=self.mes_anterior
        )
        self.btn_mes_anterior.pack(side="left", padx=10, pady=2)

        self.btn_mes_proximo = ctk.CTkButton(
            self.frame_nav, 
            text="▶", 
            font=("Roboto", 22, "bold"), 
            text_color="#1a73e8", 
            fg_color="transparent", 
            hover_color="#e8f0fe",
            width=45,
            height=45,
            corner_radius=10,
            command=self.mes_proximo
        )
        self.btn_mes_proximo.pack(side="right", padx=10, pady=2)

        # Frame do calendário com scrollbar integrada
        self.frame_calendario = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=12)
        self.frame_calendario.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        # Container para o conteúdo do calendário
        self.frame_dias_container = ctk.CTkScrollableFrame(
            self.frame_calendario,
            fg_color="#ffffff",
            corner_radius=0,
            scrollbar_button_color="#c0c0c0",
            scrollbar_button_hover_color="#a0a0a0"
        )
        self.frame_dias_container.pack(fill="both", expand=True, padx=5, pady=5)

        # Label de informação melhorada
        self.label_info = ctk.CTkLabel(
            self, 
            text="Selecione uma data", 
            font=("Roboto", 13),
            text_color="#5f6368"
        )
        self.label_info.pack(pady=(0, 10))

    def atualizar_calendario(self):
        # Limpar apenas o conteúdo, não recriar o container
        for widget in self.frame_dias_container.winfo_children():
            widget.destroy()
        
        self.frames_dias.clear()
        self.data_ultima_selecionada = None
        self.frame_dia_selecionado = None
        self.btn_agendamento.configure(state="disabled")
        self.btn_limpar_data.configure(state="disabled")
        self.label_info.configure(text="Selecione uma data")

        meses = {
            1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
            5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
            9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
        }
        nome_mes = meses[self.mes]

        self.label_mes_ano.configure(text=f"{nome_mes} {self.ano}")

        # Criar cabeçalhos
        dias_semana = ["Domingo", "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"]
        for col, dia in enumerate(dias_semana):
            lbl = ctk.CTkLabel(
                self.frame_dias_container,
                text=dia,
                font=("Roboto", 13, "bold"),
                fg_color="#f8f9fa",
                text_color="#5f6368",
                height=35,
                corner_radius=8,
                anchor="center"
            )
            lbl.grid(row=0, column=col, sticky="nsew", padx=2, pady=(0, 5))

        primeiro_dia_semana, ultimo_dia = calendar.monthrange(self.ano, self.mes)
        
        if self.mes == 1:
            mes_anterior = 12
            ano_anterior = self.ano - 1
        else:
            mes_anterior = self.mes - 1
            ano_anterior = self.ano
            
        if self.mes == 12:
            mes_posterior = 1
            ano_posterior = self.ano + 1
        else:
            mes_posterior = self.mes + 1
            ano_posterior = self.ano
            
        _, ultimo_dia_anterior = calendar.monthrange(ano_anterior, mes_anterior)
        
        dias_mes_anterior = primeiro_dia_semana
        dias_anteriores = []
        if dias_mes_anterior > 0:
            dias_anteriores = list(range(ultimo_dia_anterior - dias_mes_anterior + 1, ultimo_dia_anterior + 1))
        
        dias_mes_atual = list(range(1, ultimo_dia + 1))
        
        dias_prox_mes = 42 - (len(dias_anteriores) + len(dias_mes_atual))
        dias_posteriores = list(range(1, dias_prox_mes + 1))
        
        todos_dias = dias_anteriores + dias_mes_atual + dias_posteriores
        
        # Criar frames de dias de forma otimizada
        for i in range(42):
            linha = i // 7 + 1
            col = i % 7
            
            if i < len(dias_anteriores):
                dia = todos_dias[i]
                mes = mes_anterior
                ano = ano_anterior
                cor_texto = "#9e9e9e"
                cor_fundo = "#fafafa"
                e_mes_atual = False
            elif i < len(dias_anteriores) + len(dias_mes_atual):
                dia = todos_dias[i]
                mes = self.mes
                ano = self.ano
                cor_texto = "#202124"
                cor_fundo = "white"
                e_mes_atual = True
            else:
                dia = todos_dias[i]
                mes = mes_posterior
                ano = ano_posterior
                cor_texto = "#9e9e9e"
                cor_fundo = "#fafafa"
                e_mes_atual = False
            
            data_str = f"{dia:02d}-{mes:02d}-{ano}"
            frame_dia = self.criar_frame_dia_otimizado(linha, col, dia, mes, ano, data_str, cor_texto, cor_fundo, e_mes_atual)
            self.frames_dias[data_str] = frame_dia

        # Configurar colunas
        for col in range(7):
            self.frame_dias_container.grid_columnconfigure(col, weight=1, uniform="dias")

    def atualizar_calendario_rapido(self):
        """Atualização rápida sem recriar toda a estrutura"""
        for data_str, frame_dia in self.frames_dias.items():
            # Atualizar apenas marcador e anotações
            if hasattr(frame_dia, 'marcador'):
                cor_marcador = self.datas_marcadas.get(data_str, "#e8eaed")
                frame_dia.marcador.configure(fg_color=cor_marcador)
            
            if hasattr(frame_dia, 'frame_anotacoes'):
                # Limpar anotações antigas
                for widget in frame_dia.frame_anotacoes.winfo_children():
                    widget.destroy()
                
                # Adicionar novas anotações
                if data_str in self.anotacoes:
                    self.adicionar_anotacoes_widget(frame_dia.frame_anotacoes, data_str, 
                                                   lambda e, d=data_str: self.selecionar_data(d))

    def criar_frame_dia_otimizado(self, linha, col, dia, mes, ano, data_str, cor_texto, cor_fundo, e_mes_atual):
        frame_dia = ctk.CTkFrame(
            self.frame_dias_container,
            fg_color=cor_fundo,
            corner_radius=10,
            border_width=2,
            border_color="#e8eaed"
        )
        frame_dia.grid(row=linha, column=col, padx=3, pady=3, sticky="nsew")
        frame_dia.grid_rowconfigure(0, weight=1)
        frame_dia.grid_columnconfigure(0, weight=1)

        def on_click(e):
            self.selecionar_data(data_str)
        
        frame_dia.bind("<Button-1>", on_click)

        frame_interno = ctk.CTkFrame(frame_dia, fg_color="transparent")
        frame_interno.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        frame_interno.bind("<Button-1>", on_click)
        
        # Marcador lateral
        cor_marcador = self.datas_marcadas.get(data_str, "#e8eaed" if e_mes_atual else cor_fundo)
        marcador = ctk.CTkFrame(
            frame_interno, 
            width=5, 
            corner_radius=3,
            fg_color=cor_marcador
        )
        marcador.grid(row=0, column=0, rowspan=2, sticky="nsw", padx=(0, 8))
        marcador.bind("<Button-1>", on_click)
        frame_dia.marcador = marcador

        # Número do dia
        lbl_dia = ctk.CTkLabel(
            frame_interno,
            text=str(dia),
            font=("Roboto", 15, "bold"),
            anchor="nw",
            text_color=cor_texto
        )
        lbl_dia.grid(row=0, column=1, sticky="nw", pady=(0, 3))
        lbl_dia.bind("<Button-1>", on_click)

        # Frame para anotações
        frame_anotacoes = ctk.CTkFrame(frame_interno, fg_color="transparent")
        frame_anotacoes.grid(row=1, column=1, sticky="nsew")
        frame_anotacoes.bind("<Button-1>", on_click)
        frame_dia.frame_anotacoes = frame_anotacoes

        frame_interno.grid_rowconfigure(1, weight=1)
        frame_interno.grid_columnconfigure(1, weight=1)

        if data_str in self.anotacoes:
            self.adicionar_anotacoes_widget(frame_anotacoes, data_str, on_click)
        
        return frame_dia

    def adicionar_anotacoes_widget(self, frame_anotacoes, data_str, on_click):
        anotacao = self.anotacoes[data_str]
        descricao = ""
        observacao = ""
        
        if isinstance(anotacao, dict):
            descricao = anotacao.get("descricao", "")
            observacao = anotacao.get("observacao", "")
        elif isinstance(anotacao, str):
            observacao = anotacao
        
        if descricao:
            texto_desc = descricao[:28]
            if len(descricao) > 28:
                texto_desc += "..."
                
            lbl_desc = ctk.CTkLabel(
                frame_anotacoes,
                text=texto_desc,
                font=("Roboto", 10, "bold"),
                anchor="w",
                justify="left",
                text_color="#1a73e8"
            )
            lbl_desc.pack(anchor="w", fill="x", pady=(0, 2))
            lbl_desc.bind("<Button-1>", on_click)
        
        if observacao:
            texto_obs = observacao[:55]
            if len(observacao) > 55:
                texto_obs += "..."
                
            lbl_obs = ctk.CTkLabel(
                frame_anotacoes,
                text=texto_obs,
                font=("Roboto", 9),
                anchor="w",
                justify="left",
                text_color="#5f6368"
            )
            lbl_obs.pack(anchor="w", fill="x")
            lbl_obs.bind("<Button-1>", on_click)

    def selecionar_data(self, data):
        if self.frame_dia_selecionado:
            self.frame_dia_selecionado.configure(border_color="#e8eaed", border_width=2)

        self.data_ultima_selecionada = data
        self.frame_dia_selecionado = self.frames_dias.get(data)

        if self.frame_dia_selecionado:
            self.frame_dia_selecionado.configure(border_color="#1a73e8", border_width=3)
            self.label_info.configure(text=f"📅 Data selecionada: {data}")
            self.btn_agendamento.configure(state="normal")
            self.btn_limpar_data.configure(state="normal")

    def mes_anterior(self):
        if self.mes == 1:
            self.mes = 12
            self.ano -= 1
        else:
            self.mes -= 1
        self.atualizar_calendario()

    def mes_proximo(self):
        if self.mes == 12:
            self.mes = 1
            self.ano += 1
        else:
            self.mes += 1
        self.atualizar_calendario()

if __name__ == "__main__":
    app = Agenda()
    app.mainloop()