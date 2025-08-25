import os
import tkinter as tk
from tkinter import ttk, Frame, Label, Scrollbar
from PIL import Image, ImageTk
import fitz  # PyMuPDF

class PDFViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Manual do Sistema")
        self.root.geometry("950x720") 
        self.root.resizable(True, True) 
        
        # Variável para armazenar referências das imagens
        self.page_images = []
        
        # Configurar layout principal
        main_frame = Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame para navegação de arquivos (esquerda)
        left_frame = Frame(main_frame, width=280) 
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_frame.pack_propagate(False) 
        
        # Frame para visualização do PDF (direita)
        right_frame = Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Título do sistema
        Label(left_frame, text="Manual do Sistema", 
              font=('Arial', 15, 'bold'), anchor='w', padx=5).pack(fill=tk.X, pady=(0, 15)) 
        
        # Configurar estilo para a treeview
        style = ttk.Style()
        style.configure("Treeview", font=('Arial', 11), rowheight=28) 
        
        # Treeview para navegação de arquivos
        self.tree = ttk.Treeview(left_frame, show="tree", selectmode="browse", style="Treeview")
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar para a treeview
        tree_scroll = Scrollbar(left_frame, orient="vertical", command=self.tree.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        
        # Label para status na parte inferior da janela - SEMPRE FIXA
        self.default_status_text = "Manual Operacional do Sistema de Cadastros e Gerenciamento de Dados."
        self.status = Label(right_frame, text=self.default_status_text, 
                            bd=1, relief=tk.SUNKEN, anchor=tk.W, padx=5, font=('Arial', 10)) 
        self.status.pack(side=tk.BOTTOM, fill=tk.X, pady=(5,0)) 
        
        # Frame para conter o Canvas e sua Scrollbar
        canvas_container_frame = Frame(right_frame)
        canvas_container_frame.pack(fill=tk.BOTH, expand=True) 
        
        # Scrollbar para a visualização do PDF (dentro do novo container)
        self.scrollbar = Scrollbar(canvas_container_frame, orient="vertical")
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y) 
        
        # Canvas para visualização do PDF (dentro do novo container)
        self.canvas = tk.Canvas(canvas_container_frame, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True) 
        
        # Link scrollbar ao canvas
        self.scrollbar.config(command=self.canvas.yview)
        self.canvas.config(yscrollcommand=self.scrollbar.set)
        
        # Frame interno para as páginas do PDF (dentro do canvas)
        self.pdf_frame = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window((0, 0), window=self.pdf_frame, anchor="nw")
        
        # Configurar evento de redimensionamento do canvas para ajustar a largura do pdf_frame
        self.canvas.bind('<Configure>', self.on_canvas_configure) 
        self.pdf_frame.bind("<Configure>", self.on_frame_configure)
        
        # Carregar estrutura de arquivos do diretório "Manual do Sistema"
        self.manual_dir = "Manual do Sistema"

        if os.path.exists(self.manual_dir):
            root_item = self.tree.insert("", "end", text="📁 " + self.manual_dir, 
                                         values=(self.manual_dir, True))
            self.populate_tree(root_item, self.manual_dir)
        else:
            print(f"Diretório '{self.manual_dir}' não encontrado. Por favor, crie-o na mesma pasta do aplicativo.")
        
        # Eventos da Treeview
        self.tree.bind('<<TreeviewSelect>>', self.on_file_select)
        self.tree.bind('<<TreeviewOpen>>', self.on_folder_open)
        self.tree.bind('<<TreeviewClose>>', self.on_folder_close)

    def on_frame_configure(self, event):
        """Atualiza a região de rolagem do canvas quando o pdf_frame muda de tamanho."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        """Ajusta a largura do pdf_frame para preencher o canvas."""
        self.canvas.itemconfigure(self.canvas.winfo_children()[0], width=event.width)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def populate_tree(self, parent, path):
        """Popula a treeview com arquivos e pastas."""
        try:
            items = sorted(os.listdir(path), key=lambda x: (not os.path.isdir(os.path.join(path, x)), x))
            
            for item in items:
                full_path = os.path.join(path, item)
                is_dir = os.path.isdir(full_path) 
                icon = "📁" if is_dir else "📄"
                
                item_id = self.tree.insert(
                    parent, "end", text=f"{icon} {item}", 
                    values=(full_path, is_dir) 
                )
                
                if is_dir:
                    self.tree.insert(item_id, "end", text="Carregando...")
        except Exception as e:
            print(f"Erro ao carregar diretório '{path}': {e}")

    def on_folder_open(self, event):
        """Lida com a abertura de uma pasta na treeview."""
        item_id = self.tree.focus()
        item = self.tree.item(item_id)
        
        if not item['values']: 
            return
            
        path, is_dir = item['values']
        
        if is_dir:
            current_text = item['text']
            if current_text.startswith("📁"):
                new_text = "📂" + current_text[1:]
                self.tree.item(item_id, text=new_text)
            
            children = self.tree.get_children(item_id)
            if children and self.tree.item(children[0])['text'] == "Carregando...":
                self.tree.delete(children[0])
                self.populate_tree(item_id, path)

    def on_folder_close(self, event):
        """Lida com o fechamento de uma pasta na treeview."""
        item_id = self.tree.focus()
        item = self.tree.item(item_id)
        
        if not item['values']:
            return
            
        path, is_dir = item['values']
        
        if is_dir:
            current_text = item['text']
            if current_text.startswith("📂"):
                new_text = "📁" + current_text[1:]
                self.tree.item(item_id, text=new_text)

    def on_file_select(self, event):
        """Lida com a seleção de um item na treeview (arquivo ou pasta)."""
        selected = self.tree.focus()
        if not selected:
            print("DEBUG: Nenhum item selecionado na treeview.")
            return
            
        item = self.tree.item(selected)
        if not item['values']:
            print(f"DEBUG: Item selecionado '{item['text']}' não tem valores associados.")
            return
            
        path, _ = item['values'] 
        
        is_directory_real = os.path.isdir(path) 
        print(f"DEBUG: Item selecionado: Path='{path}', É diretório (da Treeview)={_}, É diretório (revalidado)={is_directory_real}")
        
        if is_directory_real: 
            print("DEBUG: Item selecionado é um diretório (confirmado). Limpando visualizador.)")
            self.clear_viewer() 
            return 
        
        if not path.lower().endswith('.pdf'):
            self.clear_viewer() # Limpa o visualizador se não for PDF
            print(f"DEBUG: Arquivo '{path}' não é um PDF. Limpando visualizador.")
            return 
        
        print(f"DEBUG: Tentando exibir todas as páginas do PDF: {path}")
        self.display_pdf_preview(path) # Renomeada para melhor clareza na função

    def clear_viewer(self):
        """Limpa o visualizador de PDF (remove todas as imagens de página)."""
        for widget in self.pdf_frame.winfo_children():
            widget.destroy()
        self.page_images = [] 
        self.canvas.configure(scrollregion=(0,0,0,0)) 

    def display_pdf_preview(self, file_path):
        """Exibe todas as páginas do PDF no frame de visualização."""
        self.clear_viewer() # Limpa o visualizador antes de carregar um novo PDF
        
        if not os.path.exists(file_path):
            error_msg = f"ERRO: Arquivo não encontrado em '{file_path}'"
            print(error_msg) 
            error_label = Label(self.pdf_frame, text=error_msg, fg="red", 
                                font=('Arial', 10), bg="white")
            error_label.pack(pady=20)
            return

        if not os.path.isfile(file_path):
            error_msg = f"ERRO: '{file_path}' não é um arquivo válido."
            print(error_msg) 
            error_label = Label(self.pdf_frame, text=error_msg, fg="red", 
                                font=('Arial', 10), bg="white")
            error_label.pack(pady=20)
            return
        
        try:
            self.root.update_idletasks() # Força a atualização da UI
            
            doc = fitz.open(file_path)
            num_pages = doc.page_count
            
            if num_pages > 0:
                self.canvas.update_idletasks() # Garante que o canvas tenha o tamanho final
                canvas_width = self.canvas.winfo_width()
                
                if canvas_width < 10: 
                    canvas_width = 600 # Fallback razoável
                
                # Renderizar e exibir cada página
                for i in range(num_pages):
                    page = doc.load_page(i)
                    
                    original_pdf_width = page.rect.width
                    
                    # Calcula o fator de escala para que a largura da pagina caiba no canvas,
                    # e aplica uma pequena margem (0.95) para evitar cortes na borda.
                    scale_factor = (canvas_width / original_pdf_width) * 0.95 if original_pdf_width > 0 else 0.95

                    mat = fitz.Matrix(scale_factor, scale_factor)
                    pix = page.get_pixmap(matrix=mat, alpha=False) 
                    
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    photo_img = ImageTk.PhotoImage(img) 
                    
                    self.page_images.append(photo_img) # Manter referência para evitar garbage collection
                    
                    page_label = Label(self.pdf_frame, image=photo_img, bg="white") 
                    page_label.image = photo_img # Armazenar referência no label
                    page_label.pack(pady=5, fill=tk.X, expand=False) # Cada página preenche a largura, mas não se expande verticalmente
                    
                print(f"DEBUG: Todas as {num_pages} páginas de '{os.path.basename(file_path)}' carregadas.") 
            else:
                print(f"DEBUG: PDF '{os.path.basename(file_path)}' não contém páginas.")
            
            doc.close() 
            
            # Atualizar a região de rolagem após todas as páginas serem empacotadas
            self.pdf_frame.update_idletasks() 
            self.canvas.configure(scrollregion=self.canvas.bbox("all")) 
            
        except fitz.FileDataError as e:
            error_msg = f"ERRO ao ler o PDF (arquivo corrompido ou inválido?): {file_path}\nDetalhes: {str(e)}"
            print(error_msg) 
            error_label = Label(self.pdf_frame, text=error_msg, fg="red", 
                                font=('Arial', 10), bg="white")
            error_label.pack(pady=20)
        except Exception as e:
            error_msg = f"ERRO inesperado ao abrir/exibir o arquivo: {file_path}\nDetalhes: {str(e)}"
            print(error_msg) 
            error_label = Label(self.pdf_frame, text=error_msg, fg="red", 
                                font=('Arial', 10), bg="white")
            error_label.pack(pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFViewerApp(root)
    root.mainloop()