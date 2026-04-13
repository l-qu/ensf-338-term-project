# booking_seed.py
from __future__ import annotations

from datetime import date, datetime, time, timedelta
from math import ceil
from typing import List

from event_booking import Booking, RoomBookingIndex
from dijkstra import Campus, Room


def get_all_rooms(campus: Campus) -> List[Room]:
    """
    Collect every room from every building in the campus.
    """
    rooms: List[Room] = []

    for building in campus.buildings.values():
        for room in building.rooms.values():
            rooms.append(room)

    return rooms


def ensure_booking_indices(campus: Campus) -> None:
    """
    Make sure every room has a RoomBookingIndex stored in room.bookings.
    """
    for building in campus.buildings.values():
        for room in building.rooms.values():
            if not hasattr(room, "bookings") or not isinstance(
                room.bookings, RoomBookingIndex
            ):
                room.bookings = RoomBookingIndex()


def clear_all_bookings(campus: Campus) -> None:
    """
    Remove all existing bookings from every room.
    """
    for building in campus.buildings.values():
        for room in building.rooms.values():
            room.bookings = RoomBookingIndex()


def seed_bookings(
    campus: Campus,
    total_bookings: int = 105,
    start_day: date | None = None,
    clear_existing: bool = True,
) -> int:
    """
    Seed the campus with at least total_bookings bookings spread across all rooms.

    Returns:
        The number of bookings successfully inserted.

    Strategy:
    - Get all rooms on campus
    - Ensure each room has a RoomBookingIndex
    - Spread bookings across rooms as evenly as possible
    - Use fixed time slots so bookings never overlap within a room
    """

    ensure_booking_indices(campus)

    if clear_existing:
        clear_all_bookings(campus)

    rooms = get_all_rooms(campus)
    if not rooms:
        raise ValueError("Cannot seed bookings because campus has no rooms.")

    if start_day is None:
        start_day = date.today()

    organiser_event_types = {
        "Wellness Services": ["Workshop", "Seminar", "Support Group"],
        "Engineering Students Society": ["Workshop", "Guest Talk"],
        "Trivia Club": ["Club Event", "Exec Meeting"],
        "TFDL Staff": ["Meeting", "Seminar"],
        "Students' Union": ["Volunteer Training", "Guest Talk", "Club Event"],
        "Schulich Soundstage": ["Club Event", "Lesson", "Showcase"],
        "CPSC Department": ["Tutorial", "Lecture", "Lab"],
        "Research Group": ["Project Meeting", "Seminar", "Guest Talk"],
    }

    organisers = list(organiser_event_types.keys())

    # Enough distinct non-overlapping slots per day.
    daily_slots = [
        (time(9, 0), timedelta(hours=1, minutes=30)),
        (time(11, 0), timedelta(hours=1, minutes=30)),
        (time(13, 30), timedelta(hours=1, minutes=30)),
        (time(15, 30), timedelta(hours=1, minutes=30)),
    ]

    bookings_per_room = ceil(total_bookings / len(rooms))
    inserted = 0

    for room_index, room in enumerate(rooms):
        for i in range(bookings_per_room):
            if inserted >= total_bookings:
                return inserted

            # Use i to choose both:
            # 1. which day this booking should be on
            # 2. which time slot on that day it should use
            day_offset = i // len(daily_slots)
            slot_index = i % len(daily_slots)

            booking_day = start_day + timedelta(days=day_offset)
            slot_start_time, duration = daily_slots[slot_index]

            start_dt = datetime.combine(booking_day, slot_start_time)
            end_dt = start_dt + duration

            # Choose an organiser in a repeating cycle.
            # Adding room_index shifts the pattern for each room so
            # they don't all have the same organiser at the same time.
            organiser = organisers[(i + room_index) % len(organisers)]
            allowed_titles = organiser_event_types[organiser]
            base_title = allowed_titles[i % len(allowed_titles)]
            title = f"{base_title} {inserted + 1}"

            # Create the Booking object for this room, day, and time slot.
            booking = Booking(
                start_time=start_dt,
                end_time=end_dt,
                title=title,
                organiser=organiser,
            )

            # Insert the booking into the room's booking index.
            added = room.bookings.add_booking(booking)
            if not added:
                raise RuntimeError(
                    f"Failed to insert seeded booking in room {room.room_id}: {booking}"
                )

            inserted += 1

    return inserted
