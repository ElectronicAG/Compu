# Importar las bibliotecas necesarias
import tkinter as tk
from tkinter import ttk
import math
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter.messagebox


# Función para calcular la frecuencia de resonancia
def calcular_frecuencia_resonancia():
    try:
        R_val = float(entry_resistencia.get())
        L_val = float(entry_inductancia.get())
        C_val = float(entry_capacitor.get())

        prefijo_R = combo_resistencia.get()
        prefijo_L = combo_inductancia.get()
        prefijo_C = combo_capacitor.get()

        R = R_val * convert_prefijo(prefijo_R)
        L = L_val * convert_prefijo(prefijo_L)
        C = C_val * convert_prefijo(prefijo_C)

        f_resonancia = 1 / (2 * math.pi * math.sqrt(L * C))
        label_resultado.config(text=f"Frecuencia de Resonancia: {f_resonancia:.2f} Hz")

    except ValueError:
        label_resultado.config(text="Por favor ingresa valores válidos.")

# Función para convertir los prefijos a unidades estándar
def convert_prefijo(prefijo):
    prefijos = {
        'pico': 1e-12, 'nano': 1e-9, 'micro': 1e-6, 'mili': 1e-3,
        'centi': 1e-2, 'kilo': 1e3, 'mega': 1e6, 'giga': 1e9
    }
    return prefijos.get(prefijo, 1)

# Función para calcular la impedancia y el tipo de amortiguamiento
def calcular_impedancia():
    try:
        f_ingresada = float(entry_frecuencia.get())
        prefijo_f = combo_frecuencia.get()
        f = f_ingresada * convert_prefijo(prefijo_f)

        L_val = float(entry_inductancia.get())
        C_val = float(entry_capacitor.get())

        prefijo_L = combo_inductancia.get()
        prefijo_C = combo_capacitor.get()

        L = L_val * convert_prefijo(prefijo_L)
        C = C_val * convert_prefijo(prefijo_C)

        R_val = float(entry_resistencia.get())
        prefijo_R = combo_resistencia.get()
        R = R_val * convert_prefijo(prefijo_R)

        # Obtener el tipo de circuito seleccionado
        tipo_circuito = var_tipo_circuito.get()

        # Calcular las reactancias
        X_L = 2 * math.pi * f * L
        X_C = 1 / (2 * math.pi * f * C)

        # Calcular la impedancia y el factor de amortiguamiento según el tipo de circuito
        if tipo_circuito == "Serie":
            Z = math.sqrt(R**2 + (X_L - X_C)**2)
            # Factor de amortiguamiento para circuito serie
            zeta = R / (2 * math.sqrt(L / C))
        elif tipo_circuito == "Paralelo":
            Z = 1 / math.sqrt((1 / R)**2 + (1 / X_L - 1 / X_C)**2)
            # Factor de amortiguamiento para circuito paralelo
            zeta = (1 / R) / (2 * math.sqrt(C / L))

        # Calcular la frecuencia angular
        omega = 2 * math.pi * f

        # Determinar el tipo de amortiguamiento
        if zeta > 1:
            amortiguamiento = "Sobreamortiguado"
        elif abs(zeta - 1) < 1e-6:
            amortiguamiento = "Críticamente Amortiguado"
        else:
            amortiguamiento = "Subamortiguado"

        # Mostrar los resultados en la interfaz gráfica
        label_impedancia.config(text=f"Impedancia: {Z:.2f} Ω")
        label_XL.config(text=f"Reactancia Inductiva: {X_L:.2f} Ω")
        label_XC.config(text=f"Reactancia Capacitiva: {X_C:.2f} Ω")
        label_omega.config(text=f"Frecuencia Angular: {omega:.2f} rad/s")
        label_amortiguamiento.config(text=f"Tipo de Amortiguamiento: {amortiguamiento}")

    except ValueError:
        label_impedancia.config(text="Por favor ingresa valores válidos.")


