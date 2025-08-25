import tkinter 
from tkinter import messagebox

def criar_tela():
    tela = tkinter.Tk()
    tela.title("brincando com interface")
    tela.geometry("800x600")

    botão = tkinter.Button(
        tela, 
        text="Clique aqui", 
        font=("Roboto", 24),
        fg="white", 
        bg="red",                              
        borderwidth=5,
        width=20, height=2, 
        command=lambda:messagebox.showinfo("Olá", "Você clicou no botão!"))
    botão.pack(anchor="center", expand=True)

    botão.bind("<Enter>", lambda e: botão.config(bg="darkred"))
    botão.bind("<Leave>", lambda e: botão.config(bg="red"))

    tela.mainloop()
criar_tela()

