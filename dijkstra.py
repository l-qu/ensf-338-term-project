import csv
import heapq
import sys

def load_graph(filename):
    graph = {}
    # Read csv file and build the graph as an adjacency list
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            u, v, w = row['source'], row['target'], int(row['weight'])
            
            # Check if both nodes exist in graph, if not init them as empty lists
            if u not in graph: 
                graph[u] = []
            if v not in graph: 
                graph[v] = []
            
            # Add edge to the graph (undirected (not sure if they want directed))
            graph[u].append((v, w))
            graph[v].append((u, w))
    return graph

def dijkstra(graph, start_node):
    # Init distances with inf and set start to 0 
    distances = {node: sys.maxsize for node in graph}
    distances[start_node] = 0
    predecessors = {node: None for node in graph}
    
    priority_queue = [(0, start_node)]
    
    # Loop until the priority queue is empty
    while priority_queue:
        current_dist, u = heapq.heappop(priority_queue)
        
        # If current > distance skip node 
        if current_dist > distances[u]:
            continue
            
        # Iterates through the neighbors of node u and updates their distances if a shorter path is found
        for neighbor, weight in graph[u]:
            new_dist = current_dist + weight
            if new_dist < distances[neighbor]: 
                predecessors[neighbor] = u
                distances[neighbor] = new_dist 
                heapq.heappush(priority_queue, (new_dist, neighbor))
                
    return distances, predecessors


def get_path(predecessors, target_node):
    path = []
    current = target_node
    while current is not None:
        path.append(current)
        current = predecessors[current]
    return path[::-1]  # Reverse the path to get the correct order 


start = input("Enter the starting node: ")
end = input("Enter the destination node: ")

my_graph = load_graph('vals.csv')
distances, predecessors = dijkstra(my_graph, start)

print('Shortest distances from ' + start + ' to ' + end + ':')
print(f"Destination: {end}")
print(f"Total Time: {distances[end]} min")
print(f"Route: {' -> '.join(get_path(predecessors, end))}")
