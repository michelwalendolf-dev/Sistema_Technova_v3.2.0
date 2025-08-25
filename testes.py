import customtkinter as ctk
import random
import time
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os

ctk.set_appearance_mode("light") 
ctk.set_default_color_theme("blue")

# Configurações da API do Unsplash:
APP_KEY = "qNwenen3u6h3BDhdNqHksvhupYwU9ZbTLQkfUQVVB1k"  # Substitua pela sua chave API
ENDPOINT = "https://api.unsplash.com/search/photos"

class CaptchaApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Verificação de Humanidade")
        self.geometry("450x630")
        self.resizable(False, False)
        
        # Variáveis de controle
        self.selected_images = []
        self.images_data = []
        self.attempts = 0
        self.start_time = time.time()
        self.theme_translation = {
            "car": "carros",
            "tree": "árvores",
            "animal": "animais",
            "building": "edifícios",
            "mountain": "montanhas",
            "ocean": "oceanos",
            "forest": "florestas",
            "flower": "flores"
        }
        
        # Elementos da interface
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.pack(pady=15, padx=20, fill="x")
        
        self.title_label = ctk.CTkLabel(self.header_frame, 
                                       text="Verificação de Humanidade",
                                       font=("Arial", 18, "bold"))
        self.title_label.pack(pady=5)
        
        self.instructions_label = ctk.CTkLabel(self.header_frame, 
                                             text="Selecione todas as imagens que correspondem ao tema:",
                                             font=("Arial", 14))
        self.instructions_label.pack(pady=(0, 10))
        
        self.theme_label = ctk.CTkLabel(self.header_frame, 
                                      text="",
                                      font=("Arial", 16, "bold"),
                                      text_color="#4CC9F0")
        self.theme_label.pack(pady=(0, 15))
        
        self.images_frame = ctk.CTkFrame(self)
        self.images_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.footer_frame = ctk.CTkFrame(self)
        self.footer_frame.pack(pady=15, padx=20, fill="x")
        
        self.verify_button = ctk.CTkButton(self.footer_frame, 
                                          text="Verificar", 
                                          command=self.verify,
                                          font=("Arial", 14),
                                          height=35)
        self.verify_button.pack(side="right", padx=10)
        
        self.reset_button = ctk.CTkButton(self.footer_frame, 
                                         text="Recarregar", 
                                         command=self.new_challenge,
                                         font=("Arial", 14),
                                         fg_color="#2b2b2b",
                                         height=35)
        self.reset_button.pack(side="right")
        
        self.resultado_label = ctk.CTkLabel(self.footer_frame, 
                                        text="",
                                        font=("Arial", 14))
        self.resultado_label.pack(side="left", padx=10, fill="x", expand=True)
        
        self.loading_label = ctk.CTkLabel(self, text="Carregando imagens...", font=("Arial", 14))
        
        # Iniciar novo desafio
        self.new_challenge()

    def download_image(self, keyword, is_correct):
        """Baixa uma imagem do Unsplash baseada na palavra-chave"""
        try:
            params = {
                "query": keyword,
                "per_page": 1,
                "page": random.randint(1, 10),
                "client_id": APP_KEY
            }
            response = requests.get(ENDPOINT, params=params)
            data = response.json()
            
            if "results" in data and data["results"]:
                image_url = data["results"][0]["urls"]["small"]
                img_response = requests.get(image_url)
                img = Image.open(BytesIO(img_response.content))
                
                # Redimensionar para 120x120 mantendo proporções
                img.thumbnail((120, 120))
                
                # Criar nova imagem com fundo branco
                criar_img = Image.new("RGB", (120, 120), (255, 255, 255))
                criar_img.paste(img, ((120 - img.width) // 2, (120 - img.height) // 2))
                
                return criar_img
        except Exception as e:
            print(f"Erro ao baixar imagem: {e}")
        
        # Fallback: criar imagem simples
        return self.create_fallback_image(keyword, is_correct)

    def create_fallback_image(self, keyword, is_correct):
        """Cria uma imagem de fallback caso o download falhe"""
        img = Image.new("RGB", (120, 120), self.get_random_color())
        draw = ImageDraw.Draw(img)
        
        try:
            fonte = ImageFont.truetype("arial.ttf", 14)
        except:
            fonte = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), keyword, font=fonte)
        text_largura = bbox[2] - bbox[0]
        text_altura = bbox[3] - bbox[1]
        posicao = ((120 - text_largura) // 2, (120 - text_altura) // 2)

        cor = "#2ecc71" if is_correct else "#e74c3c"
        draw.text(posicao, keyword, font=fonte, fill=cor)

        return img

    def get_random_color(self):
        """Gera uma cor aleatória pastel"""
        r = random.randint(150, 255)
        g = random.randint(150, 255)
        b = random.randint(150, 255)
        return (r, g, b)

    def new_challenge(self):
        """Cria um desafio de captcha com imagens reais"""
        # Mostrar mensagem de carregamento
        self.loading_label.pack(pady=100)
        self.update()
        
        # Resetar variáveis
        self.selected_images = []
        self.images_data = []
        self.attempts += 1
        self.iniciar_temporizador = time.time()
        self.resultado_label.configure(text="")
        
        # Definir tema aleatório (em inglês para a API)
        themes = list(self.theme_translation.keys())
        self.current_theme = random.choice(themes)
        theme_pt = self.theme_translation[self.current_theme]
        self.theme_label.configure(text=theme_pt)
        
        # Gerar imagens corretas (3)
        for _ in range(3):
            img = self.download_image(self.current_theme, True)
            self.images_data.append({
                "image": img,
                "correct": True
            })
        
        # Gerar imagens incorretas (6)
        incorrect_themes = [t for t in themes if t != self.current_theme]
        for _ in range(6):
            theme = random.choice(incorrect_themes)
            img = self.download_image(theme, False)
            self.images_data.append({
                "image": img,
                "correct": False
            })
        
        random.shuffle(self.images_data)
        
        # Esconder mensagem de carregamento e exibir imagens
        self.loading_label.pack_forget()
        self.display_images()
        
        # Iniciar verificação de tempo
        self.check_timeout()

    def display_images(self):
        """Exibe as imagens na interface"""
        # Limpar frame anterior
        for widget in self.images_frame.winfo_children():
            widget.destroy()
        
        # Organizar em grid 3x3
        for i, img_data in enumerate(self.images_data):
            row, col = divmod(i, 3)
            
            # Converter PIL Image para CTkImage
            pil_image = img_data["image"]
            ctk_image = ctk.CTkImage(light_image=pil_image, size=(110, 110))
            
            # Criar botão com imagem
            btn = ctk.CTkButton(
                self.images_frame,
                image=ctk_image,
                text="",
                width=120,
                height=120,
                fg_color="#2b2b2b",
                hover_color="#3a3a3a",
                border_width=2,
                border_color="#1a1a1a",
                command=lambda idx=i: self.select_image(idx)
            )
            btn.grid(row=row, column=col, padx=5, pady=5)

    def select_image(self, index):
        """Lida com a seleção de uma imagem pelo usuário"""
        button = self.images_frame.winfo_children()[index]
        
        if index in self.selected_images:
            # Desselecionar
            self.selected_images.remove(index)
            button.configure(border_color="#1a1a1a", fg_color="#2b2b2b")
        else:
            # Selecionar
            self.selected_images.append(index)
            button.configure(border_color="#4CC9F0", fg_color="#3a3a3a")

    def verify(self):
        """Verifica as seleções do usuário"""
        elapsed = time.time() - self.start_time
        
        # Verificar tempo limite (30 segundos)
        if elapsed > 30:
            self.resultado_label.configure(text="Tempo esgotado! Tente novamente.", text_color="#e74c3c")
            self.after(2000, self.new_challenge)
            return
        
        # Verificar número de tentativas
        if self.attempts >= 3:
            self.resultado_label.configure(text="Muitas tentativas! Tente novamente mais tarde.", text_color="#e74c3c")
            self.after(3000, self.destroy)
            return
        
        # Contar seleções corretas e incorretas
        correct_count = 0
        incorrect_count = 0
        required_correct = sum(1 for img in self.images_data if img["correct"])
        
        for idx in self.selected_images:
            if self.images_data[idx]["correct"]:
                correct_count += 1
            else:
                incorrect_count += 1
        
        # Verificar resultados
        if incorrect_count > 0:
            self.resultado_label.configure(text=f"Seleções incorretas detectadas! Tentativa {self.attempts}/3", text_color="#e74c3c")
            self.after(2000, self.new_challenge)
        elif correct_count < required_correct:
            self.resultado_label.configure(text=f"Selecione todas as imagens corretas! Tentativa {self.attempts}/3", text_color="#f39c12")
            self.after(2000, self.new_challenge)
        else:
            self.resultado_label.configure(text="Verificação bem-sucedida! Você é humano.", text_color="#2ecc71")
            self.verify_button.configure(state="disabled")
            self.reset_button.configure(state="disabled")
            self.after(3000, self.destroy)

    def check_timeout(self):
        """Verifica periodicamente se o tempo expirou"""
        elapsed = time.time() - self.start_time
        remaining = max(0, 30 - int(elapsed))
        
        if remaining > 0:
            self.title_label.configure(text=f"Verificação de Humanidade ({remaining}s)")
            self.after(1000, self.check_timeout)
        else:
            self.title_label.configure(text="Verificação de Humanidade")

if __name__ == "__main__":
    app = CaptchaApp()
    app.mainloop()