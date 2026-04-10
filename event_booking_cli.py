# event_booking_cli.py
from datetime import date, time, datetime
from typing import List, Optional

from event_booking import Booking, RoomBookingIndex
from temp_map_classes import (
    Campus,
    Building,
    Room,
)  # replace with import statement from actual main


def booking_menu(campus: Campus):
    """
    Provides the main CLI to interact with the user.
    User should be able to:
    - Add, remove, and retrieve room bookings by date and time
    - Query all events within a time range
    - Have efficient ordered access to bookings
    """

    while True:
        print("-" * 70)
        print("\nROOM AND EVENT BOOKING:")
        print("\t1. Add booking")
        print("\t2. Remove booking")
        print("\t3. View room bookings")
        print("\t0. Return to main menu")
        print("\nEnter your selection:")

        # valid options are 0, 1, 2, and 3
        choice = get_valid_int(list(range(0, 4)))
        print()

        match choice:
            case 1:
                add_booking_menu(campus)
            case 2:
                remove_booking_menu(campus)
            case 3:
                view_bookings_menu(campus)
                pass
            case _:
                print("Returning to main menu.\n")
                print("-" * 70)
                break


def add_booking_menu(campus: Campus):
    """
    CLI for adding a booking.
    Asks user for building, room, date, start time, end time, and event name and organizer,
    then attempts to add a booking to that room. Prints a message upon success or failure.
    """

    print("-" * 70)

    print(f"\nTo book an event space, please fill out the following fields.\n")

    event = input("Event name: ")
    organizer = input("Organizer: ")
    booking_date = get_valid_date_str("Date (YYYY-MM-DD): ")

    while True:
        start_time = get_valid_time_str("Start time (HH:MM): ")
        end_time = get_valid_time_str("End time (HH:MM): ")

        datetime_start = datetime.strptime(
            booking_date + " " + start_time, "%Y-%m-%d %H:%M"
        )
        datetime_end = datetime.strptime(
            booking_date + " " + end_time, "%Y-%m-%d %H:%M"
        )

        # Valid start and end times if start takes place before end
        if datetime_start < datetime_end:
            break

        print("\tError: start time must take place before end time. Please try again.")

    new_booking = Booking(
        datetime_start, datetime_end, title=event, organiser=organizer
    )

    while True:
        room = get_room(campus)

        # If the user chose to quit, return from the function
        if not room:
            return

        curr_bookings = room.bookings.get_events_on_day(
            datetime.strptime(booking_date, "%Y-%m-%d").date()
        )

        # Check if any of the bookings in the chosen room overlap with the user's booking
        for booking in curr_bookings:
            if new_booking.overlaps(booking):
                print(
                    f"\n! The following room booking in {room.room_id} overlaps with yours: "
                )
                print(f"\t{booking}\n")
                print("Please choose a different room.")
                break
        else:
            # No bookings in the room overlap with the user's booking
            break

    # Add the new booking
    booking_status = room.bookings.add_booking(new_booking)

    if booking_status:
        print("\nBooked successfully!\n")
    else:
        print("\nBooking failed. Something went wrong.\n")


def remove_booking_menu(campus: Campus):
    """
    CLI for removing a booking.
    Asks user for a room and a date, shows bookings on that day, then removes the selected booking.
    """

    print("-" * 70)
    print(f"\nTo remove a booking, please fill out the following fields.\n")

    room = get_room(campus)

    # If the user chose to quit, return from the function
    if not room:
        return

    booking_date = get_valid_date_str("Date (YYYY-MM-DD): ")
    target_day = datetime.strptime(booking_date, "%Y-%m-%d").date()

    # This returns a list of Booking objects.
    curr_bookings = room.bookings.get_events_on_day(target_day)

    if not curr_bookings:
        print(f"\nNo bookings found in {room.room_id} on {booking_date}.\n")
        return

    # Show the user all bookings for that room on that date.
    # Each booking is numbered starting at 1 so the user can pick one.
    print(f"\nBookings in {room.room_id} on {booking_date}:")
    for i in range(len(curr_bookings)):
        print(f"\t{i + 1}. {curr_bookings[i]}")
    print("\t0. Cancel")

    print("\nEnter your selection: ")
    choice = get_valid_int(list(range(0, len(curr_bookings) + 1)))

    if choice == 0:
        print("\nCancelled.\n")
        return

    # This calls the remove_booking() method from RoomBookingIndex.
    selected_booking = curr_bookings[choice - 1]
    removed = room.bookings.remove_booking(selected_booking.booking_id)

    if removed:
        print("\nRemoved successfully!\n")
        print(f"\t{selected_booking}\n")
    else:
        print("\nBooking removal failed. Something went wrong.\n")

