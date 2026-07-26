"""
Weighted Graph Algorithms Module
================================

This module implements a Weighted Graph data structure along with two fundamental 
graph optimization solvers:
1. Shortest Path (Dijkstra's Algorithm)
2. The Traveling Salesman Problem (Exact and Heuristic solvers)

The code has been optimized to ensure high scalability, defensive input 
validation (security checks), and clear coding patterns.
"""

import heapq
import random
import time


# =====================================================================
# 1. Scalable Weighted Graph Structure
# =====================================================================
class Graph:
    """
    A Graph data structure using an Adjacency List format.
    
    The adjacency list is stored as a nested dictionary:
    self.graph = {
        vertex_A: { neighbor_B: weight, neighbor_C: weight },
        vertex_B: { ... }
    }
    """

    def __init__(self, directed=False):
        """
        Initializes an empty graph.

        Args:
            directed (bool): True if edges are one-way; False if two-way.
        """
        self.graph = {}
        self.directed = directed
    
    def add_vertex(self, vertex):
        """
        Registers a new vertex (city/node) on the map.

        Args:
            vertex: Must be a hashable object (string, integer, or tuple) 
                    so it can serve as a key in our self.graph dictionary.
        """
        # Security Guard: Explicitly disallow 'None' which is hashable but logically invalid
        if vertex is None:
            raise ValueError("Vertex cannot be None.")
            
        # Security Guard: Ensure we can safely use this as a dictionary key
        if not isinstance(vertex, (int, str, tuple)):
            raise ValueError("Vertex must be a hashable type.")
            
        # Register the vertex with an empty adjacency map (no roads attached yet)
        if vertex not in self.graph:
            self.graph[vertex] = {}
     
    def add_edge(self, src, dest, weight=1.0):
        """
        Establishes a weighted connection (highway) between two existing vertices.

        Args:
            src: The source vertex key.
            dest: The destination vertex key.
            weight (float): The cost/distance of the edge (must be non-negative).
        """
        # Security Guard: Both cities must exist on the map before we can build a road
        if src not in self.graph or dest not in self.graph:
            raise KeyError("Both vertices must exist in the graph.")
        
        # Security Guard: Negative weights break the mathematical foundation of Dijkstra
        if float(weight) < 0:
            raise ValueError("Edge weight cannot be negative.")
            
        # Add or update the connection in the source's road dictionary
        self.graph[src][dest] = float(weight)
        
        # If the map represents a two-way street network, register the reverse highway
        if not self.directed:
            self.graph[dest][src] = float(weight)
    
    def remove_edge(self, src, dest):
        """
        Deletes the connection (highway) between two vertices.
        """
        # Safely remove src -> dest
        if src in self.graph and dest in self.graph[src]:
            del self.graph[src][dest]
            
        # If undirected, also safely remove the reciprocal dest -> src road
        if not self.directed and dest in self.graph and src in self.graph[dest]:
            del self.graph[dest][src]
    
    def remove_vertex(self, vertex):
        """
        Deletes a vertex (city) and all incoming/outgoing edges connected to it.
        
        Performance Optimizations:
        - For Undirected Graphs: This runs in O(Degree) time. Instead of scanning 
          every node, we only visit the neighbors connected directly to the target.
        - For Directed Graphs: Fallback to O(V) scan to find all incoming links.
        """
        if vertex in self.graph:
            if not self.directed:
                # Scalability Optimization: Only look up direct neighbors instead of all V nodes
                for neighbor in list(self.graph[vertex].keys()):
                    if vertex in self.graph[neighbor]:
                        del self.graph[neighbor][vertex]
            else:
                # Directed: We must scan all vertices in the graph to prune incoming edges
                for adj in list(self.graph):
                    if vertex in self.graph[adj]:
                        del self.graph[adj][vertex]
            
            # Finally, delete the city entry itself from the outer map
            del self.graph[vertex]
    
    def get_adjacent_vertices(self, vertex):
        """
        Returns a dictionary of all direct neighbors and their corresponding edge weights.
        Format: { neighbor: weight }
        """
        return self.graph.get(vertex, {})
    
    def __str__(self):
        """Renders the graph dictionary as a string for debugging and print statements."""
        return str(self.graph)


