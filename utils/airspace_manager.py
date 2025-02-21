import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
import pyperclip
from airac_import import convert_airac_to_openair

"""
pro lepší zážitek doporučuju nainstalovat font Roboto a JetBrains Mono
Roboto: https://fonts.google.com/specimen/Roboto
JetBrains Mono: https://fonts.google.com/specimen/JetBrains+Mono, https://www.jetbrains.com/lp/mono/
"""

class AirspaceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Airspace Converter")
        self.root.geometry("1600x800")

        # Ovládací lišta s Unicode ikonami
        self.create_toolbar()

        # Rámce pro textová pole s popisky
        self.create_text_fields()

    def create_toolbar(self):
        """ Vytvoří ovládací lištu s Unicode ikonami na tlačítkách """
        toolbar = tk.Frame(self.root, bd=1, relief=tk.RAISED)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # Přidání pružné mezery vlevo
        tk.Label(toolbar, text="").pack(side=tk.LEFT, expand=True)

        # Vycentrovaná tlačítka s větším fontem
        paste_btn = tk.Button(toolbar, text="📋 Vložit z clipboardu", font=("Roboto", 12), command=self.paste_from_clipboard)
        paste_btn.pack(side=tk.LEFT, padx=2, pady=2)

        process_btn = tk.Button(toolbar, text="▶️ Spustit zpracování", font=("Roboto", 12), command=self.process_text)
        process_btn.pack(side=tk.LEFT, padx=2, pady=2)

        copy_btn = tk.Button(toolbar, text="📄 Kopírovat výstup", font=("Roboto", 12), command=self.copy_to_clipboard)
        copy_btn.pack(side=tk.LEFT, padx=2, pady=2)

        # Přidání pružné mezery vpravo od vycentrovaných tlačítek
        tk.Label(toolbar, text="").pack(side=tk.LEFT, expand=True)

        # Tlačítko Reset na pravém okraji
        reset_btn = tk.Button(toolbar, text="🔄 Reset", font=("Roboto", 12), command=self.reset_fields)
        reset_btn.pack(side=tk.RIGHT, padx=2, pady=2)


    def create_text_fields(self):
        """ Vytvoří textová pole s popisky pro vstup a výstup """

        # Detekce dostupnosti fontu JetBrains Mono
        try:
            import tkinter.font as tkFont
            available_fonts = tkFont.families()
            if "JetBrains Mono" in available_fonts:
                font_to_use = ("JetBrains Mono", 12)
            else:
                font_to_use = ("Courier New", 12)  # Defaultní monospace
        except Exception:
            font_to_use = ("Courier New", 12)  # Fallback na Courier New

        # Rámec pro vstupní pole a popisek
        input_frame = tk.Frame(self.root)
        input_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Popisek pro vstup
        input_label = tk.Label(input_frame, text="Vstup", font=("Arial", 12, "bold"))
        input_label.pack(anchor="w")  # Zarovnáno vlevo

        # Vstupní pole (80 znaků na šířku) s JetBrains Mono nebo Courier New
        self.input_text = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, width=80, height=30)
        self.input_text.config(font=font_to_use)
        self.input_text.pack(fill=tk.BOTH, expand=True)

        # Rámec pro výstupní pole a popisek
        output_frame = tk.Frame(self.root)
        output_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Popisek pro výstup
        output_label = tk.Label(output_frame, text="Výstup", font=("Arial", 12, "bold"))
        output_label.pack(anchor="w")  # Zarovnáno vlevo

        # Výstupní pole (readonly, 80 znaků na šířku) s JetBrains Mono nebo Courier New
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, width=80, height=30, state='disabled')
        self.output_text.config(font=font_to_use)
        self.output_text.pack(fill=tk.BOTH, expand=True)



    def paste_from_clipboard(self):
        """ Vloží text z clipboardu do vstupního pole """
        try:
            clipboard_content = pyperclip.paste()
            self.input_text.delete(1.0, tk.END)
            self.input_text.insert(tk.END, clipboard_content)
        except Exception as e:
            messagebox.showerror("Chyba", f"Chyba při vkládání z clipboardu: {e}")

    def process_text(self):
        """ Spustí zpracování vstupního textu """
        input_text = self.input_text.get(1.0, tk.END).strip()
        if input_text:
            self.output_text.config(state='normal')
            self.output_text.delete(1.0, tk.END)
            try:
                # Zpracování vstupu
                output = convert_airac_to_openair(input_text)
                self.output_text.insert(tk.END, output)
            except Exception as e:
                self.output_text.insert(tk.END, f"Chyba při zpracování: {e}")
            self.output_text.config(state='disabled')
        else:
            messagebox.showwarning("Upozornění", "Vstupní pole je prázdné.")

    def copy_to_clipboard(self):
        """ Zkopíruje výstup do clipboardu bez pop-up okna """
        output_text = self.output_text.get(1.0, tk.END).strip()
        if output_text:
            pyperclip.copy(output_text)
        else:
            messagebox.showwarning("Upozornění", "Výstupní pole je prázdné.")

    def reset_fields(self):
        """ Resetuje vstupní a výstupní pole """
        self.input_text.delete(1.0, tk.END)
        self.output_text.config(state='normal')
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state='disabled')


# Spuštění aplikace
if __name__ == "__main__":
    root = tk.Tk()
    app = AirspaceApp(root)
    root.mainloop()
