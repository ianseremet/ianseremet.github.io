import tkinter as tk
from tkinter import ttk, messagebox
from fpdf import FPDF

def launch_bearing_sizer():
    def calculate():
        try:
            L_hours = float(entry_life.get())
            Fr = float(entry_radial.get())
            Ft = float(entry_thrust.get())
            L = L_hours * 60 * 60  # Convert hours to revolutions

            if Fr == 0:
                raise ValueError("Radial load must be non-zero.")

            ft_fr_ratio = Ft / Fr
            bearing_type = bearing_type_var.get()

            if bearing_type == "Radial Ball Bearing (α = 0°)":
                if ft_fr_ratio < 0.35:
                    Fe = Fr
                    Fe_formula = "Fe = Fr"
                elif ft_fr_ratio < 10:
                    Fe = Fr * (1 + 1.115 * (ft_fr_ratio - 0.35))
                    Fe_formula = "Fe = Fr * [1 + 1.115 * (Ft/Fr - 0.35)]"
                else:
                    Fe = 1.176 * Ft
                    Fe_formula = "Fe = 1.176 * Ft"
            elif bearing_type == "Angular Contact Ball Bearing (α = 25°)":
                if ft_fr_ratio < 0.68:
                    Fe = Fr
                    Fe_formula = "Fe = Fr"
                elif ft_fr_ratio < 10:
                    Fe = Fr * (1 + 0.870 * (ft_fr_ratio - 0.68))
                    Fe_formula = "Fe = Fr * [1 + 0.870 * (Ft/Fr - 0.68)]"
                else:
                    Fe = 0.911 * Ft
                    Fe_formula = "Fe = 0.911 * Ft"
            else:
                raise ValueError("Invalid bearing type.")

            K_r = reliability_factors[reliability_var.get()]
            K_a = shock_factors[shock_var.get()]
            a = 3
            L_rating = 1e6

            Creq = Fe * K_r * K_a * (L / L_rating) ** (1 / a)

            for widget in result_frame.winfo_children():
                widget.destroy()

            def row(label, value, unit=""):
                f = ttk.Frame(result_frame); f.pack(anchor='w', pady=1)
                try: formatted = f"{float(value):.2f}"
                except: formatted = str(value)
                ttk.Label(f, text=f"{label}: ", width=32).pack(side='left')
                ttk.Label(f, text=f"{formatted} {unit}", font=("Segoe UI", 11, "bold")).pack(side='left')

            ttk.Label(result_frame, text="Bearing Sizing Result", font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=5)
            row("Ft / Fr Ratio", ft_fr_ratio)
            row("Equivalent Load (Fe)", Fe, "N")
            row("Required Dynamic Load Rating (Creq)", Creq, "N")

            generate_pdf_report(L_hours, Fr, Ft, ft_fr_ratio, Fe, Creq, Fe_formula, K_r, K_a, L, bearing_type)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def generate_pdf_report(L_hours, Fr, Ft, ratio, Fe, Creq, Fe_formula, Kr, Ka, L_revs, btype):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Bearing Sizing Report", ln=True)

        # Replace unsupported characters for PDF (like α)
        clean_type = btype.replace("α", "alpha")

        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, "Input Parameters:", ln=True)
        pdf.cell(0, 8, f" - Design Life (hrs): {L_hours}", ln=True)
        pdf.cell(0, 8, f" - Radial Load Fr (N): {Fr}", ln=True)
        pdf.cell(0, 8, f" - Thrust Load Ft (N): {Ft}", ln=True)
        pdf.cell(0, 8, f" - Bearing Type: {clean_type}", ln=True)
        pdf.cell(0, 8, f" - Reliability Factor (Kr): {Kr}", ln=True)
        pdf.cell(0, 8, f" - Shock Load Factor (Ka): {Ka}", ln=True)

        pdf.ln(5)
        pdf.cell(0, 10, "Calculations:", ln=True)
        pdf.multi_cell(0, 8, f" - Ft / Fr = {ratio:.3f}")
        pdf.multi_cell(0, 8, f" - Formula Used: {Fe_formula}")
        pdf.multi_cell(0, 8, f" - Fe = {Fe:.2f} N")
        pdf.multi_cell(0, 8, f" - Creq = Fe * Kr * Ka * (L / L_rating)^(1/3)")
        pdf.multi_cell(0, 8, f" - Creq = {Creq:.2f} N")

        pdf.ln(5)
        pdf.cell(0, 10, "Conclusion:", ln=True)
        pdf.multi_cell(0, 8, "The bearing selected must have a dynamic load rating (C) greater than or equal to the required Creq above.")

        output_path = "bearing_sizing_report.pdf"
        pdf.output(output_path)
        messagebox.showinfo("PDF Generated", f"Report saved as {output_path}")

    root = tk.Tk()
    root.title("Bearing Sizing Tool")
    root.geometry("850x400")
    root.configure(bg="#f4f4f4")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TLabel", font=("Segoe UI", 11), background="#f4f4f4")
    style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"), background="#f4f4f4")
    style.configure("TButton", font=("Segoe UI", 11))

    ttk.Label(root, text="Rolling Bearing Sizing Tool (with PDF Report)", style="Header.TLabel").pack(pady=10)

    container = ttk.Frame(root); container.pack(fill='both', expand=True)
    left_frame = ttk.Frame(container); left_frame.pack(side='left', padx=10, fill='y')
    right_frame = ttk.Frame(container); right_frame.pack(side='right', fill='both', expand=True)

    form = ttk.Frame(left_frame); form.pack(pady=5)

    def row(label, default, r):
        ttk.Label(form, text=label).grid(row=r, column=0, sticky="e", padx=5, pady=2)
        e = ttk.Entry(form, width=20)
        e.grid(row=r, column=1, pady=2)
        e.insert(0, default)
        return e

    entry_life = row("Design Life (hrs)", "8000", 0)
    entry_radial = row("Radial Load Fr (N)", "1800", 1)
    entry_thrust = row("Thrust Load Ft (N)", "0", 2)

    ttk.Label(form, text="Bearing Type").grid(row=3, column=0, sticky="e", padx=5)
    bearing_type_var = tk.StringVar(value="Radial Ball Bearing (α = 0°)")
    bearing_menu = ttk.Combobox(form, textvariable=bearing_type_var,
                                values=["Radial Ball Bearing (α = 0°)", "Angular Contact Ball Bearing (α = 25°)"])
    bearing_menu.grid(row=3, column=1)

    ttk.Label(form, text="Reliability").grid(row=4, column=0, sticky="e", padx=5)
    reliability_var = tk.StringVar(value="90% (L10)")
    reliability_menu = ttk.Combobox(form, textvariable=reliability_var,
                                    values=["90% (L10)", "95%", "99%"])
    reliability_menu.grid(row=4, column=1)

    ttk.Label(form, text="Shock Load").grid(row=5, column=0, sticky="e", padx=5)
    shock_var = tk.StringVar(value="Smooth/Uniform")
    shock_menu = ttk.Combobox(form, textvariable=shock_var,
                               values=["Smooth/Uniform", "Moderate Shock", "Heavy Shock"])
    shock_menu.grid(row=5, column=1)

    ttk.Button(left_frame, text="Calculate + Generate PDF", command=calculate).pack(pady=10)
    ttk.Button(left_frame, text="Terminate Program", command=lambda: [root.destroy(), quit()]).pack()

    result_frame = ttk.Frame(right_frame); result_frame.pack(pady=20, fill='x')

    reliability_factors = {
        "90% (L10)": 1.0,
        "95%": 0.62,
        "99%": 0.21
    }

    shock_factors = {
        "Smooth/Uniform": 1.0,
        "Moderate Shock": 1.5,
        "Heavy Shock": 2.0
    }

    root.mainloop()

launch_bearing_sizer()
