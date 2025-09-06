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

        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.winfo_screenheight() // 2) - (500 // 2)
        self.geometry(f"500x500+{x}+{y}")
        
        self.attempts = 0
        self.max_attempts = 3
        self.captcha_type = random.choice(["text", "math", "word"])
        
        self.captcha_text, self.captcha_question = self.generate_captcha()
        
        self.create_widgets()
        
        self.refresh_captcha()

    def create_widgets(self):
        self.main_frame = ctk.CTkFrame(
            self, 
            fg_color="#ffffff",
            corner_radius=12,
            border_width=2,
            border_color="#357ae8"
        )
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.title_label = ctk.CTkLabel(
            self.main_frame, 
            text="Verificação de Segurança",
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color="#2d3748"
        )
        self.title_label.pack(pady=(20, 10))
        
        self.attempts_label = ctk.CTkLabel(
            self.main_frame,
            text=f"Tentativas restantes: {self.max_attempts - self.attempts}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#e53e3e" if self.max_attempts - self.attempts == 1 else "#d69e2e"
        )
        self.attempts_label.pack(pady=(0, 5))
        
        self.instruction_label = ctk.CTkLabel(
            self.main_frame,
            text=self.captcha_question,
            font=ctk.CTkFont(size=13),
            text_color="#718096"
        )
        self.instruction_label.pack(pady=(0, 10))
        
        self.captcha_frame = ctk.CTkFrame(
            self.main_frame, 
            height=140,  
            fg_color="#f7fafc",
            corner_radius=8,
            border_width=2,
            border_color="#357ae8"  
        )
        self.captcha_frame.pack(fill="x", padx=25, pady=(0, 15))
        self.captcha_frame.pack_propagate(False)
        
        self.captcha_label = ctk.CTkLabel(self.captcha_frame, text="", fg_color="#f7fafc")
        self.captcha_label.pack(expand=True, fill="both", padx=5, pady=5)
        
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
        self.entry.bind("<Button-1>", lambda e: self.clear_error_message())  
        
        self.button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.button_frame.pack(fill="x", padx=25, pady=(0, 10))
        
        self.button_container = ctk.CTkFrame(self.button_frame, fg_color="transparent")
        self.button_container.pack(expand=True)
        
        self.audio_button = ctk.CTkButton(
            self.button_container,
            text="🎧 Ouvir Código",
            command=self.speak_captcha,
            font=ctk.CTkFont(family="Segoe UI Emoji", size=12, weight="bold"),
            height=38,
            fg_color="#357ae8",
            hover_color="#2a65c7",
            width=110
        )
        self.audio_button.pack(side="left", padx=(0, 10))
        
        self.refresh_button = ctk.CTkButton(
            self.button_container,
            text="↺ Novo Desafio",
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
        
        self.submit_button = ctk.CTkButton(
            self.button_container, 
            text="✓ Verificar", 
            command=self.verify_captcha,
            height=38,
            font=ctk.CTkFont(family="Segoe UI Emoji", size=12, weight="bold"),
            fg_color="#48bb78",
            hover_color="#38a169",
            width=110
        )
        self.submit_button.pack(side="left")
        
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
            length = random.randint(6, 8)
            characters = string.ascii_letters + string.digits
            ambiguous_chars = '0Oo1Il'
            for char in ambiguous_chars:
                characters = characters.replace(char, '')
            text = ''.join(random.choices(characters, k=length))
            question = "Digite o texto que aparece na imagem:"
            return text, question
            
        elif captcha_type == "math":
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
        width, height = 400, 120  
        
        image = Image.new('RGB', (width, height), color='#ffffff')
        draw = ImageDraw.Draw(image)
        
        for _ in range(1000):  
            x, y = random.randint(0, width), random.randint(0, height)
            size = random.randint(1, 3)
            color = random.choice(['#f7fafc', '#edf2f7', '#e2e8f0'])
            draw.rectangle((x, y, x+size, y+size), fill=color)
        
        for _ in range(6):  
            x1, y1 = random.randint(0, width), random.randint(0, height)
            x2, y2 = random.randint(0, width), random.randint(0, height)
            color = random.choice(['#e2e8f0', '#cbd5e0'])
            draw.line((x1, y1, x2, y2), fill=color, width=1)
        
        try:
            font = ImageFont.truetype("arialbd.ttf", 40)  
        except:
            font = ImageFont.load_default()
        
        text = self.captcha_text
        text_width = 0
        char_widths = []
        
        for char in text:
            if hasattr(font, 'getbbox'):
                bbox = font.getbbox(char)
                char_width = bbox[2] - bbox[0]
            else:
                char_width = font.getsize(char)[0]
            char_widths.append(char_width)
            text_width += char_width
        
        spacing = 6  
        text_width += (len(text) - 1) * spacing
        
        x_start = (width - text_width) // 2
        y_position = (height - 50) // 2  
        
        x_offset = x_start
        for i, char in enumerate(text):
            colors = ['#357ae8', '#2d3748', '#2b6cb0']
            color = random.choice(colors)
            
            angle = random.randint(-12, 12)  
            
            y_offset = y_position + random.randint(-8, 8)  
            
            char_img = Image.new('RGBA', (char_widths[i] + 15, 60), (0, 0, 0, 0))  
            char_draw = ImageDraw.Draw(char_img)
            char_draw.text((7, 10), char, fill=color, font=font)  
            
            if angle != 0:
                rotated_char = char_img.rotate(angle, expand=1, resample=Image.BICUBIC)
                paste_x = x_offset - (rotated_char.width - char_widths[i]) // 2
                paste_y = y_offset - (rotated_char.height - 50) // 2
                image.paste(rotated_char, (paste_x, paste_y), rotated_char)
            else:
                image.paste(char_img, (x_offset, y_offset), char_img)
            
            x_offset += char_widths[i] + spacing
        
        return image

    def display_captcha(self):
        """Exibe a imagem CAPTCHA no label"""
        photo = ImageTk.PhotoImage(self.captcha_image)
        self.captcha_label.configure(image=photo)
        self.captcha_label.image = photo  

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
        def speak():
            try:
                engine = pyttsx3.init()

                voices = engine.getProperty('voices')
                if voices:
                    for voice in voices:
                        if "portuguese" in voice.name.lower() or "brazil" in voice.name.lower():
                            engine.setProperty('voice', voice.id)
                            break
                        else:
                            engine.setProperty('voice', voices[0].id)
                
                engine.setProperty('rate', 160)
                engine.setProperty('volume', 0.9)
                
                if self.captcha_type == "text":
                    message = f"O código é: {' '.join(self.captcha_text)}"
                elif self.captcha_type == "math":
                    message = self.captcha_question.replace(":", "").replace("?", "")
                else:
                    message = f"A palavra é: {self.captcha_text}"
                
                engine.say(message)
                engine.runAndWait()
                
                engine.stop()
                
            except Exception as e:
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
        
        self.entry.delete(0, 'end')
        
        if user_input == self.captcha_text:
            self.captcha_success = True  
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
                self.captcha_success = False  
                self.result_label.configure(...)
                self.after(2000, self.destroy)
                return False
            else:
                self.captcha_success = False  
                return False

if __name__ == "__main__":
    try:
        app = CaptchaApp()
        app.mainloop()
    except Exception as e:
        print(f"Erro no CAPTCHA: {str(e)}")
        sys.exit(1)