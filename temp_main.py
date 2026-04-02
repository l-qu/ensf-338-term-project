# Temporary main class to test the booking_menu CLI from event_booking_cli.py.
# We can delete this file once we have an actual main with a populated Campus.

from temp_map_classes import Room, Building, Campus
from event_booking_cli import booking_menu

# hardcoded test values
# I know this looks awful but it is only temporary
room121 = Room("ICT-121")
room319 = Room("ICT-319")
room024 = Room("ENG-024")
room101 = Room("ENG-101")
ict = Building("ICT")
eng = Building("ENG")
ict.rooms[room121.room_id] = room121
ict.rooms[room319.room_id] = room319
eng.rooms[room024.room_id] = room024
eng.rooms[room101.room_id] = room101
ucalgary = Campus()
ucalgary.buildings[ict.building_id] = ict
ucalgary.buildings[eng.building_id] = eng

booking_menu(ucalgary)