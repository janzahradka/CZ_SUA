# main.py
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import pyperclip
import webbrowser
import folium
from controller import process_plain_text, process_openair_text  # veškerá logika je v controller.py


class AirspaceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Airspace Manager")
        self.root.geometry("1600x800")

        # Konfigurace stylu pro záložky
        style = ttk.Style()
        style.configure("TNotebook.Tab", font=("Arial", 14), padding=[10, 5])

        self.create_main_layout()

        # Po změně záložek aktualizujeme stav tlačítka "Add to multi"
        self.output_notebook.bind("<<NotebookTabChanged>>", lambda e: self.update_add_to_multi_button_state())

    def create_main_layout(self):
        # Hlavní horizontální rozdělení: levý panel (INPUT) a pravý panel (OUTPUT)
        self.paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)

        # Levý panel – INPUT
        self.left_frame = ttk.Frame(self.paned)
        self.paned.add(self.left_frame, weight=1)
        self.create_left_panel(self.left_frame)

        # Pravý panel – OUTPUT
        self.right_frame = ttk.Frame(self.paned)
        self.paned.add(self.right_frame, weight=1)
        self.create_right_panel(self.right_frame)

    def create_left_panel(self, parent):
        # Velký nadpis
        header = tk.Label(parent, text="INPUT", font=("Arial", 20, "bold"))
        header.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Nástrojová lišta pod nadpisem
        left_toolbar = tk.Frame(parent, bd=1, relief=tk.RAISED)
        left_toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        paste_btn = tk.Button(left_toolbar, text="Paste from Clipboard", font=("Roboto", 12),
                              command=self.paste_from_clipboard)
        paste_btn.pack(side=tk.LEFT, padx=2, pady=2)

        clear_input_btn = tk.Button(left_toolbar, text="Clear Input", font=("Roboto", 12), command=self.clear_input)
        clear_input_btn.pack(side=tk.LEFT, padx=2, pady=2)

        process_btn = tk.Button(left_toolbar, text="Run Processing", font=("Roboto", 12), command=self.process_text)
        process_btn.pack(side=tk.LEFT, padx=2, pady=2)

        # Notebook pro levý panel s kartami "plain text" a "OpenAir"
        self.input_notebook = ttk.Notebook(parent)
        self.input_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.plain_text_tab = ttk.Frame(self.input_notebook)
        self.input_notebook.add(self.plain_text_tab, text="plain text")
        self.plain_text = scrolledtext.ScrolledText(self.plain_text_tab, wrap=tk.WORD, font=("JetBrains Mono", 12))
        self.plain_text.pack(fill=tk.BOTH, expand=True)

        self.openair_tab = ttk.Frame(self.input_notebook)
        self.input_notebook.add(self.openair_tab, text="OpenAir")
        self.openair_text = scrolledtext.ScrolledText(self.openair_tab, wrap=tk.WORD, font=("JetBrains Mono", 12))
        self.openair_text.pack(fill=tk.BOTH, expand=True)

    def create_right_panel(self, parent):
        # Velký nadpis
        header = tk.Label(parent, text="OUTPUT", font=("Arial", 20, "bold"))
        header.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Nástrojová lišta pod nadpisem
        right_toolbar = tk.Frame(parent, bd=1, relief=tk.RAISED)
        right_toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        map_btn = tk.Button(right_toolbar, text="Show Map", font=("Roboto", 12), command=self.show_map)
        map_btn.pack(side=tk.LEFT, padx=2, pady=2)

        clear_output_btn = tk.Button(right_toolbar, text="Clear Output", font=("Roboto", 12), command=self.clear_output)
        clear_output_btn.pack(side=tk.LEFT, padx=2, pady=2)

        # Tlačítko "Add to multi" – aktivní pouze pro single output s obsahem
        self.add_to_multi_button = tk.Button(right_toolbar, text="Add to multi", font=("Roboto", 12),
                                             command=self.transfer_to_multi_output, state=tk.DISABLED)
        self.add_to_multi_button.pack(side=tk.LEFT, padx=2, pady=2)

        # Notebook pro pravý panel s kartami "single" a "multi"
        self.output_notebook = ttk.Notebook(parent)
        self.output_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.single_tab = ttk.Frame(self.output_notebook)
        self.output_notebook.add(self.single_tab, text="single")
        self.single_output = scrolledtext.ScrolledText(self.single_tab, wrap=tk.WORD, font=("JetBrains Mono", 12))
        self.single_output.pack(fill=tk.BOTH, expand=True)

        self.multi_tab = ttk.Frame(self.output_notebook)
        self.output_notebook.add(self.multi_tab, text="multi")
        self.multi_output = scrolledtext.ScrolledText(self.multi_tab, wrap=tk.WORD, font=("JetBrains Mono", 12))
        self.multi_output.pack(fill=tk.BOTH, expand=True)

    def paste_from_clipboard(self):
        try:
            content = pyperclip.paste()
            # Vložíme text do "plain text" karty levého panelu
            self.plain_text.delete(1.0, tk.END)
            self.plain_text.insert(tk.END, content)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to paste from clipboard: {e}")

    def clear_input(self):
        self.plain_text.delete(1.0, tk.END)
        self.openair_text.delete(1.0, tk.END)

    def process_text(self):
        # Zjistíme, která karta ve vstupním notebooku je aktuálně aktivní.
        current_input_tab = self.input_notebook.index("current")

        if current_input_tab == 0:
            # Zpracování pomocí Extractoru pro "plain text"
            input_data = self.plain_text.get(1.0, tk.END).strip()
            if not input_data:
                messagebox.showwarning("Warning", "Input field is empty.")
                return
            try:
                result = process_plain_text(input_data)
                self.single_output.delete(1.0, tk.END)
                self.single_output.insert(tk.END, result)
                self.output_notebook.select(self.single_tab)
                self.update_add_to_multi_button_state()
            except Exception as e:
                messagebox.showerror("Error", f"Processing error: {e}")

        elif current_input_tab == 1:
            # Zpracování pomocí ExtractorOpenAir pro "OpenAir"
            input_data = self.openair_text.get(1.0, tk.END).strip()
            if not input_data:
                messagebox.showwarning("Warning", "Input field is empty.")
                return
            try:
                result = process_openair_text(input_data)
                self.single_output.delete(1.0, tk.END)
                self.single_output.insert(tk.END, result)
                self.output_notebook.select(self.single_tab)
                self.update_add_to_multi_button_state()
            except Exception as e:
                messagebox.showerror("Error", f"Processing error: {e}")

    def clear_output(self):
        self.single_output.delete(1.0, tk.END)
        # Po vymazání aktualizujeme stav tlačítka "Add to multi"
        self.update_add_to_multi_button_state()

    def transfer_to_multi_output(self):
        """Přenese obsah z single output do multi output karty."""
        output_data = self.single_output.get(1.0, tk.END).strip()
        if output_data:
            current_text = self.multi_output.get(1.0, tk.END).strip()
            if current_text:
                new_text = current_text + "\n\n" + output_data
            else:
                new_text = output_data
            self.multi_output.delete(1.0, tk.END)
            self.multi_output.insert(tk.END, new_text)
            self.output_notebook.select(self.multi_tab)
            # Po přesunu také aktualizujeme stav tlačítka "Add to multi"
            self.update_add_to_multi_button_state()
        else:
            messagebox.showwarning("Warning", "Single output field is empty.")

    def update_add_to_multi_button_state(self):
        """Aktualizuje, zda má být tlačítko 'Add to multi' aktivní.
           Tlačítko je povoleno, pouze pokud je aktivní karta 'single'
           a není prázdná."""
        # Zkontrolujeme, zda je aktivní karta single (index 0)
        current_tab = self.output_notebook.index("current")
        single_text = self.single_output.get(1.0, tk.END).strip()
        if current_tab == 0 and single_text:
            self.add_to_multi_button.config(state=tk.NORMAL)
        else:
            self.add_to_multi_button.config(state=tk.DISABLED)

    def show_map(self):
        """
        Sample function: creates a map using Folium and opens it in the browser.
        """
        map_object = folium.Map(location=[50.0, 15.0], zoom_start=6)
        folium.Marker(location=[50.0, 15.0], popup="Airspace").add_to(map_object)
        map_object.save("airspace_map.html")
        webbrowser.open("airspace_map.html")


if __name__ == "__main__":
    root = tk.Tk()
    app = AirspaceApp(root)
    root.mainloop()
