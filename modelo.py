from dataclasses import dataclass


REQUERIMIENTOS_PDF = [5, 7, 8, 4, 6]
COSTO_EXCEDENTE_PDF = 300
COSTO_FIJO_PDF = 400
COSTO_VARIABLE_PDF = 200
FUERZA_INICIAL_PDF = 0


class FuncionCosto:

    def __init__(self, costo_excedente, costo_fijo_contratacion, costo_variable_contratacion):
        self.costo_excedente = costo_excedente
        self.costo_fijo = costo_fijo_contratacion
        self.costo_variable = costo_variable_contratacion

    def c1(self, x, b):
        return self.costo_excedente * (x - b)

    def c2(self, x, x_anterior):
        if x > x_anterior:
            return self.costo_fijo + self.costo_variable * (x - x_anterior)
        return 0


class ProblemaFuerzaTrabajo:

    def __init__(self, requerimientos, costos, fuerza_inicial=0):
        if not requerimientos:
            raise ValueError("Debe haber al menos una semana.")
        if any(b < 0 for b in requerimientos):
            raise ValueError("Los requerimientos no pueden ser negativos.")
        if fuerza_inicial < 0:
            raise ValueError("La fuerza de trabajo inicial no puede ser negativa.")
        if min(costos.costo_excedente, costos.costo_fijo, costos.costo_variable) < 0:
            raise ValueError("Los costos no pueden ser negativos.")
        self.b = list(requerimientos)
        self.costos = costos
        self.fuerza_inicial = fuerza_inicial

    @classmethod
    def del_pdf(cls):
        return cls(REQUERIMIENTOS_PDF,
                   FuncionCosto(COSTO_EXCEDENTE_PDF, COSTO_FIJO_PDF, COSTO_VARIABLE_PDF),
                   FUERZA_INICIAL_PDF)

    @property
    def n(self):
        return len(self.b)

    def requerimiento(self, i):
        return self.b[i - 1]

    def valores_decision(self, i):
        return list(range(self.b[i - 1], max(self.b[i - 1:]) + 1))

    def valores_estado(self, i):
        if i == 1:
            return [self.fuerza_inicial]
        return self.valores_decision(i - 1)


@dataclass
class Celda:
    c1: int
    c2: int
    f_siguiente: int

    @property
    def total(self):
        return self.c1 + self.c2 + self.f_siguiente


class Etapa:

    def __init__(self, numero, b, estados, decisiones):
        self.numero = numero
        self.b = b
        self.estados = estados
        self.decisiones = decisiones
        self.celdas = {}
        self.f = {}
        self.decision_optima = {}

    def registrar(self, x_anterior, x, celda):
        self.celdas[(x_anterior, x)] = celda

    def fijar_optimo(self, x_anterior):
        mejor_x = min(self.decisiones, key=lambda x: self.celdas[(x_anterior, x)].total)
        self.decision_optima[x_anterior] = mejor_x
        self.f[x_anterior] = self.celdas[(x_anterior, mejor_x)].total


@dataclass
class PasoPolitica:
    semana: int
    b: int
    x_anterior: int
    x: int
    celda: Celda

    @property
    def costo_semana(self):
        return self.celda.c1 + self.celda.c2

    @property
    def descripcion(self):
        if self.x > self.x_anterior:
            texto = f"Contratar {self.x - self.x_anterior}"
        elif self.x < self.x_anterior:
            texto = f"Despedir {self.x_anterior - self.x}"
        else:
            texto = "Sin cambios"
        if self.x > self.b:
            texto += f" (excedente de {self.x - self.b})"
        return texto


class SolucionadorPD:

    def __init__(self, problema):
        self.problema = problema
        self.etapas = {}

    def resolver(self):
        p = self.problema
        f_siguiente = {x: 0 for x in p.valores_decision(p.n)}
        for i in range(p.n, 0, -1):
            etapa = Etapa(i, p.requerimiento(i), p.valores_estado(i), p.valores_decision(i))
            for x_anterior in etapa.estados:
                for x in etapa.decisiones:
                    etapa.registrar(x_anterior, x, Celda(
                        c1=p.costos.c1(x, etapa.b),
                        c2=p.costos.c2(x, x_anterior),
                        f_siguiente=f_siguiente[x],
                    ))
                etapa.fijar_optimo(x_anterior)
            self.etapas[i] = etapa
            f_siguiente = etapa.f
        return self.politica_optima()

    def politica_optima(self):
        p = self.problema
        politica = []
        x_anterior = p.fuerza_inicial
        for i in range(1, p.n + 1):
            etapa = self.etapas[i]
            x = etapa.decision_optima[x_anterior]
            politica.append(PasoPolitica(i, etapa.b, x_anterior, x, etapa.celdas[(x_anterior, x)]))
            x_anterior = x
        return politica

    @property
    def costo_minimo(self):
        return self.etapas[1].f[self.problema.fuerza_inicial]


