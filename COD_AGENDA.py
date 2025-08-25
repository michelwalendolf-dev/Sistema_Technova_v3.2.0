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
        self.geometry("710x550")
        self.configure(bg="#f8f9fa")
        self.resizable(False, False)

        self.ano = datetime.now().year
        self.mes = datetime.now().month

        # Dicionários inicializados vazios
        self.datas_marcadas = {}
        self.anotacoes = {}

        self.data_ultima_selecionada = None
        self.frame_dia_selecionado = None
        self.frames_dias = {}
        self.dias_widgets = []  # Para armazenar widgets de dias para reutilização

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
        janela.geometry("450x320")
        janela.grab_set()
        janela.transient(self)
        janela.focus_set()

        # Armazena a cor temporária na janela
        if self.data_ultima_selecionada in self.datas_marcadas:
            janela.cor_temp = self.datas_marcadas[self.data_ultima_selecionada]
        else:
            janela.cor_temp = "#4285F4"  # Cor padrão

        # Frame principal para organizar o conteúdo
        main_frame = ctk.CTkFrame(janela, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        label_info = ctk.CTkLabel(main_frame, text=f"Agendamento para: {self.data_ultima_selecionada}", font=("Roboto", 14, "bold"))
        label_info.pack(pady=(0, 10))

        # Frame para descrição
        frame_descricao = ctk.CTkFrame(main_frame, fg_color="transparent")
        frame_descricao.pack(fill="x", pady=(0, 5))
        
        lbl_descricao = ctk.CTkLabel(frame_descricao, text="Descrição:", font=("Roboto", 12))
        lbl_descricao.pack(side="left", padx=(0, 10))
        
        self.entry_descricao = ctk.CTkEntry(frame_descricao)
        self.entry_descricao.pack(side="left", fill="x", expand=True)

        # Preencher com dados existentes
        anotacao = self.anotacoes.get(self.data_ultima_selecionada, {})
        descricao = ""
        observacao = ""
        if isinstance(anotacao, dict):
            descricao = anotacao.get("descricao", "")
            observacao = anotacao.get("observacao", "")
        elif isinstance(anotacao, str):
            observacao = anotacao

        self.entry_descricao.insert(0, descricao)

        # Campo para observação
        lbl_observacao = ctk.CTkLabel(main_frame, text="Observação:", font=("Roboto", 12))
        lbl_observacao.pack(pady=(10, 5), anchor="w")
        
        # Frame para o campo de texto e o contador
        frame_texto = ctk.CTkFrame(main_frame, fg_color="transparent")
        frame_texto.pack(fill="x", pady=(0, 10))
        
        # Widget Text
        self.text_observacao = Text(frame_texto, height=5, width=40)
        self.text_observacao.pack(fill="x")
        
        # Frame para o contador (no canto inferior direito do campo de texto)
        frame_contador = ctk.CTkFrame(
            frame_texto, 
            width=80, 
            height=20,
            fg_color="#f0f0f0",
            corner_radius=4
        )
        frame_contador.pack_propagate(False)
        frame_contador.place(relx=1.0, rely=1.0, anchor="se", x=-5, y=-5)
        
        # Label do contador
        self.contador_caracteres = ctk.CTkLabel(
            frame_contador, 
            text="0/200", 
            text_color="#666666",
            font=("Roboto", 9)
        )
        self.contador_caracteres.pack(padx=5, pady=2)
        
        # Preencher o campo de observação
        self.text_observacao.insert("1.0", observacao)
        
        # Atualizar contador inicial
        self.atualizar_contador()
        
        # Vincular evento de digitação para atualizar o contador
        self.text_observacao.bind("<KeyRelease>", lambda e: self.atualizar_contador())

        # Frame para os controles inferiores (centralizado)
        frame_controles = ctk.CTkFrame(main_frame, fg_color="transparent")
        frame_controles.pack(fill="x", pady=(0, 10))
        
        # Container para centralizar os elementos
        center_container = ctk.CTkFrame(frame_controles, fg_color="transparent")
        center_container.pack(expand=True)

        # Frame para o seletor de cor
        frame_cor = ctk.CTkFrame(center_container, fg_color="transparent")
        frame_cor.pack(side="left", padx=(0, 20))
        
        lbl_cor = ctk.CTkLabel(frame_cor, text="Cor:", font=("Roboto", 12))
        lbl_cor.pack(side="left", padx=(0, 5))
        
        # Indicador visual da cor selecionada
        self.cor_indicator = ctk.CTkLabel(
            frame_cor, 
            text="", 
            width=10, 
            height=28,
            corner_radius=5,
            fg_color=janela.cor_temp
        )
        self.cor_indicator.pack(side="left", padx=(0, 10))
        
        btn_cor = ctk.CTkButton(
            frame_cor, 
            text="Selecionar", 
            width=80,
            fg_color="#2c49c9",
            hover_color="#4f51d9",
            border_width=2,
            border_color="#2523a8",
            command=lambda: self.adicionar_cor_modal(janela)
        )
        btn_cor.pack(side="left")

        # Botão Salvar
        btn_salvar = ctk.CTkButton(
            center_container, 
            text="Salvar", 
            width=80,
            fg_color="#2c49c9",
            hover_color="#4f51d9",
            border_width=2,
            border_color="#2523a8",
            command=lambda: self.salvar_agendamento(janela)
        )
        btn_salvar.pack(side="left")

    def adicionar_cor_modal(self, janela):
        cor = colorchooser.askcolor(title="Escolher cor da marcação")
        if cor and cor[1]:
            # Atualiza a cor temporária na janela
            janela.cor_temp = cor[1]
            # Atualiza o indicador visual
            self.cor_indicator.configure(fg_color=cor[1])

    def atualizar_contador(self):
        """Atualiza o contador de caracteres e aplica o limite"""
        texto = self.text_observacao.get("1.0", "end-1c")
        num_caracteres = len(texto)
        
        # Atualizar o texto do contador
        self.contador_caracteres.configure(text=f"{num_caracteres}/200")
        
        # Mudar cor se estiver perto do limite
        if num_caracteres > 180:
            self.contador_caracteres.configure(text_color="#e53935")  # Vermelho
        else:
            self.contador_caracteres.configure(text_color="#666666")  # Cinza
        
        # Aplicar limite de 200 caracteres
        if num_caracteres > 200:
            # Truncar o texto para 200 caracteres
            texto = texto[:200]
            self.text_observacao.delete("1.0", "end")
            self.text_observacao.insert("1.0", texto)
            # Atualizar contador novamente
            self.contador_caracteres.configure(text="200/200", text_color="#e53935")

    def salvar_agendamento(self, janela):
        descricao = self.entry_descricao.get().strip()
        observacao = self.text_observacao.get("1.0", END).strip()
        
        if not descricao:
            messagebox.showwarning("Aviso", "A descrição não pode ser vazia.")
            return

        # Aplicar limite de 200 caracteres (redundância de segurança)
        if len(observacao) > 200:
            observacao = observacao[:200]
            
        # Salva anotação com descrição e observação
        self.anotacoes[self.data_ultima_selecionada] = {
            "descricao": descricao,
            "observacao": observacao
        }

        # Salva a cor selecionada
        self.datas_marcadas[self.data_ultima_selecionada] = janela.cor_temp

        self.salvar_dados()
        self.atualizar_calendario()
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
        self.atualizar_calendario()
        self.data_ultima_selecionada = None
        self.btn_agendamento.configure(state="disabled")
        self.btn_limpar_data.configure(state="disabled")
        self.label_info.configure(text="*Selecione uma data*")

    def criar_widgets(self):
        self.frame_topo = ctk.CTkFrame(self, height=50, fg_color="#ebebeb", corner_radius=8)
        self.frame_topo.pack(fill="x", padx=10, pady=(12, 5))

        self.label_mes_ano = ctk.CTkLabel(self.frame_topo, text="", font=("Roboto", 20, "bold"))
        self.label_mes_ano.pack(side="left", padx=10)

        self.btn_agendamento = ctk.CTkButton(
            self.frame_topo,
            text="Agendamento",
            text_color="white",
            font=("Roboto", 14, "bold"),
            width=110,
            height=30,
            state="disabled",
            fg_color="#2c49c9",
            border_color="#2523a8",
            border_width=2,
            hover_color="#4f51d9",
            corner_radius=8,
            command=self.abrir_janela_marcacao
        )
        self.btn_agendamento.pack(side="right", padx=10)

        self.btn_limpar_data = ctk.CTkButton(
            self.frame_topo,
            text="Limpar Data",
            text_color="white",
            font=("Roboto", 14, "bold"),
            width=100,
            height=30,
            state="disabled",
            fg_color="#c9302c",
            border_color="#a82823",
            border_width=2,
            hover_color="#d9534f",
            corner_radius=8,
            command=self.limpar_data_selecionada
        )
        self.btn_limpar_data.pack(side="right", padx=(0, 10))

        self.frame_nav = ctk.CTkFrame(self, height=20, fg_color="white", corner_radius=8)
        self.frame_nav.pack(fill="x", padx=10, pady=(0, 5))

        self.btn_mes_anterior = ctk.CTkButton(
            self.frame_nav, 
            text="◀", 
            font=("Roboto", 26, "bold"), 
            text_color="#2c70c9", 
            fg_color="white", 
            hover_color="white",  
            width=20, height=20, 
            command=self.mes_anterior
        )
        self.btn_mes_anterior.pack(side="left", padx=5, pady=5)

        self.btn_mes_proximo = ctk.CTkButton(
            self.frame_nav, 
            text="▶", 
            font=("Roboto", 26, "bold"), 
            text_color="#2c70c9", 
            fg_color="white", 
            hover_color="white", 
            width=20, height=20, 
            command=self.mes_proximo
        )
        self.btn_mes_proximo.pack(side="right", padx=5, pady=5)

        # Frame para o calendário
        self.frame_calendario = ctk.CTkFrame(self, fg_color="#f8f9fa", corner_radius=10)
        self.frame_calendario.pack(fill="both", expand=True, padx=10, pady=5)

        self.canvas = tk.Canvas(self.frame_calendario, bg="#f8f9fa", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = ctk.CTkScrollbar(
            self.frame_calendario, 
            orientation="vertical", 
            command=self.canvas.yview
        )
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.frame_dias_container = ctk.CTkFrame(
            self.canvas, 
            fg_color="#f8f9fa", 
            border_color="#DFDFDF", 
            border_width=1, 
            corner_radius=10
        )
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.frame_dias_container, anchor="nw")

        def on_configure(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            self.canvas.itemconfig(self.canvas_frame, width=event.width)
            
        self.frame_dias_container.bind("<Configure>", on_configure)
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_frame, width=e.width))

        # Mensagem inicial com asteriscos
        self.label_info = ctk.CTkLabel(self, text="*Selecione uma data*", font=("Roboto", 12, "bold"), text_color="#5f6368")
        self.label_info.pack(pady=(0, 5))

    def atualizar_calendario(self):
        self.frames_dias.clear()
        self.data_ultima_selecionada = None
        self.frame_dia_selecionado = None
        self.btn_agendamento.configure(state="disabled")
        self.btn_limpar_data.configure(state="disabled")
        self.label_info.configure(text="*Selecione uma data*")

        meses = {
            1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
            5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
            9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
        }
        nome_mes = meses[self.mes]

        self.label_mes_ano.configure(text=f"{nome_mes} {self.ano}")

        # Criar cabeçalhos apenas se não existirem
        if not hasattr(self, 'cabecalhos_criados'):
            dias_semana = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sab"]
            for col, dia in enumerate(dias_semana):
                lbl = ctk.CTkLabel(
                    self.frame_dias_container,
                    text=dia,
                    font=("Roboto", 14, "bold"),
                    fg_color="transparent",
                    text_color="#5f6368",
                    width=95,  # Aumentei a largura para 95
                    height=24,
                    anchor="center"
                )
                lbl.grid(row=0, column=col, sticky="nsew", padx=2, pady=2)
            self.cabecalhos_criados = True

        cal = calendar.monthcalendar(self.ano, self.mes)
        primeiro_dia_semana, ultimo_dia = calendar.monthrange(self.ano, self.mes)
        
        # Obter informações sobre meses adjacentes
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
        
        # Calcular dias do mês anterior e posterior
        dias_mes_anterior = primeiro_dia_semana
        dias_anteriores = []
        if dias_mes_anterior > 0:
            dias_anteriores = list(range(ultimo_dia_anterior - dias_mes_anterior + 1, ultimo_dia_anterior + 1))
        
        # Dias do mês atual
        dias_mes_atual = list(range(1, ultimo_dia + 1))
        
        # Dias do próximo mês
        dias_prox_mes = 42 - (len(dias_anteriores) + len(dias_mes_atual))
        dias_posteriores = list(range(1, dias_prox_mes + 1))
        
        # Combinar todos os dias
        todos_dias = dias_anteriores + dias_mes_atual + dias_posteriores
        
        # Reutilizar widgets existentes ou criar novos
        total_dias = 42  # Sempre 6 semanas
        for i in range(total_dias):
            linha = i // 7 + 1
            col = i % 7
            
            # Determinar a qual mês pertence
            if i < len(dias_anteriores):
                dia = todos_dias[i]
                mes = mes_anterior
                ano = ano_anterior
                cor_texto = "#9e9e9e"
                cor_fundo = "#f5f5f5"
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
                cor_fundo = "#f5f5f5"
                e_mes_atual = False
            
            data_str = f"{dia:02d}-{mes:02d}-{ano}"
            
            # Reutilizar widget se existir
            if i < len(self.dias_widgets):
                frame_dia = self.dias_widgets[i]
                frame_dia.grid(row=linha, column=col, padx=3, pady=3, sticky="nsew")
                self.atualizar_frame_dia(frame_dia, dia, mes, ano, data_str, cor_texto, cor_fundo, e_mes_atual)
            else:
                frame_dia = self.criar_frame_dia(linha, col, dia, mes, ano, cor_texto, cor_fundo, e_mes_atual)
                self.dias_widgets.append(frame_dia)
            
            if e_mes_atual:
                self.frames_dias[data_str] = frame_dia

        # Configurar colunas para expansão uniforme
        for col in range(7):
            self.frame_dias_container.grid_columnconfigure(col, weight=1, uniform="dias")
            
        # Forçar atualização do layout
        self.frame_dias_container.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        # Rolagem para o topo
        self.canvas.yview_moveto(0)

    def criar_frame_dia(self, linha, col, dia, mes, ano, cor_texto, cor_fundo, e_mes_atual):
        """Cria um frame para um dia específico com as configurações dadas"""
        frame_dia = ctk.CTkFrame(
            self.frame_dias_container,
            fg_color=cor_fundo,
            width=95,  # Largura aumentada em 5
            height=45,  # Altura reduzida em 15
            corner_radius=8,  # Borda mais suave
            border_width=1,
            border_color="#dadce0"
        )
        frame_dia.grid(row=linha, column=col, padx=3, pady=3, sticky="nsew")
        frame_dia.grid_propagate(False)
        frame_dia.bind("<Button-1>", lambda e, d=f"{dia:02d}-{mes:02d}-{ano}": self.selecionar_data(d))

        # Frame interno para organizar conteúdo
        frame_interno = ctk.CTkFrame(frame_dia, fg_color="transparent")
        frame_interno.pack(fill="both", expand=True, padx=3, pady=3)
        frame_interno.bind("<Button-1>", lambda e, d=f"{dia:02d}-{mes:02d}-{ano}": self.selecionar_data(d))
        
        # Marcador
        marcador = ctk.CTkFrame(
            frame_interno, 
            width=6, 
            height=12,  # Altura reduzida
            corner_radius=3,
            fg_color="#dbdbdb"
        )
        marcador.pack(side="left", fill="y", padx=(0, 3))
        marcador.bind("<Button-1>", lambda e, d=f"{dia:02d}-{mes:02d}-{ano}": self.selecionar_data(d))

        # Frame para o conteúdo
        frame_conteudo = ctk.CTkFrame(frame_interno, fg_color="transparent")
        frame_conteudo.pack(side="left", fill="both", expand=True)
        frame_conteudo.bind("<Button-1>", lambda e, d=f"{dia:02d}-{mes:02d}-{ano}": self.selecionar_data(d))

        lbl_dia = ctk.CTkLabel(
            frame_conteudo,
            text=str(dia),
            font=("Roboto", 12, "bold"),
            anchor="nw",
            text_color=cor_texto
        )
        lbl_dia.pack(anchor="nw", padx=0, pady=0)
        lbl_dia.bind("<Button-1>", lambda e, d=f"{dia:02d}-{mes:02d}-{ano}": self.selecionar_data(d))

        # Frame para anotações (será preenchido quando necessário)
        frame_anotacoes = ctk.CTkFrame(frame_conteudo, fg_color="transparent")
        frame_anotacoes.pack(fill="x", pady=(0, 0))  # Reduzi o espaçamento
        frame_anotacoes.bind("<Button-1>", lambda e, d=f"{dia:02d}-{mes:02d}-{ano}": self.selecionar_data(d))

        # Armazenar referências para atualização
        frame_dia.marcador = marcador
        frame_dia.lbl_dia = lbl_dia
        frame_dia.frame_anotacoes = frame_anotacoes
        
        # Configurar anotações se for o mês atual
        if e_mes_atual:
            data_str = f"{dia:02d}-{mes:02d}-{ano}"
            self.atualizar_anotacoes(frame_dia, data_str)
        
        return frame_dia

    def atualizar_frame_dia(self, frame_dia, dia, mes, ano, data_str, cor_texto, cor_fundo, e_mes_atual):
        """Atualiza um frame de dia existente com novas informações"""
        frame_dia.configure(fg_color=cor_fundo, border_color="#dadce0", border_width=1)
        
        # Atualizar dia
        frame_dia.lbl_dia.configure(text=str(dia), text_color=cor_texto)
        
        # Atualizar marcador
        if e_mes_atual:
            cor_marcador = self.datas_marcadas.get(data_str, "#dbdbdb")
            frame_dia.marcador.configure(fg_color=cor_marcador)
        else:
            frame_dia.marcador.configure(fg_color=cor_fundo)
        
        # Limpar anotações anteriores
        for widget in frame_dia.frame_anotacoes.winfo_children():
            widget.destroy()
        
        # Adicionar anotações para o mês atual
        if e_mes_atual:
            self.atualizar_anotacoes(frame_dia, data_str)

    def atualizar_anotacoes(self, frame_dia, data_str):
        """Atualiza as anotações para um frame de dia específico"""
        if data_str in self.anotacoes:
            anotacao = self.anotacoes[data_str]
            descricao = ""
            observacao = ""
            
            if isinstance(anotacao, dict):
                descricao = anotacao.get("descricao", "")
                observacao = anotacao.get("observacao", "")
            elif isinstance(anotacao, str):
                observacao = anotacao
            
            # Exibir descrição
            if descricao:
                lbl_desc = ctk.CTkLabel(
                    frame_dia.frame_anotacoes,
                    text=descricao,
                    font=("Roboto", 12, "bold"),
                    anchor="nw",
                    justify="left",
                    text_color="#5f6368",
                    wraplength=85  # Ajustado para a nova largura
                )
                lbl_desc.pack(anchor="nw", fill="x")
            
            # Exibir observação (até 50 caracteres)
            if observacao:
                # Limitar a 50 caracteres
                texto_obs = observacao[:50]
                if len(observacao) > 50:
                    texto_obs += "..."
                    
                lbl_obs = ctk.CTkLabel(
                    frame_dia.frame_anotacoes,
                    text=texto_obs,
                    font=("Roboto", 12),
                    anchor="nw",
                    justify="left",
                    text_color="#5f6368",
                    wraplength=85
                )
                lbl_obs.pack(anchor="nw", fill="x", pady=(0, 0))

    def selecionar_data(self, data):
        if self.frame_dia_selecionado:
            self.frame_dia_selecionado.configure(border_color="#dadce0", border_width=1)

        self.data_ultima_selecionada = data
        self.frame_dia_selecionado = self.frames_dias.get(data)

        if self.frame_dia_selecionado:
            self.frame_dia_selecionado.configure(border_color="#4285F4", border_width=2)
            
            # Atualizar o label para mostrar apenas a data
            self.label_info.configure(text=f"Data selecionada: {data}")
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