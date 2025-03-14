import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk, simpledialog
import pyperclip
import webbrowser
import folium
from controller import process_plain_text, process_openair_text  # Logika z controller.py
from renderer import Renderer


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

        # Levá tlačítka
        paste_btn = tk.Button(left_toolbar, text="Paste from Clipboard", font=("Roboto", 12),
                              command=self.paste_from_clipboard)
        paste_btn.pack(side=tk.LEFT, padx=2, pady=2)

        clear_input_btn = tk.Button(left_toolbar, text="Clear Input", font=("Roboto", 12), command=self.clear_input)
        clear_input_btn.pack(side=tk.LEFT, padx=2, pady=2)

        # Filler pro posunutí tlačítka "Run Processing" doprava
        filler = tk.Label(left_toolbar, text="")
        filler.pack(side=tk.LEFT, expand=True, fill=tk.X)

        # Tlačítko "Run Processing" napravo
        process_btn = tk.Button(left_toolbar, text="Run Processing", font=("Roboto", 12), command=self.process_text)
        process_btn.pack(side=tk.RIGHT, padx=2, pady=2)

        # Notebook pro levý panel s kartami "plain text" a "OpenAir"
        self.input_notebook = ttk.Notebook(parent)
        self.input_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tab pro "plain text"
        self.plain_text_tab = ttk.Frame(self.input_notebook)
        self.input_notebook.add(self.plain_text_tab, text="plain text")
        self.plain_text = scrolledtext.ScrolledText(
            self.plain_text_tab, wrap=tk.WORD,
            font=("JetBrains Mono", 12), undo=True  # Undo podpora
        )
        self.plain_text.pack(fill=tk.BOTH, expand=True)
        # Vazby pro undo/redo a vyhledávání
        self.plain_text.bind("<Control-z>", lambda event: self.plain_text.edit_undo())
        self.plain_text.bind("<Control-y>", lambda event: self.plain_text.edit_redo())
        self.plain_text.bind("<Control-f>", self.search_text)

        # Tab pro "OpenAir"
        self.openair_tab = ttk.Frame(self.input_notebook)
        self.input_notebook.add(self.openair_tab, text="OpenAir")
        self.openair_text = scrolledtext.ScrolledText(
            self.openair_tab, wrap=tk.WORD,
            font=("JetBrains Mono", 12), undo=True  # Undo podpora
        )
        self.openair_text.pack(fill=tk.BOTH, expand=True)
        # Vazby pro undo/redo a vyhledávání
        self.openair_text.bind("<Control-z>", lambda event: self.openair_text.edit_undo())
        self.openair_text.bind("<Control-y>", lambda event: self.openair_text.edit_redo())
        self.openair_text.bind("<Control-f>", self.search_text)

    def create_right_panel(self, parent):
        # Velký nadpis
        header = tk.Label(parent, text="OUTPUT", font=("Arial", 20, "bold"))
        header.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Nástrojová lišta pod nadpisem
        right_toolbar = tk.Frame(parent, bd=1, relief=tk.RAISED)
        right_toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Levá tlačítka na pravé liště
        clear_output_btn = tk.Button(right_toolbar, text="Clear Output", font=("Roboto", 12), command=self.clear_output)
        clear_output_btn.pack(side=tk.LEFT, padx=2, pady=2)

        self.add_to_multi_button = tk.Button(
            right_toolbar, text="Add to multi", font=("Roboto", 12),
            command=self.transfer_to_multi_output, state=tk.DISABLED
        )
        self.add_to_multi_button.pack(side=tk.LEFT, padx=2, pady=2)

        # Filler pro posunutí tlačítka "Show Map" doprava
        filler = tk.Label(right_toolbar, text="")
        filler.pack(side=tk.LEFT, expand=True, fill=tk.X)

        # Tlačítko "Show Map" nyní volá show_map_handler
        map_btn = tk.Button(right_toolbar, text="Show Map", font=("Roboto", 12), command=self.show_map_handler)
        map_btn.pack(side=tk.RIGHT, padx=2, pady=2)

        # Notebook pro pravý panel s kartami "single" a "multi"
        self.output_notebook = ttk.Notebook(parent)
        self.output_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tab "single"
        self.single_tab = ttk.Frame(self.output_notebook)
        self.output_notebook.add(self.single_tab, text="single")
        self.single_output = scrolledtext.ScrolledText(
            self.single_tab, wrap=tk.WORD, font=("JetBrains Mono", 12), undo=True  # Undo podpora
        )
        self.single_output.pack(fill=tk.BOTH, expand=True)
        # Undo/Redo a Hledání
        self.single_output.bind("<Control-z>", lambda event: self.single_output.edit_undo())
        self.single_output.bind("<Control-y>", lambda event: self.single_output.edit_redo())
        self.single_output.bind("<Control-f>", self.search_text)

        # Tab "multi"
        self.multi_tab = ttk.Frame(self.output_notebook)
        self.output_notebook.add(self.multi_tab, text="multi")
        self.multi_output = scrolledtext.ScrolledText(
            self.multi_tab, wrap=tk.WORD, font=("JetBrains Mono", 12), undo=True  # Undo podpora
        )
        self.multi_output.pack(fill=tk.BOTH, expand=True)
        # Undo/Redo a Hledání
        self.multi_output.bind("<Control-z>", lambda event: self.multi_output.edit_undo())
        self.multi_output.bind("<Control-y>", lambda event: self.multi_output.edit_redo())
        self.multi_output.bind("<Control-f>", self.search_text)

    def search_text(self, event=None):
        # Určíme widget, ve kterém bylo stisknuto Ctrl+F
        widget = event.widget if event is not None else None
        if widget is None:
            return "break"  # Zabrání defaultnímu chování Ctrl+F

        # Dialog pro zadání hledaného výrazu
        search_term = simpledialog.askstring("Hledat", "Zadejte hledaný text:")
        if search_term:
            # Odstranit předchozí značky "found"
            widget.tag_remove("found", "1.0", tk.END)
            # Vyhledání textu
            start_pos = widget.search(search_term, "1.0", tk.END)
            if start_pos:
                end_pos = f"{start_pos}+{len(search_term)}c"
                # Zvýrazní najitý text
                widget.tag_add("found", start_pos, end_pos)
                widget.tag_config("found", background="yellow")
                widget.mark_set("insert", end_pos)  # Posune kurzor na konec nalezeného výrazu
                widget.see(start_pos)  # Zajistí zobrazení nalezeného výrazu
            else:
                # Zobrazí hlášení, že text nebyl nalezen
                messagebox.showinfo("Hledat", "Text nebyl nalezen.")
        return "break"  # Zabrání standardnímu hledání

    def paste_from_clipboard(self):
        try:
            content = pyperclip.paste()
            # Vložíme text do "plain text" karty levého panelu
            self.plain_text.delete(1.0, tk.END)
            self.plain_text.insert(tk.END, content)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to paste from clipboard: {e}")

    def clear_input(self):
        # Vymažeme pouze obsah aktivního vstupního tabu
        current_tab = self.input_notebook.index("current")
        if current_tab == 0:
            self.plain_text.delete(1.0, tk.END)
        elif current_tab == 1:
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
        # Vymažeme pouze obsah aktivního výstupního tabu
        current_tab = self.output_notebook.index("current")
        if current_tab == 0:
            self.single_output.delete(1.0, tk.END)
        elif current_tab == 1:
            self.multi_output.delete(1.0, tk.END)
        self.update_add_to_multi_button_state()

    def transfer_to_multi_output(self):
        """Transfer content from single output to multi output tab."""
        output_data = self.single_output.get(1.0, tk.END).strip()
        if output_data:
            current_text = self.multi_output.get(1.0, tk.END).strip()
            # Přidáme ještě jeden řádek, takže oddělovač bude "\n\n\n"
            new_text = current_text + "\n\n\n" + output_data if current_text else output_data
            self.multi_output.delete(1.0, tk.END)
            self.multi_output.insert(tk.END, new_text)
            self.output_notebook.select(self.multi_tab)
            self.update_add_to_multi_button_state()
        else:
            messagebox.showwarning("Warning", "Single output field is empty.")

    def update_add_to_multi_button_state(self):
        """Aktualizuje, zda má být tlačítko 'Add to multi' aktivní.
           Tlačítko je povoleno, pouze pokud je aktivní karta 'single'
           a není prázdná."""
        current_tab = self.output_notebook.index("current")
        single_text = self.single_output.get(1.0, tk.END).strip()
        if current_tab == 0 and single_text:
            self.add_to_multi_button.config(state=tk.NORMAL)
        else:
            self.add_to_multi_button.config(state=tk.DISABLED)

    def show_map(self):
        """
        Retrieves the content from the 'single' output tab (which is in OpenAir format),
        converts it into an Airspace object, and then uses Renderer to display the space on a map.
        """
        single_content = self.single_output.get(1.0, tk.END).strip()
        if not single_content:
            messagebox.showwarning("Warning", "Single output is empty.")
            return
        try:
            # Convert the OpenAir formatted text into an Airspace object
            from controller import airspace_from_openair
            airspace_obj = airspace_from_openair(single_content)

            # Use the Renderer to render the map.
            renderer = Renderer([airspace_obj])  # Note: renderer expects a list of Airspace objects.
            renderer.render_map()
        except Exception as e:
            messagebox.showerror("Error", f"Error rendering map: {e}")

    def show_map_handler(self):
        """Determines which output tab is active and calls the appropriate map rendering function."""
        current_tab = self.output_notebook.index("current")
        if current_tab == 0:
            # Active tab is "single"
            self.show_map()
        elif current_tab == 1:
            # Active tab is "multi"
            self.show_multi_map()

    def show_multi_map(self):
        """
        Render map from multi output content.
        Splits the multi output into blocks (each representing one airspace),
        converts each block to an Airspace object, and then renders all airspaces on one map.
        """
        multi_content = self.multi_output.get(1.0, tk.END).strip()
        if not multi_content:
            messagebox.showwarning("Warning", "Multi output field is empty.")
            return
        try:
            from controller import airspace_from_openair  # Funkce převádějící OpenAir text na Airspace objekt
            # Split multi output into blocks using triple newlines as separator
            blocks = multi_content.split("\n\n\n")
            airspaces = []
            for block in blocks:
                block = block.strip()
                if block:
                    try:
                        airspace_obj = airspace_from_openair(block)
                        airspaces.append(airspace_obj)
                    except Exception as e:
                        print(f"Error processing block: {e}")
            if not airspaces:
                messagebox.showwarning("Warning", "No valid airspaces found in multi output.")
                return

            from renderer import Renderer
            renderer = Renderer(airspaces)
            renderer.render_map()
        except Exception as e:
            messagebox.showerror("Error", f"Error rendering multi map: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = AirspaceApp(root)
    root.mainloop()
