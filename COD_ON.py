import os
import tkinter as tk
from tkinter import ttk, Frame, Label, Scrollbar
from PIL import Image, ImageTk
import fitz  # PyMuPDF

class PDFViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sobre o Sistema")
        self.root.geometry("950x720") 
        self.root.resizable(True, True) 
        
        self.page_images = []
        
        main_frame = Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        left_frame = Frame(main_frame, width=280) 
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_frame.pack_propagate(False) 
        
        right_frame = Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        Label(left_frame, text="Sobre o Sistema", 
              font=('Arial', 15, 'bold'), anchor='w', padx=5).pack(fill=tk.X, pady=(0, 15)) 
        
        style = ttk.Style()
        style.configure("Treeview", font=('Arial', 11), rowheight=28) 
        
        self.tree = ttk.Treeview(left_frame, show="tree", selectmode="browse", style="Treeview")
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        tree_scroll = Scrollbar(left_frame, orient="vertical", command=self.tree.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        
        self.default_status_text = "Sistema de Cadastros e Gerenciamento de Dados | Sistema de Locação de Androides."
        self.status = Label(right_frame, text=self.default_status_text, 
                            bd=1, relief=tk.SUNKEN, anchor=tk.W, padx=5, font=('Arial', 10)) 
        self.status.pack(side=tk.BOTTOM, fill=tk.X, pady=(5,0)) 
        
        canvas_container_frame = Frame(right_frame)
        canvas_container_frame.pack(fill=tk.BOTH, expand=True) 
        
        self.scrollbar = Scrollbar(canvas_container_frame, orient="vertical")
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y) 
        
        self.canvas = tk.Canvas(canvas_container_frame, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True) 
        
        self.scrollbar.config(command=self.canvas.yview)
        self.canvas.config(yscrollcommand=self.scrollbar.set)
        
        self.pdf_frame = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window((0, 0), window=self.pdf_frame, anchor="nw")
        
        self.canvas.bind('<Configure>', self.on_canvas_configure) 
        self.pdf_frame.bind("<Configure>", self.on_frame_configure)
        
        self.load_specific_pdfs()
        
        self.tree.bind('<<TreeviewSelect>>', self.on_file_select)
        
        # Exibir automaticamente o primeiro PDF ao iniciar
        self.display_first_pdf()

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        self.canvas.itemconfigure(self.canvas.winfo_children()[0], width=event.width)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def load_specific_pdfs(self):
        """Carrega os PDFs específicos diretamente na treeview."""
        self.pdf_files = [
            "Sistema de Locação.pdf",
            "Sistema de Cadastro.pdf"
        ]
        
        # Adicionar cada PDF à treeview diretamente (sem item raiz)
        for pdf in self.pdf_files:
            if os.path.exists(pdf):
                self.tree.insert("", "end", text=f"💡 {pdf}", values=(pdf, False))
            else:
                self.tree.insert("", "end", text=f"💡 {pdf} (não encontrado)", values=("", False))

    def display_first_pdf(self):
        """Exibe o primeiro PDF disponível ao iniciar o aplicativo."""
        # Verificar se há pelo menos um PDF válido
        for pdf in self.pdf_files:
            if os.path.exists(pdf):
                self.display_pdf_preview(pdf)
                # Selecionar o item correspondente na treeview
                for item in self.tree.get_children():
                    if pdf in self.tree.item(item)['text']:
                        self.tree.selection_set(item)
                        self.tree.focus(item)
                        break
                return
        
        # Se nenhum PDF for encontrado, exibir mensagem
        error_label = Label(self.pdf_frame, text="Nenhum PDF encontrado!", 
                            fg="red", font=('Arial', 12), bg="white")
        error_label.pack(pady=50)

    def on_file_select(self, event):
        selected = self.tree.focus()
        if not selected:
            return
            
        item = self.tree.item(selected)
        if not item['values']:
            return
            
        path, _ = item['values'] 
        
        # Verificar se é um caminho válido para PDF
        if not path or not path.endswith('.pdf'):
            self.clear_viewer() 
            return 
        
        # Verificar se o arquivo existe
        if not os.path.exists(path):
            self.clear_viewer()
            error_msg = f"ERRO: Arquivo não encontrado: {path}"
            error_label = Label(self.pdf_frame, text=error_msg, fg="red", 
                                font=('Arial', 10), bg="white")
            error_label.pack(pady=20)
            return
        
        # Exibir o PDF selecionado
        self.display_pdf_preview(path)

    def clear_viewer(self):
        """Limpa o visualizador de PDF."""
        for widget in self.pdf_frame.winfo_children():
            widget.destroy()
        self.page_images = [] 
        self.canvas.configure(scrollregion=(0,0,0,0)) 

    def display_pdf_preview(self, file_path):
        """Exibe todas as páginas do PDF no frame de visualização."""
        self.clear_viewer()
        
        try:
            self.root.update_idletasks()
            doc = fitz.open(file_path)
            num_pages = doc.page_count
            
            if num_pages > 0:
                self.canvas.update_idletasks()
                canvas_width = self.canvas.winfo_width()
                
                if canvas_width < 10: 
                    canvas_width = 600
                
                # Renderizar e exibir cada página
                for i in range(num_pages):
                    page = doc.load_page(i)
                    original_pdf_width = page.rect.width
                    
                    # Calcula o fator de escala
                    scale_factor = (canvas_width / original_pdf_width) * 0.95 if original_pdf_width > 0 else 0.95

                    mat = fitz.Matrix(scale_factor, scale_factor)
                    pix = page.get_pixmap(matrix=mat, alpha=False) 
                    
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    photo_img = ImageTk.PhotoImage(img) 
                    
                    self.page_images.append(photo_img)
                    
                    page_label = Label(self.pdf_frame, image=photo_img, bg="white") 
                    page_label.image = photo_img
                    page_label.pack(pady=5, fill=tk.X, expand=False)
            
            doc.close() 
            
            # Atualizar a região de rolagem
            self.pdf_frame.update_idletasks() 
            self.canvas.configure(scrollregion=self.canvas.bbox("all")) 
            
        except Exception as e:
            error_msg = f"ERRO ao abrir o arquivo: {file_path}\n{str(e)}"
            error_label = Label(self.pdf_frame, text=error_msg, fg="red", 
                                font=('Arial', 10), bg="white")
            error_label.pack(pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFViewerApp(root)
    root.mainloop()