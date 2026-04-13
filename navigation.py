"""
Stack-based route histroy and navigation undo.
    - Maintains a navigation history for each user session
    - Allows the user to undo their last navigation query and return to the previous origin.
    - Supports 10 levels of undo within a single session.
"""
class Route:
    """
    Represents a navigation route.

    Parameters:
        source (str): starting building
        destination (str): destination building
        path (list[str]): list of buildings in route
        cost (int): total travel time
    """

    def __init__(self, source: str, destination: str, path: list[str], cost: int) -> None:
        self.source: str = source
        self.destination: str = destination
        self.path: list[str] = path
        self.cost: int = cost

    def __str__(self) -> str:
        return (
            "Route: " + self.source + " -> " + self.destination +
            " | Path: " + " -> ".join(self.path) +
            " | Cost: " + str(self.cost)
        )


class Stack:
    """
    Simple stack implementation using a Python list.
    """
    def __init__(self, capacity: int = 10) -> None:
        self.items: list[Route] = []
        self.capacity: int = capacity

    def push(self, item: Route) -> None:
        """
        Adds item to top of stack.
        Removes oldest item if capacity is exceeded.
        """
        if len(self.items) >= self.capacity:
            self.items.pop(0)
        self.items.append(item)

    def pop(self) -> Route | None:
        """
        Removes and returns top item.
        Returns None if empty.
        """
        if self.is_empty():
            return None
        return self.items.pop()

    def peek(self) -> Route | None:
        """
        Returns top item without removing it.
        """
        if self.is_empty():
            return None
        return self.items[-1]

    def is_empty(self) -> bool:
        return len(self.items) == 0

    def size(self) -> int:
        return len(self.items)


class NavigationSession:
    """
    Manages navigation and undo history.
    """

    def __init__(self, campus: object) -> None:
        """
        Parameters:
            campus: Campus object (from dijkstra.py)
        """
        self.campus: object = campus
        self.history: Stack = Stack(10)
        self.current_route: Route | None = None

    def navigate(self, source: str, destination: str) -> Route:
        """
        Computes shortest path and updates current route.

        Parameters:
            source (str)
            destination (str)

        Returns:
            Route
        """
        path, cost = self.campus.shortest_path(source, destination)

        new_route = Route(source, destination, path, cost)

        if self.current_route is not None:
            self.history.push(self.current_route)

        self.current_route = new_route
        return new_route

    def navigation(self, source: str, destination: str) -> Route:
        return self.navigate(source, destination)

    def undo(self) -> Route | None:
        """
        Restores previous route.

        Returns:
            Route or None if no history
        """
        previous = self.history.pop()

        if previous is None:
            return None

        self.current_route = previous
        return self.current_route

    def get_current_route(self) -> Route | None:
        return self.current_route

    def can_undo(self) -> bool:
        return not self.history.is_empty()