# =====================================================================
# 2. Problem 1: Scalable Dijkstra's Shortest Path Algorithm
# =====================================================================
def dijkstra(graph, start, target):
    """
    Finds the shortest path between 'start' and 'target' in a weighted graph.

    This is an implementation of Dijkstra's Algorithm using a binary Min-Heap.
    
    Scalability Optimization (Lazy Initialization):
    - Traditional Dijkstra initializes the distance of all nodes to 'infinity' 
      before starting. For massive graphs (e.g., millions of nodes), this takes O(V) 
      time and memory even if the target is only a few hops away.
    - This version uses a sparse lookup. It assumes any vertex not present in the 
      'distances' dictionary has a distance of infinity. This reduces initialization 
      overhead from O(V) to O(D log D) where D is only the explored region of the graph.

    Returns:
        tuple: (shortest_distance, path_list)
               Returns (float('inf'), []) if no path exists.
    """
    # 1. Defensive input checks
    if start not in graph.graph or target not in graph.graph:
        raise KeyError("Start and target vertices must exist in the graph.")

    # 2. Sparse (Lazy) initialization
    distances = {start: 0.0}  # Only register the start node at distance 0
    previous = {}             # Track backward steps dynamically
    pq = [(0.0, start)]       # Priority Queue (Min-Heap) holds (distance, vertex) tuples

    # 3. Main Exploration Loop
    while pq:
        # heappop() instantly gives us the unvisited vertex with the smallest distance
        current_distance, current_vertex = heapq.heappop(pq)

        # Early exit: If we reached our target, we've found the shortest route!
        if current_vertex == target:
            break

        # Since nodes can be pushed to the heap multiple times with different distances,
        # we skip processing if we have already finalized a shorter path to this node.
        # We use .get(..., float('inf')) to safely handle undiscovered nodes.
        if current_distance > distances.get(current_vertex, float('inf')):
            continue

        # Look at all direct neighbors of our current city
        neighbors = graph.get_adjacent_vertices(current_vertex)
        for neighbor, weight in neighbors.items():
            # Calculate the total accumulated mileage to this neighbor through the current city
            distance = current_distance + weight

            # If this new path is shorter than any previously recorded path to the neighbor,
            # update our records and push the neighbor onto the priority queue for exploration.
            if distance < distances.get(neighbor, float('inf')):
                distances[neighbor] = distance
                previous[neighbor] = current_vertex
                heapq.heappush(pq, (distance, neighbor))

    # 4. Path Reconstruction (Walk backward using 'previous' links)
    path = []
    current = target
    
    # If the target is unreachable, its distance remains infinity
    if distances.get(target, float('inf')) == float('inf'):
        return float('inf'), []

    # Trace backward from the destination to the start
    while current is not None:
        path.append(current)
        current = previous.get(current)  # Use .get() due to lazy sparse dictionary

    # Reverse the backward-traced list so it reads start -> target
    path.reverse()
    return distances[target], path


# =====================================================================
# 3. Problem 2: Traveling Salesman Problem (TSP) Solvers
# =====================================================================

