# ensf-338-term-project

GitHub Link: https://github.com/l-qu/ensf-338-term-project

Group Members:

- Noor Ali (30089446)
- Lindsey Quong (30245714)
- Gianna Kong (30241947)
- Chloe Khoo (30247640)
- Javier Dal Monte Casoni (30254262)
- Omar Al-Mahfoodh (30257072)
- Sharar Masud (30205753)

### First time setup

#### Windows:

```
setup_env.bat
python tui_app.py
```

#### macOS/Linux:

```
chmod +x setup_env.sh
./setup_env.sh
python tui_app.py
```

### Running after setup

#### Windows:

```
.venv\Scripts\activate
python tui_app.py
```

#### macOS/Linux:

```
source .venv/bin/activate
python tui_app.py
```

### Reproducing demo scenarios

#### Shortest path query:

1. In the 'Navigation' tab select:
   - Start: 'Administration'
   - End: 'Student Union'
2. Observe total time and shortest path displayed on top

#### Undo navigation:

1. In the 'Navigation' tab, first select:
   - Start: 'Administration'
   - End: 'Student Union'
2. Then change the route to:
   - Start: 'Library'
   - End: 'ICT'
3. Click 'Undo Route'
4. Observe that the route returns to 'Administration -> Student Union'

#### Booking range query:

1. Navigate to the 'Bookings' tab.
2. Enter the start date (YYYY-MM-DD) and start time (HH:MM) that will be used as the beginning of the range for the query. In the demo, this was 2026-04-15 and 12:00.
3. Enter the end date (YYYY-MM-DD) and end time (HH:MM) that will be used as the end of the range for the query. In the demo, this was 2026-04-15 and 15:00.
4. Click "View Bookings in Range".
5. All bookings within the given range should be displayed, grouped by the room they are occuring in. Note that the seeded bookings may be different when you run the app, so this may not produce the same result as the demo screenshots. If it returns "No bookings found", try adding a booking first, or query closer to the current date.

#### Priority queue demo:

1. Navigate to the 'Service Queue' tab
2. Enter each of the following description and priority pairs in 'Describe issue...' and 'Priority' fields and click 'Add Request'
   - 'the wifi is down' : STANDARD
   - 'fire alarm' : EMERGENCY
   - 'broken projector' : STANDARD
   - 'move tables' : LOW
   - 'something very bad' : EMERGENCY
3. Click 'Process Next' to process each request in order

#### Fast lookup demo:

1. Navigate to the 'Information Lookup' tab.
2. Enter new building
   - Building ID: KINES
   - Building Name: Kineseology
3. Switch the lookup mode to 'Search' from 'List All' and look up KINES
4. Try to look up MATH (will not exist)
5. Switch to the 'Rooms' menu form 'Buildings'
6. Enter new room
   - Choose building: Kineseology (KINES)
   - Room ID: KINES-123
   - Room Capacity: 100
   - Room Type: Lab
7. Make sure the 'Search' mode is on and search for KINES-123
8. Search for KINES-1234 (will not exist)

#### Request pipeline demo:

1. Run `python request_processing_demo.py`
