import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
import re

# --- Load Bolt Tables ---
full_df = pd.read_csv("Tables.csv", skiprows=1)

unified_df = full_df.rename(columns={
    'Size': 'Thread Size', 'UNC TPI': 'TPI', 'UNC Aₜ (in²)': 'Tensile Area'
})[['Thread Size', 'TPI', 'Tensile Area']].dropna()
unified_df['Tensile Area'] = pd.to_numeric(unified_df['Tensile Area'], errors='coerce')
unified_df['TPI'] = pd.to_numeric(unified_df['TPI'], errors='coerce')
unified_df.dropna(inplace=True)

metric_df = full_df.rename(columns={
    'Nominal Dia d (mm)': 'Thread Size', 'Coarse Pitch p (mm)': 'TPI', 'Coarse Stress Area Aₜ (mm²)': 'Tensile Area'
})[['Thread Size', 'TPI', 'Tensile Area']].dropna()
metric_df['Tensile Area'] = pd.to_numeric(metric_df['Tensile Area'], errors='coerce')
metric_df['TPI'] = pd.to_numeric(metric_df['TPI'], errors='coerce')
metric_df.dropna(inplace=True)

imperial_stresses = ['60000', '80000', '105000', '115000', '120000']
metric_stresses = ['400', '600', '700', '800', '1000']

# --- Calculation Logic ---
def calculate_required_area_tension(load, proof_stress):
    return load / proof_stress

def calculate_required_area_shear(load, proof_stress):
    return load / (0.6 * proof_stress)

def calculate_required_area_composite(load, proof_stress):
    return load / (proof_stress * (3**0.5 / 2))

