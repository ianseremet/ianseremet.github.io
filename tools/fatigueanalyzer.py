import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def launch_fatigue_gui():
    def calculate():
        try:
            Su = float(entry_Su.get())
            Sy = float(entry_Sy.get())
            Se_prime = float(entry_Se.get())
            Sm = float(entry_Sm.get())
            Sa = float(entry_Sa.get())

            C_load = float(entry_Cload.get())
            C_surf = float(entry_Csurf.get())
            C_size = float(entry_Csize.get())
            C_temp = float(entry_Ctemp.get())
            C_reliab = float(entry_Crel.get())

            Se = Se_prime * C_load * C_surf * C_size * C_temp * C_reliab

            # Safety factors
            n_goodman = 1 / ((Sa / Se) + (Sm / Su))
            n_alt = Se / Sa if Sa > 0 else float('inf')
            n_mean = Su / Sm if Sm > 0 else float('inf')

            # --- Display Results ---
            for widget in result_frame.winfo_children():
                widget.destroy()

            def row(label, value, unit=""):
                frame = ttk.Frame(result_frame); frame.pack(anchor='w', pady=1)
                try:
                    num = float(value)
                    formatted = f"{num:.2f}"
                except:
                    formatted = str(value)
                ttk.Label(frame, text=f"{label}: ", width=28).pack(side='left')
                ttk.Label(frame, text=f"{formatted} {unit}", font=("Segoe UI", 11, "bold")).pack(side='left')

            ttk.Label(result_frame, text="Fatigue Summary", font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=5)

            row("Ultimate Strength (Su)", Su, "psi")
            row("Yield Strength (Sy)", Sy, "psi")
            row("Endurance Limit (Se)", Se, "psi")
            row("Mean Stress (σm)", Sm, "psi")
            row("Alt Stress (σa)", Sa, "psi")
            row("Safety Factor (Goodman)", n_goodman)
            row("SF (σa only)", n_alt)
            row("SF (σm only)", n_mean)
            row("Result", "PASS ✅" if n_goodman >= 1 else "FAIL ❌")

            # --- Plotting ---
            fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
            ax.set_title("Goodman Diagram", fontsize=12)
            ax.set_xlabel("Mean Stress σm [psi]")
            ax.set_ylabel("Alternating Stress σa [psi]")
            ax.grid(True, linestyle='--', alpha=0.6)

            ax.plot([0, Su], [Se, 0], 'r-', label='Goodman Line')
            ax.plot([0, Sy], [Sy, 0], 'orange', linestyle='--', label='Yield Line (Sy)')
            ax.axhline(Se, color='green', linestyle=':', label='σa = Se')
            ax.axvline(Su, color='purple', linestyle=':', label='σm = Su')
            ax.plot(Sm, Sa, 'bo', label='Operating Point')
            ax.set_xlim(0, Su * 1.1)
            ax.set_ylim(0, Se * 1.1)
            ax.legend(fontsize=8)

            for widget in plot_frame.winfo_children():
                widget.destroy()

            canvas = FigureCanvasTkAgg(fig, master=plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # --- GUI Setup ---
    root = tk.Tk()
    root.title("Goodman Fatigue Analysis Tool")
    root.geometry("1050x600")
    root.configure(bg="#f4f4f4")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TLabel", font=("Segoe UI", 11), background="#f4f4f4")
    style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"), background="#f4f4f4")
    style.configure("TButton", font=("Segoe UI", 11))

    ttk.Label(root, text="Goodman Fatigue Calculator (Ductile Materials)", style="Header.TLabel").pack(pady=10)

    # Layout
    container = ttk.Frame(root); container.pack(fill='both', expand=True)

    left_frame = ttk.Frame(container); left_frame.pack(side='left', padx=10, fill='y')
    right_frame = ttk.Frame(container); right_frame.pack(side='right', padx=10, fill='both', expand=True)

    form = ttk.Frame(left_frame); form.pack(pady=10)

    def row(label, default, r):
        ttk.Label(form, text=label).grid(row=r, column=0, sticky="e", padx=5, pady=2)
        e = ttk.Entry(form, width=18)
        e.grid(row=r, column=1, pady=2)
        e.insert(0, default)
        return e

    # Entry Fields
    entry_Su = row("Ultimate Strength Su (psi)", "100000", 0)
    entry_Sy = row("Yield Strength Sy (psi)", "70000", 1)
    entry_Se = row("Endurance Limit Se′ (psi)", "50000", 2)
    entry_Sm = row("Mean Stress σm (psi)", "20000", 3)
    entry_Sa = row("Alt Stress σa (psi)", "15000", 4)

    ttk.Label(form, text="--- Modification Factors ---").grid(columnspan=2, pady=10)

    entry_Cload = row("C_load", "1.0", 5)
    entry_Csurf = row("C_surface", "0.8", 6)
    entry_Csize = row("C_size", "0.85", 7)
    entry_Ctemp = row("C_temp", "1.0", 8)
    entry_Crel = row("C_reliab", "0.9", 9)

    # Buttons
    ttk.Button(left_frame, text="Calculate Fatigue Safety", command=calculate).pack(pady=10)
    ttk.Button(left_frame, text="Terminate Program", command=lambda: [root.destroy(), quit()]).pack()

    # Right side
    result_frame = ttk.Frame(right_frame); result_frame.pack(anchor="nw", fill='x', pady=10)
    plot_frame = ttk.Frame(right_frame); plot_frame.pack(fill='both', expand=True)

    root.mainloop()

launch_fatigue_gui()
