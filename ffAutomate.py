import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import subprocess
import threading
from pathlib import Path

class VideoConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Converter")
        self.root.geometry("600x400")
        self.root.configure(bg="#f0f0f0")
        
        # Style configuration
        self.style = ttk.Style()
        self.style.configure("Custom.TFrame", background="#f0f0f0")
        self.style.configure("Custom.TButton", padding=5, font=('Helvetica', 10))
        self.style.configure("Custom.TLabel", background="#f0f0f0", font=('Helvetica', 10))
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, style="Custom.TFrame", padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Source folder selection
        source_frame = ttk.Frame(main_frame, style="Custom.TFrame")
        source_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(source_frame, text="Source Folder:", style="Custom.TLabel").pack(side=tk.LEFT)
        self.source_path = tk.StringVar()
        source_entry = ttk.Entry(source_frame, textvariable=self.source_path, width=50)
        source_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(source_frame, text="Browse", style="Custom.TButton",
                   command=self.browse_source).pack(side=tk.LEFT)
        
        # Destination folder selection
        dest_frame = ttk.Frame(main_frame, style="Custom.TFrame")
        dest_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(dest_frame, text="Output Folder:", style="Custom.TLabel").pack(side=tk.LEFT)
        self.dest_path = tk.StringVar()
        dest_entry = ttk.Entry(dest_frame, textvariable=self.dest_path, width=50)
        dest_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(dest_frame, text="Browse", style="Custom.TButton",
                   command=self.browse_destination).pack(side=tk.LEFT)
        
        # Progress frame
        progress_frame = ttk.Frame(main_frame, style="Custom.TFrame")
        progress_frame.pack(fill=tk.X, pady=20)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                          maximum=100, length=400)
        self.progress_bar.pack(pady=10)
        
        self.status_label = ttk.Label(progress_frame, text="Ready", style="Custom.TLabel")
        self.status_label.pack()
        
        # Convert button
        self.convert_btn = ttk.Button(main_frame, text="Start Conversion",
                                    style="Custom.TButton", command=self.start_conversion)
        self.convert_btn.pack(pady=20)
        
    def browse_source(self):
        folder = filedialog.askdirectory()
        if folder:
            self.source_path.set(folder)
            
    def browse_destination(self):
        folder = filedialog.askdirectory()
        if folder:
            self.dest_path.set(folder)
            
    def start_conversion(self):
        if not self.source_path.get() or not self.dest_path.get():
            messagebox.showerror("Error", "Please select both source and destination folders")
            return
            
        self.convert_btn.configure(state="disabled")
        conversion_thread = threading.Thread(target=self.convert_videos)
        conversion_thread.start()
        
    def convert_videos(self):
        source_dir = self.source_path.get()
        dest_dir = self.dest_path.get()
        
        # Get list of .mpg files
        mpg_files = list(Path(source_dir).glob("*.mpg"))
        total_files = len(mpg_files)
        
        if total_files == 0:
            messagebox.showinfo("Info", "No .mpg files found in the source directory")
            self.convert_btn.configure(state="normal")
            return
        
        for index, input_file in enumerate(mpg_files, 1):
            try:
                output_file = Path(dest_dir) / f"{input_file.stem}.mp4"
                
                # Update status
                self.status_label.configure(
                    text=f"Converting: {input_file.name} ({index}/{total_files})")
                
                # Run ffmpeg conversion
                result = subprocess.run([
                    'ffmpeg', '-i', str(input_file),
                    '-c:v', 'libx264', '-c:a', 'aac',
                    '-y', str(output_file)
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    raise Exception(f"FFmpeg error: {result.stderr}")
                
                # Update progress bar
                progress = (index / total_files) * 100
                self.progress_var.set(progress)
                self.root.update_idletasks()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error converting {input_file.name}: {str(e)}")
        
        self.status_label.configure(text="Conversion completed!")
        self.convert_btn.configure(state="normal")
        messagebox.showinfo("Success", "All videos have been converted!")

def main():
    root = tk.Tk()
    app = VideoConverterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
