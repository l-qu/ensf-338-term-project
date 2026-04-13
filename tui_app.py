"""Textual TUI for selecting nodes and viewing shortest-path results."""

from __future__ import annotations

import csv
from pathlib import Path

from textual import events, on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, RichLog, Select, Static, Tabs, Tab, Button, Input
from service_queue import PriorityQueue, ServiceRequest, Priority

import dijkstra


def load_map_data(csv_path: Path) -> tuple[list[str], list[tuple[str, str, int]], str | None]:
    """Load node and edge data from vals.csv."""
    if not csv_path.exists():
        return [], [], f"CSV file not found: {csv_path.name}"

    nodes: set[str] = set()
    edges: list[tuple[str, str, int]] = []

    try:
        with csv_path.open("r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            required = {"source", "target", "weight"}
            if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
                return [], [], "vals.csv must include columns: source,target,weight"

            for row in reader:
                source = (row.get("source") or "").strip()
                target = (row.get("target") or "").strip()
                if not source or not target:
                    continue

                try:
                    weight = int((row.get("weight") or "").strip())
                except ValueError:
                    weight = 0

                nodes.update((source, target))
                edges.append((source, target, weight))
    except OSError as exc:
        return [], [], f"Error reading vals.csv: {exc}"

    return sorted(nodes), edges, None


class CampusMapApp(App):
    """Main application for route selection and map display."""

    CSS_PATH = "styles.css"
    BINDINGS = [("q", "quit_app", "Quit")]

    GRID_ROWS = 5
    GRID_COLS = 6
    CELL_WIDTH = 14
    CELL_HEIGHT = 4

    DEFAULT_KEY_BUILDINGS = {"Library", "ICT", "ENG Block"}

    def __init__(self) -> None:
        """Initialize app state and preload map data."""
        super().__init__()
        self.csv_path = Path(__file__).with_name("vals.csv")
        self.nodes, self.edges, self.load_error = load_map_data(self.csv_path)
        self.service_queue = PriorityQueue()
        self.request_counter = 1

    def compose(self) -> ComposeResult:
        """Build widgets shown in the TUI."""
        yield Header()

        yield Tabs(
            Tab("Navigation", id="tab_nav"),
            Tab("Service Queue", id="tab_service"),
            id="tabs"
        )

        with Vertical(id="service_view"):
            yield Static("[bold]Service Request Queue[/bold]")
            yield Input(placeholder="Describe issue...", id="service_desc")
            yield Select(
                options=[("EMERGENCY", Priority.EMERGENCY), ("STANDARD", Priority.STANDARD), ("LOW", Priority.LOW),],
                prompt="Priority",
                id="service_priority",
            )
            yield Button("Add Request", id="add_request", variant="primary")
            yield Button("Process Next", id="process_request")
            yield RichLog(id="service_log", highlight=True, markup=True)
    
        with Vertical(id="nav_view"):
            yield Static("Select a starting and ending node from the dropdowns.")
            yield Static("[green]Available nodes:[/green] " + ", ".join(self.nodes))
            yield Static("[yellow]Shortest Path:[/yellow] pick both nodes", id="path_summary")
            yield RichLog(id="map_display", highlight=True, markup=True)

        with Horizontal(id="selectors_row"):
            yield Select(
                options=[(node, node) for node in self.nodes],
                prompt="Starting Node",
                id="start_node",
                allow_blank=True,
            )
            yield Select(
                options=[(node, node) for node in self.nodes],
                prompt="Ending Node",
                id="end_node",
                allow_blank=True,
            )

        yield Footer()

    def on_mount(self) -> None:
        """Render initial state and focus start select."""
        self.refresh_display()
        self.query_one("#start_node", Select).focus()

    @on(Select.Changed, "#start_node")
    @on(Select.Changed, "#end_node")
    def on_select_changed(self, _event: Select.Changed) -> None:
        """Refresh output whenever either dropdown changes."""
        self.refresh_display()

    @on(events.MouseDown, "#map_display")
    def on_map_mouse_down(self, event: events.MouseDown) -> None:
        """Keep map panel non-interactive and return focus to inputs."""
        event.stop()
        self.query_one("#start_node", Select).focus()

    def _put_text(self, canvas: list[list[str]], x: int, y: int, text: str) -> None:
        """Write text into a 2D char canvas."""
        if y < 0 or y >= len(canvas):
            return
        for index, char in enumerate(text):
            x_pos = x + index
            if 0 <= x_pos < len(canvas[0]):
                canvas[y][x_pos] = char

    def _draw_line(
        self,
        canvas: list[list[str]],
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        line_char: str,
    ) -> None:
        """Draw an approximate straight line between two canvas points."""
        steps = max(abs(x2 - x1), abs(y2 - y1))
        if steps == 0:
            return

        for step in range(1, steps):
            x_pos = round(x1 + (x2 - x1) * (step / steps))
            y_pos = round(y1 + (y2 - y1) * (step / steps))
            if not (0 <= y_pos < len(canvas) and 0 <= x_pos < len(canvas[0])):
                continue

            existing = canvas[y_pos][x_pos]
            if existing == " ":
                canvas[y_pos][x_pos] = line_char
            elif existing != line_char and existing not in "0123456789m":
                canvas[y_pos][x_pos] = "+"

    def _node_positions(self) -> dict[str, tuple[int, int]]:
        """Return fixed grid coordinates for known buildings."""
        positions: dict[str, tuple[int, int]] = {
            "Library": (0, 0),
            "Science A": (0, 2),
            "ICT": (1, 0),
            "ENG Block": (1, 2),
            "Gym": (1, 4),
            "Student Union": (2, 0),
            "MFH": (2, 2),
            "Parkade": (3, 1),
            "Residence": (4, 0),
        }

        occupied = set(positions.values())
        for node in self.nodes:
            if node in positions:
                continue
            for row in range(self.GRID_ROWS):
                for col in range(self.GRID_COLS):
                    if (row, col) not in occupied:
                        positions[node] = (row, col)
                        occupied.add((row, col))
                        break
                else:
                    continue
                break

        return positions

    def _get_key_buildings(self) -> set[str]:
        """Choose key buildings from defaults, or by highest degree as fallback."""
        configured = {name for name in self.DEFAULT_KEY_BUILDINGS if name in self.nodes}
        if configured:
            return configured

        degree: dict[str, int] = {node: 0 for node in self.nodes}
        for source, target, _weight in self.edges:
            degree[source] = degree.get(source, 0) + 1
            degree[target] = degree.get(target, 0) + 1

        ranked = sorted(degree.items(), key=lambda item: (-item[1], item[0]))
        return {name for name, _ in ranked[:3]}

    def _render_grid_map(self, display: RichLog, route_path: list[str]) -> None:
        """Render the 5x6 ASCII-style campus map."""
        width = self.GRID_COLS * self.CELL_WIDTH + 1
        height = self.GRID_ROWS * self.CELL_HEIGHT + 1
        canvas = [[" " for _ in range(width)] for _ in range(height)]

        positions = self._node_positions()
        key_buildings = self._get_key_buildings()
        has_route = bool(route_path)
        route_edges = {
            frozenset((route_path[index], route_path[index + 1]))
            for index in range(len(route_path) - 1)
        }

        for source, target, weight in self.edges:
            if source not in positions or target not in positions:
                continue

            row1, col1 = positions[source]
            row2, col2 = positions[target]
            x1 = col1 * self.CELL_WIDTH + self.CELL_WIDTH // 2
            y1 = row1 * self.CELL_HEIGHT + self.CELL_HEIGHT // 2
            x2 = col2 * self.CELL_WIDTH + self.CELL_WIDTH // 2
            y2 = row2 * self.CELL_HEIGHT + self.CELL_HEIGHT // 2

            if frozenset((source, target)) in route_edges:
                edge_char = "*"
            elif x1 == x2:
                edge_char = "|"
            elif y1 == y2:
                edge_char = "-"
            elif (x2 - x1) * (y2 - y1) > 0:
                edge_char = "\\"
            else:
                edge_char = "/"

            self._draw_line(canvas, x1, y1, x2, y2, edge_char)

            mid_x = (x1 + x2) // 2
            mid_y = (y1 + y2) // 2
            self._put_text(canvas, mid_x - 1, mid_y, f"{weight}m")

        overlays: dict[int, dict[int, tuple[int, str]]] = {}
        for node, (row, col) in positions.items():
            x_center = col * self.CELL_WIDTH + self.CELL_WIDTH // 2
            y_center = row * self.CELL_HEIGHT + self.CELL_HEIGHT // 2

            label_text = f"{node[:12]:^12}"
            start_x = max(0, x_center - 6)
            self._put_text(canvas, start_x, y_center, label_text)

            if node in route_path:
                style = "black on bright_green"
            elif has_route and node in key_buildings:
                style = "white on red"
            else:
                style = "white on grey23"

            overlays.setdefault(y_center, {})[start_x] = (
                len(label_text),
                f"[{style}]{label_text}[/]",
            )

        display.write("[bold]Grid Map (5x6)[/bold]")
        for y_pos, row_chars in enumerate(canvas):
            row_overlays = overlays.get(y_pos, {})
            x_pos = 0
            parts: list[str] = []

            while x_pos < width:
                overlay = row_overlays.get(x_pos)
                if overlay:
                    length, styled = overlay
                    parts.append(styled)
                    x_pos += length
                    continue
                parts.append(row_chars[x_pos])
                x_pos += 1

            line = "".join(parts).rstrip()
            display.write(line if line else " ")

        if has_route:
            display.write("[white on red] key building [/]: " + ", ".join(sorted(key_buildings)))
        else:
            display.write("[white on red] key building [/]: select start/end to show")
        display.write("[white on grey23] support building [/]")
        display.write("[black on bright_green] selected path building [/]")
        display.write("[bold]*[/bold] selected route edge")

    def refresh_display(self) -> None:
        """Redraw route text and map panel."""
        start_select = self.query_one("#start_node", Select)
        end_select = self.query_one("#end_node", Select)
        path_summary = self.query_one("#path_summary", Static)
        display = self.query_one("#map_display", RichLog)

        start_node = start_select.value if start_select.value != Select.BLANK else None
        end_node = end_select.value if end_select.value != Select.BLANK else None

        display.clear()
        display.write("[bold cyan]Campus Map[/bold cyan]")

        if self.load_error:
            display.write(f"[bold red]{self.load_error}[/bold red]")
            return

        display.write("[bold]Edges:[/bold]")
        for source, target, weight in self.edges:
            display.write(f"- {source} <-> {target} ({weight} min)")

        route_path: list[str] = []
        display.write("")

        if start_node and end_node:
            path_summary.update(
                f"[cyan]Shortest Path:[/cyan] request {start_node} -> {end_node}"
            )
            try:
                route_path, total_time = dijkstra.shortest_path_from_csv(
                    self.csv_path,
                    start_node,
                    end_node,
                )
                path_summary.update(
                    "[bold green]Shortest Path:[/bold green] "
                    + " -> ".join(route_path)
                    + f" ([bold]{total_time} min[/bold])"
                )
            except ValueError as exc:
                path_summary.update(f"[bold yellow]Shortest Path:[/bold yellow] {exc}")
                display.write(f"[bold yellow]{exc}[/bold yellow]")
            except OSError as exc:
                path_summary.update(f"[bold red]Shortest Path:[/bold red] {exc}")
                display.write(f"[bold red]Error reading map data: {exc}[/bold red]")
            except Exception as exc:
                path_summary.update(f"[bold red]Shortest Path:[/bold red] {exc}")
                display.write(f"[bold red]Error computing path: {exc}[/bold red]")
        else:
            path_summary.update("[yellow]Shortest Path:[/yellow] pick both nodes")
            display.write("[yellow]Pick both nodes to request a route.[/yellow]")

        display.write("")
        self._render_grid_map(display, route_path)

    def action_quit_app(self) -> None:
        """Quit the app."""
        self.exit()

    def on_key(self, event: events.Key) -> None:
        """Custom keyboard behavior for select widgets."""
        focused = self.focused

        if event.key in {"left", "right"}:
            if isinstance(focused, Select) and bool(getattr(focused, "expanded", False)):
                return
            target_id = "#start_node" if event.key == "left" else "#end_node"
            self.query_one(target_id, Select).focus()
            event.stop()
            return

        if not isinstance(focused, Select):
            return

        is_expanded = bool(getattr(focused, "expanded", False))
        if event.key == "enter" and not is_expanded:
            if hasattr(focused, "action_show_overlay"):
                focused.action_show_overlay()
            elif hasattr(focused, "action_toggle_overlay"):
                focused.action_toggle_overlay()
            elif hasattr(focused, "action_toggle"):
                focused.action_toggle()
            event.stop()

        if event.key in {"down", "up", "space"} and not is_expanded:
            event.stop()

    @on(Tabs.TabActivated)
    def switch_tabs(self, event: Tabs.TabActivated) -> None:
        nav = self.query_one("#nav_view")
        service = self.query_one("#service_view")
        if event.tab.id == "tab_nav":
            nav.display = True
            service.display = False
        else:
            nav.display = False
            service.display = True

    def on_mount(self) -> None:
        self.refresh_display()
        self.query_one("#service_view").display = False

    @on(Button.Pressed, "#add_request")
    def add_request(self) -> None:
        desc = self.query_one("#service_desc", Input).value
        priority = self.query_one("#service_priority", Select).value
        log = self.query_one("#service_log", RichLog)
        if not desc:
            log.write("[red]Error: Description is required[/red]")
            return
        if priority is None or str(priority) == "Select.NULL":
            log.write("[red]Error: Please select a priority[/red]")
            return
        request = ServiceRequest(request_id=self.request_counter,description=desc,priority=int(priority),)
        self.service_queue.enqueue(request)
        self.request_counter += 1
        log.write(f"Enqueued: {request.display_request()}")

    @on(Button.Pressed, "#process_request")
    def process_request(self) -> None:
        req = self.service_queue.dequeue()
        log = self.query_one("#service_log", RichLog)
        if not req:
            log.write("[yellow]No requests in queue[/yellow]")
            return
        log.write(f"[green]Processing:[/green] {req.display_request()}")

if __name__ == "__main__":
    CampusMapApp().run()