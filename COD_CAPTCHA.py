import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import random
import time
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os

ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("blue")

# Configurações da API do Unsplash:
APP_KEY = "qNwenen3u6h3BDhdNqHksvhupYwU9ZbTLQkfUQVVB1k" 
ENDPOINT = "https://api.unsplash.com/search/photos"

class CaptchaApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Verificação de Captcha")
        self.geometry("450x630")
        self.resizable(False, False)
        
        # Variáveis de controle
        self.imagens_selecionadas = []  # Renomeado!
        self.imagens_data = []
        self.tentativas = 0
        self.carregar_temporisador = time.time()
        self.transicao_tema = {
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
        
        self.titulo_label = ctk.CTkLabel(
            self.header_frame, 
            text="Verificação de Captcha",
            font=("Arial", 18, "bold")
            )
        self.titulo_label.pack(pady=5)
        
        self.instrucoes_label = ctk.CTkLabel(
            self.header_frame, 
            text="Selecione todas as imagens que correspondem ao tema:",
            font=("Arial", 14)
            )
        self.instrucoes_label.pack(pady=(0, 10))
        
        self.tema_label = ctk.CTkLabel(
            self.header_frame, 
            text="",
            font=("Arial", 16, "bold"),
            text_color="#3CBDE4")
        self.tema_label.pack(pady=(0, 15))
        
        self.frame_imagens = ctk.CTkFrame(self)
        self.frame_imagens.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.rodape_frame = ctk.CTkFrame(self)
        self.rodape_frame.pack(pady=15, padx=20, fill="x")
        
        self.bt_verificar = ctk.CTkButton(
            self.rodape_frame, 
            text="Verificar", 
            command=self.verificacao,  
            font=("Arial", 14),
            height=35
            )
        self.bt_verificar.pack(side="right", padx=10)

        self.bt_recarregar = ctk.CTkButton(
            self.rodape_frame, 
            text="Recarregar", 
            command=self.novo_desafio,
            font=("Arial", 14),
            fg_color="#2b2b2b",
            height=35
            )
        self.bt_recarregar.pack(side="right")
        
        self.resultado_label = ctk.CTkLabel(
            self.rodape_frame, 
            text="",
            font=("Arial", 14)
            )
        self.resultado_label.pack(side="left", padx=10, fill="x", expand=True)
        
        self.carregando_label = ctk.CTkLabel(self, text="Carregando imagens...", font=("Arial", 14))
        
        # Iniciar novo desafio
        self.novo_desafio()

    def baixando_imagen(self, keyword, is_correct):
        """Baixa uma imagem do Unsplash baseada na palavra-chave"""
        try:
            parametros = {
                "query": keyword,
                "per_page": 1,
                "page": random.randint(1, 10),
                "client_id": APP_KEY
            }
            resposta = requests.get(ENDPOINT, params=parametros)
            data = resposta.json()
            
            if "results" in data and data["results"]:
                url_imagen = data["results"][0]["urls"]["small"]
                img_resposta = requests.get(url_imagen)
                img = Image.open(BytesIO(img_resposta.content))
                
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
        img = Image.new("RGB", (120, 120), self.obter_cor_aleatoria())
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

    def obter_cor_aleatoria(self):
        """Gera uma cor aleatória pastel"""
        r = random.randint(150, 255)
        g = random.randint(150, 255)
        b = random.randint(150, 255)
        return (r, g, b)

    def novo_desafio(self):
        """Cria um desafio de captcha com imagens"""
        # Mostrar mensagem de carregamento
        self.carregando_label.pack(pady=100)
        self.update()
        
        # Resetar variáveis
        self.imagens_selecionadas = []  
        self.imagens_data = []
        self.tentativas += 1
        self.carregar_temporisador = time.time()  
        self.resultado_label.configure(text="")
        
        # Definir tema aleatório de imagens
        temas = list(self.transicao_tema.keys())
        self.tema_atual = random.choice(temas)
        theme_pt = self.transicao_tema[self.tema_atual]
        self.tema_label.configure(text=theme_pt)
        
        # Gerar imagens corretas 
        for _ in range(3):
            img = self.baixando_imagen(self.tema_atual, True)
            self.imagens_data.append({
                "image": img,
                "correct": True
            })
        
        # Gerar imagens incorretas 
        tema_incorreto = [t for t in temas if t != self.tema_atual]
        for _ in range(6):
            theme = random.choice(tema_incorreto)
            img = self.baixando_imagen(theme, False)
            self.imagens_data.append({
                "image": img,
                "correct": False
            })
        
        random.shuffle(self.imagens_data)
        
        # Esconder mensagem de carregamento e exibir imagens
        self.carregando_label.pack_forget()
        self.display_imagens()
        
        # Iniciar verificação de tempo
        self.verifica_tempo()

    def display_imagens(self):
        """Exibe as imagens na interface"""
        # Limpar frame anterior
        for widget in self.frame_imagens.winfo_children():
            widget.destroy()
        
        # Organizar em grid 3x3
        for i, img_data in enumerate(self.imagens_data):
            row, col = divmod(i, 3)
            pil_imagem = img_data["image"]
            ctk_image = ctk.CTkImage(light_image=pil_imagem, size=(110, 110))
            botao = ctk.CTkButton(
                self.frame_imagens,
                image=ctk_image,
                text="",
                width=120,
                height=120,
                fg_color="#2b2b2b",
                hover_color="#3a3a3a",
                border_width=2,
                border_color="#1a1a1a",
                command=lambda idx=i: self.selecionar_imagens(idx)
            )
            botao.grid(row=row, column=col, padx=5, pady=5)

    def selecionar_imagens(self, index):
        """Lida com a seleção de uma imagem pelo usuário"""
        botao = self.frame_imagens.winfo_children()[index]
        
        if index in self.imagens_selecionadas:  # Renomeado!
            # Desselecionar
            self.imagens_selecionadas.remove(index)  # Renomeado!
            botao.configure(border_color="#1a1a1a", fg_color="#2b2b2b")
        else:
            # Selecionar
            self.imagens_selecionadas.append(index)  # Renomeado!
            botao.configure(border_color="#4CC9F0", fg_color="#3a3a3a")

    def verificacao(self):
        """Verifica as seleções do usuário"""
        cronometrando = time.time() - self.carregar_temporisador
        
        # Verificar tempo limite (30 segundos)
        if cronometrando > 30:
            self.resultado_label.configure(text="Tempo esgotado! Tente novamente.", text_color="#e74c3c")
            self.after(2000, self.novo_desafio)
            return
        
        # Verificar número de tentativas
        if self.tentativas >= 3:
            self.resultado_label.configure(text="Muitas tentativas! Tente novamente mais tarde.", text_color="#e74c3c")
            self.after(3000, self.destroy)
            return
        
        # seleções corretas e incorretas
        selecao_correta = 0
        selecao_incorreta = 0
        obrigatorio_selecionar = sum(1 for img in self.imagens_data if img["correct"])
        
        for idx in self.imagens_selecionadas: 
            if self.imagens_data[idx]["correct"]:
                selecao_correta += 1
            else:
                selecao_incorreta += 1
        
        # Verificar resultados
        if selecao_incorreta > 0:
            self.resultado_label.configure(text=f"Seleções incorretas detectadas! Tentativa {self.tentativas}/3", text_color="#e74c3c")
            self.after(2000, self.novo_desafio)
        elif selecao_correta < obrigatorio_selecionar:
            self.resultado_label.configure(text=f"Selecione todas as imagens corretas! Tentativa {self.tentativas}/3", text_color="#f39c12")
            self.after(2000, self.novo_desafio)
        else:
            self.resultado_label.configure(text="Verificação bem-sucedida! Você é humano.", text_color="#2ecc71")
            self.bt_verificar.configure(state="disabled")
            self.bt_recarregar.configure(state="disabled")
            self.after(3000, self.destroy)

    def verifica_tempo (self):
        """Verifica periodicamente se o tempo expirou"""
        cronometrando = time.time() - self.carregar_temporisador  
        tempo_restante = max(0, 30 - int(cronometrando))
        
        if tempo_restante > 0:
            self.titulo_label.configure(text=f"Verificação de Captcha ({tempo_restante}s)")
            self.after(1000, self.verifica_tempo )
        else:
            self.titulo_label.configure(text="Verificação de Captcha")

if __name__ == "__main__":
    app = CaptchaApp()
    app.mainloop()