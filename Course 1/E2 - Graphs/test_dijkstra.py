import heapq

# =====================================================================
# 1. Our Weighted Graph Class (from graph3.py design)
# =====================================================================
class Graph:
    def __init__(self, directed=False):
        self.graph = {}
        self.directed = directed
    
    def add_vertex(self, vertex):
        if not isinstance(vertex, (int, str, tuple)):
            raise ValueError("Vertex must be a hashable type.")
        if vertex not in self.graph:
            self.graph[vertex] = {}
    
    def add_edge(self, src, dest, weight=1.0):
        if src not in self.graph or dest not in self.graph:
            raise KeyError("Both vertices must exist in the graph.")
        self.graph[src][dest] = float(weight)
        if not self.directed:
            self.graph[dest][src] = float(weight)
    
    def get_adjacent_vertices(self, vertex):
        return self.graph.get(vertex, {})

# =====================================================================
# 2. Our Dijkstra's Algorithm Function
# =====================================================================
def dijkstra(graph, start, target):
    if start not in graph.graph or target not in graph.graph:
        raise KeyError("Start and target vertices must exist in the graph.")

    distances = {vertex: float('inf') for vertex in graph.graph}
    distances[start] = 0.0
    previous = {vertex: None for vertex in graph.graph}
    pq = [(0.0, start)]

    while pq:
        current_distance, current_vertex = heapq.heappop(pq)

        if current_vertex == target:
            break

        if current_distance > distances[current_vertex]:
            continue

        neighbors = graph.get_adjacent_vertices(current_vertex)
        for neighbor, weight in neighbors.items():
            distance = current_distance + weight

            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_vertex
                heapq.heappush(pq, (distance, neighbor))

    # Path Reconstruction
    path = []
    current = target
    
    if distances[target] == float('inf'):
        return float('inf'), []

    while current is not None:
        path.append(current)
        current = previous[current]

    path.reverse()
    return distances[target], path

# =====================================================================
# 3. Running the Test Cases
# =====================================================================
if __name__ == "__main__":
    # Create an undirected graph (two-way roads)
    g = Graph(directed=False)

    # Add our 8 cities
    cities = ["Seattle", "Denver", "Chicago", "Boston", "Dallas", "New York", "Miami", "Orlando"]
    for city in cities:
        g.add_vertex(city)

    # Build the highways with mileage (weights)
    g.add_edge("Seattle", "Denver", 1300)
    g.add_edge("Seattle", "Chicago", 2000)
    
    g.add_edge("Denver", "Dallas", 800)
    g.add_edge("Denver", "Chicago", 1000)
    
    g.add_edge("Chicago", "Boston", 1000)
    g.add_edge("Chicago", "New York", 800)
    
    g.add_edge("Dallas", "Miami", 1300)
    
    g.add_edge("New York", "Boston", 200)
    g.add_edge("New York", "Miami", 1300)
    
    g.add_edge("Boston", "Miami", 1500)

    # Note: "Orlando" is left with no roads leading to it to test unreachable nodes.

    print("--- Test 1: Seattle to Miami ---")
    # Path possibilities:
    # 1. Seattle -> Denver -> Dallas -> Miami = 1300 + 800 + 1300 = 3400 miles.
    # 2. Seattle -> Chicago -> New York -> Miami = 2000 + 800 + 1300 = 4100 miles.
    # Dijkstra should choose the Denver -> Dallas route (3400 miles).
    distance, route = dijkstra(g, "Seattle", "Miami")
    print(f"Shortest distance: {distance} miles")
    print(f"Route: {' -> '.join(route)}")
    print("Expected: Seattle -> Denver -> Dallas -> Miami (3400.0 miles)\n")

    print("--- Test 2: Denver to Boston ---")
    # Path possibilities:
    # 1. Denver -> Chicago -> Boston = 1000 + 1000 = 2000 miles.
    # 2. Denver -> Chicago -> New York -> Boston = 1000 + 800 + 200 = 2000 miles.
    # 3. Denver -> Seattle -> Chicago -> ... (obviously too long)
    distance, route = dijkstra(g, "Denver", "Boston")
    print(f"Shortest distance: {distance} miles")
    print(f"Route: {' -> '.join(route)}")
    print("Expected: Denver -> Chicago -> Boston OR Denver -> Chicago -> New York -> Boston (2000.0 miles)\n")

    print("--- Test 3: Seattle to Orlando (Unreachable) ---")
    # Since Orlando has no roads connected to it, Dijkstra should return float('inf') and an empty list.
    distance, route = dijkstra(g, "Seattle", "Orlando")
    print(f"Shortest distance: {distance}")
    print(f"Route: {route}")
    print("Expected: inf and []\n")


import random
import time

def generate_large_graph(num_vertices=5000, connections_per_node=3):
    """
    Generates a large, connected weighted graph for scalability testing.
    """
    large_graph = Graph(directed=False)
    
    # 1. Add all vertices (0 to num_vertices - 1)
    for i in range(num_vertices):
        large_graph.add_vertex(i)
        
    # 2. To guarantee a path exists from start to end,
    # we first connect all vertices in a linear chain (0 -> 1 -> 2 -> ... -> N-1)
    for i in range(num_vertices - 1):
        # Assign a random weight between 1.0 and 10.0
        weight = random.uniform(1.0, 10.0)
        large_graph.add_edge(i, i + 1, weight)
        
    # 3. Add extra random connections (shortcuts) to simulate a real road network
    for i in range(num_vertices):
        for _ in range(connections_per_node):
            random_neighbor = random.randint(0, num_vertices - 1)
            if random_neighbor != i:
                weight = random.uniform(1.0, 10.0)
                # Ensure we don't accidentally raise a KeyError by checking existence
                if random_neighbor in large_graph.graph:
                    large_graph.add_edge(i, random_neighbor, weight)
                    
    return large_graph

# --- Run the Large Scale Test ---
if __name__ == "__main__":
    print("--- Generating Large Graph (5,000 Nodes) ---")
    num_nodes = 5000
    g_large = generate_large_graph(num_nodes, connections_per_node=3)
    print(f"Successfully generated graph with {num_nodes} nodes.")

    print("\n--- Running Dijkstra on 5,000 Nodes ---")
    start_node = 0
    end_node = num_nodes - 1

    start_time = time.perf_counter()
    distance, route = dijkstra(g_large, start_node, end_node)
    end_time = time.perf_counter()

    execution_time = end_time - start_time
    print(f"Calculation complete!")
    print(f"Shortest path distance: {distance:.2f}")
    print(f"Path length: {len(route)} nodes visited")
    print(f"Execution time: {execution_time:.6f} seconds")