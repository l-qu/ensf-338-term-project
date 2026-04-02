# Temporary file with Room, Building, and Campus classes so the CLI can be written and tested.
# Once we integrate our code with the other parts and actually have a main file, we can delete this.

from event_booking import RoomBookingIndex

# capacity and room_type removed: unnecessary for testing event booking
class Room:
    def __init__(self, room_id: str):
        self.room_id    = room_id               # e.g. "ICT-121"
        self.bookings   = RoomBookingIndex()    # RoomBookingIndex object to store/manage bookings

# name and location removed: unnecessary for testing event booking
class Building:
    def __init__(self, building_id: str):
        self.building_id    = building_id       # e.g. "ICT"
        self.rooms          = {}                # room_id -> Room

# pathways removed: unnecessary for testing event booking
class Campus:
    def __init__(self):
        self.buildings = {}     # building_id -> Building