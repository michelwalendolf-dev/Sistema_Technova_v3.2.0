import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import random
import string
import pyttsx3
import threading
import sys

class CaptchaApp(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Verificação de Segurança")
        self.geometry("500x500")
        self.resizable(False, False)
        self.configure(fg_color="#f8f9fa")
        self.iconbitmap("icones//captcha.ico")
        self.captcha_success = False 

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
            font=ctk.CTkFont(size=30, weight="bold"),
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
        
        # Frame do CAPTCHA com borda azul
        self.captcha_frame = ctk.CTkFrame(
            self.main_frame, 
            height=140,  # Aumentado para acomodar a imagem maior
            fg_color="#f7fafc",
            corner_radius=8,
            border_width=2,
            border_color="#357ae8"  # Borda azul
        )
        self.captcha_frame.pack(fill="x", padx=25, pady=(0, 15))
        self.captcha_frame.pack_propagate(False)
        
        # Label para a imagem CAPTCHA
        self.captcha_label = ctk.CTkLabel(self.captcha_frame, text="", fg_color="#f7fafc")
        self.captcha_label.pack(expand=True, fill="both", padx=5, pady=5)
        
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
        self.entry.bind("<Button-1>", lambda e: self.clear_error_message())  # Limpar mensagem ao clicar
        
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
        """Gera uma imagem CAPTCHA com tamanho aumentado e texto centralizado"""
        # Tamanho aumentado da imagem
        width, height = 400, 120  # Aumentado para 400x120 pixels
        
        image = Image.new('RGB', (width, height), color='#ffffff')
        draw = ImageDraw.Draw(image)
        
        # Adicionar ruído de fundo
        for _ in range(1000):  # Aumentado o ruído para preencher a imagem maior
            x, y = random.randint(0, width), random.randint(0, height)
            size = random.randint(1, 3)
            color = random.choice(['#f7fafc', '#edf2f7', '#e2e8f0'])
            draw.rectangle((x, y, x+size, y+size), fill=color)
        
        # Adicionar linhas de interferência
        for _ in range(6):  # Aumentado o número de linhas
            x1, y1 = random.randint(0, width), random.randint(0, height)
            x2, y2 = random.randint(0, width), random.randint(0, height)
            color = random.choice(['#e2e8f0', '#cbd5e0'])
            draw.line((x1, y1, x2, y2), fill=color, width=1)
        
        # Fonte maior
        try:
            font = ImageFont.truetype("arialbd.ttf", 40)  # Aumentado para 40px
        except:
            # Fallback para fonte padrão se arialbd não estiver disponível
            font = ImageFont.load_default()
        
        # Calcular a largura total do texto
        text = self.captcha_text
        text_width = 0
        char_widths = []
        
        for char in text:
            if hasattr(font, 'getbbox'):
                bbox = font.getbbox(char)
                char_width = bbox[2] - bbox[0]
            else:
                # Para versões mais antigas do PIL
                char_width = font.getsize(char)[0]
            char_widths.append(char_width)
            text_width += char_width
        
        # Adicionar espaçamento entre caracteres
        spacing = 6  # Aumentado ligeiramente o espaçamento
        text_width += (len(text) - 1) * spacing
        
        # Calcular a posição inicial para centralizar o texto
        x_start = (width - text_width) // 2
        y_position = (height - 50) // 2  # Ajustado para a nova altura
        
        # Desenhar cada caractere individualmente com efeitos visuais
        x_offset = x_start
        for i, char in enumerate(text):
            # Cor aleatória para cada caractere
            colors = ['#357ae8', '#2d3748', '#2b6cb0']
            color = random.choice(colors)
            
            # Pequena rotação aleatória
            angle = random.randint(-12, 12)  # Aumentado ligeiramente a rotação
            
            # Deslocamento vertical aleatório
            y_offset = y_position + random.randint(-8, 8)  # Aumentado o deslocamento
            
            # Criar uma imagem para o caractere individual
            char_img = Image.new('RGBA', (char_widths[i] + 15, 60), (0, 0, 0, 0))  # Aumentado o tamanho
            char_draw = ImageDraw.Draw(char_img)
            char_draw.text((7, 10), char, fill=color, font=font)  # Ajustada a posição
            
            # Aplicar rotação
            if angle != 0:
                rotated_char = char_img.rotate(angle, expand=1, resample=Image.BICUBIC)
                # Calcular a posição para manter o alinhamento
                paste_x = x_offset - (rotated_char.width - char_widths[i]) // 2
                paste_y = y_offset - (rotated_char.height - 50) // 2
                image.paste(rotated_char, (paste_x, paste_y), rotated_char)
            else:
                image.paste(char_img, (x_offset, y_offset), char_img)
            
            # Avançar a posição para o próximo caractere
            x_offset += char_widths[i] + spacing
        
        return image

    def display_captcha(self):
        """Exibe a imagem CAPTCHA no label"""
        photo = ImageTk.PhotoImage(self.captcha_image)
        self.captcha_label.configure(image=photo)
        self.captcha_label.image = photo  # Manter referência

    def clear_error_message(self):
        """Limpa a mensagem de erro quando o usuário clica no campo de entrada"""
        if "❌" in self.result_label.cget("text"):
            self.result_label.configure(text="")

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
        
        # Limpar o campo de entrada independente do resultado
        self.entry.delete(0, 'end')
        
        if user_input == self.captcha_text:
            self.captcha_success = True  # Adicionar esta linha
            self.result_label.configure(...)
            self.after(1000, self.destroy)
            return True
        else:
            self.attempts += 1
            remaining = self.max_attempts - self.attempts
            
            self.attempts_label.configure(
                text=f"Tentativas restantes: {remaining}",
                text_color="#e53e3e" if remaining == 1 else "#d69e2e"
            )
            
            if self.attempts >= self.max_attempts:
                self.captcha_success = False  # Adicionar esta linha
                self.result_label.configure(...)
                self.after(2000, self.destroy)
                return False
            else:
                self.captcha_success = False  # Adicionar esta linha
                return False

# No final do COD_CAPTCHA.py, substitua a linha exit(0 if app.captcha_success else 1) por:

if __name__ == "__main__":
    try:
        app = CaptchaApp()
        app.mainloop()
        sys.exit(0 if app.captcha_success else 1)
    except Exception as e:
        print(f"Erro no CAPTCHA: {str(e)}")
        sys.exit(1)