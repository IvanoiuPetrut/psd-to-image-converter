import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from main import convert_psd_to_image, get_file_creation_date_str, ensure_dependencies
from PIL import Image, ImageTk

class PSDConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PSD to Image Converter")
        self.root.geometry("800x600")
        
        # Set application icon for both window and taskbar
        try:
            # Try to load icon from the same directory as the script
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
            if os.path.exists(icon_path):
                # This sets both window and taskbar icon on Windows
                self.root.iconbitmap(icon_path)
            else:
                # If .ico not found, try .png
                icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.png")
                if os.path.exists(icon_path):
                    # Load and resize the image to ensure proper taskbar display
                    icon_image = Image.open(icon_path)
                    # Resize to common taskbar icon sizes
                    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
                    icon_photos = []
                    for size in icon_sizes:
                        resized = icon_image.resize(size, Image.Resampling.LANCZOS)
                        icon_photos.append(ImageTk.PhotoImage(resized))
                    # Set the icon for both window and taskbar
                    self.root.iconphoto(True, *icon_photos)
                    # Store references to prevent garbage collection
                    self.icon_photos = icon_photos
        except Exception as e:
            print(f"Could not load icon: {e}")
        
        # Configure style
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", background="#ccc")
        style.configure("TLabel", padding=6)
        style.configure("TFrame", padding=10)
        
        # Create main frame
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Source paths section
        source_frame = ttk.LabelFrame(main_frame, text="Source Files/Folders")
        source_frame.pack(fill=tk.X, pady=5)
        
        self.source_listbox = tk.Listbox(source_frame, height=5)
        self.source_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        source_buttons_frame = ttk.Frame(source_frame)
        source_buttons_frame.pack(side=tk.RIGHT, padx=5, pady=5)
        
        ttk.Button(source_buttons_frame, text="Add File", command=self.add_file).pack(pady=2)
        ttk.Button(source_buttons_frame, text="Add Folder", command=self.add_folder).pack(pady=2)
        ttk.Button(source_buttons_frame, text="Remove", command=self.remove_source).pack(pady=2)
        
        # Output settings section
        output_frame = ttk.LabelFrame(main_frame, text="Output Settings")
        output_frame.pack(fill=tk.X, pady=5)
        
        # Output directory
        ttk.Label(output_frame, text="Output Directory:").pack(anchor=tk.W, padx=5)
        output_dir_frame = ttk.Frame(output_frame)
        output_dir_frame.pack(fill=tk.X, padx=5, pady=2)
        
        self.output_dir_var = tk.StringVar()
        self.output_dir_entry = ttk.Entry(output_dir_frame, textvariable=self.output_dir_var)
        self.output_dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(output_dir_frame, text="Browse", command=self.select_output_dir).pack(side=tk.RIGHT, padx=5)
        
        # Output format
        format_frame = ttk.Frame(output_frame)
        format_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(format_frame, text="Output Format:").pack(side=tk.LEFT)
        self.format_var = tk.StringVar(value="png")
        formats = ["png", "jpg", "webp"]
        format_combo = ttk.Combobox(format_frame, textvariable=self.format_var, values=formats, state="readonly")
        format_combo.pack(side=tk.LEFT, padx=5)
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress")
        progress_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=5, pady=5)
        
        self.status_text = tk.Text(progress_frame, height=10, wrap=tk.WORD)
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(control_frame, text="Start Conversion", command=self.start_conversion).pack(side=tk.RIGHT, padx=5)
        ttk.Button(control_frame, text="Clear All", command=self.clear_all).pack(side=tk.RIGHT, padx=5)
        
        # Initialize source paths list
        self.source_paths = []
        
        # Ensure dependencies are installed
        ensure_dependencies()
    
    def add_file(self):
        files = filedialog.askopenfilenames(
            title="Select PSD Files",
            filetypes=[("Photoshop Files", "*.psd")]
        )
        for file in files:
            if file not in self.source_paths:
                self.source_paths.append(file)
                self.source_listbox.insert(tk.END, file)
    
    def add_folder(self):
        folder = filedialog.askdirectory(title="Select Folder with PSD Files")
        if folder and folder not in self.source_paths:
            self.source_paths.append(folder)
            self.source_listbox.insert(tk.END, folder)
    
    def remove_source(self):
        selection = self.source_listbox.curselection()
        if selection:
            index = selection[0]
            self.source_listbox.delete(index)
            self.source_paths.pop(index)
    
    def select_output_dir(self):
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir_var.set(directory)
    
    def log_message(self, message):
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.root.update()
    
    def clear_all(self):
        self.source_paths.clear()
        self.source_listbox.delete(0, tk.END)
        self.output_dir_var.set("")
        self.progress_var.set(0)
        self.status_text.delete(1.0, tk.END)
    
    def start_conversion(self):
        if not self.source_paths:
            messagebox.showwarning("Warning", "Please add at least one source file or folder.")
            return
        
        if not self.output_dir_var.get():
            messagebox.showwarning("Warning", "Please select an output directory.")
            return
        
        output_dir = self.output_dir_var.get()
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except OSError as e:
                messagebox.showerror("Error", f"Could not create output directory: {e}")
                return
        
        self.progress_var.set(0)
        self.status_text.delete(1.0, tk.END)
        
        total_files = 0
        for path in self.source_paths:
            if os.path.isfile(path):
                if path.lower().endswith(".psd"):
                    total_files += 1
            else:
                for root, _, files in os.walk(path):
                    total_files += sum(1 for f in files if f.lower().endswith(".psd"))
        
        if total_files == 0:
            messagebox.showinfo("Info", "No PSD files found in the selected locations.")
            return
        
        processed_files = 0
        successful_conversions = 0
        
        for source_path in self.source_paths:
            if os.path.isfile(source_path):
                if source_path.lower().endswith(".psd"):
                    self.log_message(f"Processing: {source_path}")
                    creation_date = get_file_creation_date_str(source_path)
                    if convert_psd_to_image(source_path, output_dir, self.format_var.get(), creation_date):
                        successful_conversions += 1
                    processed_files += 1
                    self.progress_var.set((processed_files / total_files) * 100)
            else:
                for root, _, files in os.walk(source_path):
                    for file in files:
                        if file.lower().endswith(".psd"):
                            full_path = os.path.join(root, file)
                            self.log_message(f"Processing: {full_path}")
                            creation_date = get_file_creation_date_str(full_path)
                            if convert_psd_to_image(full_path, output_dir, self.format_var.get(), creation_date):
                                successful_conversions += 1
                            processed_files += 1
                            self.progress_var.set((processed_files / total_files) * 100)
        
        self.log_message(f"\nConversion complete!")
        self.log_message(f"Successfully converted: {successful_conversions} of {total_files} files")
        messagebox.showinfo("Complete", f"Conversion complete!\nSuccessfully converted: {successful_conversions} of {total_files} files")

def main():
    root = tk.Tk()
    app = PSDConverterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 