import heapq

class Graph:
    def __init__(self, directed=False):
        """
        Initialize a Weighted Graph.

        Attributes:
        - graph (dict): Dict mapping vertices to a dict of neighbors and weights.
                        Format: { vertex: { neighbor: weight } }
        - directed (bool): Indicates whether the graph is directed.
        """
        self.graph = {}
        self.directed = directed
    
    def add_vertex(self, vertex):
        """Add a hashable vertex to the graph."""
        if not isinstance(vertex, (int, str, tuple)):
            raise ValueError("Vertex must be a hashable type.")
        if vertex not in self.graph:
            self.graph[vertex] = {}  # Store neighbors as a dictionary {neighbor: weight}
     
    def add_edge(self, src, dest, weight=1.0):
        """
        Add a weighted edge from src to dest. 
        If undirected, also add from dest to src.
        """
        if src not in self.graph or dest not in self.graph:
            raise KeyError("Both vertices must exist in the graph.")
        
        # Add or update the edge with the given weight
        self.graph[src][dest] = float(weight)
        
        if not self.directed:
            self.graph[dest][src] = float(weight)
    
    def remove_edge(self, src, dest):
        """Remove a weighted edge between src and dest."""
        if src in self.graph and dest in self.graph[src]:
            del self.graph[src][dest]
        if not self.directed and dest in self.graph and src in self.graph[dest]:
            del self.graph[dest][src]
    
    def remove_vertex(self, vertex):
        """Remove a vertex and all edges connected to it."""
        if vertex in self.graph:
            # Remove references to this vertex in other vertices' neighbor lists
            for adj in list(self.graph):
                if vertex in self.graph[adj]:
                    del self.graph[adj][vertex]
            # Remove the vertex entry itself
            del self.graph[vertex]
    
    def get_adjacent_vertices(self, vertex):
        """
        Get a dictionary of adjacent vertices and their weights.
        
        Returns:
            dict: A dictionary of {neighbor: weight}
        """
        return self.graph.get(vertex, {})
    
    def __str__(self):
        return str(self.graph)


def dijkstra(graph, start, target):
    """
    Finds the shortest path between a start and target vertex in a weighted graph 
    using Dijkstra's algorithm with a priority queue (Min-Heap).

    Parameters:
    - graph (Graph): The weighted graph instance.
    - start: The starting vertex.
    - target: The destination vertex.

    Returns:
    - tuple: (shortest_distance, path_list)
      Returns (inf, []) if no path exists.
    """
    # 1. Validate that start and target exist in the graph
    if start not in graph.graph or target not in graph.graph:
        raise KeyError("Start and target vertices must exist in the graph.")

    # 2. Initialize our "notepad" dictionaries
    # distances maps every vertex to its currently known shortest distance from start
    distances = {vertex: float('inf') for vertex in graph.graph}
    distances[start] = 0.0

    # previous keeps track of the path by storing the preceding node for each vertex
    previous = {vertex: None for vertex in graph.graph}

    # 3. Initialize our priority queue (our Magic Inbox)
    # We store tuples of (current_distance, vertex)
    pq = [(0.0, start)]

    # 4. The Exploration Loop
    while pq:
        current_distance, current_vertex = heapq.heappop(pq)

        # If we have reached our target, we can stop early!
        if current_vertex == target:
            break

        # If the distance in our queue is greater than the best recorded distance, skip it
        if current_distance > distances[current_vertex]:
            continue

        # 5. Look at all neighbors of the current vertex
        neighbors = graph.get_adjacent_vertices(current_vertex)
        for neighbor, weight in neighbors.items():
            # Calculate total distance from start through current_vertex to neighbor
            distance = current_distance + weight

            # If we found a shorter path to the neighbor, update our records
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_vertex
                heapq.heappush(pq, (distance, neighbor))

    # 6. Path Reconstruction (Tracing backward from target to start)
    path = []
    current = target
    
    # If the target is unreachable, distances[target] will still be infinity
    if distances[target] == float('inf'):
        return float('inf'), []

    while current is not None:
        path.append(current)
        current = previous[current]

    # Because we traced backward, reverse the list so it goes from start -> target
    path.reverse()

    return distances[target], path

def tsp_nearest_neighbor(graph, start_vertex):
    """
    Solves the Traveling Salesman Problem (TSP) approximately using the 
    Nearest Neighbor heuristic. Highly scalable for large graphs.

    Parameters:
    - graph (Graph): The weighted graph.
    - start_vertex: The starting (and ending) city.

    Returns:
    - tuple: (total_distance, path_list)
      Returns (float('inf'), []) if no complete tour can be found.
    """
    all_vertices = set(graph.graph.keys())
    visited = {start_vertex}
    path = [start_vertex]
    current_vertex = start_vertex
    total_distance = 0.0

    # Continue until we have visited every node
    while len(visited) < len(all_vertices):
        neighbors = graph.get_adjacent_vertices(current_vertex)
        
        # Find the closest unvisited neighbor
        closest_neighbor = None
        min_weight = float('inf')
        
        for neighbor, weight in neighbors.items():
            if neighbor not in visited and weight < min_weight:
                min_weight = weight
                closest_neighbor = neighbor
                
        # If we get stuck and there are no unvisited neighbors we can reach directly,
        # a complete tour cannot be completed using this simple heuristic.
        if closest_neighbor is None:
            return float('inf'), []
            
        # Move to the closest neighbor
        visited.add(closest_neighbor)
        path.append(closest_neighbor)
        total_distance += min_weight
        current_vertex = closest_neighbor

    # Final step: Try to return back to the starting vertex from our last city
    final_neighbors = graph.get_adjacent_vertices(current_vertex)
    if start_vertex in final_neighbors:
        total_distance += final_neighbors[start_vertex]
        path.append(start_vertex)
    else:
        # Cannot return to start
        return float('inf'), []

    return total_distance, path

import random
import time

# --- Helper to generate a fully connected graph for TSP ---
def generate_complete_tsp_graph(num_nodes=1000):
    g = Graph(directed=False)
    for i in range(num_nodes):
        g.add_vertex(i)
        
    # Connect every node to every other node with a random weight (distance)
    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            weight = random.uniform(5.0, 100.0)
            g.add_edge(i, j, weight)
    return g

if __name__ == "__main__":
    print("--- Generating Large Complete Graph (1,000 Nodes) ---")
    print("This means 499,500 total highways connecting all cities...")
    start_gen = time.perf_counter()
    large_tsp_graph = generate_complete_tsp_graph(1000)
    end_gen = time.perf_counter()
    print(f"Graph generated in {end_gen - start_gen:.4f} seconds.")

    print("\n--- Running Nearest Neighbor TSP on 1,000 Nodes ---")
    start_time = time.perf_counter()
    distance, path = tsp_nearest_neighbor(large_tsp_graph, 0)
    end_time = time.perf_counter()

    if distance == float('inf'):
        print("Failed to find a complete tour.")
    else:
        print("Success!")
        print(f"Total distance of tour: {distance:.2f}")
        print(f"Nodes visited in loop: {len(path)}")
        print(f"Execution time: {end_time - start_time:.6f} seconds")