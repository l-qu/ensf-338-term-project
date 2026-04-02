import csv
from pathlib import Path

from textual import events, on
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Footer, Header, RichLog, Select, Static


def load_map_data(csv_path: Path) -> tuple[list[str], list[tuple[str, str, int]], str | None]:
    """\
    @brief Load map node/edge metadata from the CSV input file.

    @param csv_path
        Filesystem path to the CSV file expected to include the columns:
        source,target,weight.

    @details Description:
        Reads each row and normalizes values (trimmed node names, integer weight).
        Nodes are collected into a unique set, then sorted for deterministic dropdown
        ordering in the TUI. Edges are preserved in file order for display.

    @details Expectations:
        1. The file exists and is readable.
        2. CSV header includes source,target,weight.
        3. Weight values are ideally numeric; non-numeric values are converted to 0
           so the TUI remains resilient and still displays data.

    @return tuple[list[str], list[tuple[str, str, int]], str | None]
        Returns (nodes, edges, load_error):
        - nodes: Sorted unique node list for Select options.
        - edges: Parsed edge tuples as (source, target, weight).
        - load_error: Human-readable error string on failure, else None.
    """
    if not csv_path.exists():
        return [], [], f"CSV file not found: {csv_path.name}"

    nodes: set[str] = set()
    edges: list[tuple[str, str, int]] = []

    try:
        with csv_path.open("r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            required_columns = {"source", "target", "weight"}
            if not reader.fieldnames or not required_columns.issubset(set(reader.fieldnames)):
                return [], [], "vals.csv must include columns: source,target,weight"


            for row in reader:
                source = (row.get("source") or "").strip()
                target = (row.get("target") or "").strip()
                weight_raw = (row.get("weight") or "").strip()
                if not source or not target:
                    continue

                try:
                    weight = int(weight_raw)
                except ValueError:
                    weight = 0

                nodes.update((source, target))
                edges.append((source, target, weight))

    except OSError as exc:
        return [], [], f"Error reading vals.csv: {exc}"

    return sorted(nodes), edges, None


class CampusMapApp(App):
    """\
    @brief Textual-based campus navigation TUI.

    @details Expectations:
        1. styles.css must be in the project root.
        2. vals.csv must be located beside this module.
        3. Textual and Rich must be installed.
    """

    CSS_PATH = "styles.css"
    BINDINGS = [("q", "quit_app", "Quit")]

    def __init__(self) -> None:
        """\
        @brief Initialize app state and preload map data.

        @details Description:
            Must resolve vals.csv path relative to this file and execute load_map_data().

        @return None
        """
        super().__init__()
        csv_path = Path(__file__).with_name("vals.csv")
        self.nodes, self.edges, self.load_error = load_map_data(csv_path)

    def compose(self) -> ComposeResult:
        """\
        @brief Build the static widget tree for the TUI.

        @details Description:
            Must yield Header, Footer, Select dropdowns, and a RichLog panel.

        @return ComposeResult
        """
        yield Header()
        with Vertical():
            yield Static("Select a starting and ending node from the dropdowns.")
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
            yield RichLog(id="map_display", highlight=True, markup=True)
        yield Footer()

    def on_mount(self) -> None:
        """\
        @brief Render the initial map panel on startup.

        @details Description:
            Must trigger the first display paint so the UI is immediately populated.

        @return None
        """
        self.refresh_display()
    @on(Select.Changed, "#start_node")
    @on(Select.Changed, "#end_node")

    def on_select_changed(self, event: Select.Changed) -> None:
        """\
        @brief React to dropdown selection changes.

        @param event Textual Select.Changed event payload.

        @details Description:
            Must force a display refresh when the user alters either dropdown.

        @return None
        """
        _ = event
        self.refresh_display()

    def refresh_display(self) -> None:
        """\
        @brief Repaint the map/results panel using current state and selections.

        @details Description:
            Must clear the RichLog.
            Must write load errors if present.
            Must print available nodes and edges.
            Must display the selected route if both dropdowns have values.

        @return None
        """
        start_select = self.query_one("#start_node", Select)
        end_select = self.query_one("#end_node", Select)
        display = self.query_one("#map_display", RichLog)

        start_node = start_select.value if start_select.value != Select.BLANK else None
        end_node = end_select.value if end_select.value != Select.BLANK else None

        display.clear()
        display.write("[bold cyan]Campus Map[/bold cyan]")

        if self.load_error:
            display.write(f"[bold red]{self.load_error}[/bold red]")
            return

        display.write("[green]Available nodes:[/green] " + ", ".join(self.nodes))
        display.write("")
        display.write("[bold]Edges:[/bold]")

        for source, target, weight in self.edges:
            display.write(f"- {source} <-> {target} ({weight} min)")

        display.write("")
        if start_node and end_node:
            display.write(
                f"[bold green]Selected route request:[/bold green] {start_node} -> {end_node}"
            )
            # TODO: Integrate shortest-path logic from backend module once import-safe.
            # TODO: After path is computed, highlight route edges in the map display section.
            display.write("[yellow]TODO: Compute and render shortest path here.[/yellow]")
        else:
            display.write("[yellow]Pick both nodes to request a route.[/yellow]")
            # TODO: Render a richer ASCII/graphical campus map visualization.

    def action_quit_app(self) -> None:
        self.exit()

    def on_key(self, event: events.Key) -> None:
        focused = self.focused
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

        if event.key == "down" and not is_expanded:
            event.stop()


if __name__ == "__main__":
    app = CampusMapApp()
    app.run()