class Reporte:

    ANCHO = 100

    def __init__(self, problema, solucionador):
        self.problema = problema
        self.solucionador = solucionador
        self.lineas = []

    def texto(self):
        self.lineas = []
        self._datos()
        for i in range(self.problema.n, 0, -1):
            self._etapa(self.solucionador.etapas[i])
        self._solucion()
        return "\n".join(self.lineas) + "\n"

    def _p(self, texto=""):
        self.lineas.append(texto)

    def _titulo(self, texto, caracter="="):
        self._p(caracter * self.ANCHO)
        self._p(texto.center(self.ANCHO).rstrip())
        self._p(caracter * self.ANCHO)

    def _datos(self):
        p, c = self.problema, self.problema.costos
        self._titulo("MODELO DE TAMAÑO DE LA FUERZA DE TRABAJO - PROGRAMACIÓN DINÁMICA")
        self._p()
        self._p("Datos del problema:")
        for i in range(1, p.n + 1):
            self._p(f"   Semana {i}: b{i} = {p.requerimiento(i)} trabajadores")
        self._p(f"   Fuerza de trabajo inicial x0 = {p.fuerza_inicial}")
        self._p()
        self._p("Funciones de costo:")
        self._p(f"   C1(xi - bi)   = {c.costo_excedente}(xi - bi)                          -> costo del excedente")
        self._p(f"   C2(xi - xi-1) = {c.costo_fijo} + {c.costo_variable}(xi - xi-1), si xi > xi-1   -> costo de contratación")
        self._p("                 = 0, si xi <= xi-1                          -> despido sin costo")
        self._p()
        self._p("Ecuación recursiva (hacia atrás):")
        self._p(f"   f{p.n + 1}(x{p.n}) = 0")
        self._p("   fi(xi-1) = min { C1(xi - bi) + C2(xi - xi-1) + fi+1(xi) },  bi <= xi <= max{bi, ..., bn}")
        self._p()
        self._p("Rangos de las variables:")
        for i in range(1, p.n + 1):
            d = p.valores_decision(i)
            self._p(f"   x{i}: {d[0]} <= x{i} <= {d[-1]}   -> {d}")
        self._p()

    def _etapa(self, etapa):
        i = etapa.numero
        self._titulo(f"ETAPA {i}  (semana {i}, b{i} = {etapa.b})", "-")
        self._p(f"f{i}(x{i - 1}) = min {{ C1(x{i} - {etapa.b}) + C2(x{i} - x{i - 1}) + f{i + 1}(x{i}) }}")
        self._p()
        self._p("Cálculos:")
        for x_ant in etapa.estados:
            for x in etapa.decisiones:
                c = etapa.celdas[(x_ant, x)]
                marca = "  <- óptimo" if etapa.decision_optima[x_ant] == x else ""
                self._p(f"   x{i - 1}={x_ant}, x{i}={x}:  C1={c.c1:>6}  + C2={c.c2:>6}"
                        f"  + f{i + 1}({x})={c.f_siguiente:>6}  = {c.total:>7}{marca}")
        self._p()
        ancho = max(9, max(len(str(c.total)) for c in etapa.celdas.values()) + 2)
        enc = f"{'x' + str(i - 1):>6} |" + "".join(
            f"{'x' + str(i) + '=' + str(x):>{ancho}}" for x in etapa.decisiones)
        enc += f" | {'f' + str(i) + '(x' + str(i - 1) + ')':>10} {'x' + str(i) + '*':>5}"
        self._p("Tabla de la etapa:")
        self._p(enc)
        self._p("-" * len(enc))
        for x_ant in etapa.estados:
            fila = f"{x_ant:>6} |" + "".join(
                f"{etapa.celdas[(x_ant, x)].total:>{ancho}}" for x in etapa.decisiones)
            fila += f" | {etapa.f[x_ant]:>10} {etapa.decision_optima[x_ant]:>5}"
            self._p(fila)
        self._p()

    def _solucion(self):
        politica = self.solucionador.politica_optima()
        self._titulo("SOLUCIÓN ÓPTIMA")
        self._p()
        enc = (f"{'Semana':>6} {'bi':>4} {'xi-1':>6} {'xi':>4}  {'Decisión':<34}"
               f"{'C1':>8} {'C2':>8} {'Costo':>9}")
        self._p(enc)
        self._p("-" * len(enc))
        for paso in politica:
            self._p(f"{paso.semana:>6} {paso.b:>4} {paso.x_anterior:>6} {paso.x:>4}  {paso.descripcion:<34}"
                    f"{paso.celda.c1:>8} {paso.celda.c2:>8} {paso.costo_semana:>9}")
        self._p("-" * len(enc))
        self._p(f"{'Costo total mínimo:':>70} ${self.solucionador.costo_minimo:,}")
        self._p()
        self._p("Política óptima: " + ", ".join(f"x{p.semana} = {p.x}" for p in politica))
