"""Campus map model + Dijkstra shortest path utilities."""

from __future__ import annotations

import csv
import heapq
from pathlib import Path


Graph = dict[str, list[tuple[str, int]]]


class Room:
    """Represents one room inside a building."""

    def __init__(self, room_id: str, capacity: int, room_type: str):
        self.room_id = room_id
        self.capacity = capacity
        self.room_type = room_type
        self.bookings: list[object] = []


class Building:
    """Represents one campus building."""

    def __init__(self, building_id: str, name: str, location: tuple[float, float]):
        self.building_id = building_id
        self.name = name
        self.location = location
        self.rooms: dict[str, Room] = {}

    def add_room(self, room: Room) -> None:
        """Add a room to this building."""
        self.rooms[room.room_id] = room


class Campus:
    """Stores buildings and weighted pathways between them."""

    def __init__(self) -> None:
        self.buildings: dict[str, Building] = {}
        self.pathways: Graph = {}

    def add_building(self, building: Building) -> None:
        """Register a building in the campus."""
        self.buildings[building.building_id] = building
        self.pathways.setdefault(building.building_id, [])

    def add_pathway(self, source_id: str, target_id: str, minutes: int) -> None:
        """Add an undirected walking path between two buildings."""
        if source_id not in self.buildings or target_id not in self.buildings:
            raise ValueError("Both buildings must exist before adding a pathway")

        self.pathways[source_id].append((target_id, minutes))
        self.pathways[target_id].append((source_id, minutes))

    def shortest_path(self, start_id: str, end_id: str) -> tuple[list[str], int]:
        """Find shortest path and travel time between two building IDs."""
        if start_id not in self.buildings:
            raise ValueError(f"Unknown starting node: {start_id}")
        if end_id not in self.buildings:
            raise ValueError(f"Unknown destination node: {end_id}")

        distances, predecessors = dijkstra(self.pathways, start_id)
        if distances[end_id] == float("inf"):
            raise ValueError(f"No route found from {start_id} to {end_id}")

        return get_path(predecessors, end_id), distances[end_id]


def load_campus_from_csv(filename: str | Path) -> Campus:
    """Load campus buildings/pathways from a source,target,weight CSV file."""
    campus = Campus()

    with Path(filename).open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        required_columns = {"source", "target", "weight"}
        if not reader.fieldnames or not required_columns.issubset(set(reader.fieldnames)):
            raise ValueError("CSV must include columns: source,target,weight")

        for row in reader:
            source = (row.get("source") or "").strip()
            target = (row.get("target") or "").strip()
            if not source or not target:
                continue

            try:
                weight = int((row.get("weight") or "").strip())
            except ValueError:
                weight = 0

            if source not in campus.buildings:
                campus.add_building(Building(source, source, (0.0, 0.0)))
            if target not in campus.buildings:
                campus.add_building(Building(target, target, (0.0, 0.0)))

            campus.add_pathway(source, target, weight)

    return campus


def load_graph(filename: str | Path) -> Graph:
    """Backward-compatible helper that returns only adjacency lists."""
    return load_campus_from_csv(filename).pathways


def dijkstra(graph: Graph, start_node: str) -> tuple[dict[str, int], dict[str, str | None]]:
    """Run Dijkstra from one source node over a weighted graph."""
    if start_node not in graph:
        raise ValueError(f"Unknown starting node: {start_node}")

    distances = {node: float("inf") for node in graph}
    predecessors: dict[str, str | None] = {node: None for node in graph}
    distances[start_node] = 0

    queue: list[tuple[int, str]] = [(0, start_node)]
    while queue:
        current_dist, node = heapq.heappop(queue)
        if current_dist > distances[node]:
            continue

        for neighbor, weight in graph[node]:
            new_dist = current_dist + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                predecessors[neighbor] = node
                heapq.heappush(queue, (new_dist, neighbor))

    return distances, predecessors


def get_path(predecessors: dict[str, str | None], target_node: str) -> list[str]:
    """Rebuild the path to target by following predecessor links."""
    path: list[str] = []
    current: str | None = target_node
    while current is not None:
        path.append(current)
        current = predecessors.get(current)
    path.reverse()
    return path


def shortest_path_from_csv(
    filename: str | Path,
    start_node: str,
    end_node: str,
) -> tuple[list[str], int]:
    """Load graph from CSV and return shortest path + total travel time."""
    campus = load_campus_from_csv(filename)
    return campus.shortest_path(start_node, end_node)


def main() -> None:
    """Simple CLI runner for manual testing."""
    start = input("Enter the starting node: ").strip()
    end = input("Enter the destination node: ").strip()

    path, total_time = shortest_path_from_csv("vals.csv", start, end)

    print(f"Shortest path from {start} to {end}:")
    print(f"Destination: {end}")
    print(f"Total Time: {total_time} min")
    print(f"Route: {' -> '.join(path)}")


if __name__ == "__main__":
    main()