def view_bookings_menu(campus: Campus):
    """
    CLI for viewing bookings. This includes options to search for events within a given time
    range, events on a given day, and the next upcoming event.

    This mainly acts as a sub-menu, and calls other functions to handle the different viewing options.
    """

    while True:
        print("-" * 70)
        print(f"\nHow would you like to search for a booking?")
        print("\t1. Next upcoming event")
        print("\t2. Events on a given day")
        print("\t3. Events occurring within a certain time range")
        print("\t0. Return to booking menu")
        print("\nEnter your selection:")

        # valid options are 0, 1, 2, and 3
        choice = get_valid_int(list(range(0, 4)))
        print()

        match choice:
            case 1:
                view_upcoming(campus)
            case 2:
                view_on_day(campus)
            case 3:
                view_within_range(campus)
            case _:
                print("Returning to booking menu.\n")
                break

def view_upcoming(campus: Campus):
    """
    Handles the viewing option for finding the next upcoming event. Searches through the bookings
    list in each room on campus, and displays the event that is happening the soonest.
    """

    next_event: Booking = None
    next_room_booking: Booking
    next_event_room: str

    building: Building
    room: Room
    for building in campus.buildings.values():
        for room in building.rooms.values():
            next_room_booking = room.bookings.next_upcoming_event(datetime.now())
            
            # skip if no upcoming events in that room
            if next_room_booking is None:
                continue

            # check against current "next event" value to see if it happens sooner
            if (next_event is None) or (next_room_booking.start_time < next_event.start_time):
                next_event = next_room_booking
                next_event_room = room.room_id

    if next_event is None:
        print("No upcoming events found on campus.\n")
    else:
        print(f"The next event is occurring in {next_event_room}:\n{next_event}\n")

    print("Press ENTER to continue...")
    input()

def view_on_day(campus: Campus):
    """
    Handles the viewing option for viewing all the bookings on a certain day. Asks the user
    to enter a date, and prints out the bookings for each room under that day.
    """

    search_date_str = get_valid_date_str("Enter a date to view bookings on (YYYY-MM-DD): ")
    search_date = datetime.strptime(search_date_str, "%Y-%m-%d").date()

    bookings_on_day: dict[str, List[Booking]] = {}        # room_id -> List[Booking]

    building: Building
    room: Room
    for building in campus.buildings.values():
        for room in building.rooms.values():
            # get the room's bookings on that day
            room_bookings = room.bookings.get_events_on_day(search_date)

            # if there are bookings on that day, put them in the dictionary
            if room_bookings:
                bookings_on_day[room.room_id] = room_bookings

    # Check if any bookings were found on that day, and if so, print them
    if not bookings_on_day:
        print(f"\nNo events were found on {search_date_str}.")
    else:
        print(f"\nHere are the events occuring on {search_date_str}:\n")
        print_bookings(bookings_on_day)
    
    print("\nPress ENTER to continue...")
    input()

def view_within_range(campus: Campus):
    """
    Handles the viewing option for viewing all the bookings within a certain time range.
    Asks the user to enter a start date and time, end date and time, and prints out the
    bookings for each room in that time range.
    """

    print("Enter a time range to search for events in.\n")

    while True:
        start_date = get_valid_date_str("Start date (YYYY-MM-DD): ")
        start_time = get_valid_time_str("Start time (HH:MM): ")

        end_date = get_valid_date_str("End date (YYYY-MM-DD): ")
        end_time = get_valid_time_str("End time (HH:MM): ")

        datetime_start = datetime.strptime(
            start_date + " " + start_time, "%Y-%m-%d %H:%M"
        )
        datetime_end = datetime.strptime(
            end_date + " " + end_time, "%Y-%m-%d %H:%M"
        )

        # Valid start and end times if start takes place before end
        if datetime_start < datetime_end:
            break

        print("\tError: start time must take place before end time. Please try again.")
    
    bookings_in_range: dict[str, List[Booking]] = {}        # room_id -> List[Booking]

    building: Building
    room: Room
    for building in campus.buildings.values():
        for room in building.rooms.values():
            # get the room's bookings in that range
            room_bookings = room.bookings.get_bookings_in_range(datetime_start, datetime_end)

            # if there are bookings in that range for this room, put into dictionary
            if room_bookings:
                bookings_in_range[room.room_id] = room_bookings

    # Check if any bookings were found on that day, and if so, print them
    if not bookings_in_range:
        print(f"\nNo events were found between {datetime_start} and {datetime_end}.")
    else:
        print(f"\nHere are the events occuring between {datetime_start} and {datetime_end}:\n")
        print_bookings(bookings_in_range)
        
    print("\nPress ENTER to continue...")
    input()