def tsp_exact(graph, start_vertex):
    """
    Solves the Traveling Salesman Problem (TSP) exactly using backtracking (DFS).
    
    Complexity: O(N!) - Exponential.
    Use case: Guarantees the absolute mathematically perfect shortest loop, but 
              only suitable for small graphs (N <= 12) due to processing limits.
    """
    # Security Guard: Limit input size to prevent severe CPU-exhaustion DoS and stack overflow
    MAX_EXACT_NODES = 12
    if len(graph.graph) > MAX_EXACT_NODES:
        raise ValueError(
            f"Graph size ({len(graph.graph)} nodes) exceeds the safe threshold for exact TSP solver "
            f"(max {MAX_EXACT_NODES} nodes). Use the heuristic solver instead."
        )

    all_vertices = set(graph.graph.keys())
    best_path = []
    # We store best_distance inside a list so we can mutate it inside the helper backtracking function
    best_distance = [float('inf')]  

    def backtrack(current_vertex, visited, path, current_distance):
        # Base Case: If we have visited every city exactly once
        if len(visited) == len(all_vertices):
            # Check if we can close the loop by driving from this last city back to the start_vertex
            neighbors = graph.get_adjacent_vertices(current_vertex)
            if start_vertex in neighbors:
                total_distance = current_distance + neighbors[start_vertex]
                # If this total cycle distance is shorter than our best loop, record it
                if total_distance < best_distance[0]:
                    best_distance[0] = total_distance
                    best_path[:] = path + [start_vertex]
            return

        # Recursive Step: Try visiting every unvisited neighbor
        neighbors = graph.get_adjacent_vertices(current_vertex)
        for neighbor, weight in neighbors.items():
            if neighbor not in visited:
                # 1. Step Forward (Mark as visited)
                visited.add(neighbor)
                path.append(neighbor)
                
                # 2. Explore recursively from this neighbor
                backtrack(neighbor, visited, path, current_distance + weight)
                
                # 3. Step Backward (Unmark / Backtrack to allow different pathways)
                path.pop()
                visited.remove(neighbor)

    # Initialize backtracking starting at the start_vertex
    initial_visited = {start_vertex}
    initial_path = [start_vertex]
    backtrack(start_vertex, initial_visited, initial_path, 0.0)
    
    return best_distance[0], best_path


def tsp_nearest_neighbor(graph, start_vertex):
    """
    Solves the Traveling Salesman Problem (TSP) approximately using the 
    Nearest Neighbor heuristic.
    
    Complexity: O(V^2) - Polynomial.
    Use case: Scalable up to thousands of nodes. It does not guarantee the 
              perfect route, but finds a highly optimized route in milliseconds.
    """
    # Security Guard 1: Prevent silent logical failures by validating the starting vertex
    if start_vertex not in graph.graph:
        raise KeyError("Start vertex must exist in the graph.")

    # Security Guard 2: Prevent thread-blocking CPU exhaustion on massive graphs
    MAX_HEURISTIC_NODES = 20000
    if len(graph.graph) > MAX_HEURISTIC_NODES:
        raise ValueError(
            f"Graph size ({len(graph.graph)} nodes) exceeds safe processing limit "
            f"(max limit: {MAX_HEURISTIC_NODES} nodes)."
        )

    all_vertices = set(graph.graph.keys())
    visited = {start_vertex}
    path = [start_vertex]
    current_vertex = start_vertex
    total_distance = 0.0

    # Greedy Traversal Loop: Keep visiting the closest neighbor until all nodes are visited
    while len(visited) < len(all_vertices):
        neighbors = graph.get_adjacent_vertices(current_vertex)
        
        closest_neighbor = None
        min_weight = float('inf')
        
        # Look at all neighbors to find the closest unvisited one
        for neighbor, weight in neighbors.items():
            if neighbor not in visited and weight < min_weight:
                min_weight = weight
                closest_neighbor = neighbor
                
        # Safe exit: If there are unvisited cities but we have no roads to reach them
        if closest_neighbor is None:
            return float('inf'), []
            
        # Move to the closest neighbor
        visited.add(closest_neighbor)
        path.append(closest_neighbor)
        total_distance += min_weight
        current_vertex = closest_neighbor

    # Final Step: Close the loop back to the start_vertex
    final_neighbors = graph.get_adjacent_vertices(current_vertex)
    if start_vertex in final_neighbors:
        total_distance += final_neighbors[start_vertex]
        path.append(start_vertex)
    else:
        # If we cannot return to our origin city, the loop is incomplete
        return float('inf'), []

    return total_distance, path


