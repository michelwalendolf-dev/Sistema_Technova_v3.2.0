import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageFilter
import random
import string
import pyttsx3
import threading
import re

class AdvancedCaptchaWindow(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Verificação de Segurança")
        self.geometry("550x500")
        self.resizable(False, False)
        self.configure(fg_color="#f5f7fa")  # Fundo claro suave
        
        # Centralizar a janela
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (550 // 2)
        y = (self.winfo_screenheight() // 2) - (500 // 2)
        self.geometry(f"550x500+{x}+{y}")
        
        # Configurações
        self.attempts = 0
        self.max_attempts = 3
        self.captcha_type = random.choice(["text", "math", "word"])  # Tipos de desafio
        
        # Inicializar o engine de voz
        self.voice_engine = pyttsx3.init()
        
        # Tentar configurar para uma voz mais natural
        voices = self.voice_engine.getProperty('voices')
        for voice in voices:
            if "female" in voice.name.lower() or "zira" in voice.name.lower():
                self.voice_engine.setProperty('voice', voice.id)
                break
        
        self.voice_engine.setProperty('rate', 160)
        self.voice_engine.setProperty('volume', 0.9)
        
        # Variáveis
        self.captcha_text, self.captcha_question = self.generate_captcha()
        
        # Widgets
        self.create_widgets()
        
        # Exibir a imagem CAPTCHA
        self.refresh_captcha()
        
        self.grab_set()  # Tornar a janela modal
    
    def create_widgets(self):
        # Frame principal
        self.main_frame = ctk.CTkFrame(
            self, 
            fg_color="#ffffff",
            corner_radius=12,
            border_width=2,
            border_color="#357ae8"
        )
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        self.title_label = ctk.CTkLabel(
            self.main_frame, 
            text="Verificação de Segurança",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#2d3748"
        )
        self.title_label.pack(pady=(25, 10))
        
        # Instruções
        self.instruction_label = ctk.CTkLabel(
            self.main_frame,
            text=self.captcha_question,
            font=ctk.CTkFont(size=14),
            text_color="#718096"
        )
        self.instruction_label.pack(pady=(0, 15))
        
        # Frame do CAPTCHA
        self.captcha_frame = ctk.CTkFrame(
            self.main_frame, 
            height=130,
            fg_color="#f7fafc",
            corner_radius=10,
            border_width=2,
            border_color="#357ae8"
        )
        self.captcha_frame.pack(fill="x", padx=30, pady=(0, 15))
        self.captcha_frame.pack_propagate(False)
        
        self.captcha_label = ctk.CTkLabel(self.captcha_frame, text="")
        self.captcha_label.pack(expand=True)
        
        # Campo de entrada
        self.entry = ctk.CTkEntry(
            self.main_frame, 
            placeholder_text="Digite sua resposta aqui...",
            font=ctk.CTkFont(size=16),
            height=45,
            corner_radius=8,
            border_width=2,
            border_color="#357ae8"
        )
        self.entry.pack(fill="x", padx=30, pady=(0, 15))
        self.entry.bind("<Return>", lambda e: self.verify_captcha())
        
        # Label de tentativas (acima dos botões)
        self.attempts_label = ctk.CTkLabel(
            self.main_frame,
            text=f"Tentativas restantes: {self.max_attempts - self.attempts}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#e53e3e" if self.max_attempts - self.attempts == 1 else "#d69e2e"
        )
        self.attempts_label.pack(pady=(0, 10))
        
        # Frame de botões
        self.button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.button_frame.pack(fill="x", padx=30, pady=(0, 15))
        
        # Botão de áudio
        self.audio_button = ctk.CTkButton(
            self.button_frame,
            text="🔊 Ouvir Código",
            command=self.speak_captcha,
            height=40,
            fg_color="#357ae8",
            hover_color="#2a65c7",
            font=ctk.CTkFont(size=13, weight="bold"),
            width=120
        )
        self.audio_button.pack(side="left")
        
        # Botão de novo desafio
        self.refresh_button = ctk.CTkButton(
            self.button_frame,
            text="🔄 Novo Desafio",
            command=self.refresh_captcha,
            height=40,
            fg_color="transparent",
            border_width=2,
            text_color="#357ae8",
            border_color="#357ae8",
            hover_color="#ebf2ff",
            font=ctk.CTkFont(size=13),
            width=120
        )
        self.refresh_button.pack(side="left", padx=(10, 0))
        
        # Botão de verificar
        self.submit_button = ctk.CTkButton(
            self.button_frame, 
            text="✅ Verificar", 
            command=self.verify_captcha,
            height=40,
            font=ctk.CTkFont(weight="bold"),
            fg_color="#48bb78",
            hover_color="#38a169",
            width=120
        )
        self.submit_button.pack(side="right")
        
        # Label de resultado (abaixo dos botões)
        self.result_label = ctk.CTkLabel(
            self.main_frame, 
            text="",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.result_label.pack(pady=(0, 20))
    
    def generate_captcha(self):
        """Gera diferentes tipos de CAPTCHA mais difíceis"""
        captcha_type = self.captcha_type
        
        if captcha_type == "text":
            # CAPTCHA de texto mais difícil
            length = random.randint(7, 9)
            # Usar letras maiúsculas, minúsculas e números
            characters = string.ascii_letters + string.digits
            # Remover caracteres ambíguos
            ambiguous_chars = '0Oo1Il'
            for char in ambiguous_chars:
                characters = characters.replace(char, '')
            text = ''.join(random.choices(characters, k=length))
            question = "Digite o texto que aparece na imagem (diferencie maiúsculas de minúsculas):"
            return text, question
            
        elif captcha_type == "math":
            # CAPTCHA matemático mais difícil
            operations = [
                ('+', lambda a, b: a + b),
                ('-', lambda a, b: a - b),
                ('*', lambda a, b: a * b)
            ]
            
            op_symbol, op_func = random.choice(operations)
            
            # Números maiores para operações mais difíceis
            if op_symbol == '*':
                a = random.randint(2, 12)
                b = random.randint(2, 12)
            else:
                a = random.randint(10, 50)
                b = random.randint(5, 49)
            
            # Garantir que não haja números negativos na subtração
            if op_symbol == '-' and a < b:
                a, b = b, a
                
            result = op_func(a, b)
            text = str(result)
            question = f"Resolva: {a} {op_symbol} {b} = ?"
            return text, question
            
        elif captcha_type == "word":
            # CAPTCHA de palavras (mais difícil de automatizar)
            words = ["segurança", "verificação", "acesso", "sistema", "proteção", 
                    "código", "digital", "autenticação", "privacidade", "confidencial"]
            text = random.choice(words)
            # Adicionar alguns números para aumentar a dificuldade
            if random.random() > 0.5:
                text += str(random.randint(1, 9))
            question = "Digite a palavra que aparece na imagem:"
            return text, question
        
        return "ERROR", "Erro ao gerar desafio"
    
    def generate_captcha_image(self):
        """Gera uma imagem CAPTCHA mais difícil sem sombras"""
        width, height = 350, 120
        
        # Criar imagem com fundo claro
        image = Image.new('RGB', (width, height), color='#ffffff')
        draw = ImageDraw.Draw(image)
        
        # Adicionar ruído de fundo mais intenso
        for _ in range(1000):
            x, y = random.randint(0, width), random.randint(0, height)
            size = random.randint(1, 3)
            color = random.choice(['#f7fafc', '#edf2f7', '#e2e8f0'])
            draw.rectangle((x, y, x+size, y+size), fill=color)
        
        # Adicionar mais linhas de interferência
        for _ in range(8):
            x1, y1 = random.randint(0, width), random.randint(0, height)
            x2, y2 = random.randint(0, width), random.randint(0, height)
            color = random.choice(['#e2e8f0', '#cbd5e0', '#a0aec0'])
            draw.line((x1, y1, x2, y2), fill=color, width=1)
        
        # Adicionar círculos de interferência
        for _ in range(5):
            x, y = random.randint(0, width), random.randint(0, height)
            radius = random.randint(5, 15)
            color = random.choice(['#e2e8f0', '#cbd5e0', '#a0aec0'])
            draw.ellipse((x, y, x+radius, y+radius), fill=color)
        
        # Tentar carregar uma fonte moderna e em negrito
        try:
            font = ImageFont.truetype("arialbd.ttf", 36)
        except:
            try:
                font = ImageFont.truetype("Arial", 36)
            except:
                font = ImageFont.load_default()
        
        # Desenhar o texto sem sombra
        text = self.captcha_text
        for i, char in enumerate(text):
            # Cores com bom contraste (escuras sobre fundo claro)
            colors = ['#357ae8', '#2d3748', '#2b6cb0', '#1a365d', '#2c5282']
            color = random.choice(colors)
            
            # Posição com maior variação aleatória
            x = 20 + i * 40 + random.randint(-8, 8)
            y = 40 + random.randint(-10, 10)
            
            # Rotação aleatória mais pronunciada
            angle = random.randint(-20, 20)
            
            # Desenhar o caractere
            char_image = Image.new('RGBA', (45, 55), (0, 0, 0, 0))
            char_draw = ImageDraw.Draw(char_image)
            char_draw.text((10, 5), char, fill=color, font=font)
            
            # Aplicar rotação
            rotated_char = char_image.rotate(angle, expand=1, resample=Image.BICUBIC)
            
            # Colocar o texto diretamente (sem sombra)
            image.paste(rotated_char, (x, y), rotated_char)
        
        # Aplicar um filtro de distorção leve
        image = image.filter(ImageFilter.SMOOTH_MORE)
        
        return image
    
    def display_captcha(self):
        """Exibe a imagem CAPTCHA no label"""
        photo = ImageTk.PhotoImage(self.captcha_image)
        self.captcha_label.configure(image=photo)
        self.captcha_label.image = photo  # Manter uma referência
    
    def refresh_captcha(self):
        """Atualiza o CAPTCHA"""
        self.captcha_type = random.choice(["text", "math", "word"])
        self.captcha_text, self.captcha_question = self.generate_captcha()
        self.instruction_label.configure(text=self.captcha_question)
        self.captcha_image = self.generate_captcha_image()
        self.display_captcha()
        self.entry.delete(0, 'end')
        self.result_label.configure(text="")
        
        # Atualizar contador de tentativas
        remaining = self.max_attempts - self.attempts
        self.attempts_label.configure(
            text=f"Tentativas restantes: {remaining}",
            text_color="#e53e3e" if remaining == 1 else "#d69e2e"
        )
    
    def speak_captcha(self):
        """Faz o texto do CAPTCHA em áudio"""
        def speak():
            try:
                if self.captcha_type == "text":
                    # Para texto, soletrar as letras de forma clara
                    text_to_speak = " ".join(self.captcha_text)
                    self.voice_engine.say(f"O código é: {text_to_speak}")
                elif self.captcha_type == "math":
                    # Para matemática, dizer a pergunta de forma natural
                    question_text = self.captcha_question.replace(":", "").replace("?", "")
                    self.voice_engine.say(f"{question_text}")
                else:
                    # Para palavras, dizer a palavra claramente
                    self.voice_engine.say(f"A palavra é: {self.captcha_text}")
                
                self.voice_engine.runAndWait()
            except Exception as e:
                print(f"Erro ao reproduzir áudio: {e}")
        
        # Executar em uma thread separada para não travar a interface
        thread = threading.Thread(target=speak)
        thread.daemon = True
        thread.start()
    
    def verify_captcha(self):
        """Verifica se o texto digitado corresponde ao CAPTCHA"""
        user_input = self.entry.get().replace(" ", "")
        
        # Para CAPTCHA de texto, diferenciar maiúsculas de minúsculas
        if self.captcha_type == "text":
            user_input = user_input  # Manter caso sensível
        else:
            user_input = user_input.upper()  # Para outros tipos, usar maiúsculas
        
        self.attempts += 1
        remaining = self.max_attempts - self.attempts
        
        # Atualizar contador de tentativas
        self.attempts_label.configure(
            text=f"Tentativas restantes: {remaining}",
            text_color="#e53e3e" if remaining == 1 else "#d69e2e"
        )
        
        if user_input == self.captcha_text:
            self.result_label.configure(text="✓ Verificação bem-sucedida!", text_color="#48bb78")
            self.after(1000, self.destroy)
            return True
        else:
            if self.attempts >= self.max_attempts:
                self.result_label.configure(text="✗ Número máximo de tentativas excedido!", text_color="#e53e3e")
                self.after(2000, self.destroy)
                return False
            else:
                self.result_label.configure(text="✗ Resposta incorreta. Tente novamente.", text_color="#e53e3e")
                self.refresh_captcha()
                return False

if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    # Criar uma janela principal oculta (necessária para o CTkToplevel)
    root = ctk.CTk()
    root.withdraw()
    
    app = AdvancedCaptchaWindow(root)
    app.mainloop()