def print_bookings(bookings_per_room: dict[str, List[Booking]]):
    """
    Given a dictionary mapping room_id to a list of bookings for that room, nicely prints out
    the booking(s) for each room. 
    """
    
    for room, bookings_list in bookings_per_room.items():
        print(f"{room}:")
        for booking in bookings_list:
            print(f"\t{booking}")

def get_valid_int(valid_options: list[int], display_str="  >> ") -> int:
    """
    Continuously ask the user for input until they select a valid option from the given list.
    Returns: the user's selected option as an int.
    """

    while True:
        # Must be an integer.
        try:
            choice = int(input(display_str))
        except ValueError:
            print("\tError: must be an integer. Please try again. ")
            continue

        # Must be in the list of valid options.
        if choice not in valid_options:
            print(f"\tError: {choice} is not a valid option. Please try again. ")
            continue

        return choice


def get_valid_date_str(display_str="") -> str:
    """
    Continuously ask user to enter a date until they provide a date in a valid form. (YYYY-MM-DD)

    Returns: valid str representation of a date.
    """

    # %Y: Full year, %m: month as a number from 01-12, %d: Day of month 01-31
    date_format = "%Y-%m-%d"

    while True:
        try:
            date_str = input(display_str)
            datetime.strptime(date_str, date_format)
            break
        except ValueError:
            print("\tError: invalid date or format. Please try again. ")

    return date_str


def get_valid_time_str(display_str="") -> str:
    """
    Continuously ask the user to enter a time until they provide a time in a valid form. (HH:MM)

    Additionally, checks to ensure that the time entered ends in XX:00 or XX:30, which
    enforces that bookings should be done in increments of 30 minutes.

    Returns: valid str representation of a time.
    """

    # %H: Hour 00-23, %M: Minute 00-59
    time_format = "%H:%M"

    while True:
        try:
            time_str = input(display_str)
            datetime.strptime(time_str, time_format)

            # Format is valid if it reaches this point. Check the minutes, which
            # is the second element after splitting along ":".
            minutes = time_str.split(":")[1]

            if minutes in ["00", "30"]:
                break

            print(
                "\tError: booking times should end in XX:00 or XX:30. Please try again. "
            )

        except ValueError:
            print("\tError: invalid time or format. Please try again. ")

    return time_str


def get_room(campus: Campus) -> Optional[Room]:
    """
    Walks the user through prompts to choose a room in a building. This method assumes that
    the first part of the room ID is the same as the ID of the building it resides in.

    eg. It assumes the room with the ID "ICT-121" can be found in the building with the ID "ICT".

    Returns: the chosen room, or None if the user decided to quit.
    """

    # print out all buildings to choose from
    print("\nChoose a building to select a room from:")

    building_ids = list(campus.buildings.keys())

    for i in range(len(building_ids)):
        print(f"\t{i + 1}. {building_ids[i]}")

    print("\t0. Quit")

    # get user's choice and quit if necessary
    print("\nEnter your selection: ")
    choice = get_valid_int(range(len(building_ids) + 1))

    if choice == 0:
        return None

    building = campus.buildings[building_ids[choice - 1]]

    # ask  for a room number
    while True:
        choice = input("Enter a room number: ")
        room_id = building.building_id + "-" + choice

        # check if room exists in the building
        if room_id in building.rooms.keys():
            break

        print(f"\tError: Room {room_id} does not exist. Please try again.")

    return building.rooms[room_id]
