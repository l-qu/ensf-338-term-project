from collections import deque
class Route:
    """
    represents a navigation route

    parameters:
        source(str): source building
        destination(str): destination building
        path(list[str]): sequence of buildings along the route
        cost(int): total travel time or distance

    returns:
        Route: an instance of the Route class containing the navigation details
    """
    def __init__(self, source: str, destination: str, path: list[str], cost: int) -> None:
        self.source = source
        self.destination = destination
        self.path = path
        self.cost = cost
class NavigationSession:
    """
    manages navigation sessions, allowing users to navigate between buildings and undo previous navigations

    parameters:
        campus(Campus): the campus graph for navigation

    returns:
        NavigationSession: an instance of the NavigationSession class to manage navigation and undo functionality
    """
    def __init__(self, campus: "Campus") -> None:
        MAX_UNDO = 10
        self.campus = campus
        self.history = deque()
        self.current_route: Route | None = None
        self.max_undo = MAX_UNDO

    """
    calculates the shortest route from source to destination, updates the current route, and manages 
    navigation history for undo functionality

    parameters:
        source(str): the starting building
        destination(str): the target building
    
    returns:
        Route: an instance of the Route class containing the navigation details for the new route
    """
    def navigation(self, source: str, destination: str) -> Route:
        path, total_cost = self.campus.shortest_path(source, destination) # need a shortest path method in Campus Map or class ?
        new_route = Route(source, destination, path, total_cost)

        if self.current_route is not None:
            self.history.append(self.current_route)
            if len(self.history) > self.max_undo:
                self.history.popleft()

        self.current_route = new_route
        return new_route

    """
    undoes the last navigation action by reverting to the previous route in the history
    
    returns:
        Route | None: the previous route if available, or None if there is no history to undo
    """
    def undo(self) -> Route | None:
        if not self.history:
            return None
        self.current_route = self.history.pop()
        return self.current_route   