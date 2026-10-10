import sys

from modelo import ProblemaFuerzaTrabajo, SolucionadorPD, Reporte


def modo_consola():
    problema = ProblemaFuerzaTrabajo.del_pdf()
    solucionador = SolucionadorPD(problema)
    solucionador.resolver()
    texto = Reporte(problema, solucionador).texto()
    sys.stdout.reconfigure(encoding="utf-8")
    print(texto, end="")
    with open("salidas.txt", "w", encoding="utf-8") as archivo:
        archivo.write(texto)


def modo_grafico():
    from interfaz import AplicacionFuerzaTrabajo
    AplicacionFuerzaTrabajo().mainloop()


if __name__ == "__main__":
    if "--consola" in sys.argv:
        modo_consola()
    else:
        modo_grafico()
