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
        if vertex is None:
            raise ValueError("Vertex cannot be None.")
        if not isinstance(vertex, (int, str, tuple)):
            raise ValueError("Vertex must be a hashable type.")
        if vertex not in self.graph:
            self.graph[vertex] = {}
     
    def add_edge(self, src, dest, weight=1.0):
        if src not in self.graph or dest not in self.graph:
            raise KeyError("Both vertices must exist in the graph.")
        
        # Security Guard: Prevent negative weights
        if float(weight) < 0:
            raise ValueError("Edge weight cannot be negative.")
            
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

def tsp_exact(graph, start_vertex):
    """
    Solves the Traveling Salesman Problem (TSP) exactly using backtracking.
    Guarantees the absolute shortest route that visits all nodes and returns to start.

    Parameters:
    - graph (Graph): The weighted graph.
    - start_vertex: The starting (and ending) city.

    Returns:
    - tuple: (best_distance, best_path)
      Returns (float('inf'), []) if no valid tour exists.
    """
    # Security Guard: Limit input size to prevent CPU exhaustion and stack overflow
    MAX_EXACT_NODES = 12
    if len(graph.graph) > MAX_EXACT_NODES:
        raise ValueError(
            f"Graph size ({len(graph.graph)} nodes) exceeds the safe threshold for exact TSP solver "
            f"(max {MAX_EXACT_NODES} nodes). Use the heuristic solver instead to prevent DoS."
        )
    all_vertices = set(graph.graph.keys())
    best_path = []
    # We use a list to store best_distance so we can mutate it inside the helper function
    best_distance = [float('inf')]  

    def backtrack(current_vertex, visited, path, current_distance):
        # Base Case: If we have visited every city
        if len(visited) == len(all_vertices):
            # Check if there is a road from our final city back to the start_vertex
            neighbors = graph.get_adjacent_vertices(current_vertex)
            if start_vertex in neighbors:
                total_distance = current_distance + neighbors[start_vertex]
                # If this complete loop is shorter than our previous best, save it!
                if total_distance < best_distance[0]:
                    best_distance[0] = total_distance
                    best_path[:] = path + [start_vertex]
            return

        # Recursive Step: Try visiting every unvisited neighbor
        neighbors = graph.get_adjacent_vertices(current_vertex)
        for neighbor, weight in neighbors.items():
            if neighbor not in visited:
                # 1. Take a step forward (Mark as visited)
                visited.add(neighbor)
                path.append(neighbor)
                
                # 2. Explore further from this neighbor
                backtrack(neighbor, visited, path, current_distance + weight)
                
                # 3. Backtrack (Take a step backward, unmark, and try the next neighbor)
                path.pop()
                visited.remove(neighbor)

    # Start the backtracking process
    # Initially, we have visited only the starting vertex
    initial_visited = {start_vertex}
    initial_path = [start_vertex]
    
    backtrack(start_vertex, initial_visited, initial_path, 0.0)
    
    return best_distance[0], best_path

# Create a small graph of 4 cities
g_tsp = Graph(directed=False)

for city in ["A", "B", "C", "D"]:
    g_tsp.add_vertex(city)

# Connect all cities to each other with different distances
g_tsp.add_edge("A", "B", 10)
g_tsp.add_edge("A", "C", 15)
g_tsp.add_edge("A", "D", 20)
g_tsp.add_edge("B", "C", 35)
g_tsp.add_edge("B", "D", 25)
g_tsp.add_edge("C", "D", 30)

# Let's run TSP starting and ending at 'A'
print("--- Running Exact TSP starting at 'A' ---")
distance, path = tsp_exact(g_tsp, "A")
print(f"Shortest complete loop distance: {distance}")
print(f"Path: {' -> '.join(path)}")
# The shortest loop should be A -> B -> D -> C -> A (Distance: 10 + 25 + 30 + 15 = 80)