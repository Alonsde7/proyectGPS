import math
import sys
import pygame as pygame
import serial
import threading
import utm
import requests
import io
from pygame.time import delay

# Huso para la conversión
HusoHorario = 30

gData = [0, 0, 0, 'N']
cerrado = 0


def IsINSIA(px, py):
    resultado = False
    if 446187 < px < 446373 and 4470749 < py < 4471018:
        resultado = True
    return resultado


def ObtenerImagen(pxcentro: float, pycentro: float):  # el pycntro se da en utm
    # |---------------------------------------------------------------------------------------|
    # |----------------------------  VARIABLES  ----------------------------------------------|
    global imagen, pxmin, pxmax, pymin, pymax, rp, esperallamada
    rp = abs(156543.04 * math.cos(utm.to_latlon(pxcentro, pycentro, 30, 'T')[1]) / math.pow(2, 19))

    pxmin = pxcentro - (1294 * rp / 2)  # Cambiar según la imagen
    pxmax = pxcentro + (1294 * rp / 2)  # Cambiar según la imagen
    pymin = pycentro - (632 * rp / 2)  # Cambiar según la imagen
    pymax = pycentro + (632 * rp / 2)  # Cambiar según la imagen

    # --------------------------Llamada al endpoint de la API-----------------------------------------------------
    pxcentrograde, pycentrograde = utm.to_latlon(pxcentro, pycentro, 30, 'T')
    url = 'https://dev.virtualearth.net/REST/v1/Imagery/Map/Aerial/' + str(pxcentrograde) + ',' + str(
        pycentrograde) + '?mapSize=1294,632&zoomlevel=19&key=AjWZ4tM-gHmcfGv99DGtfGRuY_iikb1yEwpc6TVvsVq83d6VySdVlEqF' \
                         '-GIoWYD5 '
    response = requests.get(url)
    imagefile = io.BytesIO(response.content)
    imagen = pygame.image.load(imagefile)
    # Actualizar variable de control
    esperallamada = 0


def ColorVelocidad(velocidad: float, limite: float):
    if velocidad > limite * 1.1:
        color = (255, 0, 0)
    elif velocidad < limite * 0.9:
        color = (0, 255, 0)
    else:
        color = (255, 255, 0)

    return color


def ObtenerLimite(x: float, y: float, sentido: chr):
    # ---------------------ELIGE LA VELOCIDAD LIMITE DEL INSIA SEGÚN UN ÁRBOL BINARIO HECHO CON C4.8-------------
    if x <= 446321.7377:
        if y <= 4470885.003:
            if y <= 4470838.737:
                limite = 15
            else:
                if sentido == 'O':
                    limite = 18
                else:
                    limite = 20
        else:
            if sentido == 'O':
                limite = 18
            else:
                limite = 20
    else:
        if y <= 4470969.447:
            if sentido == 'O' or x > 446339.3589:
                limite = 5
            else:
                limite = 20
        else:
            if y <= 4470974.363:
                if sentido == 'O':
                    if x <= 446349.552 or y <= 4470970.938:
                        limite = 5
                    else:
                        limite = 10
                else:
                    if x <= 446336.9667:
                        limite = 10
                    else:
                        limite = 5
            else:
                limite = 10

    return limite


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
        # ----- INICIALIZACIÓN   -------------   VARIABLES   ----- #
        x, y, hora_antigua = 0, 0, 0
        res = 0, 0, 0, 'N'
        while True:
            if ser.inWaiting():
                line = str(ser.readline())
                # Si la línea tiene 'GPGGA' la parseamos y extraemos el
                if line.split(',')[0] == "b'$GPGGA" and line.split(',')[6] != '0':
                    splitline = line.split(',')[2:6]

                    # ----- Conversion de grados a UTM ----- #
                    aux = utm.from_latlon(
                        cambiarsigno(fullgrade(float(splitline[0][0:2]), float(splitline[0][2::])), splitline[1]),
                        cambiarsigno(fullgrade(float(splitline[2][0:3]), float(splitline[2][3::])), splitline[3]),
                        HusoHorario, 'T')

                    # ----- Obtener la hora con decimales de la trama que manda el GPS ----- #
                    hh = line.split(',')[1][0:2]
                    mm = line.split(',')[1][2:4]
                    ss = line.split(',')[1][4::]
                    hora = int(hh) + int(mm) / 60 + float(ss) / 3600

                    # ----- Diferencia de posicioón respecto de la anterior ----- #
                    x = aux[0]  # valor nuevo
                    y = aux[1]  # valor nuevo

                    distancia = math.sqrt(math.pow(res[0] - x, 2) + math.pow(res[1] - y, 2)) / 1000
                    velocidad = distancia / abs(hora - hora_antigua)

                    # ----- pasar la velocidad a medidas estandarizadas (no como en EEUU :P)    ----- #
                    if res[0] < x:
                        sentido = 'O'
                    else:
                        sentido = 'E'
                    hora_antigua = hora
                    res = [x, y, velocidad, sentido]
                    setdata(res)

                # ----- hay que cerrar cada thread si queremos salir además de cerrar los puertos ----- #
                if getcerrar() == 1:
                    ser.close()
                    sys.exit()


