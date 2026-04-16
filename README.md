# ensf-338-term-project

GitHub Link: https://github.com/l-qu/ensf-338-term-project

Group Members: 
- Noor Ali (30089446)
- Lindsey Quong (30245714)
- Gianna Kong (30241947)
- Chloe Khoo (30247640)
- Javier Dal Monte Casoni (########)
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
1. Select "Administration" as the starting node
2. Select "Student Union" as ending node
4. Observe shortest path and total time displayed at top

#### Undo navigation:

#### Booking range query:

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

#### Request pipeline demo:
1. Run ```python request_processing_demo.py```
