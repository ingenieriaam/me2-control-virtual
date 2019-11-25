# Control virtual de instrumental de medición en radio frecuencia - Proyecto anual de [Medidas Electrónicas 2](http://www.electron.frba.utn.edu.ar/materias.php?cod=95-0458#marca)
[![UTN](https://actividades.frba.utn.edu.ar/imagenes/logo-con-margenes.jpg)](https://www.frba.utn.edu.ar/)

_______________________________________

En este trabajo de creo una herramienta de control remoto de instrumentos de medición hasta ***1.5GHz***.
El desarrollo ha permitido tanto seteos como consultas a los equipos detallados a continuación
_______________________________________
## Equipos:
- [Analizador de espectro Rigol DSA815](https://www.rigolna.com/products/spectrum-analyzers/dsa800/)
- [Generador de señal en RF Rigol DSG815](https://www.rigolna.com/products/rf-signal-generators/dsg800/)
- [Medidor de potencia en RF Anritsu ML2487B](https://www.anritsu.com/en-us/test-measurement/products/ml2487b)

_______________________________________
## Servidor:
Se utilizo para estos fines el kit [BeagleBone Black](https://beagleboard.org/black) con servicio sobre linux.
[![bbb](https://beagleboard.org/static/ti/product_detail_black_sm.jpg)](https://beagleboard.org/black)

_______________________________________
## Software:

Se ha utilizado Python 3 para el desarrollo grafico, HTML para lograr captar datos y JavaScript para comunicarse tanto el servidor con los clientes y viceversa.

[![py](https://www.python.org/static/img/python-logo.png)](https://www.python.org/)
[![html](https://upload.wikimedia.org/wikipedia/commons/thumb/6/61/HTML5_logo_and_wordmark.svg/230px-HTML5_logo_and_wordmark.svg.png)](https://developer.mozilla.org/es/docs/Web/HTML)
[![js](https://www.espai.es/blog/wp-content/uploads/2015/11/acb_art01_00.png)](https://www.javascript.com/)


Haciendo uso de los siguientes paquetes, se desarrolla integramente el resultado final:

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


