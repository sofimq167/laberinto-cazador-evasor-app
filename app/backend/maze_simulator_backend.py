# maze_simulator_backend.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import heapq
from collections import deque, defaultdict
import math

app = Flask(__name__, static_url_path='', static_folder='.')
CORS(app)  # Permite peticiones desde el frontend

# ALGORITMOS VORACES

class PriorityQueue:
    """Cola de prioridad para A* y Dijkstra"""
    def __init__(self):
        self.elements = []
    
    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))
    
    def get(self):
        return heapq.heappop(self.elements)[1]
    
    def empty(self):
        return len(self.elements) == 0


def heuristic(a, b):
    """Distancia Manhattan para A*"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def a_star(grid, start, goal, avoid_pos=None):
    """
    Algoritmo A* (Voraz con heurística)
    Encuentra el camino más corto usando distancia Manhattan
    """
    rows, cols = len(grid), len(grid[0])
    frontier = PriorityQueue()
    frontier.put(start, 0)
    
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0
    
    visited = []
    
    while not frontier.empty():
        current = frontier.get()
        visited.append(current)
        
        if current == goal:
            break
        
        # Explorar vecinos
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            neighbor = (current[0] + dr, current[1] + dc)
            
            # Validar límites
            if not (0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols):
                continue
            
            # Validar obstáculos
            if grid[neighbor[0]][neighbor[1]] == 1:
                continue
            
            # Evitar posición del otro agente
            if avoid_pos and neighbor == avoid_pos:
                continue
            
            new_cost = cost_so_far[current] + 1
            
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + heuristic(neighbor, goal)
                frontier.put(neighbor, priority)
                came_from[neighbor] = current
    
    # Reconstruir camino
    path = []
    current = goal
    while current is not None:
        path.append(list(current))
        current = came_from.get(current)
    path.reverse()
    
    return {
        'path': path,
        'visited': [list(v) for v in visited],
        'cost': cost_so_far.get(goal, float('inf'))
    }


def dijkstra(grid, start, goal, avoid_pos=None):
    """
    Algoritmo de Dijkstra (Voraz sin heurística)
    Encuentra el camino más corto explorando sistemáticamente
    """
    rows, cols = len(grid), len(grid[0])
    distances = {start: 0}
    pq = PriorityQueue()
    pq.put(start, 0)
    came_from = {start: None}
    visited = []
    
    while not pq.empty():
        current = pq.get()
        
        if current in visited:
            continue
        
        visited.append(current)
        
        if current == goal:
            break
        
        # Explorar vecinos
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            neighbor = (current[0] + dr, current[1] + dc)
            
            # Validar límites
            if not (0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols):
                continue
            
            # Validar obstáculos
            if grid[neighbor[0]][neighbor[1]] == 1:
                continue
            
            # Evitar posición del otro agente
            if avoid_pos and neighbor == avoid_pos:
                continue
            
            new_dist = distances[current] + 1
            
            if neighbor not in distances or new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                came_from[neighbor] = current
                pq.put(neighbor, new_dist)
    
    # Reconstruir camino
    path = []
    current = goal
    while current is not None:
        path.append(list(current))
        current = came_from.get(current)
    path.reverse()
    
    return {
        'path': path,
        'visited': [list(v) for v in visited],
        'cost': distances.get(goal, float('inf'))
    }


# ALGORITMOS DINÁMICOS

def dfs_memoized(grid, start, goal, avoid_pos=None):
    """
    DFS con Memoización (Programación Dinámica)
    Búsqueda en profundidad con cache de estados visitados
    """
    rows, cols = len(grid), len(grid[0])
    memo = {}
    visited = []
    path = []
    
    def dfs(pos, current_path):
        if pos in memo:
            return memo[pos]
        
        r, c = pos
        
        # Validaciones
        if not (0 <= r < rows and 0 <= c < cols):
            return False
        if grid[r][c] == 1:
            return False
        if avoid_pos and pos == avoid_pos:
            return False
        if pos in current_path:
            return False
        
        visited.append(pos)
        current_path.append(pos)
        
        # Objetivo encontrado
        if pos == goal:
            path.extend([list(p) for p in current_path])
            memo[pos] = True
            return True
        
        # Explorar vecinos
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for dr, dc in directions:
            next_pos = (r + dr, c + dc)
            if dfs(next_pos, current_path[:]):
                memo[pos] = True
                return True
        
        memo[pos] = False
        return False
    
    dfs(start, [])
    
    return {
        'path': path if path else [list(start)],
        'visited': [list(v) for v in visited],
        'cost': len(path) - 1 if path else float('inf')
    }


def bellman_ford(grid, start, goal, avoid_pos=None):
    """
    Algoritmo Bellman-Ford (Programación Dinámica)
    Calcula distancias mínimas mediante relajación de aristas
    """
    rows, cols = len(grid), len(grid[0])
    
    # Inicializar distancias
    distances = defaultdict(lambda: float('inf'))
    distances[start] = 0
    parent = {}
    
    # Relajación de aristas (V-1 iteraciones)
    num_vertices = rows * cols
    for _ in range(num_vertices - 1):
        updated = False
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == 1:
                    continue
                
                current = (r, c)
                if distances[current] == float('inf'):
                    continue
                
                # Explorar vecinos
                for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nr, nc = r + dr, c + dc
                    
                    if not (0 <= nr < rows and 0 <= nc < cols):
                        continue
                    if grid[nr][nc] == 1:
                        continue
                    
                    neighbor = (nr, nc)
                    if avoid_pos and neighbor == avoid_pos:
                        continue
                    
                    new_dist = distances[current] + 1
                    if new_dist < distances[neighbor]:
                        distances[neighbor] = new_dist
                        parent[neighbor] = current
                        updated = True
        
        if not updated:
            break
    
    # Reconstruir camino
    path = []
    current = goal
    while current in parent or current == start:
        path.append(list(current))
        if current == start:
            break
        current = parent.get(current)
    path.reverse()
    
    # Crear lista de visitados
    visited = [list(pos) for pos, dist in distances.items() if dist != float('inf')]
    
    return {
        'path': path,
        'visited': visited,
        'cost': distances[goal] if distances[goal] != float('inf') else float('inf')
    }


# ENDPOINTS DE LA API

@app.route('/api/compute-path', methods=['POST'])
def compute_path():
    """
    Endpoint para calcular el camino de un agente
    """
    data = request.json
    
    grid = data['grid']
    start = tuple(data['start'])
    goal = tuple(data['goal'])
    algorithm = data['algorithm']
    avoid_pos = tuple(data['avoid_pos']) if data.get('avoid_pos') else None
    
    # Seleccionar algoritmo
    algorithms = {
        'aStar': a_star,
        'dijkstra': dijkstra,
        'dfsMemo': dfs_memoized,
        'bellmanFord': bellman_ford
    }
    
    if algorithm not in algorithms:
        return jsonify({'error': 'Invalid algorithm'}), 400
    
    try:
        result = algorithms[algorithm](grid, start, goal, avoid_pos)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/simulate-step', methods=['POST'])
def simulate_step():
    """
    Endpoint para simular un paso de la simulación
    Calcula los movimientos de ambos agentes
    """
    data = request.json
    
    grid = data['grid']
    agent1_pos = tuple(data['agent1_pos'])
    agent2_pos = tuple(data['agent2_pos'])
    exit_pos = tuple(data['exit_pos'])
    agent1_config = data['agent1_config']
    agent2_config = data['agent2_config']
    
    # Determinar roles y objetivos
    hunter_pos = agent1_pos if agent1_config['role'] == 'hunter' else agent2_pos
    prey_pos = agent1_pos if agent1_config['role'] == 'prey' else agent2_pos
    hunter_algo = agent1_config['algorithm'] if agent1_config['role'] == 'hunter' else agent2_config['algorithm']
    prey_algo = agent1_config['algorithm'] if agent1_config['role'] == 'prey' else agent2_config['algorithm']
    
    algorithms = {
        'aStar': a_star,
        'dijkstra': dijkstra,
        'dfsMemo': dfs_memoized,
        'bellmanFord': bellman_ford
    }
    
    # Calcular camino del cazador (objetivo: presa)
    hunter_result = algorithms[hunter_algo](grid, hunter_pos, prey_pos)
    
    # Calcular camino de la presa (objetivo: salida, evitando cazador)
    prey_result = algorithms[prey_algo](grid, prey_pos, exit_pos, hunter_pos)
    
    # Determinar nuevas posiciones
    new_agent1_pos = agent1_pos
    new_agent2_pos = agent2_pos
    
    if agent1_config['role'] == 'hunter' and len(hunter_result['path']) > 1:
        new_agent1_pos = hunter_result['path'][1]
    elif agent1_config['role'] == 'prey' and len(prey_result['path']) > 1:
        new_agent1_pos = prey_result['path'][1]
    
    if agent2_config['role'] == 'hunter' and len(hunter_result['path']) > 1:
        new_agent2_pos = hunter_result['path'][1]
    elif agent2_config['role'] == 'prey' and len(prey_result['path']) > 1:
        new_agent2_pos = prey_result['path'][1]
    
    # Verificar condiciones de victoria
    winner = None
    if new_agent1_pos == new_agent2_pos:
        winner = 'Agent 1 (Hunter)' if agent1_config['role'] == 'hunter' else 'Agent 2 (Hunter)'
        winner += ' captured the prey'
    elif (agent1_config['role'] == 'prey' and new_agent1_pos == exit_pos) or \
         (agent2_config['role'] == 'prey' and new_agent2_pos == exit_pos):
        winner = 'Agent 1 (Evader)' if agent1_config['role'] == 'prey' else 'Agent 2 (Evader)'
        winner += ' escaped the maze'
    
    return jsonify({
        'new_agent1_pos': list(new_agent1_pos),
        'new_agent2_pos': list(new_agent2_pos),
        'hunter_path': hunter_result['path'],
        'prey_path': prey_result['path'],
        'winner': winner
    })


@app.route('/api/health', methods=['GET'])
def health():
    """
    Endpoint para verificar que el servidor está funcionando
    """
    return jsonify({'status': 'ok', 'message': 'Backend running correctly'})

@app.route('/')
def serve_index():
    # Servir el frontend estático
    return send_from_directory('.', 'index.html')


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))

    app.run(host='0.0.0.0', port=port, debug=False)
