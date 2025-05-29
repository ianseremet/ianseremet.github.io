import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def launch_buckling_gui():
    def calculate():
        try:
            E = float(entry_E.get())
            Sy = float(entry_Sy.get())
            Le = float(entry_Le.get())
            r = float(entry_r.get())
            A = float(entry_A.get())
            P_applied = float(entry_P.get())

            slenderness = Le / r
            cutoff = 2 * np.pi * np.sqrt(E / Sy)

            if slenderness > cutoff:
                # Euler
                Pcr = (np.pi ** 2 * E * A * r**2) / (Le ** 2)
                mode = "Euler (Long Column)"
            else:
                # Johnson
                Pcr = A * Sy * (1 - ((Sy / (4 * np.pi**2 * E)) * (slenderness ** 2)))
                mode = "Johnson (Intermediate Column)"

            safety_factor = Pcr / P_applied

            # Clear results
            for widget in result_frame.winfo_children():
                widget.destroy()

            def row(label, value, unit=""):
                f = ttk.Frame(result_frame); f.pack(anchor='w', pady=1)
                try: formatted = f"{float(value):.2f}"
                except: formatted = str(value)
                ttk.Label(f, text=f"{label}: ", width=28).pack(side='left')
                ttk.Label(f, text=f"{formatted} {unit}", font=("Segoe UI", 11, "bold")).pack(side='left')

            ttk.Label(result_frame, text="Buckling Result", font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=5)
            row("Slenderness Ratio (Le/r)", slenderness)
            row("Euler-Johnson Cutoff", cutoff)
            row("Critical Load (Pcr)", Pcr, "lbf")
            row("Applied Load (P)", P_applied, "lbf")
            row("Safety Factor (n = Pcr / P)", safety_factor)
            row("Buckling Mode", mode)

            # --- Plotting ---
            fig, ax = plt.subplots(figsize=(6.5, 4.5), dpi=100)

            x_vals = np.linspace(10, int(slenderness * 1.5), 300)
            euler_vals = (np.pi**2 * E * A * r**2) / (x_vals**2)
            johnson_vals = A * Sy * (1 - ((Sy / (4 * np.pi**2 * E)) * x_vals**2))

            ax.plot(x_vals, euler_vals, label="Euler", color='red')
            ax.plot(x_vals, johnson_vals, label="Johnson", color='blue')
            ax.axvline(cutoff, color='gray', linestyle='--', label="Euler–Johnson Cutoff")
            ax.plot(slenderness, Pcr, 'ko', label="Your Column")

            ax.set_xlabel("Slenderness Ratio (Le/r)")
            ax.set_ylabel("Critical Load (lbf)")
            ax.set_title("Euler–Johnson Buckling Curve")
            ax.grid(True)
            ax.legend()

            for widget in plot_frame.winfo_children():
                widget.destroy()

            canvas = FigureCanvasTkAgg(fig, master=plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    root = tk.Tk()
    root.title("Buckling Analysis – Euler & Johnson")
    root.geometry("1050x600")
    root.configure(bg="#f4f4f4")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TLabel", font=("Segoe UI", 11), background="#f4f4f4")
    style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"), background="#f4f4f4")
    style.configure("TButton", font=("Segoe UI", 11))

    ttk.Label(root, text="Buckling Analysis Calculator (Euler–Johnson)", style="Header.TLabel").pack(pady=10)

    container = ttk.Frame(root); container.pack(fill='both', expand=True)
    left_frame = ttk.Frame(container); left_frame.pack(side='left', padx=10, fill='y')
    right_frame = ttk.Frame(container); right_frame.pack(side='right', fill='both', expand=True)

    form = ttk.Frame(left_frame); form.pack(pady=5)

    def row(label, default, r):
        ttk.Label(form, text=label).grid(row=r, column=0, sticky="e", padx=5, pady=2)
        e = ttk.Entry(form, width=18)
        e.grid(row=r, column=1, pady=2)
        e.insert(0, default)
        return e

    # Inputs
    entry_E = row("Young's Modulus E (psi)", "29000000", 0)
    entry_Sy = row("Yield Strength Sy (psi)", "36000", 1)
    entry_Le = row("Effective Length Le (in)", "36", 2)
    entry_r = row("Radius of Gyration r (in)", "0.3", 3)
    entry_A = row("Cross Section Area A (in²)", "0.75", 4)
    entry_P = row("Applied Load P (lbf)", "2500", 5)

    ttk.Button(left_frame, text="Calculate Buckling", command=calculate).pack(pady=10)
    ttk.Button(left_frame, text="Terminate Program", command=lambda: [root.destroy(), quit()]).pack()

    result_frame = ttk.Frame(right_frame); result_frame.pack(pady=10, fill='x')
    plot_frame = ttk.Frame(right_frame); plot_frame.pack(fill='both', expand=True)

    root.mainloop()

launch_buckling_gui()
