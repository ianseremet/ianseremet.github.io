import os
import cv2
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.widgets import LassoSelector, Button
from matplotlib.path import Path as MplPath
import tkinter as tk
from tkinter import ttk
import threading

# Optional: Lower DPI for faster rendering
import matplotlib
matplotlib.rcParams['figure.dpi'] = 100

# === Folders ===
input_folder = r"C:\Users\ianse\Downloads\input"
output_folder = r"C:\Users\ianse\Downloads\output"
os.makedirs(output_folder, exist_ok=True)

image_files = sorted([
    f for f in os.listdir(input_folder)
    if f.lower().endswith(('.png', '.jpg', '.jpeg'))
])
image_index = 0

# === Thread-Based Loading Popup ===
def show_loading_popup(text="Processing..."):
    def run_popup():
        popup = tk.Tk()
        popup.title("Automated Research Tools — Status")
        popup.geometry("400x100+500+300")
        label = tk.Label(popup, text=text, font=("Segoe UI", 12))
        label.pack(pady=10)
        bar = ttk.Progressbar(popup, mode="indeterminate", length=300)
        bar.pack(pady=5)
        bar.start(5)
        popup.after(1500, popup.destroy)
        popup.mainloop()
    threading.Thread(target=run_popup, daemon=True).start()

# === Main GUI Class ===
class InteractiveCropper:
    def __init__(self):
        self.image = None
        self.filename = ""
        self.verts = []
        self.result = None
        self.mask = None

        # Large image display
        self.fig, self.ax = plt.subplots(figsize=(16, 9))
        try:
            manager = plt.get_current_fig_manager()
            manager.window.state('zoomed')
        except Exception:
            try:
                manager.full_screen_toggle()
            except:
                pass

        self.fig.subplots_adjust(bottom=0.18)
        self.lasso = None
        self.fig.canvas.mpl_connect("key_press_event", self.key_handler)
        self.fig.text(0.01, 0.01, "Automated Research Tools, LLC", fontsize=10, color='gray', style='italic')
        self.add_buttons()

    def add_buttons(self):
        ax_preview = plt.axes([0.55, 0.05, 0.12, 0.075])
        ax_next = plt.axes([0.69, 0.05, 0.12, 0.075])
        ax_quit = plt.axes([0.83, 0.05, 0.12, 0.075])
        self.btn_preview = Button(ax_preview, 'Preview')
        self.btn_next = Button(ax_next, 'Save + Next')
        self.btn_quit = Button(ax_quit, 'Quit')

        self.btn_preview.on_clicked(self.preview_result)
        self.btn_next.on_clicked(self.next_image)
        self.btn_quit.on_clicked(self.quit)

    def start(self):
        self.load_image()
        plt.show()

    def key_handler(self, event):
        if event.key == 'r':
            self.verts.clear()
            self.result = None
            self.mask = None
            self.load_image()
        elif event.key == 'q':
            self.quit()

    def load_image(self):
        global image_index
        if image_index >= len(image_files):
            print("✅ All images processed.")
            plt.close(self.fig)
            return

        self.filename = image_files[image_index]
        path = os.path.join(input_folder, self.filename)
        self.image = cv2.imread(path)
        self.verts.clear()
        self.result = None
        self.mask = None
        self.ax.clear()

        # Resize large images for performance
        MAX_DIM = 1400
        h, w = self.image.shape[:2]
        if max(h, w) > MAX_DIM:
            scale = MAX_DIM / max(h, w)
            self.image = cv2.resize(self.image, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_AREA)

        self.rgb_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.ax.imshow(self.rgb_image)
        count_info = f"{image_index+1} of {len(image_files)}"
        self.ax.set_title(f"[{count_info}] Draw region — {self.filename} (press 'r' to reset)", fontsize=12)

        if self.lasso:
            self.lasso.disconnect_events()
        self.lasso = LassoSelector(self.ax, onselect=self.on_select)

        self.fig.canvas.draw_idle()

    def on_select(self, verts):
        self.verts = verts
        self.mask = self.create_mask()
        self.result = self.apply_mask()

    def create_mask(self):
        if not self.verts:
            return None
        ny, nx = self.image.shape[:2]
        path = MplPath(self.verts)
        y_grid, x_grid = np.mgrid[:ny, :nx]
        coords = np.vstack((x_grid.ravel(), y_grid.ravel())).T
        return path.contains_points(coords).reshape((ny, nx))

    def apply_mask(self, save=False):
        if self.mask is None:
            return self.image
        result = np.where(self.mask[..., None], self.image, [255, 0, 0])
        if save:
            out_name = Path(self.filename).stem + "_blue" + Path(self.filename).suffix
            out_path = os.path.join(output_folder, out_name)
            cv2.imwrite(out_path, result)
            print(f"💾 Saved: {out_path}")
        return result.astype(np.uint8)

    def preview_result(self, event):
        show_loading_popup("Generating preview...")
        if self.result is None:
            if self.mask is None:
                print("⚠ No region selected.")
                return
            self.result = self.apply_mask()

        result_rgb = cv2.cvtColor(self.result, cv2.COLOR_BGR2RGB)
        self.ax.clear()
        self.ax.imshow(result_rgb)
        self.ax.set_title(f"Preview — {self.filename}", fontsize=12)
        self.fig.canvas.draw_idle()
        plt.pause(0.001)

    def next_image(self, event):
        show_loading_popup("Saving image and loading next...")
        if self.mask is not None:
            self.apply_mask(save=True)
        else:
            print("⚠ Skipped saving (no region selected).")
        global image_index
        image_index += 1
        self.load_image()

    def quit(self, event=None):
        print("👋 Quit requested.")
        plt.close(self.fig)

# === Launch ===
if __name__ == '__main__':
    InteractiveCropper().start()
