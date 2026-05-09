import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class PyExplorer:
    def __init__(self, root):
        self.root = root
        self.root.title("PyExplorer - Gestionnaire de Fichiers")
        
        
        self.root.geometry("1000x700")
        try:
            
            if os.name == 'nt': 
                self.root.state('zoomed')
            else: 
                self.root.attributes('-fullscreen', False) 
                
                width = self.root.winfo_screenwidth()
                height = self.root.winfo_screenheight()
                self.root.geometry(f"{width}x{height}+0+0")
        except:
            pass 

        
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # --- Variables d'état ---
        self.current_path = os.path.expanduser("~")
        self.current_file = None

       
        self.paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)

        
        self.left_frame = ttk.Frame(self.paned)
        self.paned.add(self.left_frame, weight=1)

        
        self.right_frame = ttk.Frame(self.paned)
        self.paned.add(self.right_frame, weight=3)

        self.setup_left_panel()
        self.setup_right_panel()
        
        
        self.load_directory(self.current_path)

    def setup_left_panel(self):
        """Configure la liste des fichiers et la barre de navigation."""
        nav_bar = ttk.Frame(self.left_frame)
        nav_bar.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(nav_bar, text="⬆ Parent", command=self.go_up).pack(side=tk.LEFT)
        self.path_entry = ttk.Entry(nav_bar)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.path_entry.insert(0, self.current_path)
        self.path_entry.bind('<Return>', lambda e: self.load_directory(self.path_entry.get()))

        
        cols = ('Name', 'Size', 'Type')
        self.tree = ttk.Treeview(self.left_frame, columns=cols, show='headings')
        
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.tree.bind('<Double-1>', self.on_double_click)

        
        scrollbar = ttk.Scrollbar(self.tree, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def setup_right_panel(self):
        """Configure l'éditeur de texte."""
        tool_bar = ttk.Frame(self.right_frame)
        tool_bar.pack(fill=tk.X, padx=5, pady=5)

        self.file_label = ttk.Label(tool_bar, text="No files open", font=('Arial', 10, 'bold'))
        self.file_label.pack(side=tk.LEFT, padx=5)

        ttk.Button(tool_bar, text="💾 Save", command=self.save_file).pack(side=tk.RIGHT, padx=5)

        # Zone de texte
        self.text_area = tk.Text(self.right_frame, wrap=tk.WORD, font=('Consolas', 11), undo=True)
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Scrollbar pour le texte
        text_scroll = ttk.Scrollbar(self.text_area, orient=tk.VERTICAL, command=self.text_area.yview)
        self.text_area.configure(yscroll=text_scroll.set)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def load_directory(self, path):
        """Charge le contenu d'un dossier dans le Treeview."""
        if not os.path.isdir(path):
            messagebox.showerror("Error", f"The path {path} is not a valid folder.")
            return

        self.current_path = path
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, path)

        # Nettoyer l'arbre
        for i in self.tree.get_children():
            self.tree.delete(i)

        try:
            for item in os.listdir(path):
                full_path = os.path.join(path, item)
                stats = os.stat(full_path)
                
                # Taille lisible
                size = f"{stats.st_size / 1024:.1f} KB" if os.path.isfile(full_path) else "--"
                item_type = "Dossier" if os.path.isdir(full_path) else "Fichier"
                
                self.tree.insert('', tk.END, values=(item, size, item_type))
        except PermissionError:
            messagebox.showwarning("Permission", "Accès refusé à ce dossier.")

    def go_up(self):
        """Remonte d'un niveau dans l'arborescence."""
        parent = os.path.dirname(self.current_path)
        if parent != self.current_path:
            self.load_directory(parent)

    def on_double_click(self, event):
        """Gère le double-clic sur un élément de la liste."""
        item_id = self.tree.focus()
        if not item_id:
            return
            
        item_name = self.tree.item(item_id)['values'][0]
        full_path = os.path.join(self.current_path, item_name)

        if os.path.isdir(full_path):
            self.load_directory(full_path)
        else:
            self.open_file(full_path)

    def open_file(self, file_path):
        """Ouvre et affiche le contenu d'un fichier texte."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.text_area.delete('1.0', tk.END)
                self.text_area.insert('1.0', content)
                
            self.current_file = file_path
            self.file_label.config(text=f"Edition : {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error opening", f"Unable to read file :\n{e}")

    def save_file(self):
        """Enregistre les modifications dans le fichier actuel."""
        if not self.current_file:
            messagebox.showinfo("Info", "No files open")
            return

        try:
            content = self.text_area.get('1.0', tk.END)
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(content.strip())
            messagebox.showinfo("Succès", "File saved successfully.")
        except Exception as e:
            messagebox.showerror("Erreur de sauvegarde", f"Erreur lors de l'écriture :\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PyExplorer(root)
    root.mainloop()
