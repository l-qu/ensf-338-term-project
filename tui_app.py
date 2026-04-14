"""Textual TUI for navigation, service queue, and room/event booking."""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from textual import events, on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    RichLog,
    Select,
    Static,
    Tab,
    Tabs,
)

import dijkstra
from booking_seed import ensure_booking_indices, seed_bookings
from dijkstra import Room, load_campus_from_csv
from event_booking import Booking
from service_queue import Priority, PriorityQueue, ServiceRequest
from fast_lookup import FastLookup


def load_map_data(
    csv_path: Path,
) -> tuple[list[str], list[tuple[str, str, int]], str | None]:
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
    """Main application for route selection, service requests, and booking display."""

    CSS_PATH = "styles.css"
    BINDINGS = [("q", "quit_app", "Quit")]

    GRID_ROWS = 5
    GRID_COLS = 6
    CELL_WIDTH = 14
    CELL_HEIGHT = 4

    DEFAULT_KEY_BUILDINGS = {"Library", "ICT", "ENG Block"}

    def __init__(self) -> None:
        """Initialize app state and preload map / booking data."""
        super().__init__()
        self.csv_path = Path(__file__).with_name("vals.csv")
        self.nodes, self.edges, self.load_error = load_map_data(self.csv_path)

        self.service_queue = PriorityQueue()
        self.lookup = FastLookup()
        self.request_counter = 1

        # from dijkstra.py
        self.campus = load_campus_from_csv(self.csv_path)
        self._add_rooms_to_loaded_campus()
        self._rebuild_lookup_from_campus()
        ensure_booking_indices(self.campus)

        try:
            self.seeded_booking_count = seed_bookings(self.campus, total_bookings=105)
            self.booking_seed_error: str | None = None
        except Exception as exc:
            self.seeded_booking_count = 0
            self.booking_seed_error = str(exc)

        # Remember the last displayed booking list so removal can work by number.
        self.last_displayed_bookings: list[Booking] = []
        self.last_displayed_room_id: str | None = None

    def _add_rooms_to_loaded_campus(self) -> None:
        """
        Populate rooms for buildings that already exist on the CSV-loaded campus.

        vals.csv creates buildings/pathways but does not define rooms, so we need
        a small amount of room setup somewhere. The setup is tied to the
        shared Campus/Building/Room model from dijkstra.py.
        """
        room_specs_by_building: dict[str, list[tuple[str, int, str]]] = {
            "Library": [
                ("101", 120, "Lecture Hall"),
                ("201", 40, "Study Room"),
                ("301", 25, "Seminar Room"),
            ],
            "Science A": [
                ("110", 100, "Lecture Hall"),
                ("210", 36, "Lab"),
                ("310", 24, "Seminar Room"),
            ],
            "ICT": [
                ("121", 120, "Lecture Hall"),
                ("218", 45, "Lab"),
                ("319", 40, "Lab"),
                ("420", 30, "Seminar Room"),
            ],
            "ENG Block": [
                ("024", 80, "Classroom"),
                ("101", 90, "Classroom"),
                ("201", 45, "Lab"),
                ("303", 35, "Seminar Room"),
            ],
            "Gym": [
                ("A1", 150, "Multipurpose Room"),
                ("201", 30, "Meeting Room"),
            ],
            "Student Union": [
                ("104", 60, "Club Room"),
                ("212", 80, "Event Space"),
                ("315", 35, "Meeting Room"),
            ],
            "MFH": [
                ("160", 120, "Lecture Hall"),
                ("250", 28, "Seminar Room"),
            ],
            "Parkade": [
                ("101", 20, "Office"),
            ],
            "Residence": [
                ("L1", 30, "Lounge"),
                ("205", 25, "Study Room"),
            ],
        }

        for building_id, room_specs in room_specs_by_building.items():
            building = self.campus.buildings.get(building_id)
            if building is None:
                continue

            for room_suffix, capacity, room_type in room_specs:
                room_id = f"{building_id}-{room_suffix}"
                if room_id not in building.rooms:
                    building.add_room(Room(room_id, capacity, room_type))

    def _rebuild_lookup_from_campus(self) -> None:
        """Build fast lookup indexes from the shared campus model."""
        self.lookup = FastLookup()

        for building in self.campus.buildings.values():
            self.lookup.add_building(building)
            for room in building.rooms.values():
                self.lookup.add_room(building.building_id, room)

    def compose(self) -> ComposeResult:
        """Build widgets shown in the TUI."""
        yield Header()

        yield Tabs(
            Tab("Navigation", id="tab_nav"),
            Tab("Service Queue", id="tab_service"),
            Tab("Information Lookup", id ="tab_lookup"),
            Tab("Bookings", id="tab_bookings"),
            id="tabs",
        )
        with Vertical(id = "lookup_view"):
            yield Static("[bold]Building and Room Information[/bold]")
            yield Select(
                options = [
                    ("Buildings", "buildings"),
                    ("Rooms", "rooms"),
                ],
                prompt = "Choose what to display",
                id = "info_mode",
                allow_blank = False,
                value = "buildings",
            )

            yield RichLog(id = "lookup_log", highlight = True, markup = True)

            yield Static("")
            yield Static("[bold cyan]Add Room[/bold cyan]")
            yield Select(
                options = [],
                prompt = "Choose building for new room",
                id = "add_room_building_id",
                allow_blank = True,
            )
            yield Input(placeholder="Room ID (ex. ICT-212)", id = "add_room_id")
            yield Input(placeholder="Room capacity (ex. 100)", id = "add_room_capacity")
            yield Input(placeholder="Room type (ex. Lecture hall, Classroom, Lab)", id = "add_room_type")
            yield Button("Add Room to Building", id = "add_room", variant = "success")

            yield Static("")
            yield Static("[bold red]Delete Room[/bold red]")
            yield Select(
                options = [],
                prompt = "Select building",
                id = "delete_room_building",
                allow_blank = True,
            )
            yield Select(
                options = [],
                prompt = "Select room",
                id = "delete_room_id",
                allow_blank = True,
            )
            yield Button("Delete Room", id = "delete_room", variant = "error")

        with VerticalScroll(id="service_view"):
            yield Static("[bold]Service Request Queue[/bold]")
            yield Input(placeholder="Describe issue...", id="service_desc")
            yield Select(
                options=[
                    ("EMERGENCY", Priority.EMERGENCY),
                    ("STANDARD", Priority.STANDARD),
                    ("LOW", Priority.LOW),
                ],
                prompt="Priority",
                id="service_priority",
            )
            yield Button("Add Request", id="add_request", variant="primary")
            yield Button("Process Next", id="process_request")
            yield RichLog(id="service_log", highlight=True, markup=True)

        with Vertical(id="nav_view"):
            yield Static("Select a starting and ending node from the dropdowns.")
            yield Static("[green]Available nodes:[/green] " + ", ".join(self.nodes), id="available_nodes",)
            yield Static(
                "[yellow]Shortest Path:[/yellow] pick both nodes", id="path_summary"
            )
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

        with VerticalScroll(id="bookings_view"):
            yield Static("[bold]Room and Event Booking[/bold]")
            yield Static(
                "[dim]Example room IDs: ICT-121, ENG Block-101, Library-201[/dim]"
            )

            if self.booking_seed_error:
                yield Static(
                    f"[red]Booking seed error:[/red] {self.booking_seed_error}",
                    id="booking_seed_status",
                )
            else:
                yield Static(
                    f"[green]Seeded bookings:[/green] {self.seeded_booking_count}",
                    id="booking_seed_status",
                )

            yield Input(placeholder="Event title", id="booking_title")
            yield Input(placeholder="Organiser", id="booking_organiser")
            yield Input(
                placeholder="Room ID (e.g. ICT-121 or ENG Block-101)",
                id="booking_room",
            )
            yield Input(placeholder="Date (YYYY-MM-DD)", id="booking_date")
            yield Input(placeholder="Start time (HH:MM)", id="booking_start")
            yield Input(placeholder="End time (HH:MM)", id="booking_end")
            yield Input(placeholder="Booking number to remove", id="remove_booking_id")

            yield Button("Add Booking", id="add_booking", variant="primary")
            yield Button("Remove Booking", id="remove_booking", variant="error")
            yield Button("View Bookings on Day", id="view_bookings_day")
            yield Button("View Bookings in Range", id="view_bookings_range")
            yield Button("Next Upcoming Event", id="view_next_booking")
            yield Button("Show All Bookings for Room", id="view_all_bookings_room")
            yield Button("List Rooms", id="list_rooms")

            yield RichLog(id="booking_log", highlight=True, markup=True)

        yield Footer()

    def on_mount(self) -> None:
        """Render initial state and set initial tab visibility/focus."""
        self.refresh_node_selects()
        self.refresh_building_select()
        self.refresh_display()
        self.refresh_delete_building_select()

        self.query_one("#nav_view").display = True
        self.query_one("#service_view").display = False
        self.query_one("#lookup_view").display = False
        self.query_one("#bookings_view").display = False

        self.refresh_info_view()
        self.query_one("#start_node", Select).focus()

    @on(Select.Changed, "#start_node")
    @on(Select.Changed, "#end_node")
    def on_select_changed(self, _event: Select.Changed) -> None:
        """Refresh route output whenever either dropdown changes."""
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
            display.write(
                "[white on red] key building [/]: " + ", ".join(sorted(key_buildings))
            )
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
            if isinstance(focused, Select) and bool(
                getattr(focused, "expanded", False)
            ):
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
        """Show only the active tab content."""
        nav = self.query_one("#nav_view")
        service = self.query_one("#service_view")
        lookup = self.query_one("#lookup_view")
        bookings = self.query_one("#bookings_view")

        nav.display = event.tab.id == "tab_nav"
        service.display = event.tab.id == "tab_service"
        lookup.display = event.tab.id == "tab_lookup"
        bookings.display = event.tab.id == "tab_bookings"

    @on(Button.Pressed, "#add_request")
    def add_request(self) -> None:
        """Add a service request to the priority queue."""
        desc = self.query_one("#service_desc", Input).value
        priority = self.query_one("#service_priority", Select).value
        log = self.query_one("#service_log", RichLog)

        if not desc:
            log.write("[red]Error: Description is required[/red]")
            return
        if priority is None or str(priority) == "Select.NULL":
            log.write("[red]Error: Please select a priority[/red]")
            return

        request = ServiceRequest(
            request_id=self.request_counter,
            description=desc,
            priority=int(priority),
        )
        self.service_queue.enqueue(request)
        self.request_counter += 1
        log.write(f"Enqueued: {request.display_request()}")

    @on(Button.Pressed, "#process_request")
    def process_request(self) -> None:
        """Process the highest-priority service request."""
        req = self.service_queue.dequeue()
        log = self.query_one("#service_log", RichLog)

        if not req:
            log.write("[yellow]No requests in queue[/yellow]")
            return

        log.write(f"[green]Processing:[/green] {req.display_request()}")

    # -------------------------------------------------------------------------
    # Booking helpers
    # -------------------------------------------------------------------------

    def _booking_log(self) -> RichLog:
        """Convenience accessor for the booking log."""
        return self.query_one("#booking_log", RichLog)

    def _get_room_by_id(self, room_id: str):
        """Look up a room object by full room ID."""
        normalized = room_id.strip()
        if not normalized:
            return None

        for building in self.campus.buildings.values():
            if normalized in building.rooms:
                return building.rooms[normalized]

        return None

    def _parse_date(self, value: str):
        """Parse YYYY-MM-DD into a date."""
        return datetime.strptime(value.strip(), "%Y-%m-%d").date()

    def _parse_time(self, value: str):
        """Parse HH:MM into a time and enforce 30-minute increments."""
        parsed = datetime.strptime(value.strip(), "%H:%M").time()
        if parsed.minute not in (0, 30):
            raise ValueError("Time must end in :00 or :30")
        return parsed

    def _build_booking_datetimes(self) -> tuple[datetime.date, datetime, datetime]:
        """Build same-day start/end datetimes from the booking inputs."""
        booking_date = self._parse_date(self.query_one("#booking_date", Input).value)
        start_t = self._parse_time(self.query_one("#booking_start", Input).value)
        end_t = self._parse_time(self.query_one("#booking_end", Input).value)

        start_dt = datetime.combine(booking_date, start_t)
        end_dt = datetime.combine(booking_date, end_t)

        if end_dt <= start_dt:
            raise ValueError("End time must be after start time")

        return booking_date, start_dt, end_dt

    def _write_booking_list(
        self, heading: str, room_id: str, bookings: list[Booking]
    ) -> None:
        """Write a numbered booking list to the log and remember it for removal."""
        log = self._booking_log()
        log.clear()
        log.write(f"[bold]{heading}[/bold]")

        self.last_displayed_room_id = room_id
        self.last_displayed_bookings = list(bookings)

        if not bookings:
            log.write("[yellow]No bookings found.[/yellow]")
            return

        for i, booking in enumerate(bookings, start=1):
            log.write(
                f"{i}. "
                f"{booking.start_time.strftime('%d %b %Y %H:%M')} - "
                f"{booking.end_time.strftime('%H:%M')} | "
                f"{booking.title} | {booking.organiser}"
            )

    def _all_rooms(self) -> list:
        """Return every room in the campus."""
        rooms = []
        for building in self.campus.buildings.values():
            rooms.extend(building.rooms.values())
        return rooms

    # -------------------------------------------------------------------------
    # Booking actions
    # -------------------------------------------------------------------------

    @on(Button.Pressed, "#add_booking")
    def add_booking_pressed(self) -> None:
        """Add a new booking to a room."""
        log = self._booking_log()

        try:
            title = self.query_one("#booking_title", Input).value.strip()
            organiser = self.query_one("#booking_organiser", Input).value.strip()
            room_id = self.query_one("#booking_room", Input).value.strip()

            if not title:
                raise ValueError("Event title is required")
            if not organiser:
                raise ValueError("Organiser is required")
            if not room_id:
                raise ValueError("Room ID is required")

            room = self._get_room_by_id(room_id)
            if room is None:
                raise ValueError(f"Room not found: {room_id}")

            _, start_dt, end_dt = self._build_booking_datetimes()

            booking = Booking(
                start_time=start_dt,
                end_time=end_dt,
                title=title,
                organiser=organiser,
            )

            log.clear()
            if room.bookings.add_booking(booking):
                log.write(f"[green]Booked successfully in {room.room_id}[/green]")
                log.write(str(booking))
            else:
                log.write(
                    "[red]Booking rejected: overlaps an existing booking or has invalid times.[/red]"
                )

        except ValueError as exc:
            log.clear()
            log.write(f"[red]{exc}[/red]")

    @on(Button.Pressed, "#remove_booking")
    def remove_booking_pressed(self) -> None:
        """Remove a booking from the last displayed numbered list."""
        log = self._booking_log()
        log.clear()

        room_id = self.query_one("#booking_room", Input).value.strip()
        booking_number_text = self.query_one("#remove_booking_id", Input).value.strip()

        if not room_id:
            log.write("[red]Room ID is required[/red]")
            return
        if not booking_number_text:
            log.write("[red]Booking number is required[/red]")
            return

        room = self._get_room_by_id(room_id)
        if room is None:
            log.write(f"[red]Room not found: {room_id}[/red]")
            return

        if (
            self.last_displayed_room_id != room.room_id
            or not self.last_displayed_bookings
        ):
            log.write(
                "[yellow]First show bookings for this room, then remove by number from that list.[/yellow]"
            )
            return

        try:
            booking_number = int(booking_number_text)
        except ValueError:
            log.write("[red]Booking number must be an integer[/red]")
            return

        if booking_number < 1 or booking_number > len(self.last_displayed_bookings):
            log.write("[red]Booking number is out of range[/red]")
            return

        booking = self.last_displayed_bookings[booking_number - 1]
        removed = room.bookings.remove_booking(booking.booking_id)

        if removed:
            log.write(
                f"[green]Removed booking #{booking_number} from {room.room_id}[/green]"
            )
            log.write(str(booking))
            self.last_displayed_bookings.pop(booking_number - 1)
        else:
            log.write("[red]Booking removal failed.[/red]")

    @on(Button.Pressed, "#view_bookings_day")
    def view_bookings_day_pressed(self) -> None:
        """Show all bookings for a room on a given day."""
        log = self._booking_log()

        try:
            room_id = self.query_one("#booking_room", Input).value.strip()
            if not room_id:
                raise ValueError("Room ID is required")

            room = self._get_room_by_id(room_id)
            if room is None:
                raise ValueError(f"Room not found: {room_id}")

            target_day = self._parse_date(self.query_one("#booking_date", Input).value)
            bookings = room.bookings.get_events_on_day(target_day)

            self._write_booking_list(
                f"Bookings in {room.room_id} on {target_day}",
                room.room_id,
                bookings,
            )

        except ValueError as exc:
            log.clear()
            log.write(f"[red]{exc}[/red]")

    @on(Button.Pressed, "#view_bookings_range")
    def view_bookings_range_pressed(self) -> None:
        """Show all bookings for a room within the entered same-day time range."""
        log = self._booking_log()

        try:
            room_id = self.query_one("#booking_room", Input).value.strip()
            if not room_id:
                raise ValueError("Room ID is required")

            room = self._get_room_by_id(room_id)
            if room is None:
                raise ValueError(f"Room not found: {room_id}")

            _, start_dt, end_dt = self._build_booking_datetimes()
            bookings = room.bookings.get_bookings_in_range(start_dt, end_dt)

            self._write_booking_list(
                f"Bookings in {room.room_id} between {start_dt} and {end_dt}",
                room.room_id,
                bookings,
            )

        except ValueError as exc:
            log.clear()
            log.write(f"[red]{exc}[/red]")

    @on(Button.Pressed, "#view_next_booking")
    def view_next_booking_pressed(self) -> None:
        """Show the next upcoming booking across the whole campus."""
        log = self._booking_log()
        log.clear()

        now = datetime.now()
        next_event: Booking | None = None
        next_room_id: str | None = None

        for room in self._all_rooms():
            candidate = room.bookings.next_upcoming_event(now)
            if candidate is None:
                continue

            if next_event is None or candidate.start_time < next_event.start_time:
                next_event = candidate
                next_room_id = room.room_id

        if next_event is None:
            log.write("[yellow]No upcoming events found on campus.[/yellow]")
            return

        log.write(f"[bold green]Next upcoming event in {next_room_id}[/bold green]")
        log.write(str(next_event))

    @on(Button.Pressed, "#view_all_bookings_room")
    def view_all_bookings_room_pressed(self) -> None:
        """Show all bookings for the selected room in chronological order."""
        log = self._booking_log()

        try:
            room_id = self.query_one("#booking_room", Input).value.strip()
            if not room_id:
                raise ValueError("Room ID is required")

            room = self._get_room_by_id(room_id)
            if room is None:
                raise ValueError(f"Room not found: {room_id}")

            bookings = room.bookings.all_bookings()
            self._write_booking_list(
                f"All bookings for {room.room_id}",
                room.room_id,
                bookings,
            )

        except ValueError as exc:
            log.clear()
            log.write(f"[red]{exc}[/red]")

    @on(Button.Pressed, "#list_rooms")
    def list_rooms_pressed(self) -> None:
        """List all available rooms on the campus model."""
        log = self._booking_log()
        log.clear()
        log.write("[bold]Available Rooms[/bold]")

        found_any = False
        for building_id in sorted(self.campus.buildings.keys()):
            building = self.campus.buildings[building_id]
            if not building.rooms:
                continue

            found_any = True
            log.write(f"[cyan]{building_id}[/cyan]")
            for room_id in sorted(building.rooms.keys()):
                room = building.rooms[room_id]
                log.write(
                    f"  - {room.room_id} | capacity={room.capacity} | type={room.room_type}"
                )

        if not found_any:
            log.write("[yellow]No rooms are currently configured.[/yellow]")
    
    # -- LOOKUP STUFF --
    def render_buildings(self) -> None:
        """ Display all buildings in the lookup log. """
        log = self.query_one("#lookup_log", RichLog)
        log.clear()
        log.write("[bold cyan]All Buildings[/bold cyan]")
        log.write("")

        buildings = self.lookup.list_buildings()
        if not buildings:
            log.write("[yellow]No buildings available.[/yellow]")
            return

        for building in sorted(buildings, key=lambda b: b.name.lower()):
            room_count = len(building.rooms)

            log.write(
                f"- {building.name} | ID: {building.building_id} | "
                f"Location: {self._node_positions().get(building.name, 'Not placed')} | Rooms: {room_count}"
            )
    
    def refresh_building_select(self) -> None:
        """ Refresh the building dropdown used when adding a room. """
        building_select = self.query_one("#add_room_building_id", Select)

        buildings = sorted(
            self.lookup.list_buildings(),
            key=lambda building: building.name.lower()
        )

        options = [
            (f"{building.name} ({building.building_id})", building.building_id)
            for building in buildings
        ]

        building_select.set_options(options)

    def render_rooms(self) -> None:
        """ Display all rooms in the lookup log. """
        log = self.query_one("#lookup_log", RichLog)
        log.clear()
        log.write("[bold cyan]All Rooms[/bold cyan]\n")

        found_any = False

        for building in sorted(self.campus.buildings.values(), key=lambda b: b.name.lower()):
            for room in sorted(building.rooms.values(), key=lambda r: r.room_id.lower()):
                found_any = True

                booking_count = 0
                if hasattr(room.bookings, "all_bookings"):
                    booking_count = len(room.bookings.all_bookings())

                log.write(
                    f"- {room.room_id} | Building: {building.name} | "
                    f"Capacity: {room.capacity} | Type: {room.room_type} | "
                    f"Bookings: {booking_count}"
                )

        if not found_any:
            log.write("[yellow]No rooms available.[/yellow]")

    def refresh_info_view(self) -> None:
        """ Refresh the information tab based on dropdown selection. """
        mode = self.query_one("#info_mode", Select).value
        if mode == "rooms":
            self.render_rooms()
        else:
            self.render_buildings()
    
    def refresh_node_selects(self) -> None:
        """ Refresh start/end node dropdowns after buildings are added. """
        options = [(node, node) for node in self.nodes]

        self.query_one("#start_node", Select).set_options(options)
        self.query_one("#end_node", Select).set_options(options)
        self.query_one("#available_nodes", Static).update(
            "[green]Available nodes:[/green] " + ", ".join(self.nodes)
        )
    
    def refresh_delete_building_select(self):
        """ Refresh selection after deletion """
        select = self.query_one("#delete_room_building", Select)

        buildings = sorted(
            self.lookup.list_buildings(),
            key=lambda b: b.name.lower()
        )

        options = [
            (f"{b.name} ({b.building_id})", b.building_id)
            for b in buildings
        ]

        select.set_options(options)
    
    @on(Select.Changed, "#info_mode")
    def on_info_mode_changed(self, _event: Select.Changed) -> None:
        self.refresh_info_view()

    @on(Button.Pressed, "#add_room")
    def add_room_to_building(self) -> None:
        """ Adds the room to a building via lookup menu"""
        building_id = self.query_one("#add_room_building_id", Select).value
        room_id = self.query_one("#add_room_id", Input).value.strip()
        capacity_text = self.query_one("#add_room_capacity", Input).value.strip()
        room_type = self.query_one("#add_room_type", Input).value.strip()
        log = self.query_one("#lookup_log", RichLog)

        if not building_id or not room_id or not capacity_text or not room_type:
            log.write("[red]Fill all fields.[/red]")
            return
        try:
            capacity = int(capacity_text)
        except ValueError:
            log.write("[red]Capacity must be integer.[/red]")
            return

        building = self.campus.buildings.get(building_id)
        if building is None:
            log.write("[red]Building not found.[/red]")
            return

        if room_id in building.rooms:
            log.write("[red]Room already exists.[/red]")
            return

        room = Room(room_id, capacity, room_type)
        building.add_room(room)

        self.lookup.add_room(building_id, room)

        log.clear()
        log.write("[green]Room added successfully.[/green]")
        self.refresh_info_view()
    
    @on(Select.Changed, "#info_mode")
    def on_info_mode_changed(self, _event: Select.Changed) -> None:
        self.refresh_info_view()

    @on(Select.Changed, "#delete_room_building")
    def update_delete_room_list(self, event: Select.Changed):
        building_id = event.value
        room_select = self.query_one("#delete_room_id", Select)

        if not building_id:
            room_select.set_options([])
            return

        rooms = self.lookup.list_building_rooms(building_id)

        options = [
            (room.room_id, room.room_id)
            for room in rooms
        ]

        room_select.set_options(options)
    
    @on(Button.Pressed, "#delete_room")
    def delete_room(self):
        """ Delete room completely """
        building_id = self.query_one("#delete_room_building", Select).value
        room_id = self.query_one("#delete_room_id", Select).value
        log = self.query_one("#lookup_log", RichLog)

        if not building_id or not room_id:
            log.write("[red]Select building and room.[/red]")
            return

        building = self.campus.buildings.get(building_id)
        if building is None or room_id not in building.rooms:
            log.write("[red]Room not found.[/red]")
            return
        
        del building.rooms[room_id]
        self.lookup.delete_room_id(building_id, room_id)

        log.clear()
        log.write(f"[green]Deleted {room_id}[/green]")

        self.refresh_info_view()


if __name__ == "__main__":
    CampusMapApp().run()
