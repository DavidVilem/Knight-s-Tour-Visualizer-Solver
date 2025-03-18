# Knight's Tour Visualizer & Solver

Este proyecto implementa el clásico problema del **recorrido del caballo** (Knight's Tour) en Python. Utiliza varias técnicas para encontrar soluciones válidas y las visualiza de forma interactiva mediante Pygame.

## Tabla de Contenidos
- [Introducción](#introducción)
- [Antecedentes y Marco Matemático](#antecedentes-y-marco-matemático)
- [Descripción del Problema](#descripción-del-problema)
- [Soluciones y Algoritmos Utilizados](#soluciones-y-algoritmos-utilizados)
  - [Heurística de Warnsdorff](#heurística-de-warnsdorff)
  - [Backtracking Iterativo](#backtracking-iterativo)
- [Descripción del Código](#descripción-del-código)
  - [Clase `KnightsTour`](#clase-knightstour)
  - [Clase `KnightsTourVisualizer`](#clase-knightstourvisualizer)
- [Instrucciones de Uso](#instrucciones-de-uso)
- [Intervención Reciente y Mejoras](#intervención-reciente-y-mejoras)
- [Referencias](#referencias)

---

## Introducción
El **recorrido del caballo** es un problema clásico tanto en matemáticas como en ciencias de la computación. El objetivo es mover un caballo de ajedrez a través de todas las casillas de un tablero, visitando cada una exactamente una vez. Este repositorio contiene una implementación que utiliza varias estrategias para encontrar una solución y una interfaz gráfica para visualizar el recorrido.

---

## Antecedentes y Marco Matemático
El problema se puede formular matemáticamente como la búsqueda de un **camino Hamiltoniano** en un grafo: cada casilla del tablero representa un vértice, y cada movimiento válido del caballo es una arista entre dos vértices.

El problema ha sido objeto de estudio desde el siglo XIX y se han propuesto diversas soluciones:
- **Métodos Matemáticos y Heurísticos:** Uno de los enfoques más famosos es la **heurística de Warnsdorff**, propuesta por H. C. Warnsdorff en 1823. Esta técnica elige siempre el siguiente movimiento basándose en el número de movimientos futuros disponibles, minimizando el riesgo de quedar atrapado.
- **Algoritmos de Backtracking:** Se han desarrollado algoritmos de retroceso (backtracking) para explorar todas las rutas posibles de manera sistemática, lo cual es especialmente útil para tableros pequeños.

---

## Descripción del Problema
Dado un tablero de dimensiones `N x N` (por ejemplo, un tablero de ajedrez de 8×8), el objetivo es:
1. Mover el caballo de forma que cada casilla se visite **exactamente una vez**.
2. Generar una secuencia de movimientos que cumpla con la condición anterior.
3. Visualizar el recorrido de manera interactiva.

---

## Soluciones y Algoritmos Utilizados

### Heurística de Warnsdorff
La heurística de Warnsdorff selecciona el siguiente movimiento basándose en el "grado" (número de futuros movimientos posibles) de la casilla destino.  
En este proyecto se implementan **tres variaciones** de la heurística:
- **Random:** Se utiliza el grado junto con un pequeño factor aleatorio para desempate.
- **Center:** Favorece movimientos que acerquen al caballo al centro del tablero, donde suele haber más opciones.
- **Corners:** Favorece movimientos que dirigen el caballo hacia las esquinas, modificando la exploración del espacio de búsqueda.

Estas variaciones se combinan en múltiples intentos para diversificar los recorridos y evitar soluciones duplicadas.

### Backtracking Iterativo
Si la heurística de Warnsdorff falla (lo cual puede ocurrir en algunos casos), el código recurre a un algoritmo de **backtracking iterativo**. Este método explora sistemáticamente cada posible movimiento y retrocede cuando se encuentra un callejón sin salida. Es especialmente útil en tableros pequeños donde el espacio de búsqueda es manejable.

---

## Descripción del Código

### Clase `KnightsTour`
Esta clase contiene toda la lógica para resolver el problema del recorrido del caballo. Entre sus características destacan:

- **Inicialización:**
  - Crea el tablero (`board`) con valores `-1` para indicar casillas no visitadas.
  - Define los 8 movimientos posibles del caballo a través de las listas `moves_x` y `moves_y`.
  
- **Métodos de Validación y Visualización:**
  - `is_valid_move(x, y)`: Verifica si una casilla es válida y no ha sido visitada.
  - `print_solution()` y `print_path()`: Imprimen la solución en forma de matriz y la secuencia de movimientos en notación ajedrecística.

- **Resolución con Heurística de Warnsdorff:**
  - `solve_with_warnsdorff(start_x, start_y, mode)`: Implementa la heurística utilizando una función genérica que, mediante una función de puntuación, evalúa el siguiente movimiento.
  - Se implementan funciones de puntuación para las tres variaciones (random, center y corners).

- **Múltiples Intentos y Registro de Estadísticas:**
  - `solve_with_multiple_warnsdorff_attempts(...)`: Realiza varios intentos con las variaciones de Warnsdorff, registrando estadísticas y logs para detectar soluciones duplicadas mediante un hash del recorrido.

- **Backtracking Iterativo:**
  - `solve(start_x, start_y)`: Método de backtracking iterativo que se utiliza como alternativa en caso de que la heurística no encuentre solución.

### Clase `KnightsTourVisualizer`
Esta clase se encarga de la visualización del recorrido utilizando **Pygame**. Entre sus funcionalidades se incluyen:

- **Visualización del Tablero y Recorrido:**
  - Dibuja el tablero con un patrón ajedrecístico y añade notación (letras y números) en los bordes.
  - Dibuja el camino recorrido, conectando las casillas mediante líneas y resaltando la posición final (usando una imagen o un marcador gráfico).

- **Interactividad:**
  - Permite el zoom (mediante la rueda del ratón) y el desplazamiento de la vista (haciendo click y arrastrando).
  - Soporta la animación del recorrido, mostrando paso a paso los movimientos del caballo.

---

## Instrucciones de Uso

### Requisitos
- Python 3.x
- Pygame

### Instalación
1. Clona el repositorio:
   ```bash
   git clone https://github.com/DavidVilem/Knight-s-Tour-Visualizer-Solver.git
   cd knights-tour
   ```
2. Instala las dependencias:
   ```bash
   pip install pygame
   ```
   
## Ejecución
El programa se puede ejecutar desde la línea de comandos. Ejemplo:

```bash
python knight_tour.py --size 8 --start-x 0 --start-y 0 --attempts 100 --verbose
```

Argumentos Disponibles
--size: Tamaño del tablero (por ejemplo, 8 para 8x8, 200 para tableros grandes).

--start-x y --start-y: Coordenadas iniciales (filas y columnas, comenzando en 0).

--attempts: Número de intentos con la heurística de Warnsdorff.

--no-animate: Desactiva la animación en la visualización.

--delay: Retardo entre pasos de la animación.

--verbose: Muestra información detallada en la salida.

--no-logs: No guarda los archivos de log de estadísticas y depuración.

### Argumentos Disponibles
- `--size`: Tamaño del tablero (por ejemplo, 8 para 8x8, 200 para tableros grandes).
- `--start-x` y `--start-y`: Coordenadas iniciales (filas y columnas, comenzando en 0).
- `--attempts`: Número de intentos con la heurística de Warnsdorff.
- `--no-animate`: Desactiva la animación en la visualización.
- `--delay`: Retardo entre pasos de la animación.
- `--verbose`: Muestra información detallada en la salida.
- `--no-logs`: No guarda los archivos de log de estadísticas y depuración.

---

## Intervención Reciente y Mejoras
El problema del recorrido del caballo ha sido abordado durante siglos y ha evolucionado significativamente:

### Historia y Evolución:
Desde soluciones puramente matemáticas hasta heurísticas como la de Warnsdorff, el problema ha sido objeto de estudio en matemáticas recreativas y teoría de grafos. Con la llegada de la informática se han implementado algoritmos de backtracking y técnicas de optimización.

### Mejoras en este Proyecto:
- **Refactorización de Heurísticas:** Se unifica la lógica de las tres variaciones (random, center y corners) mediante una función genérica que utiliza diferentes funciones de puntuación. Esto reduce la redundancia y facilita la extensión o modificación de las estrategias.
- **Múltiples Intentos con Registro:** Se realizan numerosos intentos (por ejemplo, 100) usando las distintas variaciones para aumentar la probabilidad de obtener una solución única. Se utiliza un hash del recorrido para detectar y evitar soluciones duplicadas.
- **Solución Alternativa:** En caso de que las heurísticas fallen (especialmente en tableros pequeños), se recurre a un algoritmo de backtracking iterativo para asegurar una solución.

Estas intervenciones y mejoras reflejan el avance en la resolución del problema, combinando técnicas heurísticas con métodos exhaustivos, y aprovechando herramientas de visualización modernas para facilitar la comprensión del recorrido.

---

## Referencias
- [Knight's Tour - Wikipedia](https://en.wikipedia.org/wiki/Knight%27s_tour)
- Warnsdorff, H. C. (1823). An attempt to a solution of the knight's tour problem.
- Artículos y recursos sobre caminos Hamiltonianos y algoritmos de backtracking.

---
