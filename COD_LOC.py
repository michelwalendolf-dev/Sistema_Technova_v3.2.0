import customtkinter as ctk
import time
from PIL import Image, ImageTk
import os
import tkinter as tk
import subprocess
from tkinter import ttk
import json
import tkinter.messagebox as messagebox

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.iconbitmap("icones//logo.ico")
        self.title("Sistema de Locação")

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

        # Carregar imagens para série (sim e não) - manter como atributos
        self.tk_images = []  # Lista para manter as referências das imagens
        try:
            img_sim = Image.open(os.path.join("Icones", "sim.ico"))
            img_nao = Image.open(os.path.join("Icones", "nao.ico"))

            # Redimensionar se necessário
            img_sim = img_sim.resize((20, 20), Image.LANCZOS)
            img_nao = img_nao.resize((20, 20), Image.LANCZOS)
            
            # Converter para formato Tkinter e manter como atributos
            self.tk_img_sim = ImageTk.PhotoImage(img_sim)
            self.tk_img_nao = ImageTk.PhotoImage(img_nao)
            
            # Manter referências na lista
            self.tk_images.extend([self.tk_img_sim, self.tk_img_nao])
        except Exception as e:
            print(f"Erro ao carregar imagens de série: {e}")
            self.tk_img_sim = None
            self.tk_img_nao = None

        self.carregar_dados_json()

        self.produto_selecionado = None
        self.criar_widgets()
        self.atualizar_relogio()
        self.tela_produto = None

    def carregar_dados_json(self):
        try:
            with open('produtos.json', 'r') as f:
                self.dados_produtos = json.load(f)
        except FileNotFoundError:
            self.dados_produtos = []
            for i in range(1, 21):
                controla_serie = "Sim" if i % 2 == 0 else "Não"
                codigo = f"{i:03d}"
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
        if hasattr(self, 'tela_produto') and self.tela_produto is not None and self.tela_produto.winfo_exists():
            self.tela_produto.lift()
            self.tela_produto.focus()
            return
            
        try:
            from COD_EDIT_PRODUTO import TelaProduto
            tela_produto = TelaProduto(self, produto=produto, callback_atualizacao=self.atualizar_treeview_produtos)
            tela_produto.transient(self)
            tela_produto.grab_set()
            tela_produto.focus()
            self.wait_window(tela_produto)
            self.atualizar_treeview_produtos()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir editor de produtos: {e}")
        finally:
            if hasattr(self, 'tela_produto'):
                self.tela_produto = None
    
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

        self.carregar_dados_json()
        
        for produto in self.dados_produtos:
            if produto["serie"] == "Sim":
                imagem = self.tk_img_sim
            else:
                imagem = self.tk_img_nao
                
            self.treeview_produtos.insert("", "end", values=(
                "",  # Deixamos vazio porque vamos usar a imagem
                produto["codigo"],
                produto["nome"],
                produto["marca"],
                produto["valor"],
                produto["estoque"]
            ), image=imagem)
    
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
                # Determinar a imagem com base no valor de "serie"
                if produto["serie"] == "Sim":
                    imagem = self.tk_img_sim
                else:
                    imagem = self.tk_img_nao
                    
                self.treeview_produtos.insert("", "end", values=(
                    "",  # Deixamos vazio porque vamos usar a imagem
                    produto["codigo"],
                    produto["nome"],
                    produto["marca"],
                    produto["valor"],
                    produto["estoque"]
                ), image=imagem)
    
    def pesquisar_series(self):
        filtro_entries = [entry.get().lower() for entry in self.filtro_series_entries]
        
        for item in self.treeview_series.get_children():
            self.treeview_series.delete(item)
        
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
                    self.treeview_series.insert("", "end", values=(
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

        frame_cabecario_produtos = ctk.CTkFrame(frame_produtos, height=50, fg_color="#f0f0f0", corner_radius=0)
        frame_cabecario_produtos.pack(fill="x", pady=0)
        frame_cabecario_produtos.pack_propagate(False)

        btn_novo = ctk.CTkButton(
            frame_cabecario_produtos,
            text="Novo",
            width=80,
            height=30,
            fg_color="#4CAF50",
            hover_color="#54C057",
            border_color="#429647",
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
            font=ctk.CTkFont(family="Segoe UI Emoji", size=12),
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

        # Notebook para as abas
        self.notebook_produtos = ttk.Notebook(frame_produtos)
        self.notebook_produtos.pack(fill="both", expand=True, padx=10, pady=10)

        # Frame para a aba de Produtos
        self.frame_aba_produtos = ctk.CTkFrame(self.notebook_produtos, fg_color="white")
        self.notebook_produtos.add(self.frame_aba_produtos, text="Produtos")

        # Frame para a aba de Séries
        self.frame_aba_series = ctk.CTkFrame(self.notebook_produtos, fg_color="white")
        self.notebook_produtos.add(self.frame_aba_series, text="Séries")
        
        # Inicialmente desabilitar a aba de séries
        self.notebook_produtos.tab(1, state="disabled")

        # Construir o conteúdo das abas
        self.construir_aba_produtos()
        self.construir_aba_series()

    def construir_aba_produtos(self):
        frame_principal = ctk.CTkFrame(self.frame_aba_produtos, fg_color="white")
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
            text="Pesuisar🔎",
            height=35,
            width=120,
            font=ctk.CTkFont(family="Segoe UI Emoji", size=20, weight="bold"),
            fg_color="#4CAF50",
            hover_color="#54C057",
            border_color="#429647",
            border_width=2,
            text_color="white",
            command=self.pesquisar_produtos
        )
        btn_pesquisar.pack(pady=10)

        lista_frame = ctk.CTkFrame(frame_principal, fg_color="white")
        lista_frame.pack(side="right", fill="both", expand=True)

        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure("Treeview.Heading", font=("Roboto", 13, "bold"), background="#ebebeb")
        estilo.configure("Treeview", font=("Segoe UI Emoji", 12), background="white", fieldbackground="white", foreground="black")

        colunas = ("serie", "codigo", "nome", "marca", "valor", "estoque")
        self.treeview_produtos = ttk.Treeview(lista_frame, columns=colunas, show="headings", height=20)

        self.treeview_produtos.heading("serie", text="Série")
        self.treeview_produtos.heading("codigo", text="Cod. Produto")
        self.treeview_produtos.heading("nome", text="Descrição")
        self.treeview_produtos.heading("marca", text="Marca")
        self.treeview_produtos.heading("valor", text="Valor")
        self.treeview_produtos.heading("estoque", text="Qtde. Estoque")

        self.treeview_produtos.column("serie", width=60, anchor="center", stretch=False)
        self.treeview_produtos.column("codigo", width=100, anchor="center")
        self.treeview_produtos.column("nome", width=200, anchor="w")
        self.treeview_produtos.column("marca", width=120, anchor="w")
        self.treeview_produtos.column("valor", width=100, anchor="w")
        self.treeview_produtos.column("estoque", width=80, anchor="center")

        barra_rolagem = ttk.Scrollbar(lista_frame, orient="vertical", command=self.treeview_produtos.yview)
        self.treeview_produtos.configure(yscrollcommand=barra_rolagem.set)
        
        self.treeview_produtos.pack(side="left", fill="both", expand=True)
        barra_rolagem.pack(side="right", fill="y")

        for produto in self.dados_produtos:
            if produto["serie"] == "Sim":
                imagem = self.tk_img_sim
            else:
                imagem = self.tk_img_nao
                
            self.treeview_produtos.insert("", "end", values=(
                "",  # Deixamos vazio porque vamos usar a imagem
                produto["codigo"],
                produto["nome"],
                produto["marca"],
                produto["valor"],
                produto["estoque"]
            ), image=imagem)
        self.treeview_produtos.bind("<<TreeviewSelect>>", self.on_produto_selecionado)
        self.treeview_produtos.bind("<Double-Button-1>", self.abrir_edicao_duplo_clique)
        
    def abrir_edicao_duplo_clique(self, event):
        item_selecionado = self.treeview_produtos.selection()
        if item_selecionado:
            item = self.treeview_produtos.item(item_selecionado[0])
            valores = item['values']
            codigo = valores[1]  

            for produto in self.dados_produtos:
                if produto["codigo"] == codigo:
                    self.abrir_tela_produto(produto)
                    break

    def construir_aba_series(self):
        for widget in self.frame_aba_series.winfo_children():
            widget.destroy()
            
        frame_principal = ctk.CTkFrame(self.frame_aba_series, fg_color="white")
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

        if produto_info and produto_info["serie"] == "Não":
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
            text="Filtros",
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

        colunas = ("serie", "serie_alternativa", "produto", "estoque", "status", "contrato")
        self.treeview_series = ttk.Treeview(lista_frame, columns=colunas, show="headings", height=20)

        self.treeview_series.heading("serie", text="Série")
        self.treeview_series.heading("serie_alternativa", text="Série Alternativa")
        self.treeview_series.heading("produto", text="Produto")
        self.treeview_series.heading("estoque", text="Estoque")
        self.treeview_series.heading("status", text="Status")
        self.treeview_series.heading("contrato", text="Contrato")

        self.treeview_series.column("serie", width=150, anchor="center")
        self.treeview_series.column("serie_alternativa", width=150, anchor="center")
        self.treeview_series.column("estoque", width=100, anchor="center")
        self.treeview_series.column("produto", width=200, anchor="w")
        self.treeview_series.column("status", width=100, anchor="center")
        self.treeview_series.column("contrato", width=100, anchor="center")
        

        barra_rolagem = ttk.Scrollbar(lista_frame, orient="vertical", command=self.treeview_series.yview)
        self.treeview_series.configure(yscrollcommand=barra_rolagem.set)
        
        self.treeview_series.pack(side="left", fill="both", expand=True)
        barra_rolagem.pack(side="right", fill="y")
        
        if self.produto_selecionado in self.dados_series:
            for serie in self.dados_series[self.produto_selecionado]:
                self.treeview_series.insert("", "end", values=(
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

    def on_produto_selecionado(self, event):
        selected = self.treeview_produtos.selection()
        if selected:
            item = self.treeview_produtos.item(selected[0])
            valores = item['values']
            codigo = valores[1]  # O código está na segunda coluna (índice 1)
            
            # Encontrar o produto pelo código
            for produto in self.dados_produtos:
                if produto["codigo"] == codigo:
                    if produto["serie"] == "Sim":
                        # Habilitar a aba de séries
                        self.notebook_produtos.tab(1, state="normal")
                        self.produto_selecionado = codigo
                        self.produto_selecionado_info = produto
                        # Atualizar a aba de séries
                        self.construir_aba_series()
                    else:
                        # Desabilitar a aba de séries
                        self.notebook_produtos.tab(1, state="disabled")
                        self.produto_selecionado = None
                        self.produto_selecionado_info = None
                    break

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

        header_frame.grid_rowconfigure(0, weight=1)
        header_frame.grid_columnconfigure(0, weight=0)  
        header_frame.grid_columnconfigure(1, weight=0)  
        header_frame.grid_columnconfigure(2, weight=1)  
        header_frame.grid_columnconfigure(3, weight=0)  
        header_frame.grid_columnconfigure(4, weight=1)  
        header_frame.grid_columnconfigure(5, weight=0)  

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
    
        frame_divisoria = ctk.CTkFrame(
            self, 
            height=16,
            fg_color="#b6b4b4",
            corner_radius=0
        )
        frame_divisoria.grid(row=1, column=0, sticky="ew", padx=0, pady=0)
        frame_divisoria.grid_propagate(False)

        frame_degrade = ctk.CTkFrame(
            frame_divisoria, 
            fg_color="#b6b4b4", 
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
        
        frame_divisoria_menu = ctk.CTkFrame(
            menu_container, 
            height=16,
            fg_color="#b6b4b4",
            corner_radius=0
        )
        frame_divisoria_menu.pack(fill="x", pady=0)

        frame_degrade = ctk.CTkFrame(
            frame_divisoria_menu, 
            fg_color="#b6b4b4", 
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