#Función para calcular y graficar la respuesta temporal
def graficar_respuesta_temporal():
    try:
        # Obtener los valores de R, L y C
        R_val = float(entry_resistencia.get())
        L_val = float(entry_inductancia.get())
        C_val = float(entry_capacitor.get())

        prefijo_R = combo_resistencia.get()
        prefijo_L = combo_inductancia.get()
        prefijo_C = combo_capacitor.get()

        R = R_val * convert_prefijo(prefijo_R)
        L = L_val * convert_prefijo(prefijo_L)
        C = C_val * convert_prefijo(prefijo_C)

        # Calcular omega_0 y zeta
        omega_0 = 1 / np.sqrt(L * C)
        zeta = R / (2 * np.sqrt(L / C))

        V_0 = 1  # Escalón unitario de tensión

        if zeta < 1:  # Subamortiguado
            omega_d = omega_0 * np.sqrt(1 - zeta**2)
            t_max = 5 / omega_0
            t = np.linspace(0, t_max, 1000)
            exp_term = np.exp(-zeta * omega_0 * t)
            sin_term = np.sin(omega_d * t)
            cos_term = np.cos(omega_d * t)
            denom = np.sqrt(1 - zeta**2)
            V_t = V_0 * (1 - exp_term * (cos_term + (zeta / denom) * sin_term))
        elif abs(zeta - 1) < 1e-6:  # Críticamente amortiguado
            t_max = 5 / omega_0
            t = np.linspace(0, t_max, 1000)
            exp_term = np.exp(-omega_0 * t)
            V_t = V_0 * (1 - exp_term * (1 + omega_0 * t))
        else:  # Sobreamortiguado
            omega_d = omega_0 * np.sqrt(zeta**2 - 1)
            t_max = 5 / omega_d  # Ajuste de t_max para evitar overflow
            t = np.linspace(0, t_max, 1000)
            exp_term = np.exp(-zeta * omega_0 * t)
            denom = np.sqrt(zeta**2 - 1)
            sinh_term = np.sinh(omega_d * t)
            cosh_term = np.cosh(omega_d * t)
            V_t = V_0 * (1 - exp_term * (cosh_term + (zeta / denom) * sinh_term))

        # Crear la figura y el gráfico
        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(t, V_t)
        ax.set_title("Respuesta Temporal del Circuito RLC")
        ax.set_xlabel("Tiempo (s)")
        ax.set_ylabel("Voltaje (V)")
        ax.grid(True)

        # Limpiar el canvas si ya existe
        for widget in grafica_frame.winfo_children():
            widget.destroy()

        # Mostrar la figura en Tkinter
        canvas = FigureCanvasTkAgg(fig, master=grafica_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0)

    except ValueError:
        tk.messagebox.showerror("Error", "Por favor ingresa valores válidos.")


# Crear la ventana principal y aplicar un tema
root = tk.Tk()
root.title("Calculadora de Circuitos RLC")
root.iconbitmap("logo-uvg-1.ico")  

style = ttk.Style()
style.theme_use('xpnative')


# Crear y configurar el estilo personalizado
style.configure('Calcular.TButton',
                background='lightblue',
                foreground='black',
                font=('Helvetica', 10, 'bold'))

style.map('Calcular.TButton',
          background=[('active', 'skyblue'), ('pressed', 'steelblue')])

# Configurar el tamaño mínimo de la ventana
root.minsize(400, 600)

# Crear un Frame contenedor para el Canvas y las Scrollbars
container = ttk.Frame(root)
container.grid(row=0, column=0, sticky="nsew")

# Hacer que el contenedor se expanda
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Crear un Canvas dentro del contenedor
canvas = tk.Canvas(container)
canvas.grid(row=0, column=0, sticky="nsew")

# Agregar barras de desplazamiento al Canvas
scrollbar_y = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
scrollbar_y.grid(row=0, column=1, sticky="ns")

scrollbar_x = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
scrollbar_x.grid(row=1, column=0, sticky="ew")

canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

# Crear el frame principal dentro del Canvas
mainframe = ttk.Frame(canvas)

# Añadir el frame al Canvas
canvas.create_window((0, 0), window=mainframe, anchor="nw")

# Función para ajustar el scroll region del Canvas
def ajustar_scroll_region(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

# Vincular la función de ajuste al evento de cambio de tamaño del mainframe
mainframe.bind("<Configure>", ajustar_scroll_region)

# Hacer que el Canvas y el mainframe se expandan
container.columnconfigure(0, weight=1)
container.rowconfigure(0, weight=1)
canvas.columnconfigure(0, weight=1)
canvas.rowconfigure(0, weight=1)

# Habilitar el redimensionamiento con el ratón
def _on_mousewheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

canvas.bind_all("<MouseWheel>", _on_mousewheel)


# Parámetros de entrada
input_frame = ttk.LabelFrame(mainframe, text="Parámetros de Entrada", padding="10 10 10 10")
input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

ttk.Label(input_frame, text="Resistencia (R):").grid(row=0, column=0, sticky=tk.W)
entry_resistencia = ttk.Entry(input_frame, width=10)
entry_resistencia.grid(row=0, column=1)
combo_resistencia = ttk.Combobox(input_frame, values=['', 'pico', 'nano', 'micro', 'mili', 'centi', 'kilo', 'mega', 'giga'], width=5)
combo_resistencia.grid(row=0, column=2)
combo_resistencia.current(0)

ttk.Label(input_frame, text="Inductancia (L):").grid(row=1, column=0, sticky=tk.W)
entry_inductancia = ttk.Entry(input_frame, width=10)
entry_inductancia.grid(row=1, column=1)
combo_inductancia = ttk.Combobox(input_frame, values=['', 'pico', 'nano', 'micro', 'mili', 'centi', 'kilo', 'mega', 'giga'], width=5)
combo_inductancia.grid(row=1, column=2)
combo_inductancia.current(0)

ttk.Label(input_frame, text="Capacitancia (C):").grid(row=2, column=0, sticky=tk.W)
entry_capacitor = ttk.Entry(input_frame, width=10)
entry_capacitor.grid(row=2, column=1)
combo_capacitor = ttk.Combobox(input_frame, values=['', 'pico', 'nano', 'micro', 'mili', 'centi', 'kilo', 'mega', 'giga'], width=5)
combo_capacitor.grid(row=2, column=2)
combo_capacitor.current(0)

# Botón para calcular frecuencia de resonancia
boton_frame = ttk.Frame(mainframe, padding="10 10 10 10")
boton_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))

