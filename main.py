import math
import sys
import pygame as pygame
import serial
import threading
import utm

# Huso para la conversión
HusoHorario = 30

# Variables globales
gData = [0, 0]
cerrado = 0


# Para usar correctamente las variables gloabales, usamos estas dos funciones, como solo la funcion que lee escribe,
# no hay region critica
def setcerrar(dato):
    global cerrado
    cerrado = dato


def getcerrar():
    global cerrado
    return cerrado


def getdata():
    global gData
    return gData


def setdata(data):
    global gData
    gData = data


# Función que pasa grados y minutos a solo grados
def fullgrade(grados, minutos):
    minutos = minutos / 60.0
    return grados + minutos


def cambiarsigno(grados: int, letra: str):
    if letra == 'W' or letra == 'S':
        grados = -grados
    return grados


# Función que se va a ejecutar en otro thread
# y que guardará los datos del serial en una variable global
def GetData():
    # puerto serial
    with serial.Serial('/dev/ttyUSB0', 4800, timeout=1, parity=serial.PARITY_NONE, rtscts=1) as ser:
        ser.flush()
        # -----INICIALIZACIÓN----- #
        x, y, hora_antigua = 0, 0, 0
        while True:
            if ser.inWaiting():
                line = str(ser.readline())
                # Si la línea tiene 'GPGGA' la parseamos y extraemos el
                if line.split(',')[0] == "b'$GPGGA" and line.split(',')[6] != '0':
                    splitline = line.split(',')[2:6]

                    # Conversion de grados a utm
                    aux = utm.from_latlon(
                        cambiarsigno(fullgrade(float(splitline[0][0:2]), float(splitline[0][2::])), splitline[1]),
                        cambiarsigno(fullgrade(float(splitline[2][0:3]), float(splitline[2][3::])), splitline[3]),
                        HusoHorario, 'T')

                    # -----Obtener la hora con decimales de la trama que manda el GPS ----- #
                    hh = line.split(',')[1][0:2]
                    mm = line.split(',')[1][2:4]
                    ss = line.split(',')[1][4::]
                    hora = int(hh) + int(mm) / 60 + float(ss) / 1200

                    # -----Diferencia de posicioón respecto de la anterior ----- #
                    x = aux[0]  # valor nuevo
                    y = aux[1]  # valor nuevo

                    distancia = math.sqrt(math.pow(res[0] - x, 2) + math.pow(res[1] - y, 2)) / 1000
                    velocidad = distancia / abs(hora - hora_antigua)

                    # ----- pasar la velocidad a medidas estandarizadas (no como en EEUU :P)----- #
                    hora_antigua = hora
                    res = [x, y, velocidad]
                    setdata(res)

                # hay que cerrar cada thread si queremos salir ademas de cerrar los puertos
                if getcerrar() == 1:
                    ser.close()
                    sys.exit()


# Función que actualizará los datos de la imágen en un hilo distinto

def update_line():
    color = (0, 255, 0)  # Color con el que dibujamos la linea
    imagen = pygame.image.load("/home/alvaro/imagenGPSINSIA.jpg")  # Imagen de la pantalla,

    pxmin = 446119.19
    pxmax = 446326.69
    pymin = 4470560.11
    pymax = 4470973.64
    rpy = 1294 / (pymax - pymin)
    rpx = 632 / (pxmax - pxmin)

    # abrir display con el tamaño de la imagen, escalado
    pantalla = pygame.display.set_mode((1294, 632))
    # nombre de la pantalla
    pygame.display.set_caption("GPS! ETSISI G4")
    # Cargar imagen en el display
    pygame.display.update()
    pygame.time.Clock().tick(60)  # control del reloj de la imagen

    while True:

        for event in pygame.event.get():
            # si cierran la pantalla salimos del programa o presionamos cualquier tecla tambien
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                setcerrar(1)
                pygame.display.quit()
                sys.exit()
        pantalla.blit(imagen, (0, 0))
        data = getdata()
        # print(data)
        # el 0 es el norte
        # el 1 es con el E
        # dibujar punto en la imagen, dependiendo de la resolucion de la imagen, y la distancia de los extremos
        pygame.draw.circle(imagen, color, (rpx * (data[0] - pxmin), rpy * (pymax - data[1])), 5, 0)
        # actualizar display
        pygame.display.update()


# Configuramos y lanzamos los hilo encargado de leer datos del serial y de actualizar pantalla

dataCollector = threading.Thread(target=GetData, args=())
displayupdater = threading.Thread(target=update_line, args=())
dataCollector.start()
displayupdater.start()

dataCollector.join()
displayupdater.join()

# cerramos el programa completo en caso de que cerrar sea 1
while True:
    if getcerrar() == 1:
        sys.exit()
