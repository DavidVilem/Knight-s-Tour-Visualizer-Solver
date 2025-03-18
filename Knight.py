import pygame
import sys
import time
import os
import random
import json
from datetime import datetime

class KnightsTour:
    def __init__(self, size):
        """
        Inicializa el problema del recorrido del caballo en un tablero de tamaño size x size.
        
        Args:
            size (int): Tamaño del tablero (5 para un tablero 5x5, etc.)
        """
        self.size = size
        self.board = [[-1 for _ in range(size)] for _ in range(size)]
        self.moves_x = [2, 1, -1, -2, -2, -1, 1, 2]  # Posibles movimientos en x
        self.moves_y = [1, 2, 2, 1, -1, -2, -2, -1]  # Posibles movimientos en y
        self.path = []  # Para almacenar el camino recorrido
        
        # Registros para análisis
        self.variation_stats = []
        self.debug_log = []
    
    def is_valid_move(self, x, y):
        """Verifica si una posición es válida y no ha sido visitada."""
        return (0 <= x < self.size and 
                0 <= y < self.size and 
                self.board[x][y] == -1)
    
    def print_solution(self):
        """Imprime la solución en formato de matriz."""
        print("\nRecorrido del Caballo:")
        for i in range(self.size):
            for j in range(self.size):
                print(f"{self.board[i][j]:2d}", end=" ")
            print()
    
    def print_path(self):
        """Imprime el camino recorrido en notación de ajedrez en una sola línea."""
        print("\nSecuencia de movimientos:", end=" ")
        path_notations = []
        for x, y in self.path:
            # Convertir a notación de ajedrez (columnas: a-h, filas: 1-8)
            chess_notation = f"{chr(97 + y)}{self.size - x}"
            path_notations.append(chess_notation)
        print(" → ".join(path_notations))
        
    def log_move(self, message):
        """Añade un mensaje al registro de depuración."""
        self.debug_log.append(message)
        
    def _count_valid_moves(self, x, y):
        """Cuenta el número de movimientos válidos desde una posición dada."""
        count = 0
        for i in range(8):
            next_x = x + self.moves_x[i]
            next_y = y + self.moves_y[i]
            if self.is_valid_move(next_x, next_y):
                count += 1
        return count
    
    # ---------------------------------------------------------
    # Método genérico para obtener el siguiente movimiento con Warnsdorff
    # ---------------------------------------------------------
    def _get_next_move_warnsdorff_generic_detailed(self, x, y, move_preferences, scoring_func):
        """
        Evalúa los movimientos posibles usando una función de puntuación y retorna
        el mejor movimiento con detalles.
        
        Args:
            x, y (int): Coordenadas actuales.
            move_preferences (list): Orden en que se consideran los 8 movimientos.
            scoring_func (func): Función de puntuación para evaluar cada movimiento.
        
        Returns:
            tuple: (next_x, next_y, detalles) o None si no hay movimientos válidos.
        """
        moves = []
        considered_moves = []
        for pref_idx in move_preferences:
            next_x = x + self.moves_x[pref_idx]
            next_y = y + self.moves_y[pref_idx]
            
            # Registrar movimiento considerado
            if 0 <= next_x < self.size and 0 <= next_y < self.size:
                if self.board[next_x][next_y] == -1:
                    move_status = "válido"
                else:
                    move_status = "ya visitado"
            else:
                move_status = "fuera del tablero"
            considered_moves.append({
                "dirección": f"({self.moves_x[pref_idx]}, {self.moves_y[pref_idx]})",
                "destino": f"({next_x}, {next_y})",
                "estado": move_status
            })
            
            if self.is_valid_move(next_x, next_y):
                degree = self._count_valid_moves(next_x, next_y)
                random_factor = random.random() * 0.1  # Desempate aleatorio
                score = scoring_func(next_x, next_y, degree, random_factor, pref_idx)
                details = {
                    "grado": degree,
                    "random_factor": random_factor,
                    "preferencia": pref_idx,
                    "score": score
                }
                moves.append((score, next_x, next_y, details))
        
        if not moves:
            return None
        
        # Ordenar según la puntuación (score es una tupla)
        moves.sort(key=lambda m: m[0])
        best_move = moves[0]
        best_details = best_move[3]
        best_details["movimientos_considerados"] = considered_moves
        best_details["total_opciones"] = len(moves)
        return best_move[1], best_move[2], best_details
    
    # ---------------------------------------------------------
    # Funciones de puntuación para distintos modos
    # ---------------------------------------------------------
    def _score_random(self, next_x, next_y, degree, random_factor, pref_idx):
        """Puntuación para el modo aleatorio."""
        return (degree + random_factor,)
    
    def _score_center(self, next_x, next_y, degree, random_factor, pref_idx):
        """Puntuación que favorece movimientos hacia el centro."""
        center_x = self.size // 2
        center_y = self.size // 2
        dist_to_center = abs(next_x - center_x) + abs(next_y - center_y)
        return (degree, dist_to_center + random_factor)
    
    def _score_corners(self, next_x, next_y, degree, random_factor, pref_idx):
        """Puntuación que favorece movimientos hacia las esquinas."""
        corners = [(0, 0), (0, self.size-1), (self.size-1, 0), (self.size-1, self.size-1)]
        min_corner_dist = min(abs(next_x - cx) + abs(next_y - cy) for cx, cy in corners)
        return (degree, -min_corner_dist + random_factor)
    
    # ---------------------------------------------------------
    # Algoritmo de Warnsdorff utilizando la función genérica
    # ---------------------------------------------------------
    def solve_with_warnsdorff(self, start_x=0, start_y=0, mode='random'):
        """
        Resuelve el recorrido del caballo usando la heurística de Warnsdorff.
        
        Args:
            start_x (int): Fila inicial.
            start_y (int): Columna inicial.
            mode (str): Modo de puntuación ('random', 'center' o 'corners').
        
        Returns:
            bool: True si se encontró una solución, False en caso contrario.
        """
        if mode == 'center':
            scoring_func = self._score_center
        elif mode == 'corners':
            scoring_func = self._score_corners
        else:
            scoring_func = self._score_random
        
        move_preferences = list(range(8))
        random.shuffle(move_preferences)
        
        self.board[start_x][start_y] = 0
        self.path = [(start_x, start_y)]
        curr_x, curr_y = start_x, start_y
        
        for move_count in range(1, self.size * self.size):
            next_move = self._get_next_move_warnsdorff_generic_detailed(curr_x, curr_y, move_preferences, scoring_func)
            if next_move is None:
                return False
            next_x, next_y, move_info = next_move
            self.board[next_x][next_y] = move_count
            self.path.append((next_x, next_y))
            curr_x, curr_y = next_x, next_y
        
        return True
    
    # ---------------------------------------------------------
    # Múltiples intentos con Warnsdorff utilizando variaciones
    # ---------------------------------------------------------
    def solve_with_multiple_warnsdorff_attempts(self, start_x=0, start_y=0, max_attempts=10, verbose=False, save_logs=True):
        """
        Intenta resolver el recorrido del caballo con múltiples variaciones de la heurística de Warnsdorff.
        
        Args:
            start_x (int): Fila inicial.
            start_y (int): Columna inicial.
            max_attempts (int): Número máximo de intentos.
            verbose (bool): Si es True, muestra información detallada.
            save_logs (bool): Si es True, guarda los logs en archivos.
            
        Returns:
            bool: True si se encontró una solución, False en caso contrario.
        """
        self.variation_stats = []
        self.debug_log = []
        
        print(f"Intentando resolver con {max_attempts} variaciones de Warnsdorff...")
        attempted_paths = set()
        succeeded_attempt = None
        
        for attempt in range(max_attempts):
            # Seleccionar la variación: 0 -> random, 1 -> center, 2 -> corners
            variation = attempt % 3
            random_seed = attempt + self.size * 1000
            random.seed(random_seed)
            
            # Reiniciar tablero y camino
            self.board = [[-1 for _ in range(self.size)] for _ in range(self.size)]
            self.path = []
            
            move_preferences = list(range(8))
            random.shuffle(move_preferences)
            
            variation_info = {
                "attempt": attempt + 1,
                "variation_type": variation,
                "random_seed": random_seed,
                "move_preferences": move_preferences.copy(),
                "start_position": (start_x, start_y),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            }
            
            attempt_msg = f"=== INTENTO #{attempt+1} ===\n"
            attempt_msg += f"Tipo de variación: {variation}\n"
            attempt_msg += f"Semilla aleatoria: {random_seed}\n"
            attempt_msg += f"Preferencias de movimiento: {move_preferences}\n"
            attempt_msg += f"Posición inicial: ({start_x}, {start_y})\n"
            if verbose:
                print(attempt_msg)
            self.log_move(attempt_msg)
            
            move_tracking = []
            success = self._solve_with_warnsdorff_variation(start_x, start_y, variation, move_preferences, verbose, move_tracking)
            
            variation_info["successful"] = success
            variation_info["path_length"] = len(self.path)
            variation_info["move_tracking"] = move_tracking
            self.variation_stats.append(variation_info)
            
            if success:
                path_hash = self._get_path_hash()
                if path_hash not in attempted_paths:
                    success_msg = f"¡Éxito en el intento #{attempt+1} con variación {variation}!"
                    print(success_msg)
                    self.log_move(success_msg)
                    succeeded_attempt = (attempt, variation)
                    if save_logs:
                        self._save_variation_stats(f"knight_tour_{self.size}x{self.size}_logs.json")
                        self._save_debug_log(f"knight_tour_{self.size}x{self.size}_debug.txt")
                    return True
                else:
                    duplicate_msg = f"Intento #{attempt+1} encontró una solución duplicada, continuando..."
                    print(duplicate_msg)
                    self.log_move(duplicate_msg)
            else:
                fail_msg = f"Intento #{attempt+1} con variación {variation} fallido, probando otra variación..."
                print(fail_msg)
                self.log_move(fail_msg)
            
            if len(self.path) > 0:
                path_hash = self._get_path_hash()
                attempted_paths.add(path_hash)
        
        all_fail_msg = f"Todos los {max_attempts} intentos fallaron o produjeron soluciones duplicadas."
        print(all_fail_msg)
        self.log_move(all_fail_msg)
        if save_logs:
            self._save_variation_stats(f"knight_tour_{self.size}x{self.size}_logs.json")
            self._save_debug_log(f"knight_tour_{self.size}x{self.size}_debug.txt")
        return False
    
    def _solve_with_warnsdorff_variation(self, start_x, start_y, variation, move_preferences, verbose=False, move_tracking=None):
        """
        Resuelve el recorrido usando una variación de la heurística de Warnsdorff.
        
        Args:
            start_x, start_y: Posición inicial.
            variation (int): Selecciona la función de puntuación (0: random, 1: center, 2: corners).
            move_preferences (list): Orden de preferencia para los movimientos.
            verbose (bool): Si True, muestra detalles.
            move_tracking (list): Lista para registrar información de cada movimiento.
            
        Returns:
            bool: True si se encontró solución.
        """
        if variation == 1:
            scoring_func = self._score_center
        elif variation == 2:
            scoring_func = self._score_corners
        else:
            scoring_func = self._score_random
        
        self.board[start_x][start_y] = 0
        self.path = [(start_x, start_y)]
        curr_x, curr_y = start_x, start_y
        
        start_msg = f"Iniciando recorrido desde ({start_x}, {start_y})"
        if verbose:
            print(start_msg)
        self.log_move(start_msg)
        
        for move_count in range(1, self.size * self.size):
            next_move_details = self._get_next_move_warnsdorff_generic_detailed(curr_x, curr_y, move_preferences, scoring_func)
            if next_move_details is None:
                fail_msg = f"No hay movimientos válidos en el paso {move_count}. Posición: ({curr_x}, {curr_y})"
                if verbose:
                    print(fail_msg)
                self.log_move(fail_msg)
                return False
            next_x, next_y, move_info = next_move_details
            if move_tracking is not None:
                move_tracking.append({
                    "move_number": move_count,
                    "from": (curr_x, curr_y),
                    "to": (next_x, next_y),
                    "details": move_info
                })
            if verbose:
                move_msg = f"Paso {move_count}: ({curr_x}, {curr_y}) -> ({next_x}, {next_y}) | Detalles: {move_info}"
                print(move_msg)
                self.log_move(move_msg)
            self.board[next_x][next_y] = move_count
            self.path.append((next_x, next_y))
            curr_x, curr_y = next_x, next_y
            if move_count % 500 == 0:
                progress_msg = f"Progreso: {move_count}/{self.size * self.size} movimientos completados"
                if verbose:
                    print(progress_msg)
                self.log_move(progress_msg)
        success_msg = f"¡Recorrido completo! Total de pasos: {len(self.path)}"
        if verbose:
            print(success_msg)
        self.log_move(success_msg)
        return True
    
    def _get_path_hash(self):
        """
        Genera un hash único para el camino actual, para detectar recorridos duplicados.
        """
        sample_size = min(100, len(self.path) // 2)
        path_sample = str(self.path[:sample_size]) + str(self.path[-sample_size:])
        return hash(path_sample)
    
    def _save_variation_stats(self, filename):
        """Guarda las estadísticas de variación en un archivo JSON."""
        try:
            with open(filename, 'w') as f:
                json.dump(self.variation_stats, f, indent=2)
            print(f"Estadísticas de variación guardadas en {filename}")
        except Exception as e:
            print(f"Error al guardar estadísticas: {e}")
    
    def _save_debug_log(self, filename):
        """Guarda el registro de depuración en un archivo de texto."""
        try:
            with open(filename, 'w') as f:
                for line in self.debug_log:
                    f.write(line + '\n')
            print(f"Registro de depuración guardado en {filename}")
        except Exception as e:
            print(f"Error al guardar registro: {e}")
    
    def analyze_variation_performance(self):
        """Analiza el rendimiento de las diferentes variaciones."""
        if not self.variation_stats:
            print("No hay estadísticas de variación disponibles.")
            return
        
        variation_groups = {}
        for stat in self.variation_stats:
            var_type = stat["variation_type"]
            if var_type not in variation_groups:
                variation_groups[var_type] = []
            variation_groups[var_type].append(stat)
        
        print("\n=== ANÁLISIS DE RENDIMIENTO POR VARIACIÓN ===")
        for var_type, stats in variation_groups.items():
            successful = [s for s in stats if s["successful"]]
            success_rate = len(successful) / len(stats) * 100 if stats else 0
            avg_path_length = sum(s["path_length"] for s in stats) / len(stats) if stats else 0
            
            print(f"Variación {var_type}:")
            print(f"  - Intentos: {len(stats)}")
            print(f"  - Éxitos: {len(successful)} ({success_rate:.1f}%)")
            print(f"  - Longitud media del camino: {avg_path_length:.1f}")
    
    # ---------------------------------------------------------
    # Algoritmo de backtracking iterativo
    # ---------------------------------------------------------
    def solve(self, start_x=0, start_y=0):
        """
        Resuelve el recorrido del caballo con backtracking iterativo.
        """
        self.board[start_x][start_y] = 0
        self.path = [(start_x, start_y)]
        stack = [(1, start_x, start_y, 0)]
        
        while stack:
            move_count, curr_x, curr_y, i = stack[-1]
            if move_count == self.size * self.size:
                return True
            found_valid_move = False
            while i < 8 and not found_valid_move:
                next_x = curr_x + self.moves_x[i]
                next_y = curr_y + self.moves_y[i]
                if self.is_valid_move(next_x, next_y):
                    stack[-1] = (move_count, curr_x, curr_y, i + 1)
                    self.board[next_x][next_y] = move_count
                    self.path.append((next_x, next_y))
                    stack.append((move_count + 1, next_x, next_y, 0))
                    found_valid_move = True
                else:
                    i += 1
            if not found_valid_move:
                stack.pop()
                if stack:
                    x, y = self.path.pop()
                    self.board[x][y] = -1
        self.board = [[-1 for _ in range(self.size)] for _ in range(self.size)]
        self.path = []
        return False

class KnightsTourVisualizer:
    def __init__(self, tour):
        """
        Inicializa el visualizador del recorrido del caballo.
        
        Args:
            tour (KnightsTour): Objeto KnightsTour con la solución
        """
        self.tour = tour
        self.window_width = 900
        self.window_height = 600
        self.base_cell_size = min(self.window_width * 0.6, self.window_height) // max(tour.size, 8)
        self.cell_size = self.base_cell_size
        self.offset_x = 0
        self.offset_y = 0
        self.zoom_level = 1.0
        self.dragging = False
        self.drag_start = (0, 0)
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.LIGHT_SQUARE = (240, 217, 181)
        self.DARK_SQUARE = (181, 136, 99)
        self.PATH_COLOR = (50, 150, 50)
        self.TEXT_COLOR = (0, 0, 0)
        self.HIGHLIGHT = (255, 0, 0)
        self.BG_COLOR = (50, 50, 50)
        self.SIDEBAR_BG = (30, 30, 30)
        pygame.init()
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption(f"Recorrido del Caballo - Tablero {tour.size}x{tour.size}")
        font_size = max(10, min(20, int(self.cell_size / 4)))
        self.font = pygame.font.SysFont('Arial', font_size)
        self.info_font = pygame.font.SysFont('Arial', 16)
        self.title_font = pygame.font.SysFont('Arial', 20, bold=True)
        self.center_view()
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            knight_path = os.path.join(current_dir, 'knight.png')
            print(f"Intentando cargar imagen desde: {knight_path}")
            self.knight_img = pygame.image.load(knight_path)
            print("¡Imagen cargada correctamente!")
            self.update_knight_image()
        except Exception as e:
            print(f"Error al cargar knight.png: {e}")
            self.knight_img = None
    
    def update_knight_image(self):
        """Actualiza el tamaño de la imagen del caballo según el zoom actual."""
        if hasattr(self, 'knight_img') and self.knight_img:
            knight_size = int(self.cell_size * self.zoom_level - 30)
            if knight_size > 10:  
                self.knight_img_scaled = pygame.transform.scale(self.knight_img, (knight_size, knight_size))
            else:
                self.knight_img_scaled = None
                
    def center_view(self):
        """Posiciona el tablero en la parte derecha de la ventana."""
        board_width = self.tour.size * self.cell_size * self.zoom_level
        board_height = self.tour.size * self.cell_size * self.zoom_level
        self.offset_x = (self.window_width * 0.65) - (board_width / 2)
        self.offset_y = (self.window_height - board_height) / 2
    
    def draw_board(self):
        """Dibuja el tablero de ajedrez con zoom y desplazamiento."""
        self.screen.fill(self.BG_COLOR)
        sidebar_width = int(self.window_width * 0.3)
        pygame.draw.rect(self.screen, self.SIDEBAR_BG, (0, 0, sidebar_width, self.window_height))
        title = self.title_font.render("RECORRIDO DEL CABALLO", True, self.WHITE)
        self.screen.blit(title, (10, 20))
        subtitle = self.info_font.render(f"Tablero: {self.tour.size}x{self.tour.size}", True, self.WHITE)
        self.screen.blit(subtitle, (10, 50))
        info_text = [
            f"Total de movimientos: {len(self.tour.path)}",
            f"Zoom: x{self.zoom_level:.1f}",
            "",
            "Controles:",
            "• Rueda del ratón: Zoom in/out",
            "• Click y arrastrar: Mover vista",
            "• R: Reiniciar vista",
            "• ESC: Salir"
        ]
        for i, text in enumerate(info_text):
            info_surface = self.info_font.render(text, True, self.WHITE)
            self.screen.blit(info_surface, (10, 80 + i * 25))
        pygame.draw.line(self.screen, (100, 100, 100), (sidebar_width, 0), (sidebar_width, self.window_height), 2)
        board_area = pygame.Surface((self.window_width - sidebar_width, self.window_height))
        board_area.fill(self.BG_COLOR)
        cell_size_zoomed = self.cell_size * self.zoom_level
        for row in range(self.tour.size):
            for col in range(self.tour.size):
                x = col * cell_size_zoomed + self.offset_x - sidebar_width
                y = row * cell_size_zoomed + self.offset_y
                if (x + cell_size_zoomed < 0 or x > self.window_width - sidebar_width or 
                    y + cell_size_zoomed < 0 or y > self.window_height):
                    continue
                color = self.LIGHT_SQUARE if (row + col) % 2 == 0 else self.DARK_SQUARE
                pygame.draw.rect(board_area, color, (x, y, cell_size_zoomed, cell_size_zoomed))
                if self.zoom_level > 0.5:
                    font_size = max(10, min(20, int(self.cell_size * self.zoom_level / 4)))
                    temp_font = pygame.font.SysFont('Arial', font_size)
                    if col == 0:
                        text = temp_font.render(str(self.tour.size - row), True, self.BLACK)
                        board_area.blit(text, (x + 5, y + 5))
                    if row == self.tour.size - 1:
                        text = temp_font.render(chr(97 + col), True, self.BLACK)
                        board_area.blit(text, (x + cell_size_zoomed - 20, y + cell_size_zoomed - 20))
        self.screen.blit(board_area, (sidebar_width, 0))
    
    def draw_path(self, show_numbers=True, animate=False, delay=0.5):
        if animate:
            for i in range(len(self.tour.path)):
                self.draw_board()
                self._draw_partial_path(i + 1, show_numbers)
                pygame.display.flip()
                time.sleep(delay)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()
                        elif event.key == pygame.K_r:
                            self.center_view()
        else:
            self._draw_partial_path(len(self.tour.path), show_numbers)
    
    def _draw_partial_path(self, steps, show_numbers):
        sidebar_width = int(self.window_width * 0.3)
        board_area = pygame.Surface((self.window_width - sidebar_width, self.window_height), pygame.SRCALPHA)
        cell_size_zoomed = self.cell_size * self.zoom_level
        line_width = max(1, int(4 * self.zoom_level))
        circle_radius = max(3, int(10 * self.zoom_level))
        for i in range(min(steps, len(self.tour.path))):
            if i < len(self.tour.path) - 1:
                start_x, start_y = self.tour.path[i]
                end_x, end_y = self.tour.path[i + 1]
                start_pixel_x = start_y * cell_size_zoomed + cell_size_zoomed // 2 + self.offset_x - sidebar_width
                start_pixel_y = start_x * cell_size_zoomed + cell_size_zoomed // 2 + self.offset_y
                end_pixel_x = end_y * cell_size_zoomed + cell_size_zoomed // 2 + self.offset_x - sidebar_width
                end_pixel_y = end_x * cell_size_zoomed + cell_size_zoomed // 2 + self.offset_y
                pygame.draw.line(board_area, self.PATH_COLOR, (start_pixel_x, start_pixel_y), (end_pixel_x, end_pixel_y), line_width)
            x, y = self.tour.path[i]
            center_x = y * cell_size_zoomed + cell_size_zoomed // 2 + self.offset_x - sidebar_width
            center_y = x * cell_size_zoomed + cell_size_zoomed // 2 + self.offset_y
            pygame.draw.circle(board_area, self.PATH_COLOR, (center_x, center_y), circle_radius)
            if show_numbers and self.zoom_level >= 0.4:
                move_number = self.tour.board[x][y]
                font_size = max(8, int(10 * self.zoom_level))
                temp_font = pygame.font.SysFont('Arial', font_size)
                text = temp_font.render(str(move_number), True, self.WHITE)
                text_rect = text.get_rect(center=(center_x, center_y))
                board_area.blit(text, text_rect)
        if steps > 0 and steps <= len(self.tour.path):
            last_x, last_y = self.tour.path[steps - 1]
            center_x = last_y * cell_size_zoomed + cell_size_zoomed // 2 + self.offset_x - sidebar_width
            center_y = last_x * cell_size_zoomed + cell_size_zoomed // 2 + self.offset_y
            knight_x = center_x - (cell_size_zoomed - 20) // 2
            knight_y = center_y - (cell_size_zoomed - 20) // 2
            if hasattr(self, 'knight_img_scaled') and self.knight_img_scaled and self.zoom_level >= 0.3:
                board_area.blit(self.knight_img_scaled, (knight_x, knight_y))
            else:
                pygame.draw.circle(board_area, self.HIGHLIGHT, (center_x, center_y), max(5, int(10 * self.zoom_level)))
        self.screen.blit(board_area, (sidebar_width, 0))
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_r:
                    self.zoom_level = 1.0
                    self.center_view()
                    self.update_knight_image()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    old_zoom = self.zoom_level
                    self.zoom_level = min(5.0, self.zoom_level * 1.1)
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    self.offset_x = mouse_x - ((mouse_x - self.offset_x) * (self.zoom_level / old_zoom))
                    self.offset_y = mouse_y - ((mouse_y - self.offset_y) * (self.zoom_level / old_zoom))
                    self.update_knight_image()
                elif event.button == 5:
                    old_zoom = self.zoom_level
                    self.zoom_level = max(0.1, self.zoom_level / 1.1)
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    self.offset_x = mouse_x - ((mouse_x - self.offset_x) * (self.zoom_level / old_zoom))
                    self.offset_y = mouse_y - ((mouse_y - self.offset_y) * (self.zoom_level / old_zoom))
                    self.update_knight_image()
                elif event.button == 1:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    sidebar_width = int(self.window_width * 0.3)
                    if mouse_x > sidebar_width:
                        self.dragging = True
                        self.drag_start = (mouse_x, mouse_y)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging:
                    current_pos = pygame.mouse.get_pos()
                    dx = current_pos[0] - self.drag_start[0]
                    dy = current_pos[1] - self.drag_start[1]
                    self.offset_x += dx
                    self.offset_y += dy
                    self.drag_start = current_pos
        return True
    
    def run(self, animate=True, delay=0.1):
        clock = pygame.time.Clock()
        running = True
        animation_done = False
        current_step = 0
        total_steps = len(self.tour.path)
        self.draw_board()
        pygame.display.flip()
        time.sleep(0.5)
        while running:
            running = self.handle_events()
            self.draw_board()
            if animate and not animation_done:
                if current_step < total_steps:
                    self._draw_partial_path(current_step + 1, show_numbers=True)
                    current_step += 1
                    pygame.display.flip()
                    time.sleep(delay)
                else:
                    animation_done = True
            else:
                self._draw_partial_path(total_steps, show_numbers=True)
            pygame.display.flip()
            clock.tick(60)
        pygame.quit()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Visualizador del recorrido del caballo')
    parser.add_argument('--size', type=int, default=8 , help='Tamaño del tablero')
    parser.add_argument('--start-x', type=int, default=0, help='Posición inicial fila (default: 0)')
    parser.add_argument('--start-y', type=int, default=0, help='Posición inicial columna (default: 0)')
    parser.add_argument('--no-animate', action='store_true', help='Desactivar animación')
    parser.add_argument('--delay', type=float, default=0.15, help='Retardo entre pasos de animación')
    parser.add_argument('--attempts', type=int, default=100, help='Número de intentos con Warnsdorff')
    parser.add_argument('--verbose', action='store_true', help='Mostrar información detallada de cada intento')
    parser.add_argument('--no-logs', action='store_true', help='No guardar archivos de registro')
    args = parser.parse_args()
    
    size = args.size
    start_x, start_y = args.start_x, args.start_y
    animate = not args.no_animate
    delay = args.delay
    
    print(f"Buscando solución para un tablero {size}x{size} desde la posición ({start_x}, {start_y})...")
    tour = KnightsTour(size)
    
    if not (0 <= start_x < size and 0 <= start_y < size):
        print(f"Posición inicial ({start_x}, {start_y}) fuera del tablero {size}x{size}.")
        print("Las coordenadas deben estar entre 0 y", size-1)
        sys.exit(1)
    
    print(f"Buscando solución con {args.attempts} intentos de la heurística de Warnsdorff...")
    success = tour.solve_with_multiple_warnsdorff_attempts(start_x, start_y, max_attempts=args.attempts, verbose=args.verbose, save_logs=not args.no_logs)
    
    if success:
        print(f"\nSe encontró una solución con Warnsdorff desde la posición inicial ({start_x}, {start_y})")
    else:
        print(f"\nNo se encontró solución con Warnsdorff después de {args.attempts} intentos desde ({start_x}, {start_y})")
        if size <= 30:
            print("\nIntentando con backtracking tradicional (puede tardar para tableros grandes)...")
            tour = KnightsTour(size)
            success = tour.solve(start_x, start_y)
            if success:
                print(f"\nSe encontró solución con backtracking desde ({start_x}, {start_y})")
            else:
                print(f"\nNo existe solución para este tablero desde ({start_x}, {start_y})")
        else:
            print(f"\nEl tablero es demasiado grande ({size}x{size}) para intentar con backtracking.")
    
    if success:
        tour.print_solution()
        tour.print_path()
        
        print("\nCreando visualización gráfica...")
        print("Controles:")
        print("  - Rueda del ratón: Zoom in/out")
        print("  - Click y arrastrar: Mover vista")
        print("  - R: Reiniciar vista")
        print("  - ESC: Salir")
        
        visualizer = KnightsTourVisualizer(tour)
        visualizer.run(animate=animate, delay=delay)
