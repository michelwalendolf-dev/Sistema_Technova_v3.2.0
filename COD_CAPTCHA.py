import tkinter as tk
from tkinterweb import HtmlFrame
import threading
from flask import Flask, send_file

# Servidor Flask para servir o HTML do ALTCHA
app = Flask(__name__)
@app.route("/")
def altcha_html():
    return send_file("altcha_widget.html")  # Seu arquivo HTML com o widget ALTCHA

def run_flask():
    app.run(port=5000)

# Executar o servidor em uma thread separada
threading.Thread(target=run_flask, daemon=True).start()

# Janela Tkinter com TkinterWeb
root = tk.Tk()
frame = HtmlFrame(root)
frame.load_website("http://localhost:5000")
frame.pack(fill="both", expand=True)
root.mainloop()