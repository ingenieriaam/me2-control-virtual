# Control virtual de instrumental de medición en radio frecuencia - Proyecto anual de [Medidas Electrónicas 2](http://www.electron.frba.utn.edu.ar/materias.php?cod=95-0458#marca)
[![UTN](https://actividades.frba.utn.edu.ar/imagenes/logo-con-margenes.jpg)](https://www.frba.utn.edu.ar/)

## Autores:
- Nicolas Mariano Koremblum 
- Pablo Rodrigo D'Angelo 
- Agustin Matias Ortiz 
_______________________________________

En este trabajo de creo una herramienta de control remoto de instrumentos de medición hasta ***1.5GHz***.
El desarrollo ha permitido tanto seteos como consultas a los equipos detallados a continuación

### Conozca la idea y realización en:
[https://ingenieriaam.github.io/me2-control-virtual/](https://ingenieriaam.github.io/me2-control-virtual/)
_______________________________________
## Equipos:
- [Analizador de espectro Rigol DSA815](https://www.rigolna.com/products/spectrum-analyzers/dsa800/)
- [Generador de señal en RF Rigol DSG815](https://www.rigolna.com/products/rf-signal-generators/dsg800/)
- [Medidor de potencia en RF Anritsu ML2487B](https://www.anritsu.com/en-us/test-measurement/products/ml2487b)

_______________________________________
## Servidor:
Se utilizo para estos fines el kit [BeagleBone Black](https://beagleboard.org/black) con servicio sobre linux.
[![bbb](https://beagleboard.org/static/ti/product_detail_black_sm.jpg)](https://beagleboard.org/black).

El servidor es apto para correr en cualquier plataforma que soporte python.

_______________________________________
## Entorno grafico
- Vista sin permisos de control (requiere pass) ![inicial_sin](./info/alumno_sin_permisos.png)
- Vista con permisos de control ![inicial_con](./info/con_permisos_init.png)
- Controles del analizador de espectro ![AE](./info/analizer_set.png)
- Controles del generador ![GEN](./info/generator_set.png)
- Controles del medidor de potencia ![PM](./info/PM_set.png)

_______________________________________
## Software:

Se ha utilizado Python 3 para el desarrollo grafico, HTML para lograr captar datos y JavaScript para comunicarse tanto el servidor con los clientes y viceversa.

[![py](https://www.python.org/static/img/python-logo.png)](https://www.python.org/)
[![html](https://upload.wikimedia.org/wikipedia/commons/thumb/6/61/HTML5_logo_and_wordmark.svg/230px-HTML5_logo_and_wordmark.svg.png)](https://developer.mozilla.org/es/docs/Web/HTML)
[![js](https://www.espai.es/blog/wp-content/uploads/2015/11/acb_art01_00.png)](https://www.javascript.com/)


Haciendo uso de los siguientes paquetes, se desarrolla integramente el resultado final (ver: website/install.txt):

- Numpy
- Scipy
- Bokeh
- Ajax
- PyVisa
- Request
- Json
- Time
- Signal
- Threading
- Flask

______________________________
### En los codigos se encuentra la documentación requerida para la comprensión del paradigma empleado. Cualquier duda que pueda surgir se atenderá mediante ***Issues*** de este repositorio.


