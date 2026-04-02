class RouteResult:
    """
    represents a navigation route

    attributes:
        source(str): starting building
        destination(str): destination building
        path(list[str]): sequence of buildings along the route
        cost(int): total travel time or distance
    """
    def __init__(self, source: str, destination: str, path: list[str], cost: int) -> None:
        self.source = source
        self.destination = destination
        self.path = path
        self.cost = cost

class NavigationSession:
    def __init__(self, campus: "Campus", max_undo: int = 10) -> None:
        self.campus = campus
        self.history = []
        self.current_route = RouteResult | None = None 
        self.max_undo = max_undo

    def navigate(self, source: str, destination: str) -> RouteResult:
        path, total_cost = self.campus.shortest_path(source, destination)
        new_route = RouteResult(source, destination, path, total_cost)

        if self.current_route is not None:
            self.history.append(self.current_route)
            if len(self.history) > self.max_undo:
                self.history.pop(0)

        self.current_route = new_route
        return new_route

    def undo(self) -> RouteResult | None:
        if not self.history:
            return None
        self.current_route = self.history.pop()
        return self.current_route