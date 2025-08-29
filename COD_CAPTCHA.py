import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageFilter
import random
import string
import pyttsx3
import threading
import time

class RefinedCaptchaWindow(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Verificação de Segurança")
        self.geometry("500x500")
        self.resizable(False, False)
        self.configure(fg_color="#f8f9fa")
        
        # Centralizar a janela
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.winfo_screenheight() // 2) - (500 // 2)
        self.geometry(f"500x500+{x}+{y}")
        
        # Configurações
        self.attempts = 0
        self.max_attempts = 3
        self.captcha_type = random.choice(["text", "math", "word"])
        
        # Variáveis
        self.captcha_text, self.captcha_question = self.generate_captcha()
        
        # Widgets
        self.create_widgets()
        
        # Exibir a imagem CAPTCHA
        self.refresh_captcha()
        
        self.grab_set()

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
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#2d3748"
        )
        self.title_label.pack(pady=(20, 10))
        
        # Label de tentativas
        self.attempts_label = ctk.CTkLabel(
            self.main_frame,
            text=f"Tentativas restantes: {self.max_attempts - self.attempts}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#e53e3e" if self.max_attempts - self.attempts == 1 else "#d69e2e"
        )
        self.attempts_label.pack(pady=(0, 5))
        
        # Instruções
        self.instruction_label = ctk.CTkLabel(
            self.main_frame,
            text=self.captcha_question,
            font=ctk.CTkFont(size=13),
            text_color="#718096"
        )
        self.instruction_label.pack(pady=(0, 10))
        
        # Frame do CAPTCHA
        self.captcha_frame = ctk.CTkFrame(
            self.main_frame, 
            height=120,
            fg_color="#f7fafc",
            corner_radius=8,
            border_width=2,
            border_color="#357ae8"
        )
        self.captcha_frame.pack(fill="x", padx=25, pady=(0, 15))
        self.captcha_frame.pack_propagate(False)
        
        self.captcha_label = ctk.CTkLabel(self.captcha_frame, text="")
        self.captcha_label.pack(expand=True)
        
        # Campo de entrada
        self.entry = ctk.CTkEntry(
            self.main_frame, 
            placeholder_text="Digite sua resposta aqui...",
            font=ctk.CTkFont(size=14),
            height=40,
            corner_radius=8,
            border_width=2,
            border_color="#357ae8"
        )
        self.entry.pack(fill="x", padx=25, pady=(0, 15))
        self.entry.bind("<Return>", lambda e: self.verify_captcha())
        
        # Frame de botões (agora centralizado)
        self.button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.button_frame.pack(fill="x", padx=25, pady=(0, 10))
        
        # Container interno para centralizar os botões
        self.button_container = ctk.CTkFrame(self.button_frame, fg_color="transparent")
        self.button_container.pack(expand=True)
        
        # Botão de áudio
        self.audio_button = ctk.CTkButton(
            self.button_container,
            text="🔊 Ouvir Código",
            command=self.speak_captcha,
            font=ctk.CTkFont(family="Segoe UI Emoji", size=12, weight="bold"),
            height=38,
            fg_color="#357ae8",
            hover_color="#2a65c7",
            width=110
        )
        self.audio_button.pack(side="left", padx=(0, 10))
        
        # Botão de novo desafio
        self.refresh_button = ctk.CTkButton(
            self.button_container,
            text="🔄 Novo Desafio",
            command=self.refresh_captcha,
            height=38,
            font=ctk.CTkFont(family="Segoe UI Emoji", size=12, weight="bold"),
            fg_color="transparent",
            border_width=2,
            text_color="#357ae8",
            border_color="#357ae8",
            hover_color="#ebf2ff",
            width=110
        )
        self.refresh_button.pack(side="left", padx=(0, 10))
        
        # Botão de verificar
        self.submit_button = ctk.CTkButton(
            self.button_container, 
            text="✅ Verificar", 
            command=self.verify_captcha,
            height=38,
            font=ctk.CTkFont(family="Segoe UI Emoji", size=12, weight="bold"),
            fg_color="#48bb78",
            hover_color="#38a169",
            width=110
        )
        self.submit_button.pack(side="left")
        
        # Label de resultado
        self.result_label = ctk.CTkLabel(
            self.main_frame, 
            text="",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.result_label.pack(pady=(0, 15))

    def generate_captcha(self):
        """Gera diferentes tipos de CAPTCHA"""
        captcha_type = self.captcha_type
        
        if captcha_type == "text":
            # CAPTCHA de texto
            length = random.randint(6, 8)
            characters = string.ascii_letters + string.digits
            ambiguous_chars = '0Oo1Il'
            for char in ambiguous_chars:
                characters = characters.replace(char, '')
            text = ''.join(random.choices(characters, k=length))
            question = "Digite o texto que aparece na imagem:"
            return text, question
            
        elif captcha_type == "math":
            # CAPTCHA matemático
            operations = [('+', lambda a, b: a + b), ('-', lambda a, b: a - b), ('*', lambda a, b: a * b)]
            op_symbol, op_func = random.choice(operations)
            
            if op_symbol == '*':
                a, b = random.randint(2, 9), random.randint(2, 9)
            else:
                a, b = random.randint(10, 30), random.randint(1, 20)
                if op_symbol == '-' and a < b:
                    a, b = b, a
                    
            result = op_func(a, b)
            text = str(result)
            question = f"Resolva: {a} {op_symbol} {b} = ?"
            return text, question
            
        elif captcha_type == "word":
            # CAPTCHA de palavras
            words = ["seguranca", "verificacao", "acesso", "sistema", "protecao", 
                    "codigo", "digital", "autenticacao", "privacidade"]
            text = random.choice(words)
            if random.random() > 0.5:
                text += str(random.randint(1, 9))
            question = "Digite a palavra que aparece na imagem:"
            return text, question
        
        return "ERROR", "Erro ao gerar desafio"

    def generate_captcha_image(self):
        """Gera uma imagem CAPTCHA com tamanho dinâmico e espaçamento reduzido"""
        # Calcular largura baseada no número de caracteres (reduzida)
        base_width = 30 * len(self.captcha_text)  # Reduzido de 40 para 30
        width = min(max(280, base_width), 450)  # Limites ajustados
        height = 100
        
        image = Image.new('RGB', (width, height), color='#ffffff')
        draw = ImageDraw.Draw(image)
        
        # Adicionar ruído de fundo
        for _ in range(800):
            x, y = random.randint(0, width), random.randint(0, height)
            size = random.randint(1, 2)
            color = random.choice(['#f7fafc', '#edf2f7', '#e2e8f0'])
            draw.rectangle((x, y, x+size, y+size), fill=color)
        
        # Adicionar linhas de interferência
        for _ in range(5):
            x1, y1 = random.randint(0, width), random.randint(0, height)
            x2, y2 = random.randint(0, width), random.randint(0, height)
            color = random.choice(['#e2e8f0', '#cbd5e0'])
            draw.line((x1, y1, x2, y2), fill=color, width=1)
        
        # Fonte
        try:
            font = ImageFont.truetype("arialbd.ttf", 32)
        except:
            font = ImageFont.load_default()
        
        # Desenhar o texto com posicionamento ajustado e espaçamento reduzido
        text = self.captcha_text
        total_text_width = 0
        char_images = []
        
        # Primeiro passe: criar imagens de cada caractere
        for char in text:
            colors = ['#357ae8', '#2d3748', '#2b6cb0']
            color = random.choice(colors)
            angle = random.randint(-15, 15)
            
            char_image = Image.new('RGBA', (30, 50), (0, 0, 0, 0))  # Largura reduzida
            char_draw = ImageDraw.Draw(char_image)
            char_draw.text((5, 5), char, fill=color, font=font)  # Posição ajustada
            
            rotated_char = char_image.rotate(angle, expand=1, resample=Image.BICUBIC)
            char_images.append(rotated_char)
            total_text_width += rotated_char.width
        
        # Ajustar espaçamento (reduzido significativamente)
        spacing = 3  # Reduzido de 10 para 3
        total_width = total_text_width + (spacing * (len(text) - 1))
        
        # Centralizar horizontalmente
        x_offset = (width - total_width) // 2 if width > total_width else 5
        
        # Segundo passe: posicionar os caracteres com espaçamento reduzido
        for i, rotated_char in enumerate(char_images):
            y = 35 + random.randint(-8, 8)
            image.paste(rotated_char, (x_offset, y), rotated_char)
            x_offset += rotated_char.width + spacing
        
        return image

    def display_captcha(self):
        """Exibe a imagem CAPTCHA no label"""
        photo = ImageTk.PhotoImage(self.captcha_image)
        self.captcha_label.configure(image=photo)
        self.captcha_label.image = photo

    def refresh_captcha(self):
        """Atualiza o CAPTCHA"""
        self.captcha_type = random.choice(["text", "math", "word"])
        self.captcha_text, self.captcha_question = self.generate_captcha()
        self.instruction_label.configure(text=self.captcha_question)
        self.captcha_image = self.generate_captcha_image()
        self.display_captcha()
        self.entry.delete(0, 'end')
        self.result_label.configure(text="")
        
        remaining = self.max_attempts - self.attempts
        self.attempts_label.configure(
            text=f"Tentativas restantes: {remaining}",
            text_color="#e53e3e" if remaining == 1 else "#d69e2e"
        )

    def speak_captcha(self):
        """Faz o texto do CAPTCHA em áudio - Versão corrigida"""
        def speak():
            try:
                # Criar uma nova instância do engine para cada solicitação
                engine = pyttsx3.init()
                
                # Configurar propriedades da voz
                voices = engine.getProperty('voices')
                if voices:
                    # Tentar encontrar uma voz em português
                    for voice in voices:
                        if "portuguese" in voice.name.lower() or "brazil" in voice.name.lower():
                            engine.setProperty('voice', voice.id)
                            break
                    else:
                        # Usar a primeira voz disponível se não encontrar português
                        engine.setProperty('voice', voices[0].id)
                
                engine.setProperty('rate', 160)
                engine.setProperty('volume', 0.9)
                
                # Gerar a mensagem de áudio
                if self.captcha_type == "text":
                    message = f"O código é: {' '.join(self.captcha_text)}"
                elif self.captcha_type == "math":
                    message = self.captcha_question.replace(":", "").replace("?", "")
                else:
                    message = f"A palavra é: {self.captcha_text}"
                
                # Usar runAndWait de forma segura
                engine.say(message)
                engine.runAndWait()
                
                # Encerrar o engine após o uso
                engine.stop()
                
            except Exception as e:
                print(f"Erro ao reproduzir áudio: {e}")
                # Tentativa alternativa se a primeira falhar
                try:
                    import os
                    if self.captcha_type == "text":
                        os.system(f'say "O código é: {self.captcha_text}"')
                    elif self.captcha_type == "math":
                        os.system(f'say "{self.captcha_question.replace(":", "").replace("?", "")}"')
                    else:
                        os.system(f'say "A palavra é: {self.captcha_text}"')
                except:
                    pass

        # Executar em uma thread separada
        thread = threading.Thread(target=speak)
        thread.daemon = True
        thread.start()

    def verify_captcha(self):
        """Verifica se o texto digitado corresponde ao CAPTCHA"""
        user_input = self.entry.get().replace(" ", "")
        
        if self.captcha_type == "text" or self.captcha_type == "word":
            user_input = user_input
        else:
            user_input = user_input.upper()
        
        self.attempts += 1
        remaining = self.max_attempts - self.attempts
        
        self.attempts_label.configure(
            text=f"Tentativas restantes: {remaining}",
            text_color="#e53e3e" if remaining == 1 else "#d69e2e"
        )
        
        if user_input == self.captcha_text:
            self.result_label.configure(text="✔️ Verificação bem-sucedida!", text_color="#48bb78",font=ctk.CTkFont(size=13, family="Segoe UI Emoji", weight="bold"))
            self.after(1000, self.destroy)
            return True
        else:
            if self.attempts >= self.max_attempts:
                self.result_label.configure(text="❌ Número máximo de tentativas excedido!", text_color="#e53e3e", font=ctk.CTkFont(size=13, family="Segoe UI Emoji", weight="bold"))
                self.after(2000, self.destroy)
                return False
            else:
                self.result_label.configure(text="❌ Resposta incorreta. Tente novamente.", text_color="#e53e3e", font=ctk.CTkFont(size=13, family="Segoe UI Emoji", weight="bold"))
                self.refresh_captcha()
                return False

if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    root.withdraw()
    
    app = RefinedCaptchaWindow(root)
    app.mainloop()