# =====================================================================
# 4. Helper Test Generator
# =====================================================================
def generate_complete_tsp_graph(num_nodes=1000):
    """
    Generates a complete graph (all nodes connected to all other nodes) 
    with random edge weights for testing scale-performance of TSP solvers.
    """
    # Security Guard 3: Prevent memory exhaustion crashes (Out-Of-Memory)
    MAX_TEST_NODES = 5000
    if num_nodes > MAX_TEST_NODES:
        raise ValueError(
            f"Requested size ({num_nodes} nodes) is too large. "
            f"Max limit allowed is {MAX_TEST_NODES} to prevent memory crashes."
        )

    g = Graph(directed=False)
    for i in range(num_nodes):
        g.add_vertex(i)
        
    # Build complete connections: connect node i to every node j > i
    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            weight = random.uniform(5.0, 100.0)
            g.add_edge(i, j, weight)
    return g


# =====================================================================
# 5. Combined Verification and Test Suite
# =====================================================================
if __name__ == "__main__":
    print("==================================================")
    print("  RUNNING UNIFIED GRAPH ALGORITHM TESTS (SCALED)  ")
    print("==================================================")

    # Setup a small 8-city map for Dijkstra testing
    g_small = Graph(directed=False)
    for city in ["Seattle", "Denver", "Chicago", "Boston", "Dallas", "New York", "Miami", "Orlando"]:
        g_small.add_vertex(city)

    g_small.add_edge("Seattle", "Denver", 1300)
    g_small.add_edge("Seattle", "Chicago", 2000)
    g_small.add_edge("Denver", "Dallas", 800)
    g_small.add_edge("Denver", "Chicago", 1000)
    g_small.add_edge("Chicago", "Boston", 1000)
    g_small.add_edge("Chicago", "New York", 800)
    g_small.add_edge("Dallas", "Miami", 1300)
    g_small.add_edge("New York", "Boston", 200)
    g_small.add_edge("New York", "Miami", 1300)
    g_small.add_edge("Boston", "Miami", 1500)

    # --- Test 1: Dijkstra Shortest Path ---
    print("\n[Test 1] Dijkstra's Algorithm (Small Graph):")
    distance, route = dijkstra(g_small, "Seattle", "Miami")
    print(f"  Route: {' -> '.join(route)}")
    print(f"  Distance: {distance} miles (Expected: 3400.0)")

    # --- Test 2: Exact TSP ---
    print("\n[Test 2] Exact TSP Solver (Backtracking on 4 Nodes):")
    g_exact = Graph(directed=False)
    for node in ["A", "B", "C", "D"]:
        g_exact.add_vertex(node)
    g_exact.add_edge("A", "B", 10)
    g_exact.add_edge("A", "C", 15)
    g_exact.add_edge("A", "D", 20)
    g_exact.add_edge("B", "C", 35)
    g_exact.add_edge("B", "D", 25)
    g_exact.add_edge("C", "D", 30)

    tsp_dist, tsp_path = tsp_exact(g_exact, "A")
    print(f"  Loop Route: {' -> '.join(tsp_path)}")
    print(f"  Loop Distance: {tsp_dist} (Expected: 80.0)")

    # --- Test 3: Large Scale Nearest Neighbor TSP ---
    print("\n[Test 3] Large-Scale Heuristic TSP (1,000 Nodes):")
    print("  Generating large complete graph...")
    start_gen = time.perf_counter()
    g_large = generate_complete_tsp_graph(1000)
    end_gen = time.perf_counter()
    print(f"  Complete graph generated in {end_gen - start_gen:.4f} seconds.")

    start_tsp = time.perf_counter()
    heuristic_dist, heuristic_path = tsp_nearest_neighbor(g_large, 0)
    end_tsp = time.perf_counter()
    
    print("  Success!")
    print(f"  Calculated total loop distance: {heuristic_dist:.2f}")
    print(f"  Nodes visited in tour: {len(heuristic_path)}")
    print(f"  TSP calculation execution time: {end_tsp - start_tsp:.6f} seconds")
    print("\n==================================================")