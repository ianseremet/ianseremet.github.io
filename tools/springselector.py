import tkinter as tk
from tkinter import ttk, messagebox
import math

def launch_spring_gui():
    def calculate():
        try:
            F_min = float(entry_Fmin.get())
            F_max = float(entry_Fmax.get())
            delta_x = float(entry_dx.get())
            G = float(entry_G.get())  # psi
            Su = float(entry_Su.get())  # psi
            D_guess = float(entry_D.get())  # in
            d_guess = float(entry_d.get())  # in

            # Step 1: Spring rate
            k = (F_max - F_min) / delta_x

            # Step 2: Solid force
            F_solid = 1.1 * F_max

            # Step 3: Assume C, compute Ks, shear yield
            C = D_guess / d_guess
            Ks = (4 * C - 1) / (4 * C - 4) + 0.615 / C
            S_shear_yield = 0.45 * Su  # Juvinall & Marshek

            # Step 4: solve for required d
            d_calc = ((8 * F_solid * D_guess * Ks) / (math.pi * S_shear_yield)) ** (1 / 3)

            # Step 5: resolve D based on d
            C_updated = 5  # assume a standard ratio again
            D_calc = C_updated * d_calc
            Ks_updated = (4 * C_updated - 1) / (4 * C_updated - 4) + 0.615 / C_updated
            S_shear_yield_updated = 0.45 * Su

            # Step 6: Spring rate check
            k_check = (d_calc**4 * G) / (8 * D_calc**3)

            # Step 6 cont: solve for N (active)
            N_active = (d_calc**4 * G) / (8 * k * D_calc**3)
            N_total = N_active + 2  # for squared and ground ends

            # Step 7: solid and free length
            L_solid = N_total * d_calc
            L_free = L_solid + F_max / k

            # Display results
            for widget in result_frame.winfo_children():
                widget.destroy()

            def row(label, value, unit=""):
                frame = ttk.Frame(result_frame); frame.pack(anchor='w')
                ttk.Label(frame, text=f"{label}: ").pack(side='left')
                ttk.Label(frame, text=f"{value:.4f} {unit}", font=("Segoe UI", 11, "bold")).pack(side='left')

            ttk.Label(result_frame, text="Spring Design Results", font=("Segoe UI", 13, "bold")).pack(anchor='w', pady=5)
            row("Spring Rate", k, "lb/in")
            row("Solid Force", F_solid, "lb")
            row("d (wire diameter)", d_calc, "in")
            row("D (mean coil diameter)", D_calc, "in")
            row("Wahl Factor Ks", Ks_updated)
            row("Shear Yield (0.45 Su)", S_shear_yield_updated, "psi")
            row("Active Coils", N_active)
            row("Total Coils", N_total)
            row("Solid Length", L_solid, "in")
            row("Free Length", L_free, "in")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # GUI
    root = tk.Tk()
    root.title("Spring Selector - Juvinall & Marshek Method")
    root.geometry("640x680")
    root.configure(bg="#f4f4f4")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TLabel", font=("Segoe UI", 11), background="#f4f4f4")
    style.configure("TButton", font=("Segoe UI", 11))
    style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"))

    ttk.Label(root, text="Spring Geometry Calculator", style="Header.TLabel").pack(pady=10)

    form = ttk.Frame(root); form.pack(pady=5)

    def row(label, default, r):
        ttk.Label(form, text=label).grid(row=r, column=0, sticky="e", padx=5, pady=2)
        e = ttk.Entry(form, width=20)
        e.grid(row=r, column=1, pady=2)
        e.insert(0, default)
        return e

    entry_Fmin = row("Minimum Force F_min (lb)", "30", 0)
    entry_Fmax = row("Maximum Force F_max (lb)", "50", 1)
    entry_dx = row("Compression Δx (in)", "0.5", 2)
    entry_Su = row("Material Su (psi)", "225000", 3)
    entry_G = row("Shear Modulus G (psi)", "11500000", 4)
    entry_D = row("Initial Mean Diameter D (in)", "0.5", 5)
    entry_d = row("Initial Wire Diameter d (in)", "0.1", 6)

    ttk.Button(root, text="Calculate Spring", command=calculate).pack(pady=10)

    result_frame = ttk.Frame(root); result_frame.pack(pady=10)
    ttk.Button(root, text="Terminate", command=root.destroy).pack(pady=5)

    root.mainloop()

launch_spring_gui()
