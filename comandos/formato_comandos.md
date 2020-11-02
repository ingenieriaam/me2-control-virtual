## Mnemonicos
Muchos comandos tienen una forma larga y otra corta: use cualquiera (una combinación de los dos no está permitida). El Comando FREQuency por ejemplo:

    * forma corta: FREQ
    * forma larga :FREQUENCY 
 
SCPI no distingue entre mayúsculas y minúsculas, por lo que la fREquEncy es tan válida como FREQUENCY, pero FREQ  y FREQUENCY son las únicas formas válidas del comando FRECUENCIA.

Las letras mayúsculas indican la forma corta de la palabra clave. Las letras minúsculas indican la forma larga de la palabra clave.
___
## Puntuación
 * Una barra vertical "|" dicta la elección de un elemento de una lista. Por ejemplo: <A> | <B> indica que A o B pueden ser seleccionado, pero no ambos.
 * Los corchetes "[]" indican que los elementos son Opcionales.
 * Los corchetes angulares "<>" indican una variable de usuario.
 *  Un signo de interrogación "?" después de un comando del subsistema indica que el comando es una consulta. La información devuelta en <valor> varía su formato según el tipo de campo.
 ___

## Separador
* Los dos puntos ":" separan palabras claves en niveles, en general, se omite antes de la primer palabra.
* Un espacio separa una palabra clave y un parámetro, así como un parámetro y una unidad.