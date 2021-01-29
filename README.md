<br />
<p align="center">
  <img width="200" height="200" src="img/icon_flat.png">
</p>
<br />
<br />
<br />

![](https://img.shields.io/badge/Blender%20version-2.8x-orange?style=for-the-badge&logo=blender&logoColor=white)
![](https://img.shields.io/github/v/tag/JavierRojo/Imperium_exporter?color=green&label=Add-on%20version&logo=python&logoColor=white&style=for-the-badge)

<br />

# Imperium exporter
Una herramienta para traducir modelos 3D desde [Blender](https://www.blender.org/) a texturas de Imperium de manera automática. La herramienta consta de dos partes:

1. un add-on de Blender, que renderiza la escena varias veces y genera los sprites individuales y las distintas máscaras (nivel, color del jugador, etc.). 

2. La segunda parte de la herramienta utiliza [Octave](https://www.gnu.org/software/octave/) para combinar todas las texturas de manera rápida y eficiente, sacando como output un .BMP que se puede incorporar al sistema de texturas de Imperium.


## Road to 2.0
* [x] Arreglar apaños del color de nivel y jugador.
* [x] Limpiar el código de Python.
* [x] Documentar el add-on.
* [x] Separar el código de Octave en funciones.
* [x] Documentar el código de Octave.
* [x] Documentar el repositorio y traducir al castellano.
* [ ] Vídeo demostración.
* [ ] Vídeo promoción.

## Incluye
* [x] Implementar colores normales.
* [ ] Implementar texturas de sombra.
* [x] Implementar color del nivel.
* [x] Implementar color del jugador.
* [ ] Implementar texturas de edificio.
* [ ] Implementar texturas para la GUI.

## Limitaciones
* Ahora mismo las texturas deben ser cuadradas. Es probable que esto cambie en uno de los primeros parches para la versión 2.1, pero la 2.0 saldrá así.
* El código está dividid o en Python(Blender)+Octave. Es probable que en algún momento se unifique en Python, pero puede repercutir en la eficiencia.
* El extraño comportamiento de los colores de nivel y cómo se comportan todavía está en estudio. Es susceptible de sufrir cambios.

## Instalación
Para instalar el add-on de Imperium Exporter descarga o clona este repositorio y entonces ve a Blender. En  _edit > preferences > add-ons_ selecciona 'instalar desde archivo' y navega hasta la carpeta que acabas de descargar. Una vez allí selecciona el archivo `imperium_renderer.py`.

## Manual de uso (en desarrollo)
### Blender
Una vez instalado el add-on, podrás buscar todos los menús en el apartado de propiedades>render. Lo primero que tendrás que hacer es la parte más artística: modela tu unidad y anímala (por ejemplo en un ciclo de andar). Aplica texturas, etc. Una vez hayas acabado tendrás que ir a la sección de materiales y nombrar con prefijos específicos aquellos que quieras que se marquen como color de nivel o color del jugador. El prefijo para nivel es "ImpMat_level" y para el jugador, "ImpMat_player". Una vez hecho esto ya puedes centrarte en el menú y configurar el archivo para la exportación:

1. Indica el inicio de la animación, el final y el número de fotogramas que la compondrán. El add-on dividirá el intervalo en ese número de fotogramas.
2. Escoge un ancho de fotograma. En esta versión el sprite es forzosamente cuadrado todavía.
3. Escoge al objetivo (recomendable:empty). Al renderizar las texturas Blender girará este objeto en torno al eje z para conseguir las distintas perspectivas. Genera un objeto empty y haz que la armadura sea hija de dicho objeto.
4. Genera o selecciona una cámara para la operación.  Puedes escoger la cámara activa de la escena o escoger otra ya presente. Si no puedes generar una nueva con características por defecto que luego puedes modificar.
5. Escoge el directorio de salida. Blender generará subdirectorios para guardar el resultado.
6. Selecciona qué acciones quieres llevar a cabo. Indica qué quieres exportar. Como recomendación, desactiva siempre la opción de texturas de sombra porque no se pueden importar en el juego todavía.
7. Dale al botón de renderizar  :)

### Octave
Ahora el archivo `confiuration.cfg` debe rellenarse con algunos parámetros básicos:

* n\_frames: el número de fotogramas para la animación.
* resolution\_sprite: resolución de cada sprite, en píxeles (recordemos que de momento son cuadrados todos)
* input\_folder: carpeta donde se almacenan los resultados de Blender. El camino puede indicarse de manera relativa (p. ej.: '../blender\_output\_folder/').
* output\_folder: la carpeta donde se guardará la textura final.
* n\_level\_colors: número de colores que se usarán para definir los tonos de nivel. A más colores usados para el nivel, menos quedarán para invertirlos en colores normales.

Una vez hecho esto, abrimos octave y simplemente ejecutamos el script `imperium_assembler.m`. Aunque se puede usar como comando en la terminal, para recién llegados recomiendo descargar el entorno gráfico (Octave-GUI). Selecciona el directoiro de trabajo en el menú desplegable y dale al botón del play o escribe _imperium\_assembler_ en la consola interna. En la carpeta de output se generará un nuevo archivo .BMP con las texturas juntas y los colores ordenados. Esta textura la puedes convertir ya directamente a .MMP para insertarla en el juego.

## Más información
* Actualizaré la [wiki](https://github.com/JavierRojo/Imperium_exporter/wiki) de este repositorio cuando la herramienta esté acabada.
* El resultado parcial de esta herramienta puede verse [aquí](https://youtu.be/MGJLMHRm75E).
* Más información en el [Blog de desarrollo](https://www.youtube.com/playlist?list=PL_zV6BZZ-V3c3P5ECvt4QKXoIlzdFlKu2).
