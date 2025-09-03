import customtkinter as ctk
import os
import tkinter as tk
from tkinter import ttk
import json
import tkinter.messagebox as messagebox

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class TelaProduto(ctk.CTkToplevel):
    def __init__(self, parent=None, produto=None, callback_atualizacao=None):
        super().__init__(parent)
        self.parent = parent
        self.produto = produto
        self.title("Cadastro de Produto" if not produto else "Editar Produto")
        self.callback_atualizacao = callback_atualizacao 

        # Inicializar variáveis BooleanVar primeiro
        self.variavel_controle_serie = ctk.BooleanVar()
        self.variavel_validade = ctk.BooleanVar()
        self.variavel_inativo = ctk.BooleanVar()
        self.variavel_brinde = ctk.BooleanVar()

        # Carregar dados
        self.carregar_dados_json()
        
        # Configurar o ícone
        try:
            ico_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icones//produtos.ico")
            if os.path.exists(ico_path):
                self.after(200, lambda: self.wm_iconbitmap(ico_path))
        except Exception as e:
            print(f"Erro ao carregar ícone: {e}")
            
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
            
        # Configurar para ser modal
        self.transient(parent)
        self.grab_set()
        self.focus()
            
    def carregar_dados_json(self):
        try:
            with open('produtos.json', 'r') as f:
                self.dados_produtos = json.load(f)
        except FileNotFoundError:
            self.dados_produtos = []
            for i in range(1, 21):
                controla_serie = "Sim" if i % 2 == 0 else "Não"
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
                    {"serie": "SERIE-0005", "alternativa": "", "estoque": "Estoque 3", "status": "Inativa"}
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
            
    def gerar_codigo_sequencial(self):
        if not self.dados_produtos:
            return "00000001"
        
        codigos = []
        for produto in self.dados_produtos:
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
        
        # Usar as variáveis BooleanVar já inicializadas
        self.check_controle_serie = ctk.CTkCheckBox(
            checkbox_esquerdo, 
            text="Controlado por Série",
            variable=self.variavel_controle_serie,
            text_color="black",
            command=self.verificar_series_desmarcadas
        )
        self.check_controle_serie.pack(fill="x", pady=(0, 5))
        
        self.check_validade = ctk.CTkCheckBox(
            checkbox_esquerdo, 
            text="Por Validade",
            variable=self.variavel_validade,
            text_color="black"
        )
        self.check_validade.pack(fill="x", pady=(0, 5))
        
        self.check_inativo = ctk.CTkCheckBox(
            checkbox_direito, 
            text="Inativo",
            variable=self.variavel_inativo,
            text_color="black"
        )
        self.check_inativo.pack(fill="x", pady=(0, 5))
        
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
            if codigo_produto in self.dados_series and self.dados_series[codigo_produto]:
                resposta = messagebox.askyesno(
                    "Atenção", 
                    "Este produto possui números de série cadastrados.\nDeseja continuar?",
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
            self.produto["codigo"] in self.dados_series and
            self.dados_series[self.produto["codigo"]]):
            
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
            "serie": "Sim" if self.variavel_controle_serie.get() else "Não"
        }
        
        if self.produto:
            for i, produto in enumerate(self.dados_produtos):
                if produto["codigo"] == self.produto["codigo"]:
                    self.dados_produtos[i] = dados
                    break
        else:
            self.dados_produtos.append(dados)
        
        self.salvar_dados_json()
        self.destroy()
    
    def set_callback(self, callback):
        self.callback = callback
    
    def salvar_produto(self):
        # Verificação de série (apenas para edição)
        if (self.produto and 
            self.produto.get("controla_serie", False) and 
            not self.variavel_controle_serie.get() and
            self.produto["codigo"] in self.dados_series and
            self.dados_series[self.produto["codigo"]]):
            
            resposta = messagebox.askyesno(
                "Confirmar", 
                "Este produto possui números de série cadastrados. Deseja continuar?",
                parent=self
            )
            if not resposta:
                return

        # Coletar dados do formulário
        codigo_editavel = self.entry_codigo_editavel.get()
        codigo = f"COD{codigo_editavel}" if codigo_editavel else f"COD{self.codigo_sequencial}"

        dados = {
            "codigo_sequencial": self.entry_codigo_sequencial.get(),
            "marca": self.entry_marca.get(),
            "valor": f"R$ {self.entry_valor.get()}",
            "peso": self.entry_peso.get(),
            "altura": self.entry_altura.get(),
            "largura": self.entry_largura.get(),
            "tipo": self.combo_tipo.get(),
            "codigo": codigo,
            "nome": self.entry_nome.get(),
            "grupo": self.combo_grupo.get(),
            "local_estoque": self.combo_estoque.get(),
            "fornecedor": self.entry_fornecedor.get(),
            "estoque": f"{self.entry_quantidade_estoque.get()} unidades",
            "controla_serie": self.variavel_controle_serie.get(),
            "inativo": self.variavel_inativo.get(),
            "por_validade": self.variavel_validade.get(),
            "brinde": self.variavel_brinde.get(),
            "serie": "Sim" if self.variavel_controle_serie.get() else "Não"
        }
        
        if self.produto:
            for i, produto in enumerate(self.dados_produtos):
                if produto["codigo"] == self.produto["codigo"]:
                    self.dados_produtos[i] = dados
                    break
        else:
            self.dados_produtos.append(dados)

        self.salvar_dados_json()

        if self.parent and hasattr(self.parent, 'atualizar_treeview_produtos'):
            self.parent.atualizar_treeview_produtos()
        
        if self.callback_atualizacao:
            self.callback_atualizacao()

        self.destroy() 

# Código para executar standalone
if __name__ == "__main__":
    root = ctk.CTk()
    root.withdraw()
    app = TelaProduto(root)
    app.mainloop()
    root.mainloop()
    