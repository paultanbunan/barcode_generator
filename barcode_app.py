import tkinter as tk
from tkinter import messagebox
from barcode import Code128
from barcode.writer import ImageWriter
from PIL import ImageFont
import os
import sys
import traceback

# Logging function
def log(text):
    try:
        with open("launch_log.txt", "a") as f:
            f.write(text + "\n")
    except:
        pass

log("✅ App started")

# Resolve resource paths for PyInstaller (works in both dev and build)
def resource_path(filename):
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), filename)
    return os.path.join(os.path.dirname(__file__), filename)

# Patched writer to force custom font loading
class PatchedImageWriter(ImageWriter):
    def __init__(self, font_path=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.font_path = font_path

    def _get_font(self, size):
        try:
            return ImageFont.truetype(self.font_path, size)
        except Exception as e:
            log(f"Font load error: {e}")
            return ImageFont.load_default()

# Determine base path (whether running from .exe or raw .py)
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.dirname(sys.executable)
else:
    base_path = os.path.abspath(".")

# Load font from inside the bundled/extracted folder
font_path = os.path.join(base_path, 'Arial.ttf')
font = ImageFont.truetype(font_path, 20) # Ensure Arial.ttf is bundled

def generate_barcode():
    data = entry.get().strip()
    if not data:
        messagebox.showerror("Error", "Please enter a number or text.")
        return

    try:
        log("🟡 Generating barcode for: " + data)

        # Set save path to Downloads
        downloads_folder = os.path.expanduser("~/Downloads")
        file_path = os.path.join(downloads_folder, f"{data}_barcode")

        writer_options = {
            "module_width": 1,
            "module_height": 30.0,
            "font_size": 40,
            "text_distance": 15,
            "quiet_zone": 6.5,
            "dpi": 600,
            "write_text": True,
        }

        barcode = Code128(data, writer=PatchedImageWriter(font_path=font_path))
        barcode.save(file_path, options=writer_options)

        log("✅ Barcode saved")
        messagebox.showinfo("Success", f"Barcode saved to Downloads as {data}_barcode.png")
    except Exception as e:
        log("❌ Barcode error: " + str(e))
        log(traceback.format_exc())
        messagebox.showerror("Error", f"Failed to generate barcode:\n{e}")

# GUI setup
root = tk.Tk()
root.title("Barcode Generator")

window_width = 400
window_height = 150
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
center_x = int((screen_width - window_width) / 2)
center_y = int((screen_height - window_height) / 2)
root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

label = tk.Label(root, text="Enter number or text:")
label.pack(pady=10)

entry = tk.Entry(root, width=40)
entry.pack()

generate_button = tk.Button(root, text="Generate Barcode", command=generate_barcode)
generate_button.pack(pady=10)

log("✅ GUI loaded")
root.mainloop()
