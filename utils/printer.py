import os
import subprocess

def imprimir_ticket(contenido, impresora='SeafonPOS58'):
    """
    Imprime un ticket de texto plano en la impresora térmica conectada.

    :param contenido: El texto del ticket (str)
    :param impresora: Nombre del dispositivo CUPS (por default SeafonPOS58)
    """
    try:
        subprocess.run(['lp', '-d', impresora], input=contenido.encode('utf-8'), check=True)
    except subprocess.CalledProcessError as e:
        print("Error al imprimir ticket:", e)
