import customtkinter as ctk
import time
from PIL import Image, ImageTk
import os
import tkinter as tk
import tkinter.font as tkfont
import subprocess
from tkinter import ttk
import json
import tkinter.messagebox as messagebox

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class TelaProduto(ctk.CTkToplevel):
    def __init__(self, parent, produto=None):
        super().__init__(parent)
        self.parent = parent
        self.produto = produto
        self.title("Cadastro de Produto" if not produto else "Editar Produto")
        self.geometry("550x600")
        self.resizable(True, True)
        
        self.codigo_sequencial = self.gerar_codigo_sequencial()
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        frame_cabecalho = ctk.CTkFrame(self, height=40)
        frame_cabecalho.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        frame_cabecalho.grid_propagate(False)
        
        self.aba_cadastro = ctk.CTkButton(
            frame_cabecalho,
            text="Cadastro",
            width=100,
            height=30,
            fg_color="#4CAF50",
            hover_color="#45a049",
            text_color="white",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.mostrar_aba_cadastro
        )
        self.aba_cadastro.pack(side="left", padx=(10, 5), pady=5)
        
        self.aba_anexo = ctk.CTkButton(
            frame_cabecalho,
            text="Anexo",
            width=100,
            height=30,
            fg_color="#9E9E9E",
            hover_color="#757575",
            text_color="white",
            font=ctk.CTkFont(size=14),
            command=self.mostrar_aba_anexo
        )
        self.aba_anexo.pack(side="left", padx=5, pady=5)
        
        frame_botoes = ctk.CTkFrame(frame_cabecalho, fg_color="transparent")
        frame_botoes.pack(side="right", padx=10, pady=5)
        
        botao_cancelar = ctk.CTkButton(
            frame_botoes,
            text="Cancelar",
            width=80,
            height=30,
            fg_color="#f44336",
            hover_color="#da190b",
            text_color="white",
            command=self.destroy
        )
        botao_cancelar.pack(side="right", padx=5)
        
        botao_salvar = ctk.CTkButton(
            frame_botoes,
            text="Salvar",
            width=80,
            height=30,
            fg_color="#4CAF50",
            hover_color="#45a049",
            text_color="white",
            command=self.salvar_produto
        )
        botao_salvar.pack(side="right", padx=5)
        
        self.frame_conteudo = ctk.CTkFrame(self)
        self.frame_conteudo.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.frame_conteudo.grid_columnconfigure(0, weight=1)
        self.frame_conteudo.grid_rowconfigure(0, weight=1)
        
        self.mostrar_aba_cadastro()
        
        if produto:
            self.preencher_campos()
    
    def gerar_codigo_sequencial(self):
        if not self.parent.dados_produtos:
            return "00000001"
        
        codigos = []
        for produto in self.parent.dados_produtos:
            if produto["codigo"].startswith("COD"):
                try:
                    num = int(produto["codigo"][3:])
                    codigos.append(num)
                except ValueError:
                    pass
        
        if not codigos:
            return "00000001"
        
        novo_numero = max(codigos) + 1
        return f"{novo_numero:08d}"
    
    def mostrar_aba_cadastro(self):
        self.aba_cadastro.configure(fg_color="#4CAF50", font=ctk.CTkFont(size=14, weight="bold"))
        self.aba_anexo.configure(fg_color="#9E9E9E", font=ctk.CTkFont(size=14))
        
        for widget in self.frame_conteudo.winfo_children():
            widget.destroy()
            
        frame_principal = ctk.CTkFrame(self.frame_conteudo, fg_color="white")
        frame_principal.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(frame_principal, bg="white", highlightthickness=0)
        barra_rolagem = ttk.Scrollbar(frame_principal, orient="vertical", command=canvas.yview)
        frame_barra_rolagem = ctk.CTkFrame(canvas, fg_color="white")
        
        frame_barra_rolagem.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=frame_barra_rolagem, anchor="nw")
        canvas.configure(yscrollcommand=barra_rolagem.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        barra_rolagem.pack(side="right", fill="y")
        
        frame_principal = ctk.CTkFrame(frame_barra_rolagem, fg_color="white")
        frame_principal.pack(fill="both", expand=True, padx=10, pady=10)
        frame_principal.grid_columnconfigure(0, weight=1)
        frame_principal.grid_columnconfigure(1, weight=1)
        frame_principal.grid_rowconfigure(0, weight=1)
        
        frame_esquerda = ctk.CTkFrame(frame_principal, fg_color="white")
        frame_esquerda.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        
        label_codigo_sequencial = ctk.CTkLabel(frame_esquerda, text="Código Sequencial:", anchor="w", text_color="black")
        label_codigo_sequencial.pack(fill="x", pady=(0, 5))
        
        self.entry_codigo_sequencial = ctk.CTkEntry(
            frame_esquerda, 
            fg_color="#f0f0f0",
            text_color="black",
            state="disabled"
        )
        self.entry_codigo_sequencial.insert(0, self.codigo_sequencial)
        self.entry_codigo_sequencial.pack(fill="x", pady=(0, 10))
        
        label_marca = ctk.CTkLabel(frame_esquerda, text="Marca:", anchor="w", text_color="black")
        label_marca.pack(fill="x", pady=(0, 5))
        
        self.entry_marca = ctk.CTkEntry(frame_esquerda, fg_color="white", text_color="black")
        self.entry_marca.pack(fill="x", pady=(0, 10))
        
        label_valor = ctk.CTkLabel(frame_esquerda, text="Preço Médio (R$):", anchor="w", text_color="black")
        label_valor.pack(fill="x", pady=(0, 5))
        
        self.entry_valor = ctk.CTkEntry(frame_esquerda, fg_color="white", text_color="black")
        self.entry_valor.pack(fill="x", pady=(0, 10))
        
        label_peso = ctk.CTkLabel(frame_esquerda, text="Peso (kg):", anchor="w", text_color="black")
        label_peso.pack(fill="x", pady=(0, 5))
        
        self.entry_peso = ctk.CTkEntry(frame_esquerda, fg_color="white", text_color="black")
        self.entry_peso.pack(fill="x", pady=(0, 10))
        
        label_altura = ctk.CTkLabel(frame_esquerda, text="Altura (cm):", anchor="w", text_color="black")
        label_altura.pack(fill="x", pady=(0, 5))
        
        self.entry_altura = ctk.CTkEntry(frame_esquerda, fg_color="white", text_color="black")
        self.entry_altura.pack(fill="x", pady=(0, 10))
        
        label_largura = ctk.CTkLabel(frame_esquerda, text="Largura (cm):", anchor="w", text_color="black")
        label_largura.pack(fill="x", pady=(0, 5))
        
        self.entry_largura = ctk.CTkEntry(frame_esquerda, fg_color="white", text_color="black")
        self.entry_largura.pack(fill="x", pady=(0, 10))
        
        label_tipo = ctk.CTkLabel(frame_esquerda, text="Tipo de Produto:", anchor="w", text_color="black")
        label_tipo.pack(fill="x", pady=(0, 5))
        
        self.combo_tipo = ctk.CTkComboBox(
            frame_esquerda, 
            values=["Eletrônico", "Mecânico", "Software", "Acessório", "Outro"],
            fg_color="white",
            text_color="black",
            button_color="#d0d0d0",
            button_hover_color="#c0c0c0"
        )
        self.combo_tipo.pack(fill="x", pady=(0, 10))
        
        frame_direita = ctk.CTkFrame(frame_principal, fg_color="white")
        frame_direita.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=10)
        
        label_codigo_editavel = ctk.CTkLabel(frame_direita, text="Código:", anchor="w", text_color="black")
        label_codigo_editavel.pack(fill="x", pady=(0, 5))
        
        self.entry_codigo_editavel = ctk.CTkEntry(frame_direita, fg_color="white", text_color="black")
        self.entry_codigo_editavel.pack(fill="x", pady=(0, 10))
        
        label_nome = ctk.CTkLabel(frame_direita, text="Nome:", anchor="w", text_color="black")
        label_nome.pack(fill="x", pady=(0, 5))
        
        self.entry_nome = ctk.CTkEntry(frame_direita, fg_color="white", text_color="black")
        self.entry_nome.pack(fill="x", pady=(0, 10))
        
        label_grupo = ctk.CTkLabel(frame_direita, text="Grupo de Produto:", anchor="w", text_color="black")
        label_grupo.pack(fill="x", pady=(0, 5))
        
        self.combo_grupo = ctk.CTkComboBox(
            frame_direita, 
            values=["Grupo A", "Grupo B", "Grupo C", "Grupo D"],
            fg_color="white",
            text_color="black",
            button_color="#d0d0d0",
            button_hover_color="#c0c0c0"
        )
        self.combo_grupo.pack(fill="x", pady=(0, 10))
        
        label_estoque = ctk.CTkLabel(frame_direita, text="Estoque:", anchor="w", text_color="black")
        label_estoque.pack(fill="x", pady=(0, 5))
        
        self.combo_estoque = ctk.CTkComboBox(
            frame_direita, 
            values=["Estoque Principal", "Estoque Secundário", "Depósito"],
            fg_color="white",
            text_color="black",
            button_color="#d0d0d0",
            button_hover_color="#c0c0c0"
        )
        self.combo_estoque.pack(fill="x", pady=(0, 10))
        
        label_fornecedor = ctk.CTkLabel(frame_direita, text="Fornecedor:", anchor="w", text_color="black")
        label_fornecedor.pack(fill="x", pady=(0, 5))
        
        self.entry_fornecedor = ctk.CTkEntry(frame_direita, fg_color="white", text_color="black")
        self.entry_fornecedor.pack(fill="x", pady=(0, 10))
        
        label_quantidade_estoque = ctk.CTkLabel(frame_direita, text="Quantidade em Estoque:", anchor="w", text_color="black")
        label_quantidade_estoque.pack(fill="x", pady=(0, 5))
        
        self.entry_quantidade_estoque = ctk.CTkEntry(frame_direita, fg_color="white", text_color="black")
        self.entry_quantidade_estoque.pack(fill="x", pady=(0, 20))
        
        checkbox_frame = ctk.CTkFrame(frame_direita, fg_color="white")
        checkbox_frame.pack(fill="x", pady=(0, 10))
        
        checkbox_esquerdo = ctk.CTkFrame(checkbox_frame, fg_color="white")
        checkbox_esquerdo.pack(side="left", fill="both", expand=True)
        
        checkbox_direito = ctk.CTkFrame(checkbox_frame, fg_color="white")
        checkbox_direito.pack(side="right", fill="both", expand=True)
        
        self.variavel_controle_serie = ctk.BooleanVar()
        self.check_controle_serie = ctk.CTkCheckBox(
            checkbox_esquerdo, 
            text="Controlado por Série",
            variable=self.variavel_controle_serie,
            text_color="black",
            command=self.verificar_series_desmarcadas
        )
        self.check_controle_serie.pack(fill="x", pady=(0, 5))
        
        self.variavel_validade = ctk.BooleanVar()
        self.check_validade = ctk.CTkCheckBox(
            checkbox_esquerdo, 
            text="Por Validade",
            variable=self.variavel_validade,
            text_color="black"
        )
        self.check_validade.pack(fill="x", pady=(0, 5))
        
        self.variavel_inativo = ctk.BooleanVar()
        self.check_inativo = ctk.CTkCheckBox(
            checkbox_direito, 
            text="Inativo",
            variable=self.variavel_inativo,
            text_color="black"
        )
        self.check_inativo.pack(fill="x", pady=(0, 5))
        
        self.variavel_brinde = ctk.BooleanVar()
        self.check_brinde = ctk.CTkCheckBox(
            checkbox_direito, 
            text="Brinde",
            variable=self.variavel_brinde,
            text_color="black"
        )
        self.check_brinde.pack(fill="x", pady=(0, 5))
        
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
    
    def verificar_series_desmarcadas(self):
        if not self.variavel_controle_serie.get() and self.produto:
            codigo_produto = self.produto["codigo"]
            if codigo_produto in self.parent.dados_series and self.parent.dados_series[codigo_produto]:
                resposta = messagebox.askyesno(
                    "Atenção", 
                    "Este produto possui números de série cadastrados.\nDeseja continuar?\033",
                    parent=self
                )
                if not resposta:
                    self.variavel_controle_serie.set(True)
    
    def mostrar_aba_anexo(self):
        self.aba_cadastro.configure(fg_color="#9E9E9E", font=ctk.CTkFont(size=14))
        self.aba_anexo.configure(fg_color="#4CAF50", font=ctk.CTkFont(size=14, weight="bold"))
        
        for widget in self.frame_conteudo.winfo_children():
            widget.destroy()
            
        frame_principal = ctk.CTkFrame(self.frame_conteudo, fg_color="white")
        frame_principal.pack(fill="both", expand=True, padx=10, pady=10)
        
        label_upload_produto_imagem = ctk.CTkLabel(
            frame_principal,
            text="Arraste e solte uma imagem aqui ou clique para selecionar",
            text_color="black",
            font=ctk.CTkFont(size=14)
        )
        label_upload_produto_imagem.place(relx=0.5, rely=0.4, anchor="center")
        
        botao_selecionar = ctk.CTkButton(
            frame_principal,
            text="Selecionar Imagem",
            width=150,
            height=40,
            fg_color="#4CAF50",
            hover_color="#45a049",
            text_color="white"
        )
        botao_selecionar.place(relx=0.5, rely=0.5, anchor="center")
        
        if self.produto and "imagem" in self.produto:
            pass
    
    def preencher_campos(self):
        if not self.produto:
            return
            
        self.entry_codigo_sequencial.configure(state="normal")
        self.entry_codigo_sequencial.delete(0, "end")
        self.entry_codigo_sequencial.insert(0, self.produto.get("codigo_sequencial", ""))
        self.entry_codigo_sequencial.configure(state="disabled")
        
        self.entry_marca.insert(0, self.produto.get("marca", ""))
        self.entry_valor.insert(0, self.produto.get("valor", "").replace("R$ ", ""))
        self.entry_peso.insert(0, self.produto.get("peso", ""))
        self.entry_altura.insert(0, self.produto.get("altura", ""))
        self.entry_largura.insert(0, self.produto.get("largura", ""))
        self.combo_tipo.set(self.produto.get("tipo", ""))
        
        self.entry_codigo_editavel.insert(0, self.produto.get("codigo", "").replace("COD", ""))
        self.entry_nome.insert(0, self.produto.get("nome", ""))
        self.combo_grupo.set(self.produto.get("grupo", ""))
        self.combo_estoque.set(self.produto.get("local_estoque", ""))
        self.entry_fornecedor.insert(0, self.produto.get("fornecedor", ""))
        self.entry_quantidade_estoque.insert(0, self.produto.get("estoque", "").replace(" unidades", ""))
        
        self.variavel_controle_serie.set(self.produto.get("controla_serie", False))
        self.variavel_inativo.set(self.produto.get("inativo", False))
        self.variavel_validade.set(self.produto.get("por_validade", False))
        self.variavel_brinde.set(self.produto.get("brinde", False))
    
    def salvar_edicao_produto(self):
        if (self.produto and 
            self.produto.get("controla_serie", False) and 
            not self.variavel_controle_serie.get() and
            self.produto["codigo"] in self.parent.dados_series and
            self.parent.dados_series[self.produto["codigo"]]):
            
            resposta = messagebox.askyesno(
                "Confirmar", 
                "Este produto possui números de série cadastrados. Deseja continuar?",
                parent=self
            )
            if not resposta:
                return
        
        dados = {
            "codigo_sequencial": self.entry_codigo_sequencial.get(),
            "marca": self.entry_marca.get(),
            "valor": f"R$ {self.entry_valor.get()}",
            "peso": self.entry_peso.get(),
            "altura": self.entry_altura.get(),
            "largura": self.entry_largura.get(),
            "tipo": self.combo_tipo.get(),
            "codigo": f"COD{self.entry_codigo_editavel.get()}" if self.entry_codigo_editavel.get() else f"COD{self.codigo_sequencial}",
            "nome": self.entry_nome.get(),
            "grupo": self.combo_grupo.get(),
            "local_estoque": self.combo_estoque.get(),
            "fornecedor": self.entry_fornecedor.get(),
            "estoque": f"{self.entry_quantidade_estoque.get()} unidades",
            "controla_serie": self.variavel_controle_serie.get(),
            "inativo": self.variavel_inativo.get(),
            "por_validade": self.variavel_validade.get(),
            "brinde": self.variavel_brinde.get(),
            "serie": "✔️" if self.variavel_controle_serie.get() else "❌"
        }
        
        if self.produto:
            for i, produto in enumerate(self.parent.dados_produtos):
                if produto["codigo"] == self.produto["codigo"]:
                    self.parent.dados_produtos[i] = dados
                    break
        else:
            self.parent.dados_produtos.append(dados)
        
        self.parent.salvar_dados_json()
        self.parent.atualizar_treeview_produtos()
        self.destroy()
    
    def preencher_campos(self):
        if not self.produto:
            return
            
        self.entry_codigo_sequencial.configure(state="normal")
        self.entry_codigo_sequencial.delete(0, "end")
        self.entry_codigo_sequencial.insert(0, self.produto.get("codigo_sequencial", ""))
        self.entry_codigo_sequencial.configure(state="disabled")
        
        self.entry_marca.insert(0, self.produto.get("marca", ""))
        self.entry_valor.insert(0, self.produto.get("valor", "").replace("R$ ", ""))
        self.entry_peso.insert(0, self.produto.get("peso", ""))
        self.entry_altura.insert(0, self.produto.get("altura", ""))
        self.entry_largura.insert(0, self.produto.get("largura", ""))
        self.combo_tipo.set(self.produto.get("tipo", ""))
        
        self.entry_codigo_editavel.insert(0, self.produto.get("codigo", "").replace("COD", ""))
        self.entry_nome.insert(0, self.produto.get("nome", ""))
        self.combo_grupo.set(self.produto.get("grupo", ""))
        self.combo_estoque.set(self.produto.get("local_estoque", ""))
        self.entry_fornecedor.insert(0, self.produto.get("fornecedor", ""))
        self.entry_quantidade_estoque.insert(0, self.produto.get("estoque", "").replace(" unidades", ""))
        
        self.variavel_controle_serie.set(self.produto.get("controla_serie", False))
        self.variavel_inativo.set(self.produto.get("inativo", False))
        self.variavel_validade.set(self.produto.get("por_validade", False))
        self.variavel_brinde.set(self.produto.get("brinde", False))
    
    def salvar_produto(self):
        if (self.produto and 
            self.produto.get("controla_serie", False) and 
            not self.variavel_controle_serie.get() and
            self.produto["codigo"] in self.parent.dados_series and
            self.parent.dados_series[self.produto["codigo"]]):
            
            resposta = messagebox.askyesno(
                "Confirmar", 
                "Este produto possui números de série cadastrados. Deseja continuar?",
                parent=self
            )
            if not resposta:
                return  
        
        dados = {
            "codigo_sequencial": self.entry_codigo_sequencial.get(),
            "marca": self.entry_marca.get(),
            "valor": f"R$ {self.entry_valor.get()}",
            "peso": self.entry_peso.get(),
            "altura": self.entry_altura.get(),
            "largura": self.entry_largura.get(),
            "tipo": self.combo_tipo.get(),
            "codigo": f"COD{self.entry_codigo_editavel.get()}" if self.entry_codigo_editavel.get() else f"COD{self.codigo_sequencial}",
            "nome": self.entry_nome.get(),
            "grupo": self.combo_grupo.get(),
            "local_estoque": self.combo_estoque.get(),
            "fornecedor": self.entry_fornecedor.get(),
            "estoque": f"{self.entry_quantidade_estoque.get()} unidades",
            "controla_serie": self.variavel_controle_serie.get(),
            "inativo": self.variavel_inativo.get(),
            "por_validade": self.variavel_validade.get(),
            "brinde": self.variavel_brinde.get(),
            "serie": "✔️" if self.variavel_controle_serie.get() else "❌"
        }
        
        if self.produto:
            for i, produto in enumerate(self.parent.dados_produtos):
                if produto["codigo"] == self.produto["codigo"]:
                    self.parent.dados_produtos[i] = dados
                    break
        else:
            self.parent.dados_produtos.append(dados)
        
        self.parent.salvar_dados_json()
        
        self.parent.atualizar_treeview_produtos()
        
        self.destroy()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Locação de Androides")

        self.after(100, self.maximizar_window)

        try:
            self.banner_imagem = Image.open("banner.png")
        except:
            self.banner_imagem = None

        try:
            self.logo_imagem = Image.open("logo.png")
            self.logo_imagem = self.logo_imagem.resize((100, 100), Image.LANCZOS)  
        except:
            self.logo_imagem = None

        try:
            self.marcadagua_imagem = Image.open("marcadagua.png")
            self.marcadagua_imagem = self.marcadagua_imagem.resize((800, 800), Image.LANCZOS)
            self.marcadagua_ctk_image = ctk.CTkImage(
                light_image=self.marcadagua_imagem,
                size=(800, 800)
            )
        except Exception as e:
            print(f"Erro ao carregar marca d'água: {e}")
            self.marcadagua_ctk_image = None

        self.carregar_dados_json()

        self.produto_selecionado = None
        self.criar_widgets()
        self.atualizar_relogio()

    def carregar_dados_json(self):
        try:
            with open('produtos.json', 'r') as f:
                self.dados_produtos = json.load(f)
        except FileNotFoundError:
            self.dados_produtos = []
            for i in range(1, 21):
                controla_serie = "✔️" if i % 2 == 0 else "❌"
                codigo = f"COD{i:03d}"
                self.dados_produtos.append({
                    "serie": controla_serie,
                    "codigo": codigo,
                    "nome": f"Produto Exemplo {i}",
                    "marca": f"Marca {i % 5 + 1}",
                    "valor": f"R$ {i * 10:.2f}",
                    "estoque": f"{i * 5}"
                })

        try:
            with open('series.json', 'r') as f:
                self.dados_series = json.load(f)
        except FileNotFoundError:
            self.dados_series = {
                "COD002": [
                    {"serie": "SERIE-0001", "alternativa": "ALT-001", "estoque": "Estoque 1", "status": "Ativa"},
                    {"serie": "SERIE-0002", "alternativa": "ALT-002", "estoque": "Estoque 2", "status": "Ativa"},
                    {"serie": "SERIE-0003", "alternativa": "", "estoque": "Estoque 1", "status": "Inativa"}
                ],
                "COD004": [
                    {"serie": "SERIE-0004", "alternativa": "ALT-004", "estoque": "Estoque 1", "status": "Ativa"},
                    {"serie": "SERIE-0005", "alternativa": "", "estoque": "Estoque 3", "status": "Ativa"}
                ],
                "COD006": [
                    {"serie": "SERIE-0006", "alternativa": "ALT-006", "estoque": "Estoque 2", "status": "Ativa"},
                    {"serie": "SERIE-0007", "alternativa": "ALT-007", "estoque": "Estoque 1", "status": "Ativa"},
                    {"serie": "SERIE-0008", "alternativa": "", "estoque": "Estoque 2", "status": "Inativa"},
                    {"serie": "SERIE-0009", "alternativa": "ALT-009", "estoque": "Estoque 3", "status": "Ativa"}
                ]
            }

    def salvar_dados_json(self):
        with open('produtos.json', 'w') as f:
            json.dump(self.dados_produtos, f, indent=4)
        with open('series.json', 'w') as f:
            json.dump(self.dados_series, f, indent=4)

    def maximizar_window(self):
        self.state('zoomed')
    
    def abrir_tela_produto(self, produto=None):
        janela = TelaProduto(self, produto)
        janela.grab_set()  
        janela.focus_set()  
    
    def editar_produto(self):
        selected = self.treeview_produtos.selection()
        if selected:
            item = self.treeview_produtos.item(selected[0])
            valores = item['values']
            
            for produto in self.dados_produtos:
                if produto["codigo"] == valores[1]:  # valores[1] é o código
                    self.abrir_tela_produto(produto)
                    break
    
    def excluir_produto(self):
        selected = self.treeview_produtos.selection()
        if selected:
            item = self.treeview_produtos.item(selected[0])
            valores = item['values']
            codigo = valores[1]  
            
            resposta = messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir o produto {valores[2]}?")
            if resposta:
                for i, produto in enumerate(self.dados_produtos):
                    if produto["codigo"] == codigo:
                        del self.dados_produtos[i]
                        break
                
                if codigo in self.dados_series:
                    del self.dados_series[codigo]
                
                self.salvar_dados_json()
                
                self.atualizar_treeview_produtos()
                
                messagebox.showinfo("Sucesso", "Produto excluído com sucesso!")
        else:
            messagebox.showwarning("Aviso", "Nenhum produto selecionado para excluir.")
    
    def atualizar_treeview_produtos(self):
        for item in self.treeview_produtos.get_children():
            self.treeview_produtos.delete(item)
        
        for produto in self.dados_produtos:
            self.treeview_produtos.insert("", "end", values=(
                produto["serie"],
                produto["codigo"],
                produto["nome"],
                produto["marca"],
                produto["valor"],
                produto["estoque"]
            ))
    
    def pesquisar_produtos(self):
        filtro_entries = [entry.get().lower() for entry in self.filtro_entries]
        
        for item in self.treeview_produtos.get_children():
            self.treeview_produtos.delete(item)
        
        for produto in self.dados_produtos:
            corresponde = True
            for i, filtro in enumerate(filtro_entries):
                if filtro:  
                    campo = ""
                    if i == 0:  
                        campo = produto["serie"].lower()
                    elif i == 1:  
                        campo = produto["codigo"].lower()
                    elif i == 2:  
                        campo = produto["nome"].lower()
                    elif i == 3:  
                        campo = produto.get("grupo", "").lower()
                    elif i == 4:  
                        campo = produto.get("status", "").lower()
                    elif i == 5:  
                        campo = produto["estoque"].lower()
                    elif i == 6:  
                        campo = produto["nome"].lower()
                    elif i == 7:  
                        campo = produto["marca"].lower()
                    
                    if filtro not in campo:
                        corresponde = False
                        break
            
            if corresponde:
                self.treeview_produtos.insert("", "end", values=(
                    produto["serie"],
                    produto["codigo"],
                    produto["nome"],
                    produto["marca"],
                    produto["valor"],
                    produto["estoque"]
                ))
    
    def pesquisar_series(self):
        filtro_entries = [entry.get().lower() for entry in self.filtro_series_entries]
        
        for widget in self.frame_conteudo_abas.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Treeview):
                        treeview_series = child
                        break
        
        for item in treeview_series.get_children():
            treeview_series.delete(item)
        
        if self.produto_selecionado in self.dados_series:
            for serie in self.dados_series[self.produto_selecionado]:
                corresponde = True
                for i, filtro in enumerate(filtro_entries):
                    if filtro:  
                        campo = ""
                        if i == 0:
                            campo = serie["serie"].lower()
                        elif i == 1:
                            campo = serie["alternativa"].lower()
                        elif i == 2:
                            campo = serie["status"].lower()
                        
                        if filtro not in campo:
                            corresponde = False
                            break
                
                if corresponde:
                    treeview_series.insert("", "end", values=(
                        serie["serie"],
                        serie["alternativa"],
                        serie["estoque"],
                        serie["status"]
                    ))
    
    def abrir_ajuda(self):
        try:
            if os.path.exists("COD_GUIDE_LOC.py"):
                subprocess.Popen(["python", "COD_GUIDE_LOC.py"])
            else:
                erro_window = ctk.CTkToplevel(self)
                erro_window.title("Erro")
                erro_window.geometry("300x100")

                erro_label = ctk.CTkLabel(
                    erro_window,
                    text="Arquivo de ajuda não encontrado!\n(COD_GUIDE_LOC.py)",
                    text_color="red"
                )
                erro_label.pack(pady=20)
                
                ok_button = ctk.CTkButton(
                    erro_window,
                    text="OK",
                    command=erro_window.destroy
                )
                ok_button.pack(pady=10)
        except Exception as e:
            print(f"Erro ao abrir arquivo de ajuda: {e}")

    def abrir_sobre_sistema(self):
        try:
            if os.path.exists("COD_ON.py"):
                subprocess.Popen(["python", "COD_ON.py"])
            else:
                erro_window = ctk.CTkToplevel(self)
                erro_window.title("Erro")
                erro_window.geometry("300x100")

                erro_label = ctk.CTkLabel(
                    erro_window,
                    text="Arquivo de ajuda não encontrado!\n(COD_ON.py)",
                    text_color="red"
                )
                erro_label.pack(pady=20)
                
                ok_button = ctk.CTkButton(
                    erro_window,
                    text="OK",
                    command=erro_window.destroy
                )
                ok_button.pack(pady=10)
        except Exception as e:
            print(f"Erro ao abrir arquivo sobre o sistema: {e}")

    def pesquisar_unidade(self):
        for widget in self.area_conteudo.winfo_children():
            widget.destroy()

        titulo_label = ctk.CTkLabel(
            self.area_conteudo,
            text="Buscar Unidade",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="black"
        )
        titulo_label.pack(pady=(10, 20), anchor="w")

        frame_pesquisar = ctk.CTkFrame(self.area_conteudo, fg_color="#ffffff")
        frame_pesquisar.pack(fill="x", pady=10)

        entry_pesquisar = ctk.CTkEntry(
            frame_pesquisar,
            placeholder_text="Pesquisar unidade...",
            fg_color="#ffffff",
            border_color="#c0c0c0",
            text_color="black",
            height=35
        )
        entry_pesquisar.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        botao_pesquisar = ctk.CTkButton(
            frame_pesquisar, 
            text="Buscar", 
            width=80,
            height=35,
            fg_color="#d0d0d0",
            hover_color="#c0c0c0",
            text_color="black"
        )
        botao_pesquisar.pack(side="left")

        info_label = ctk.CTkLabel(
            self.area_conteudo,
            text="Lista de unidades aparecerá aqui",
            font=ctk.CTkFont(size=14),
            text_color="#404040"
        )
        info_label.pack(pady=50)
    
    def editar_unidade(self):
        for widget in self.area_conteudo.winfo_children():
            widget.destroy()

        titulo_label = ctk.CTkLabel(
            self.area_conteudo,
            text="Gerenciar Unidades",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="black"
        )
        titulo_label.pack(pady=(10, 20), anchor="w")

        frame_acao = ctk.CTkFrame(self.area_conteudo, fg_color="#ffffff")
        frame_acao.pack(fill="x", pady=10)

        add_btn = ctk.CTkButton(
            frame_acao,
            text="Adicionar Unidade",
            height=35,
            fg_color="#d0d0d0",
            hover_color="#c0c0c0",
            corner_radius=3,
            text_color="black"
        )
        add_btn.pack(side="left", padx=5)

        edit_btn = ctk.CTkButton(
            frame_acao,
            text="Editar Unidade",
            height=35,
            fg_color="#d0d0d0",
            hover_color="#c0c0c0",
            corner_radius=3,
            text_color="black"
        )
        edit_btn.pack(side="left", padx=5)

        info_label = ctk.CTkLabel(
            self.area_conteudo,
            text="Interface de gerenciamento de unidades aparecerá aqui",
            font=ctk.CTkFont(size=16),
            text_color="#404040"
        )
        info_label.pack(pady=50)

    def apagar_unidade(self):
        self.unit_entry.delete(0, "end")

    def abrir_agenda(self):
        try:
            if os.path.exists("COD_AGENDA.py"):
                subprocess.Popen(["python", "COD_AGENDA.py"])
            else:
                erro_window = ctk.CTkToplevel(self)
                erro_window.title("Erro")
                erro_window.geometry("300x100") 
            
                erro_label = ctk.CTkLabel(
                    erro_window,
                    text="Arquivo de agenda não encontrado!"
                )
                erro_label.pack(pady=20)

                ok_button = ctk.CTkButton(
                    erro_window,
                    text="OK",
                    command=erro_window.destroy
                )
                ok_button.pack(pady=10)
        except Exception as e:
            print(f"Erro ao abrir a agenda: {e}")

    def select_option(self, menu_title, option):
        if menu_title in self.menu_widgets:
            self.menu_widgets[menu_title].set(menu_title)

        if option == "📅Agenda":
            self.abrir_agenda()
            return
        elif option == "📦Produtos":
            self.abrir_tela_produtos()
            return

        for widget in self.area_conteudo.winfo_children():
            widget.destroy()

    def abrir_tela_produtos(self):
        if hasattr(self, 'label_marcadagua'):
            self.label_marcadagua.place_forget()

        for widget in self.area_conteudo.winfo_children():
            widget.destroy()

        frame_produtos = ctk.CTkFrame(self.area_conteudo, fg_color="white")
        frame_produtos.pack(fill="both", expand=True, padx=0, pady=0)

        frame_abas = ctk.CTkFrame(frame_produtos, height=40, fg_color="#f0f0f0")
        frame_abas.pack(fill="x", pady=0)
        frame_abas.pack_propagate(False)
        
        self.aba_produtos = ctk.CTkButton(
            frame_abas,
            text="Produtos",
            width=120,
            height=30,
            fg_color="#4CAF50",
            hover_color="#45a049",
            text_color="white",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.mostrar_aba_produtos
        )
        self.aba_produtos.pack(side="left", padx=(10, 5), pady=5)
        
        self.aba_series = ctk.CTkButton(
            frame_abas,
            text="Séries",
            width=120,
            height=30,
            fg_color="#9E9E9E",
            hover_color="#757575",
            text_color="white",
            font=ctk.CTkFont(size=14),
            command=self.mostrar_aba_series,
            state="disabled"  
        )
        self.aba_series.pack(side="left", padx=5, pady=5)

        frame_cabecario_produtos = ctk.CTkFrame(frame_produtos, height=50, fg_color="#f0f0f0")
        frame_cabecario_produtos.pack(fill="x", pady=0)
        frame_cabecario_produtos.pack_propagate(False)

        btn_novo = ctk.CTkButton(
            frame_cabecario_produtos,
            text="Novo",
            width=80,
            height=30,
            fg_color="#4CAF50",
            hover_color="#54C057",
            border_color="#45a049",
            border_width=2,
            text_color="white",
            command=self.abrir_tela_produto
        )
        btn_novo.pack(side="left", padx=(10, 5), pady=10)

        btn_editar = ctk.CTkButton(
            frame_cabecario_produtos,
            text="Editar",
            width=80,
            height=30,
            fg_color="#2196F3",
            hover_color="#46A4F1",
            border_color="#0b7dda",
            border_width=2,
            text_color="white",
            command=self.editar_produto
        )
        btn_editar.pack(side="left", padx=5, pady=10)

        btn_excluir = ctk.CTkButton(
            frame_cabecario_produtos,
            text="Excluir",
            width=80,
            height=30,
            fg_color="#f44336",
            hover_color="#da190b",
            border_color="#da190b",
            border_width=2,
            text_color="white",
            command=self.excluir_produto
        )
        btn_excluir.pack(side="left", padx=5, pady=10)

        mais_opcoes = ctk.CTkOptionMenu(
            frame_cabecario_produtos,
            values=[
                "⬆Exportar dados", 
                "💾Importar dados",
                "📄Relatório"
            ],
            width=120,
            height=30,
            fg_color="#9E9E9E",
            button_color="#9E9E9E",
            button_hover_color="#9E9E9E",
            dropdown_fg_color="#ffffff",
            dropdown_text_color="black",
            dropdown_hover_color="#f0f0f0",
        )
        mais_opcoes.set("Mais opções")
        mais_opcoes.pack(side="left", padx=5, pady=10)

        espaco_vazio = ctk.CTkFrame(frame_cabecario_produtos, fg_color="transparent")
        espaco_vazio.pack(side="left", fill="x", expand=True)

        btn_sair = ctk.CTkButton(
            frame_cabecario_produtos,
            text="Sair",
            width=80,
            height=30,
            fg_color="#f44336",
            hover_color="#da190b",
            border_color="#da190b",
            border_width=2,
            text_color="white",
            command=self.fechar_tela_produtos
        )
        btn_sair.pack(side="right", padx=10, pady=10)

        self.frame_conteudo_abas = ctk.CTkFrame(frame_produtos, fg_color="white")
        self.frame_conteudo_abas.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.mostrar_aba_produtos()

    def mostrar_aba_produtos(self):
        self.aba_produtos.configure(fg_color="#4CAF50", font=ctk.CTkFont(size=14, weight="bold"))
        self.aba_series.configure(fg_color="#9E9E9E", font=ctk.CTkFont(size=14))
        
        for widget in self.frame_conteudo_abas.winfo_children():
            widget.destroy()
            
        frame_principal = ctk.CTkFrame(self.frame_conteudo_abas, fg_color="white")
        frame_principal.pack(fill="both", expand=True)

        filtros_frame = ctk.CTkFrame(frame_principal, width=250, fg_color="#f9f9f9")
        filtros_frame.pack(side="left", fill="y", padx=(0, 10))
        filtros_frame.pack_propagate(False)

        filtro_label = ctk.CTkLabel(
            filtros_frame,
            text="Filtros",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="black"
        )
        filtro_label.pack(pady=(10, 5))

        campos_filtro = [
            "Série", "Código", "Descrição", "Grupo de produtos", 
            "Status", "Quantidade", "Nome", "Marca"
        ]

        self.filtro_entries = []  

        for campo in campos_filtro:
            campo_frame = ctk.CTkFrame(filtros_frame, fg_color="#e9e9e9", height=40)
            campo_frame.pack(fill="x", pady=2, padx=5)
            campo_frame.pack_propagate(False)

            campo_frame.grid_columnconfigure(0, weight=1)
            
            entry = ctk.CTkEntry(
                campo_frame,
                placeholder_text=campo,
                fg_color="white",
                border_width=1,
                border_color="#c0c0c0",
                height=28,
                text_color="black"
            )
            entry.grid(row=0, column=0, sticky="ew", padx=(2, 0), pady=2)
            self.filtro_entries.append(entry)  
            
            btn_clear = ctk.CTkButton(
                campo_frame,
                text="✕",
                width=28,
                height=28,
                fg_color="#d0d0d0",
                hover_color="#c0c0c0",
                text_color="black",
                corner_radius=5,
                command=lambda e=entry: e.delete(0, 'end')  
            )
            btn_clear.grid(row=0, column=1, padx=(2, 2), pady=2)

        btn_pesquisar = ctk.CTkButton(
            filtros_frame,
            text="🔍 Pesquisar",
            height=35,
            fg_color="#4CAF50",
            hover_color="#45a049",
            text_color="white",
            command=self.pesquisar_produtos
        )
        btn_pesquisar.pack(fill="x", pady=10)

        lista_frame = ctk.CTkFrame(frame_principal, fg_color="white")
        lista_frame.pack(side="right", fill="both", expand=True)

        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure("Treeview.Heading", font=("Roboto", 13, "bold"), background="#ebebeb")
        estilo.configure("Treeview", font=("Segoe UI Emoji", 12))

        colunas = ("serie", "codigo", "nome", "marca", "valor", "estoque")
        self.treeview_produtos = ttk.Treeview(lista_frame, columns=colunas, show="headings", height=20)

        self.treeview_produtos.heading("serie", text="Série")
        self.treeview_produtos.heading("codigo", text="Código")
        self.treeview_produtos.heading("nome", text="Nome")
        self.treeview_produtos.heading("marca", text="Marca")
        self.treeview_produtos.heading("valor", text="Valor")
        self.treeview_produtos.heading("estoque", text="Estoque")

        self.treeview_produtos.column("serie", width=60, anchor="center")
        self.treeview_produtos.column("codigo", width=100, anchor="center")
        self.treeview_produtos.column("nome", width=200, anchor="w")
        self.treeview_produtos.column("marca", width=120, anchor="w")
        self.treeview_produtos.column("valor", width=100, anchor="e")
        self.treeview_produtos.column("estoque", width=80, anchor="center")

        barra_rolagem = ttk.Scrollbar(lista_frame, orient="vertical", command=self.treeview_produtos.yview)
        self.treeview_produtos.configure(yscrollcommand=barra_rolagem.set)
        
        self.treeview_produtos.pack(side="left", fill="both", expand=True)
        barra_rolagem.pack(side="right", fill="y")

        for produto in self.dados_produtos:
            self.treeview_produtos.insert("", "end", values=(
                produto["serie"],
                produto["codigo"],
                produto["nome"],
                produto["marca"],
                produto["valor"],
                produto["estoque"]
            ))
        self.treeview_produtos.bind("<<TreeviewSelect>>", self.on_produto_selecionado)

    def on_produto_selecionado(self, event):
        selected = self.treeview_produtos.selection()
        if selected:
            item = self.treeview_produtos.item(selected[0])
            valores = item['values']
            
            if valores and valores[0] == "✔️":
                self.aba_series.configure(state="normal", fg_color="#4CAF50", hover_color="#45a049")
                self.produto_selecionado = valores[1]  
                for produto in self.dados_produtos:
                    if produto["codigo"] == self.produto_selecionado:
                        self.produto_selecionado_info = produto
                        break
            else:
                self.aba_series.configure(state="disabled", fg_color="#9E9E9E", hover_color="#757575")
                self.produto_selecionado = None
                self.produto_selecionado_info = None

    def mostrar_aba_series(self):
        if not hasattr(self, 'produto_selecionado') or not self.produto_selecionado:
            return
            
        self.aba_produtos.configure(fg_color="#9E9E9E", font=ctk.CTkFont(size=14))
        self.aba_series.configure(fg_color="#4CAF50", font=ctk.CTkFont(size=14, weight="bold"))

        for widget in self.frame_conteudo_abas.winfo_children():
            widget.destroy()
            
        frame_principal = ctk.CTkFrame(self.frame_conteudo_abas, fg_color="white")
        frame_principal.pack(fill="both", expand=True)

        info_frame = ctk.CTkFrame(frame_principal, height=40, fg_color="#e8f5e9")
        info_frame.pack(fill="x", pady=(0, 10))
        info_frame.pack_propagate(False)

        if hasattr(self, 'produto_selecionado_info') and self.produto_selecionado_info:
            info_text = f"Produto selecionado: {self.produto_selecionado_info['nome']} (Código: {self.produto_selecionado_info['codigo']})"
            info_label = ctk.CTkLabel(
                info_frame,
                text=info_text,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#2e7d32"
            )
            info_label.pack(side="left", padx=10, pady=10)

        produto_info = None
        for produto in self.dados_produtos:
            if produto["codigo"] == self.produto_selecionado:
                produto_info = produto
                break

        if produto_info and produto_info["serie"] == "❌":
            mensagem_frame = ctk.CTkFrame(frame_principal, fg_color="white")
            mensagem_frame.pack(fill="both", expand=True)
            
            mensagem_label = ctk.CTkLabel(
                mensagem_frame,
                text="Este produto não é controlado por série",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#757575"
            )
            mensagem_label.place(relx=0.5, rely=0.5, anchor="center")
            return

        filtros_frame = ctk.CTkFrame(frame_principal, width=250, fg_color="#f9f9f9")
        filtros_frame.pack(side="left", fill="y", padx=(0, 10))
        filtros_frame.pack_propagate(False)

        filtro_label = ctk.CTkLabel(
            filtros_frame,
            text="Filtros de Séries",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="black"
        )
        filtro_label.pack(pady=(10, 5))

        campos_filtro = ["Série", "Série Alternativa", "Status"]

        self.filtro_series_entries = []  

        for campo in campos_filtro:
            campo_frame = ctk.CTkFrame(filtros_frame, fg_color="#e9e9e9", height=40)
            campo_frame.pack(fill="x", pady=2, padx=5)
            campo_frame.pack_propagate(False)

            campo_frame.grid_columnconfigure(0, weight=1)
            
            entry = ctk.CTkEntry(
                campo_frame,
                placeholder_text=campo,
                fg_color="white",
                border_width=1,
                border_color="#c0c0c0",
                height=28,
                text_color="black"
            )
            entry.grid(row=0, column=0, sticky="ew", padx=(2, 0), pady=2)
            self.filtro_series_entries.append(entry)  # Adicionar à lista
            
            btn_clear = ctk.CTkButton(
                campo_frame,
                text="✕",
                width=28,
                height=28,
                fg_color="#d0d0d0",
                hover_color="#c0c0c0",
                text_color="black",
                corner_radius=5,
                command=lambda e=entry: e.delete(0, 'end')
            )
            btn_clear.grid(row=0, column=1, padx=(2, 2), pady=2)

        btn_pesquisar_series = ctk.CTkButton(
            filtros_frame,
            text="🔍 Pesquisar",
            height=35,
            fg_color="#4CAF50",
            hover_color="#45a049",
            text_color="white",
            command=self.pesquisar_series
        )
        btn_pesquisar_series.pack(fill="x", pady=10)

        lista_frame = ctk.CTkFrame(frame_principal, fg_color="white")
        lista_frame.pack(side="right", fill="both", expand=True)

        colunas = ("serie", "serie_alternativa", "estoque", "status")
        treeview = ttk.Treeview(lista_frame, columns=colunas, show="headings", height=20)

        treeview.heading("serie", text="Série")
        treeview.heading("serie_alternativa", text="Série Alternativa")
        treeview.heading("estoque", text="Estoque")
        treeview.heading("status", text="Status")

        treeview.column("serie", width=150, anchor="center")
        treeview.column("serie_alternativa", width=150, anchor="center")
        treeview.column("estoque", width=100, anchor="center")
        treeview.column("status", width=100, anchor="center")

        barra_rolagem = ttk.Scrollbar(lista_frame, orient="vertical", command=treeview.yview)
        treeview.configure(yscrollcommand=barra_rolagem.set)
        
        treeview.pack(side="left", fill="both", expand=True)
        barra_rolagem.pack(side="right", fill="y")
        
        if self.produto_selecionado in self.dados_series:
            for serie in self.dados_series[self.produto_selecionado]:
                treeview.insert("", "end", values=(
                    serie["serie"],
                    serie["alternativa"],
                    serie["estoque"],
                    serie["status"]
                ))
        else:
            empty_label = ctk.CTkLabel(
                lista_frame,
                text="Nenhuma série encontrada para este produto",
                font=ctk.CTkFont(size=14),
                text_color="#757575"
            )
            empty_label.place(relx=0.5, rely=0.5, anchor="center")
            
    def fechar_tela_produtos(self):
        for widget in self.area_conteudo.winfo_children():
            widget.destroy()
        
        if hasattr(self, 'label_marcadagua') and self.marcadagua_ctk_image:
            self.label_marcadagua.place(relx=0.5, rely=0.5, anchor="center")
    
    def atualizar_relogio(self):
        now = time.localtime()
        date_str = time.strftime("%d/%m/%Y", now)  
        time_str = time.strftime("%H:%M:%S", now)

        self.date_label.configure(text=date_str)
        self.time_label.configure(text=time_str)

        self.after(1000, self.atualizar_relogio)
    
    def resize_banner(self, event):
        if not hasattr(self, 'banner_label') or self.banner_imagem is None:
            return
            
        available_width = event.width
        available_height = event.height

        if available_width <= 1 or available_height <= 1:
            return

        new_width = available_width
        new_height = available_height

        redimensionamento_img = self.banner_imagem.resize((new_width, new_height), Image.LANCZOS)
        new_image = ctk.CTkImage(
            light_image=redimensionamento_img,
            size=(new_width, new_height)
        )

        self.banner_label.configure(image=new_image)
        self.banner_imagem_atual = new_image

    def criar_widgets(self):
        self.grid_rowconfigure(2, weight=1)  
        self.grid_columnconfigure(0, weight=1) 

        header_frame = ctk.CTkFrame(self, height=110, fg_color="#f2f2f2")  
        header_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        header_frame.grid_propagate(False)  

        """CONFIGURAÇÕES - GRID DO CABEçALHO"""

        header_frame.grid_rowconfigure(0, weight=1)
        header_frame.grid_columnconfigure(0, weight=0)  # Logo
        header_frame.grid_columnconfigure(1, weight=0)  # Usuário
        header_frame.grid_columnconfigure(2, weight=1)  # Espaço vazio
        header_frame.grid_columnconfigure(3, weight=0)  # Relógio
        header_frame.grid_columnconfigure(4, weight=1)  # Espaço vazio
        header_frame.grid_columnconfigure(5, weight=0)  # Botões

        logo_frame = ctk.CTkFrame(header_frame, width=100, height=100, fg_color="#f2f2f2")  
        logo_frame.grid(row=0, column=0, padx=(15, 5), sticky="w", pady=5)  
        logo_frame.grid_propagate(False)

        if self.logo_imagem:
            ctk_logo_imagem = ctk.CTkImage(
                light_image=self.logo_imagem,
                size=(90, 90))  
            logo_label = ctk.CTkLabel(
                logo_frame,
                image=ctk_logo_imagem,
                text=""
            )
            logo_label.pack(expand=True, fill="both")

        user_frame = ctk.CTkFrame(header_frame, fg_color="#f2f2f2")
        user_frame.grid(row=0, column=1, sticky="w", padx=(0, 15), pady=15)  

        user_label = ctk.CTkLabel(
            user_frame,
            text="Usuário:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="black"
        )
        user_label.pack(side="left", padx=(0, 5))

        username_label = ctk.CTkLabel(
            user_frame,
            text="Admin",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="red"
        )
        username_label.pack(side="left")

        clock_frame = ctk.CTkFrame(
            header_frame, 
            fg_color="black", 
            border_color="#a0a0a0", 
            border_width=4, 
            corner_radius=10,
            width=220, 
            height=90  
        )
        clock_frame.grid(row=0, column=3, sticky="", pady=15)
        clock_frame.grid_propagate(False)

        clock_frame.grid_rowconfigure(0, weight=3)  
        clock_frame.grid_rowconfigure(1, weight=1)  
        clock_frame.grid_columnconfigure(0, weight=1)

        self.time_label = tk.Label(
            clock_frame,
            text="00:00:00",
            fg="white",
            bg="black",
            font=("digital-7", 40)  
        )
        self.time_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=(5, 0))

        self.date_label = tk.Label(
            clock_frame,
            text=("Data: 00/00/0000"),
            fg="white",
            bg="black",
            font=("Arial", 14, "bold")  
        )
        self.date_label.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 5))

        self.time_label.config(anchor="center")
        self.date_label.config(anchor="center")

        right_frame = ctk.CTkFrame(header_frame, fg_color="#f2f2f2")
        right_frame.grid(row=0, column=4, sticky="e", padx=15, pady=15)  

        buttons_frame = ctk.CTkFrame(right_frame, fg_color="#f2f2f2")
        buttons_frame.pack(side="top", anchor="e")

        btn_sobre = ctk.CTkButton(
            buttons_frame, 
            text="💡Sobre", 
            width=60,  
            height=30,
            fg_color="#4f8cff", 
            hover_color="#357ae8", 
            text_color="#fff",
            font=("Segoe UI Emoji", 15, "bold"), 
            corner_radius=8, 
            border_color="#357ae8",
            border_width=2,
            command=self.abrir_sobre_sistema  
        )
        btn_sobre.pack(side="left", padx=2)  

        btn_ajuda = ctk.CTkButton(
            buttons_frame, 
            text="❓Ajuda", 
            width=50,  
            height=30,
            fg_color="#ebb000", 
            hover_color="#f1ba13", 
            text_color="#fff",
            font=("Segoe UI Emoji", 15, "bold"), 
            corner_radius=8, 
            border_color="#d19d01",
            border_width=2,
            command=self.abrir_ajuda  
        )
        btn_ajuda.pack(side="left", padx=2) 
        
        btn_sair = ctk.CTkButton(
            buttons_frame, 
            text="❌Sair", 
            command=self.destroy,
            width=48,  
            height=30, 
            fg_color="#e74c3c", 
            hover_color="#c0392b", 
            text_color="#fff",
            font=("Segoe UI Emoji", 15, "bold"), 
            corner_radius=8, 
            border_width=2,
            border_color="#c0392b"
        )
        btn_sair.pack(side="left", padx=2) 

        unit_frame = ctk.CTkFrame(right_frame, fg_color="#f2f2f2", height=40)
        unit_frame.pack(side="top", anchor="e", pady=(10, 0))

        unit_inner_frame = ctk.CTkFrame(unit_frame, fg_color="#9b9b9b")
        unit_inner_frame.pack(side="right", padx=(0, 12))  

        self.unit_entry = ctk.CTkEntry(
            unit_inner_frame,
            placeholder_text="Unidade",
            fg_color="#ffffff",
            border_width=1,
            border_color="#c0c0c0",
            height=28,  
            text_color="black",
            width=120
        )
        self.unit_entry.pack(side="left", fill="x", expand=False, padx=2, pady=2)
        
        btn_clear = ctk.CTkButton(
            unit_inner_frame,
            text="✕",
            width=22,
            height=28,
            fg_color="#d0d0d0",
            hover_color="#c0c0c0",
            text_color="black",
            corner_radius=5,
            command=self.apagar_unidade,
            font=ctk.CTkFont(family="Arial", size=18, weight="bold")
        )
        btn_clear.pack(side="left", padx=(0, 1))

        btn_edit = ctk.CTkButton(
            unit_inner_frame,
            text="⁝",
            width=28,
            height=28,
            fg_color="#d0d0d0",
            hover_color="#c0c0c0",
            text_color="black",
            corner_radius=5,
            command=self.editar_unidade,
            font=ctk.CTkFont(family="Arial", size=16, weight="bold")
        )
        btn_edit.pack(side="left", padx=(0, 1))

        btn_search = ctk.CTkButton(
            unit_inner_frame,
            text="🔍",
            width=12,  
            height=28,  
            fg_color="#d0d0d0",
            hover_color="#c0c0c0",
            text_color="black",
            corner_radius=5,
            command=self.pesquisar_unidade,
            font=ctk.CTkFont(family="Arial", size=16)
        )
        btn_search.pack(side="left")
    
        """INICIO DA LINHA DIVISÓRIA PRINCIPAL"""

        frame_divisoria = ctk.CTkFrame(
            self, 
            height=16,
            fg_color="#b7b7b7",
        )
        frame_divisoria.grid(row=1, column=0, sticky="ew", padx=0, pady=0)
        frame_divisoria.grid_propagate(False)

        frame_degrade = ctk.CTkFrame(
            frame_divisoria, 
            fg_color="#f2f2f2", 
            height=16,
            corner_radius=0,
        )
        frame_degrade.pack(fill="x", side="top", pady=0.003)

        ctk.CTkFrame(
            frame_degrade,
            height=8,
            fg_color="#c5c4c4",
            corner_radius=0,
        ).pack(fill="x", side="top", pady=0)
        
        ctk.CTkFrame(
            frame_degrade,
            height=3,
            fg_color="#b6b4b4",
            corner_radius=0,
            border_width=3,
            border_color="#b6b4b4"
        ).pack(fill="x", side="top", pady=0)
        
        ctk.CTkFrame(
            frame_degrade,
            height=8,
            fg_color="#A2A2A2",
            corner_radius=0
        ).pack(fill="x", side="top", pady=0.003)

        """FIM DA LINHA DIVISÓRIA PRINCIPAL"""

        body_frame = ctk.CTkFrame(self, fg_color="#b7b7b7")
        body_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))

        body_frame.grid_rowconfigure(0, weight=1)
        body_frame.grid_columnconfigure(0, weight=1, uniform="body_cols")  
        body_frame.grid_columnconfigure(1, weight=4, uniform="body_cols") 
        
        sidebar_frame = ctk.CTkFrame(
            body_frame, 
            fg_color="#f9f9f9"
        )
        sidebar_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        sidebar_frame.grid_rowconfigure(0, weight=1)
        sidebar_frame.grid_columnconfigure(0, weight=1)

        menu_container = ctk.CTkFrame(sidebar_frame, fg_color="#f9f9f9", border_color="#c0c0c0", border_width=3, corner_radius=0)
        menu_container.pack(fill="both", expand=True, padx=0, pady=0)

        """ITENS DO MENU LATERAL"""

        menu_items = [
            ("📦 Estoque", [
                "📦Cadastro e Edição de Produtos",
                "📦Controle de Estoque",
                "📦Produtos",
                "📝Contratos de Empréstimo",
                "🔧Manutenção Corretiva/Preventiva",
                "🧰Ordens de Serviço",
                "📄Relatórios",
            ]),
            ("📝 Inventário", [
                "📝Lançamento de Inventário",
                "🔁Atualização de Estoque",
                "📄Relatórios"
            ]),
            ("💰 Faturamento", [
                "💰Faturamento",
                "🧾Tabela de Preço",
                "📊Gráficos",
                "📄Relatórios"
            ]),
            ("👤 Administração", [
                "👤Usuário",
                "👥Grupo de Usuários",
                "📦Controle de Produtos/Estoque",
                "📄Relatórios"
            ]),
            ("🕒 Auditoria", [
                "🕒Ver Auditoria",
                "📄Relatórios"
            ]),
            ("📖 Origem", [
                "👤Cliente",
                "👤Funcionário",
                "👤Fornecedor",
                "📄Relatórios"
            ]),
            ("⚙️ Configurações", [
                "👤Informações pessoais",
                "📡Configurações de APIs",
                "📅Agenda"
            ]),
        ]
        
        """MENU LATERAL"""

        self.menu_widgets = {}
        for text, options in menu_items:
            menu_font = ctk.CTkFont(family="Segoe UI Emoji", size=16, weight="bold")
            dropdown_font = ctk.CTkFont(family="Segoe UI Emoji", size=14)

            menu = ctk.CTkOptionMenu(
                menu_container,
                values=options,
                command=lambda value, t=text: self.select_option(t, value),
                fg_color="#f9f9f9",
                button_color="#f9f9f9",
                button_hover_color="#f9f9f9",
                text_color="black",
                dropdown_text_color="black",
                dropdown_fg_color="#ffffff",
                dropdown_hover_color="#f0f0f0",
                anchor="w",
                height=30,
                width=230,
                font=menu_font,
                dropdown_font=dropdown_font
            )
            menu.set(text)
            menu.pack(fill="x", pady=5, padx=10)
            self.menu_widgets[text] = menu
        
        """INICIO DA LINHA DIVISÓRIA DO MENU"""
        
        frame_divisoria_menu = ctk.CTkFrame(
            menu_container, 
            height=16,
            fg_color="#b7b7b7",
        )
        frame_divisoria_menu.pack(fill="x", pady=0)

        frame_degrade = ctk.CTkFrame(
            frame_divisoria_menu, 
            fg_color="#f9f9f9", 
            height=16,
            corner_radius=0,
        )
        frame_degrade.pack(fill="x", side="top", pady=0.003)
        
        ctk.CTkFrame(
            frame_degrade,
            height=8,
            fg_color="#c5c4c4",
            corner_radius=0,
        ).pack(fill="x", side="top", pady=0)
        
        ctk.CTkFrame(
            frame_degrade,
            height=3,
            fg_color="#b6b4b4",
            corner_radius=0,
            border_width=3,
            border_color="#b6b4b4"
        ).pack(fill="x", side="top", pady=0)
        
        ctk.CTkFrame(
            frame_degrade,
            height=8,
            fg_color="#A2A2A2",
            corner_radius=0
        ).pack(fill="x", side="top", pady=0.003)

        """FIM DA LINHA DIVISÓRIA DO MENU"""

        frame_imagem = ctk.CTkFrame(
            menu_container, 
            fg_color="transparent",  
            corner_radius=0         
        )
        frame_imagem.pack(fill="both", expand=True, padx=0, pady=0)

        self.banner_label = ctk.CTkLabel(
            frame_imagem,
            text="",
            fg_color="transparent",  
            corner_radius=0          
        )
        self.banner_label.pack(fill="both", expand=True, padx=0, pady=0)

        frame_imagem.bind("<Configure>", self.resize_banner)

        if self.banner_imagem:
            self.after(100, lambda: self.resize_banner(
                type('obj', (object,), {'width': frame_imagem.winfo_width(), 'height': frame_imagem.winfo_height()})()
            ))

        frame_conteudo = ctk.CTkFrame(body_frame, fg_color="#ffffff", border_color="#c0c0c0", border_width=3)
        frame_conteudo.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)

        frame_conteudo.grid_rowconfigure(0, weight=1)
        frame_conteudo.grid_columnconfigure(0, weight=1)

        self.frame_marcdagua = ctk.CTkFrame(frame_conteudo, fg_color="white")
        self.frame_marcdagua.grid(row=0, column=0, sticky="nsew")
        self.frame_marcdagua.grid_rowconfigure(0, weight=1)
        self.frame_marcdagua.grid_columnconfigure(0, weight=1)

        self.area_conteudo = ctk.CTkFrame(self.frame_marcdagua, fg_color="white")
        self.area_conteudo.grid(row=0, column=0, sticky="nsew")
        self.area_conteudo.grid_rowconfigure(0, weight=1)
        self.area_conteudo.grid_columnconfigure(0, weight=1)

        if self.marcadagua_ctk_image:
            self.label_marcadagua = ctk.CTkLabel(
                self.frame_marcdagua,
                image=self.marcadagua_ctk_image,
                text="",  
                fg_color="transparent"
            )
            self.label_marcadagua.place(relx=0.5, rely=0.5, anchor="center")

if __name__ == "__main__":
    app = App()
    app.mainloop()