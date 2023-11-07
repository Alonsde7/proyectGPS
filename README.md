# proyectGPS

Desarrollar una aplicación en Python que sea capaz de leer los datos suministrados por 
un receptor GPS a través de un puerto serie. De entre estos datos, se adquirirá la trama 
GGA, que indica la posición calculada por el receptor en coordenadas geográficas 
(latitud, longitud). La aplicación también transformará estos datos en coordenadas 
UTM, que indica la proyección plana de dicha posición en coordenadas cartesianas (X, 
Y). Para esta práctica se utilizarán los receptores GPS Garmin eTrex H suministrados 
por el Departamento de Sistemas Informáticos, que generan tramas de posicionamiento 
GGA siguiendo el estándar NMEA con una frecuencia de 0.5 Hz.

Extender la aplicación desarrollada en la práctica 1 para que sea capaz de representar en 
pantalla la posición suministrada por el receptor GPS. Se capturará una imagen del 
Google Earth, se georeferenciará en la pantalla del 
ordenador y se mostrará junto a la posición del receptor GPS en tiempo real. Esta 
imagen debe ser coherente con la posición suministrada por el receptor GPS. La 
aplicación debe realizar las funciones de visualización similares a las de un navegador 
comercial. Las pruebas finales de esta práctica se realizarán con un vehículo 
instrumentado con GPS en la pista de ensayo del INSIA, utilizando en este caso un 
receptor GPS Trimble R4, que genera tramas de posicionamiento GGA siguiendo el 
estándar NMEA a una frecuencia de 10 Hz.

Extender la aplicación desarrollada en la práctica 2 para integrar un mapa electrónico de 
la pista de ensayo. El formato de este mapa es 
UTM_Norte, UTM_Este, Velocidad_Máxima. La aplicación debe comparar la posición 
GPS del coche en la carretera con el mapa electrónico y avisar al conductor en caso de 
velocidad excesiva. El sistema desarrollado debe comprobar en todo momento el 
sentido de la marcha y compararlo con el mapa a fin de que sea capaz de funcionar 
cuando se circula en sentido horario como antihorario. Las pruebas finales de esta 
práctica se realizarán con un vehículo instrumentado con GPS en la pista de ensayo.

En esta práctica se desarrollarán los conocimientos adquiridos en el tema de gestión de 
servicios georeferenciados. En este caso se hará uso de la API de Google Maps, Bing 
Virtualmaps o de OpenStreetMaps para representar el área por el que va circulando el 
coche, sustituyendo la imagen capturada estática por una imagen dinámica que se 
obtendrá de la cartografía de este proveedor en tiempo real a partir de la posición GPS, 
de tal manera que ya no estemos restringidos al Campus Sur de la UPM sino que 
nuestra aplicación sea funcional en cualquier otra localización.
Aparte de este cambio, la funcionalidad del sistema de navegación desarrollado debe 
mantenerse tal y como se ha especificado en la práctica 3 aunque, lógicamente, el 
sistema de aviso al conductor sólo funcionará en la pista de INSIA. En esta pista se 
realizarán las pruebas finales de la práctica. Además, se dispondrá de conexión a 
Internet vía WiFi en toda la pista a fin de mantener la conectividad con Google Maps en 
todo momento.
