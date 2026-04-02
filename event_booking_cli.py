from datetime import date, time, datetime

from event_booking import Booking, RoomBookingIndex
from temp_map_classes import Campus, Building, Room            # replace with import statement from actual main

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
                # handle remove booking
                pass
            case 3:
                # handle viewing room bookings
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
    
    This method does not give the user a chance to retry if they enter an overlapping time; 
    however, it does inform the user ahead of time about when the room will be occupied.
    """

    print("-" * 70)

    # print out all buildings to choose from
    print("\nChoose a building to book a room in:")

    building_ids = list(campus.buildings.keys())

    for i in range(len(building_ids)):
        print(f"\t{i + 1}. {building_ids[i]}")
    
    print("\t0. Quit")

    # get user's choice and quit if necessary
    print("\nEnter your selection: ")
    choice = get_valid_int(range(len(building_ids) + 1))

    if choice == 0:
        return

    building = campus.buildings[building_ids[choice - 1]]

    print(f"\nChosen building: {building.building_id}. Please fill out the following fields.\n")
    
    # ask  for a room number
    while True:
        choice = input("Room number: ")
        room_id = building.building_id + "-" + choice
        
        # check if room exists in the building
        if room_id in building.rooms.keys():
            break

        print(f"\tError: Room {room_id} does not exist. Please try again.")

    room = building.rooms[room_id]

    booking_date = get_valid_date_str("Date (YYYY-MM-DD): ")

    # inform user of bookings on that day
    curr_bookings = room.bookings.get_events_on_day(datetime.strptime(booking_date, "%Y-%m-%d"))
    if curr_bookings:
        print(f"  !!\t{room_id} already has bookings on {booking_date}.")
        print("\tPlease be mindful of these occupied times or the booking may fail:\n")
        for booking in curr_bookings:
            print(f"\t{booking}")
        print()

    start_time = get_valid_time_str("Start time (HH:MM): ")
    end_time = get_valid_time_str("End time (HH:MM): ")
    event = input("Event name: ")
    organizer = input("Organizer: ")

    datetime_start = datetime.strptime(booking_date + " " + start_time, "%Y-%m-%d %H:%M")
    datetime_end = datetime.strptime(booking_date + " " + end_time, "%Y-%m-%d %H:%M")

    new_booking = Booking(datetime_start, datetime_end, title=event, organiser=organizer)
    booking_status = room.bookings.add_booking(new_booking)

    if (booking_status):
        print("Booked successfully!")
    else:
        print("Booking failed. Something went wrong.")
    

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

            print("\tError: booking times should end in XX:00 or XX:30. Please try again. ")

        except ValueError:
            print("\tError: invalid time or format. Please try again. ")
    
    return time_str