# Función que actualizará los datos de la imágen en un hilo distinto

def update_line():
    # |---------------------------------------------------------------------------------------|
    # |----------------------------  VARIABLES  ----------------------------------------------|

    global imagen, pxmin, pxmax, pymin, pymax, rp, esperallamada

    esperallamada = 0

    # --------------------  INICIALIZACIÓN  ----------------------

    pygame.init()
    data = getdata()
    # PARA NO LLAMAR A LA API, HASTA QUE NOS DEN UNA POSICIÓN DISTINTA DE 0,0 (INICIALIZACIÓN) EN UTM, NO MOSTRAMOS NADA
    while data[0] == 0 and data[1] == 0:
        print("Buscando señal")
        data = getdata()
        delay(100)

    # --------UNA VEZ TENGAMOS UNA SEÑAL INICIAL, MOSTRAMOS POR PANTALLAS CON NUESTRA POSICIÓN COMO PUNTO CENTRAL-------

    ObtenerImagen(data[0], data[1])

    posicion_inicial_x = data[0]
    posicion_inicial_y = data[1]

    # abrir display con el tamaño de la imagen, escalado
    pantalla = pygame.display.set_mode((1294, 632))

    # nombre de la pantalla
    pygame.display.set_caption("GPS! ETSISI G4")

    # Cargar imagen en el display
    pygame.display.update()

    # inicialización de los textos
    font = pygame.font.Font('freesansbold.ttf', 32)

    txt = font.render('Velocidad límite: 25\t Velocidad: ', True, (0, 0, 0))
    txt2 = font.render('Velocidad : 25', True, (0, 0, 0))

    txtrect = txt.get_rect()
    txtrect2 = txt2.get_rect()

    txtrect.center = (260, 600)
    txtrect2.center = (1000, 600)

    pygame.time.Clock().tick(60)  # control del reloj de la imagen

    while True:
        for event in pygame.event.get():
            # si cierran la pantalla salimos del programa o presionamos cualquier tecla tambien
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                setcerrar(1)
                pygame.display.quit()
                sys.exit()

        pantalla.blit(imagen, (0, 0))

        # Obtener Datos
        data = getdata()

        # Condicional de carga de mapa en caso de que estemos en el límite de este. Para una mayor comprensión de la
        # posición de la posición que nos encontramos se mueve según unas coordenadas iniciales

        if pxmax - 40 < data[0] and esperallamada == 0:
            esperallamada = 1
            threading.Thread(target=ObtenerImagen(posicion_inicial_x + 80, posicion_inicial_y))
            posicion_inicial_x = posicion_inicial_x + 80
        elif pxmin + 40 > data[0] and esperallamada == 0:
            esperallamada = 1
            threading.Thread(target=ObtenerImagen(posicion_inicial_x - 80, posicion_inicial_y))
            posicion_inicial_x = posicion_inicial_x - 80

        if pymax - 40 < data[1] and esperallamada == 0:
            esperallamada = 1
            threading.Thread(target=ObtenerImagen(posicion_inicial_x, posicion_inicial_y + 80))
            posicion_inicial_y = posicion_inicial_y + 80
        elif pymin + 40 > data[1] and esperallamada == 0:
            esperallamada = 1
            threading.Thread(target=ObtenerImagen(posicion_inicial_x, posicion_inicial_y - 80))
            posicion_inicial_y = posicion_inicial_y - 80

        # Actualizar textos, en caso de estar en el INSIA se muestra la velocidad límite en caso contrario
        if IsINSIA(data[0], data[1]):
            color = ColorVelocidad(data[2], ObtenerLimite(data[0], data[1], data[3]))
            txt = font.render('Velocidad límite: ' + str(ObtenerLimite(data[0], data[1], data[3])) + ' Km/h', True,
                              color)
            pantalla.blit(txt, txtrect)
        else:
            color = (0, 0, 0)

        txt2 = font.render('Velocidad: ' + "{:.2f}".format(data[2]) + ' Km/h', True, color)

        pantalla.blit(txt2, txtrect2)

        # el 0 es la longitud
        # el 1 es la latitud
        # dibujar punto en la imagen, dependiendo de la resolución de la imagen y la distancia de los extremos
        pygame.draw.circle(imagen, color, ((data[0] - pxmin) / rp, (pymax - data[1]) / rp), 5, 0)
        # actualizar display
        pygame.display.update()


# Configuramos y lanzamos los hilos encargado de leer datos del serial y de actualizar pantalla

data_collector = threading.Thread(target=GetData, args=())
displayupdater = threading.Thread(target=update_line, args=())
data_collector.start()
displayupdater.start()

data_collector.join()
displayupdater.join()

# cerramos el programa completo en caso de que cerrar sea 1
while True:
    if getcerrar() == 1:
        sys.exit()
