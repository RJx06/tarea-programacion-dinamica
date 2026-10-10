import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from modelo import (
    FuncionCosto, ProblemaFuerzaTrabajo, SolucionadorPD, Reporte,
    REQUERIMIENTOS_PDF, COSTO_EXCEDENTE_PDF, COSTO_FIJO_PDF,
    COSTO_VARIABLE_PDF, FUERZA_INICIAL_PDF,
)


FONDO = "#f3f5f9"
PANEL = "#ffffff"
PRIMARIO = "#1f4e79"
PRIMARIO_HOVER = "#2a6599"
ACENTO = "#2e9e6b"
TEXTO = "#1d2733"
TEXTO_SUAVE = "#5b6776"
BORDE = "#d6dce5"
OPTIMO = "#e3f4ea"
BARRA_REQ = "#9fb6cf"
BARRA_X = "#1f4e79"

FUENTE = ("Segoe UI", 10)
FUENTE_NEGRITA = ("Segoe UI", 10, "bold")
FUENTE_TITULO = ("Segoe UI Semibold", 16)
FUENTE_SUBTITULO = ("Segoe UI Semibold", 11)
FUENTE_MONO = ("Consolas", 10)
MAX_SEMANAS = 12


class AplicacionFuerzaTrabajo(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Modelo de tamaño de la fuerza de trabajo - Programación Dinámica")
        self.geometry("1280x780")
        self.minsize(1050, 650)
        self.state("zoomed")
        self.configure(bg=FONDO)
        self.texto_reporte = ""
        self.entradas_b = []
        self._estilos()
        self._construir()
        self.restaurar_pdf()

    def _estilos(self):
        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure(".", background=FONDO, foreground=TEXTO, font=FUENTE)
        estilo.configure("Panel.TFrame", background=PANEL)
        estilo.configure("Panel.TLabel", background=PANEL, foreground=TEXTO)
        estilo.configure("Suave.TLabel", background=PANEL, foreground=TEXTO_SUAVE, font=("Segoe UI", 9))
        estilo.configure("Seccion.TLabel", background=PANEL, foreground=PRIMARIO, font=FUENTE_SUBTITULO)
        estilo.configure("Encabezado.TFrame", background=PRIMARIO)
        estilo.configure("Encabezado.TLabel", background=PRIMARIO, foreground="white", font=FUENTE_TITULO)
        estilo.configure("SubEncabezado.TLabel", background=PRIMARIO, foreground="#cfe0f1", font=FUENTE)
        estilo.configure("TEntry", fieldbackground="white", bordercolor=BORDE, padding=4)
        estilo.configure("TSpinbox", fieldbackground="white", bordercolor=BORDE, padding=4)
        estilo.configure("Primario.TButton", background=PRIMARIO, foreground="white",
                         font=FUENTE_NEGRITA, padding=(12, 8), borderwidth=0)
        estilo.map("Primario.TButton", background=[("active", PRIMARIO_HOVER)])
        estilo.configure("Secundario.TButton", background="#e6ebf2", foreground=TEXTO,
                         padding=(10, 6), borderwidth=0)
        estilo.map("Secundario.TButton", background=[("active", "#d5dde8")])
        estilo.configure("TNotebook", background=FONDO, borderwidth=0)
        estilo.configure("TNotebook.Tab", padding=(16, 8), font=FUENTE_NEGRITA,
                         background="#e6ebf2", foreground=TEXTO_SUAVE)
        estilo.map("TNotebook.Tab", background=[("selected", PANEL)], foreground=[("selected", PRIMARIO)])
        estilo.configure("Treeview", rowheight=26, font=FUENTE, fieldbackground="white", bordercolor=BORDE)
        estilo.configure("Treeview.Heading", font=FUENTE_NEGRITA, background="#e6ebf2", foreground=TEXTO)
        estilo.configure("Tarjeta.TFrame", background=PANEL, relief="solid", borderwidth=1)
        estilo.configure("TarjetaValor.TLabel", background=PANEL, foreground=ACENTO,
                         font=("Segoe UI Semibold", 20))
        estilo.configure("TarjetaValorAzul.TLabel", background=PANEL, foreground=PRIMARIO,
                         font=("Segoe UI Semibold", 13))

    def _construir(self):
        encabezado = ttk.Frame(self, style="Encabezado.TFrame", padding=(20, 14))
        encabezado.pack(fill="x")
        ttk.Label(encabezado, text="Modelo de tamaño de la fuerza de trabajo",
                  style="Encabezado.TLabel").pack(anchor="w")
        ttk.Label(encabezado, text="Programación Dinámica · Métodos Cuantitativos · UJAP",
                  style="SubEncabezado.TLabel").pack(anchor="w")

        cuerpo = ttk.Frame(self, padding=14)
        cuerpo.pack(fill="both", expand=True)
        self._panel_datos(cuerpo)
        self._panel_resultados(cuerpo)

    def _panel_datos(self, padre):
        panel = ttk.Frame(padre, style="Panel.TFrame", padding=16)
        panel.pack(side="left", fill="y", padx=(0, 14))

        ttk.Label(panel, text="Datos del problema", style="Seccion.TLabel").pack(anchor="w")
        ttk.Label(panel, text="Por defecto se cargan los datos del PDF.",
                  style="Suave.TLabel").pack(anchor="w", pady=(0, 10))

        fila = ttk.Frame(panel, style="Panel.TFrame")
        fila.pack(fill="x", pady=(0, 8))
        ttk.Label(fila, text="Número de semanas", style="Panel.TLabel").pack(side="left")
        self.var_semanas = tk.IntVar(value=len(REQUERIMIENTOS_PDF))
        ttk.Spinbox(fila, from_=1, to=MAX_SEMANAS, width=5, textvariable=self.var_semanas,
                    command=self._ajustar_semanas, state="readonly").pack(side="right")

        ttk.Label(panel, text="Trabajadores requeridos por semana (bi)",
                  style="Panel.TLabel").pack(anchor="w", pady=(4, 4))
        self.marco_b = ttk.Frame(panel, style="Panel.TFrame")
        self.marco_b.pack(fill="x")

        ttk.Separator(panel).pack(fill="x", pady=10)
        ttk.Label(panel, text="Costos ($)", style="Seccion.TLabel").pack(anchor="w", pady=(0, 6))
        self.var_excedente = tk.StringVar()
        self.var_fijo = tk.StringVar()
        self.var_variable = tk.StringVar()
        self.var_inicial = tk.StringVar()
        self._campo(panel, "Excedente por trabajador por semana", self.var_excedente)
        self._campo(panel, "Costo fijo por contratación", self.var_fijo)
        self._campo(panel, "Costo por trabajador contratado", self.var_variable)

        ttk.Separator(panel).pack(fill="x", pady=10)
        self._campo(panel, "Fuerza de trabajo inicial (x0)", self.var_inicial)

        ttk.Button(panel, text="Resolver", style="Primario.TButton",
                   command=self.resolver).pack(fill="x", pady=(14, 6))
        secundarios = ttk.Frame(panel, style="Panel.TFrame")
        secundarios.pack(fill="x")
        ttk.Button(secundarios, text="Restaurar PDF", style="Secundario.TButton",
                   command=self.restaurar_pdf).pack(side="left", fill="x", expand=True, padx=(0, 3))
        ttk.Button(secundarios, text="Guardar .txt", style="Secundario.TButton",
                   command=self.guardar_txt).pack(side="left", fill="x", expand=True, padx=(3, 0))

    def _campo(self, padre, etiqueta, variable):
        fila = ttk.Frame(padre, style="Panel.TFrame")
        fila.pack(fill="x", pady=3)
        ttk.Label(fila, text=etiqueta, style="Panel.TLabel").pack(side="left")
        ttk.Entry(fila, textvariable=variable, width=8, justify="center").pack(side="right")

    def _ajustar_semanas(self, valores=None):
        actuales = [e.get() for e in self.entradas_b]
        if valores is None:
            valores = actuales
        for hijo in self.marco_b.winfo_children():
            hijo.destroy()
        self.entradas_b = []
        n = self.var_semanas.get()
        for i in range(n):
            columna, fila = i % 4, i // 4
            celda = ttk.Frame(self.marco_b, style="Panel.TFrame")
            celda.grid(row=fila, column=columna, padx=4, pady=3, sticky="w")
            ttk.Label(celda, text=f"b{i + 1}", style="Panel.TLabel", width=3).pack(side="left")
            entrada = ttk.Entry(celda, width=5, justify="center")
            entrada.insert(0, valores[i] if i < len(valores) else "0")
            entrada.pack(side="left")
            self.entradas_b.append(entrada)

    def _panel_resultados(self, padre):
        self.cuaderno = ttk.Notebook(padre)
        self.cuaderno.pack(side="left", fill="both", expand=True)

        self.tab_solucion = ttk.Frame(self.cuaderno, style="Panel.TFrame", padding=16)
        self.tab_tablas = ttk.Frame(self.cuaderno, style="Panel.TFrame")
        self.tab_pasos = ttk.Frame(self.cuaderno, style="Panel.TFrame", padding=8)
        self.cuaderno.add(self.tab_solucion, text="Solución óptima")
        self.cuaderno.add(self.tab_tablas, text="Tablas por etapa")
        self.cuaderno.add(self.tab_pasos, text="Paso a paso")

        self._construir_tab_solucion()
        self._construir_tab_tablas()
        self._construir_tab_pasos()

    def _construir_tab_solucion(self):
        tarjetas = ttk.Frame(self.tab_solucion, style="Panel.TFrame")
        tarjetas.pack(fill="x", pady=(0, 12))
        self.lbl_costo = self._tarjeta(tarjetas, "Costo total mínimo", "TarjetaValor.TLabel")
        self.lbl_politica = self._tarjeta(tarjetas, "Política óptima", "TarjetaValorAzul.TLabel")

        columnas = ("semana", "b", "xant", "x", "decision", "c1", "c2", "costo")
        titulos = ("Semana", "bi", "xi-1", "xi", "Decisión", "C1 ($)", "C2 ($)", "Costo ($)")
        anchos = (70, 50, 60, 50, 230, 80, 80, 90)
        marco_tabla = ttk.Frame(self.tab_solucion, style="Panel.TFrame")
        marco_tabla.pack(fill="x")
        self.tabla_solucion = ttk.Treeview(marco_tabla, columns=columnas, show="headings", height=8)
        for col, tit, an in zip(columnas, titulos, anchos):
            self.tabla_solucion.heading(col, text=tit)
            self.tabla_solucion.column(col, width=an, anchor="w" if col == "decision" else "center")
        self.tabla_solucion.tag_configure("total", font=FUENTE_NEGRITA, background=OPTIMO)
        barra = ttk.Scrollbar(marco_tabla, orient="vertical", command=self.tabla_solucion.yview)
        self.tabla_solucion.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        self.tabla_solucion.pack(side="left", fill="x", expand=True)

        ttk.Label(self.tab_solucion, text="Trabajadores requeridos vs. trabajadores mantenidos",
                  style="Seccion.TLabel").pack(anchor="w", pady=(16, 4))
        self.lienzo = tk.Canvas(self.tab_solucion, bg=PANEL, highlightthickness=0, height=260)
        self.lienzo.pack(fill="both", expand=True)
        self.lienzo.bind("<Configure>", lambda e: self._dibujar_grafico())

    def _tarjeta(self, padre, titulo, estilo_valor):
        tarjeta = ttk.Frame(padre, style="Tarjeta.TFrame", padding=(16, 10))
        tarjeta.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ttk.Label(tarjeta, text=titulo, style="Suave.TLabel").pack(anchor="w")
        valor = ttk.Label(tarjeta, text="-", style=estilo_valor)
        valor.pack(anchor="w")
        return valor

    def _construir_tab_tablas(self):
        lienzo = tk.Canvas(self.tab_tablas, bg=PANEL, highlightthickness=0)
        barra = ttk.Scrollbar(self.tab_tablas, orient="vertical", command=lienzo.yview)
        self.marco_tablas = ttk.Frame(lienzo, style="Panel.TFrame", padding=16)
        self.marco_tablas.bind("<Configure>", lambda e: lienzo.configure(scrollregion=lienzo.bbox("all")))
        ventana = lienzo.create_window((0, 0), window=self.marco_tablas, anchor="nw")
        lienzo.bind("<Configure>", lambda e: lienzo.itemconfigure(ventana, width=e.width))
        lienzo.configure(yscrollcommand=barra.set)
        lienzo.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        lienzo.bind_all("<MouseWheel>", lambda e: self._desplazar(lienzo, e))

    def _desplazar(self, lienzo, evento):
        if self.cuaderno.index("current") == 1:
            lienzo.yview_scroll(int(-evento.delta / 120), "units")

    def _construir_tab_pasos(self):
        self.texto = tk.Text(self.tab_pasos, font=FUENTE_MONO, wrap="none", bg="#fbfcfe",
                             fg=TEXTO, relief="flat", padx=12, pady=10)
        barra_y = ttk.Scrollbar(self.tab_pasos, orient="vertical", command=self.texto.yview)
        barra_x = ttk.Scrollbar(self.tab_pasos, orient="horizontal", command=self.texto.xview)
        self.texto.configure(yscrollcommand=barra_y.set, xscrollcommand=barra_x.set)
        self.texto.tag_configure("titulo", foreground=PRIMARIO, font=("Consolas", 10, "bold"))
        self.texto.tag_configure("optimo", background=OPTIMO, foreground=ACENTO)
        barra_y.pack(side="right", fill="y")
        barra_x.pack(side="bottom", fill="x")
        self.texto.pack(fill="both", expand=True)

    def restaurar_pdf(self):
        self.var_semanas.set(len(REQUERIMIENTOS_PDF))
        self.entradas_b = []
        self._ajustar_semanas([str(b) for b in REQUERIMIENTOS_PDF])
        self.var_excedente.set(str(COSTO_EXCEDENTE_PDF))
        self.var_fijo.set(str(COSTO_FIJO_PDF))
        self.var_variable.set(str(COSTO_VARIABLE_PDF))
        self.var_inicial.set(str(FUERZA_INICIAL_PDF))
        self.resolver()

    def _leer_entero(self, texto, nombre):
        try:
            valor = int(texto.strip())
        except ValueError:
            raise ValueError(f"'{nombre}' debe ser un número entero (valor recibido: '{texto}').")
        if valor < 0:
            raise ValueError(f"'{nombre}' no puede ser negativo.")
        return valor

    def _leer_problema(self):
        requerimientos = [self._leer_entero(e.get(), f"b{i + 1}") for i, e in enumerate(self.entradas_b)]
        costos = FuncionCosto(
            self._leer_entero(self.var_excedente.get(), "Costo de excedente"),
            self._leer_entero(self.var_fijo.get(), "Costo fijo de contratación"),
            self._leer_entero(self.var_variable.get(), "Costo por trabajador contratado"),
        )
        inicial = self._leer_entero(self.var_inicial.get(), "Fuerza de trabajo inicial")
        return ProblemaFuerzaTrabajo(requerimientos, costos, inicial)

    def resolver(self):
        try:
            problema = self._leer_problema()
        except ValueError as error:
            messagebox.showerror("Datos inválidos", str(error))
            return
        solucionador = SolucionadorPD(problema)
        politica = solucionador.resolver()
        self.problema = problema
        self.solucionador = solucionador
        self.politica = politica
        self.texto_reporte = Reporte(problema, solucionador).texto()
        self._mostrar_solucion()
        self._mostrar_tablas()
        self._mostrar_pasos()

    def _mostrar_solucion(self):
        self.lbl_costo.configure(text=f"${self.solucionador.costo_minimo:,}")
        self.lbl_politica.configure(text="   ".join(f"x{p.semana}={p.x}" for p in self.politica))
        self.tabla_solucion.delete(*self.tabla_solucion.get_children())
        for p in self.politica:
            self.tabla_solucion.insert("", "end", values=(
                p.semana, p.b, p.x_anterior, p.x, p.descripcion,
                f"{p.celda.c1:,}", f"{p.celda.c2:,}", f"{p.costo_semana:,}"))
        self.tabla_solucion.insert("", "end", tags=("total",), values=(
            "", "", "", "", "Costo total mínimo", "", "", f"{self.solucionador.costo_minimo:,}"))
        self.tabla_solucion.configure(height=min(len(self.politica) + 1, 7))
        self._dibujar_grafico()

    def _dibujar_grafico(self):
        if not hasattr(self, "politica"):
            return
        c = self.lienzo
        c.delete("all")
        ancho, alto = c.winfo_width(), c.winfo_height()
        if ancho < 50 or alto < 50:
            return
        margen_izq, margen_inf, margen_sup = 40, 34, 26
        maximo = max(max(p.x for p in self.politica), max(p.b for p in self.politica), 1)
        util_alto = alto - margen_inf - margen_sup
        base = alto - margen_inf
        paso = max(1, -(-maximo * 18 // max(util_alto, 1)))
        for k in range(0, maximo + 1, paso):
            y = base - util_alto * k / maximo
            c.create_line(margen_izq, y, ancho - 10, y, fill="#eef1f5")
            c.create_text(margen_izq - 8, y, text=str(k), anchor="e", fill=TEXTO_SUAVE, font=("Segoe UI", 8))
        n = len(self.politica)
        grupo = (ancho - margen_izq - 20) / n
        barra = min(34, grupo / 3)
        for idx, p in enumerate(self.politica):
            centro = margen_izq + grupo * idx + grupo / 2
            for valor, color, desplazamiento in ((p.b, BARRA_REQ, -barra / 2 - 2), (p.x, BARRA_X, barra / 2 + 2)):
                x0 = centro + desplazamiento - barra / 2
                y = base - util_alto * valor / maximo
                c.create_rectangle(x0, y, x0 + barra, base, fill=color, outline="")
                c.create_text(x0 + barra / 2, y - 8, text=str(valor), fill=TEXTO, font=("Segoe UI", 9, "bold"))
            c.create_text(centro, base + 14, text=f"Semana {p.semana}", fill=TEXTO_SUAVE, font=("Segoe UI", 9))
        for k, (texto, color) in enumerate((("Requeridos (bi)", BARRA_REQ), ("Mantenidos (xi)", BARRA_X))):
            x0 = ancho - 270 + k * 135
            c.create_rectangle(x0, 6, x0 + 12, 18, fill=color, outline="")
            c.create_text(x0 + 18, 12, text=texto, anchor="w", fill=TEXTO, font=("Segoe UI", 9))

    def _mostrar_tablas(self):
        for hijo in self.marco_tablas.winfo_children():
            hijo.destroy()
        ttk.Label(self.marco_tablas,
                  text=f"fi(xi-1) = min {{ C1(xi - bi) + C2(xi - xi-1) + fi+1(xi) }}      "
                       f"f{self.problema.n + 1}(x{self.problema.n}) = 0",
                  style="Panel.TLabel", font=FUENTE_MONO).pack(anchor="w")
        ttk.Label(self.marco_tablas,
                  text="[valor] = mejor decisión para ese estado   ·   fila verde = estado en la ruta óptima",
                  style="Suave.TLabel").pack(anchor="w", pady=(2, 10))
        for i in range(self.problema.n, 0, -1):
            self._tabla_etapa(self.solucionador.etapas[i])

    def _tabla_etapa(self, etapa):
        i = etapa.numero
        ttk.Label(self.marco_tablas, text=f"Etapa {i}  ·  Semana {i}  ·  b{i} = {etapa.b}",
                  style="Seccion.TLabel").pack(anchor="w", pady=(10, 4))
        columnas = ["estado"] + [f"d{x}" for x in etapa.decisiones] + ["f", "xopt"]
        tabla = ttk.Treeview(self.marco_tablas, columns=columnas, show="headings",
                             height=len(etapa.estados))
        tabla.heading("estado", text=f"x{i - 1}")
        tabla.column("estado", width=70, anchor="center")
        for x in etapa.decisiones:
            tabla.heading(f"d{x}", text=f"x{i} = {x}")
            tabla.column(f"d{x}", width=90, anchor="center")
        tabla.heading("f", text=f"f{i}(x{i - 1})")
        tabla.column("f", width=100, anchor="center")
        tabla.heading("xopt", text=f"x{i}*")
        tabla.column("xopt", width=70, anchor="center")
        tabla.tag_configure("ruta", background=OPTIMO, font=FUENTE_NEGRITA)
        x_en_ruta = self.politica[i - 1].x_anterior
        for x_ant in etapa.estados:
            valores = [x_ant]
            for x in etapa.decisiones:
                total = etapa.celdas[(x_ant, x)].total
                valores.append(f"[{total:,}]" if etapa.decision_optima[x_ant] == x else f"{total:,}")
            valores += [f"{etapa.f[x_ant]:,}", etapa.decision_optima[x_ant]]
            tabla.insert("", "end", values=valores, tags=("ruta",) if x_ant == x_en_ruta else ())
        tabla.pack(anchor="w", fill="x")

    def _mostrar_pasos(self):
        self.texto.configure(state="normal")
        self.texto.delete("1.0", "end")
        for linea in self.texto_reporte.splitlines():
            if "<- óptimo" in linea:
                tag = "optimo"
            elif linea.lstrip().startswith(("MODELO", "ETAPA", "SOLUCIÓN")):
                tag = "titulo"
            else:
                tag = ()
            self.texto.insert("end", linea + "\n", tag)
        self.texto.configure(state="disabled")

    def guardar_txt(self):
        ruta = filedialog.asksaveasfilename(
            title="Guardar salidas", defaultextension=".txt", initialfile="salidas.txt",
            filetypes=[("Archivo de texto", "*.txt")])
        if not ruta:
            return
        with open(ruta, "w", encoding="utf-8") as archivo:
            archivo.write(self.texto_reporte)
        messagebox.showinfo("Salidas guardadas", f"Se guardaron las salidas en:\n{ruta}")