boton_calcular_frecuencia = ttk.Button(boton_frame, text="Calcular Frecuencia de Resonancia", command=calcular_frecuencia_resonancia, style='Calcular.TButton')
boton_calcular_frecuencia.grid(row=0, column=0, pady=5)

# Resultado de frecuencia de resonancia
resultado_frame = ttk.Frame(mainframe, padding="10 10 10 10")
resultado_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))

label_resultado = ttk.Label(resultado_frame, text="Frecuencia de Resonancia: ")
label_resultado.grid(row=0, column=0, sticky=tk.W)

# Tipo de circuito
tipo_circuito_frame = ttk.LabelFrame(mainframe, text="Tipo de Circuito", padding="10 10 10 10")
tipo_circuito_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))

var_tipo_circuito = tk.StringVar(value="Serie")
ttk.Radiobutton(tipo_circuito_frame, text="Serie", variable=var_tipo_circuito, value="Serie").grid(row=0, column=0, sticky=tk.W)
ttk.Radiobutton(tipo_circuito_frame, text="Paralelo", variable=var_tipo_circuito, value="Paralelo").grid(row=0, column=1, sticky=tk.W)

# Frecuencia
frecuencia_frame = ttk.LabelFrame(mainframe, text="Frecuencia", padding="10 10 10 10")
frecuencia_frame.grid(row=4, column=0, sticky=(tk.W, tk.E))

ttk.Label(frecuencia_frame, text="Frecuencia (Hz):").grid(row=0, column=0, sticky=tk.W)
entry_frecuencia = ttk.Entry(frecuencia_frame, width=10)
entry_frecuencia.grid(row=0, column=1)
combo_frecuencia = ttk.Combobox(frecuencia_frame, values=['', 'pico', 'nano', 'micro', 'mili', 'centi', 'kilo', 'mega', 'giga'], width=5)
combo_frecuencia.grid(row=0, column=2)
combo_frecuencia.current(0)

# Botón para calcular impedancia y amortiguamiento
boton_calcular_impedancia = ttk.Button(mainframe, text="Calcular Impedancia y Amortiguamiento", command=calcular_impedancia, style='Calcular.TButton')
boton_calcular_impedancia.grid(row=5, column=0, pady=5)

# Botón para graficar la respuesta temporal
boton_graficar = ttk.Button(mainframe, text="Graficar Respuesta Temporal", command=graficar_respuesta_temporal, style='Calcular.TButton')
boton_graficar.grid(row=8, column=0, pady=5)



# Resultados
resultados_frame = ttk.LabelFrame(mainframe, text="Resultados", padding="10 10 10 10")
resultados_frame.grid(row=6, column=0, sticky=(tk.W, tk.E))


# Frame para la gráfica
grafica_frame = ttk.LabelFrame(mainframe, text="Respuesta Temporal", padding="10 10 10 10")
grafica_frame.grid(row=9, column=0, sticky=(tk.W, tk.E))



label_impedancia = ttk.Label(resultados_frame, text="Impedancia: ")
label_impedancia.grid(row=0, column=0, sticky=tk.W)

label_XL = ttk.Label(resultados_frame, text="Reactancia Inductiva: ")
label_XL.grid(row=1, column=0, sticky=tk.W)

label_XC = ttk.Label(resultados_frame, text="Reactancia Capacitiva: ")
label_XC.grid(row=2, column=0, sticky=tk.W)

label_omega = ttk.Label(resultados_frame, text="Frecuencia Angular: ")
label_omega.grid(row=3, column=0, sticky=tk.W)

label_amortiguamiento = ttk.Label(resultados_frame, text="Tipo de Amortiguamiento: ")
label_amortiguamiento.grid(row=4, column=0, sticky=tk.W)

# Iniciar la interfaz gráfica
root.mainloop()