# --- GUI App ---
def launch_gui():
    root = tk.Tk()
    root.title("Bolt Selector Tool")
    root.geometry("750x720")
    root.configure(bg="#f4f4f4")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure(".", font=("Segoe UI", 11), background="#f4f4f4")
    style.configure("TLabel", background="#f4f4f4", foreground="#333")
    style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"), foreground="#222", padding=10)
    style.configure("TButton", padding=6)
    style.configure("TEntry", padding=4)

    def update_entry(entry, val): entry.delete(0, tk.END); entry.insert(0, val)

    def update_dropdowns(*_):
        if unit_var.get() == "Unified":
            proof_dropdown["values"] = imperial_stresses
            yield_dropdown["values"] = imperial_stresses
        else:
            proof_dropdown["values"] = metric_stresses
            yield_dropdown["values"] = metric_stresses

    def calculate():
        try:
            system = unit_var.get()
            load_type = load_type_var.get()
            pre_load = float(entry_load.get())
            sf = float(entry_sf.get())
            proof_stress = float(entry_proof.get())
            yield_stress = float(entry_yield.get())
            load = pre_load * sf

            if system == "Unified":
                df = unified_df.copy()
                unit_force, unit_area, unit_stress, unit_torque = "lbs", "in²", "psi", "lbf·in"
            else:
                df = metric_df.copy()
                unit_force, unit_area, unit_stress, unit_torque = "N", "mm²", "MPa", "N·mm"

            if load_type == "Tensional":
                required_area = calculate_required_area_tension(load, proof_stress)
            elif load_type == "Shear":
                required_area = calculate_required_area_shear(load, proof_stress)
            else:
                required_area = calculate_required_area_composite(load, proof_stress)

            valid_bolts = df[df['Tensile Area'] >= required_area]
            for widget in result_frame.winfo_children(): widget.destroy()

            if valid_bolts.empty:
                ttk.Label(result_frame, text="No suitable bolt found.", style="Header.TLabel", foreground="red").pack()
                return

            best = valid_bolts.iloc[0]
            name, tpi, area = best['Thread Size'], best['TPI'], best['Tensile Area']
            diameter = float(re.search(r"\(([\d.]+)\)", name).group(1)) if system == "Unified" else float(name)

            initial_tension = 0.9 * proof_stress * area
            initial_torque = 0.2 * diameter * initial_tension
            stress = load / area
            yield_result = "NO" if stress <= yield_stress else "YES"

            def row(label, value, unit=""):
                f = ttk.Frame(result_frame); f.pack(anchor="w", pady=1)
                ttk.Label(f, text=f"{label}: ").pack(side="left")
                ttk.Label(f, text=f"{value} {unit}", font=("Segoe UI", 11, "bold")).pack(side="left")

            ttk.Label(result_frame, text="RESULTS", style="Header.TLabel").pack(anchor="w")
            row("System", system)
            row("Load Type", load_type)
            row("Input Load", f"{pre_load:.2f}", unit_force)
            row("Safety Factor", sf)
            row("Post-SF Load", f"{load:.2f}", unit_force)
            row("Required Area", f"{required_area:.5f}", unit_area)
            row("Initial Tension", f"{initial_tension:.2f}", unit_force)
            row("Initial Torque", f"{initial_torque:.2f}", unit_torque)
            row("Bolt", f"{name}-{int(tpi)}")
            row("Table Area", f"{area:.4f}", unit_area)
            row("Bolt Stress", f"{stress:.2f}", unit_stress)
            row("Yield Stress", yield_stress, unit_stress)

            row("Will it Yield?", "NO" if yield_result == "NO" else "YES ⚠", "")

        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numeric values.")

    # --- Interface Layout ---
    unit_var = tk.StringVar(value="Unified")
    load_type_var = tk.StringVar(value="Tensional")

    ttk.Label(root, text="Bolt Selection Calculator", style="Header.TLabel").pack(anchor="center", pady=10)

    main_frame = ttk.Frame(root)
    main_frame.pack(pady=5)

    def form_row(label, default, row):
        ttk.Label(main_frame, text=label).grid(row=row, column=0, sticky="e", padx=5, pady=2)
        e = ttk.Entry(main_frame, width=20)
        e.grid(row=row, column=1, pady=2)
        e.insert(0, default)
        return e

    # Toggles
    ttk.Label(main_frame, text="System:").grid(row=0, column=0, sticky="e")
    ttk.Radiobutton(main_frame, text="Unified", variable=unit_var, value="Unified").grid(row=0, column=1, sticky="w")
    ttk.Radiobutton(main_frame, text="Metric", variable=unit_var, value="Metric").grid(row=0, column=2, sticky="w")

    ttk.Label(main_frame, text="Load Type:").grid(row=1, column=0, sticky="e")
    ttk.Radiobutton(main_frame, text="Tensional", variable=load_type_var, value="Tensional").grid(row=1, column=1, sticky="w")
    ttk.Radiobutton(main_frame, text="Shear", variable=load_type_var, value="Shear").grid(row=1, column=2, sticky="w")
    ttk.Radiobutton(main_frame, text="Composite", variable=load_type_var, value="Composite").grid(row=1, column=3, sticky="w")

    entry_load = form_row("Pre-SF Load", "2500", 2)
    entry_sf = form_row("Safety Factor", "2.5", 3)
    entry_proof = form_row("Proof Stress", "105000", 4)
    entry_yield = form_row("Yield Stress", "115000", 5)

    proof_dropdown = ttk.Combobox(main_frame, values=imperial_stresses, width=8)
    proof_dropdown.set("Choose")
    proof_dropdown.grid(row=4, column=2, padx=5)
    proof_dropdown.bind("<<ComboboxSelected>>", lambda e: update_entry(entry_proof, proof_dropdown.get()))

    yield_dropdown = ttk.Combobox(main_frame, values=imperial_stresses, width=8)
    yield_dropdown.set("Choose")
    yield_dropdown.grid(row=5, column=2, padx=5)
    yield_dropdown.bind("<<ComboboxSelected>>", lambda e: update_entry(entry_yield, yield_dropdown.get()))

    # --- Action Buttons ---
    ttk.Button(root, text="Calculate Bolt Properties", command=calculate).pack(pady=12)
    ttk.Button(root, text="Terminate Program", command=root.destroy).pack()

    # --- Results ---
    result_frame = ttk.Frame(root)
    result_frame.pack(pady=15)

    unit_var.trace_add("write", update_dropdowns)
    update_dropdowns()
    root.mainloop()

launch_gui()
