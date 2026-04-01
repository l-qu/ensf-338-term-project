# event_booking.py
# Room and Event Booking System

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime

# List and Optional are type hints:
# - List[Booking] means "a list of Booking objects"
# - Optional[Booking] means "either a Booking or None"
from typing import List, Optional

import uuid  # This is used to generate unique IDs for each booking.


@dataclass(order=True)
class Booking:
    start_time: datetime  # The date and time when the booking begins.
    end_time: datetime  # The date and time when the booking ends.

    # booking_id gets a default value automatically.
    # default_factory means "run this function each time a new Booking is made".
    # str(uuid.uuid4()) creates a unique random ID as a string.
    #
    # compare=False means this field is NOT used when comparing bookings.
    booking_id: str = field(default_factory=lambda: str(uuid.uuid4()), compare=False)

    # A short name for the event.
    title: str = field(default="", compare=False)

    # The person or group responsible for the booking.
    organiser: str = field(default="", compare=False)

    def overlaps(self, other: "Booking") -> bool:
        """
        Check whether this booking overlaps in time with another booking.

        We have an overlap when:
        - this booking starts before the other one ends, AND
        - the other booking starts before this one ends

        Example of overlap:
            A: 10:00 to 11:00
            B: 10:30 to 11:30
            -> True

        Example of NO overlap:
            A: 10:00 to 11:00
            B: 11:00 to 12:00
            -> False
            These touch at the boundary, but they do not overlap.
        """
        return self.start_time < other.end_time and other.start_time < self.end_time

    def __str__(self) -> str:
        """
        Return a human-readable string version of the booking.
        """
        return (
            f"[{self.booking_id[:8]}] "  # show only the first 8 characters of the ID
            f"{self.start_time.strftime('%d %b %Y %H:%M')} - "
            f"{self.end_time.strftime('%H:%M')} | "
            f"{self.title} | {self.organiser}"
        )


class RoomBookingIndex:
    """
    This class stores and manages bookings for ONE room.

    self.bookings is always kept sorted by start_time which allows us to:
    - insert new bookings in the correct place
    - find nearby bookings quickly
    - later support range queries and next-event queries efficiently
    """

    def __init__(self) -> None:
        # List that will hold Booking objects in chronological order.
        self.bookings: List[Booking] = []

    def _find_insert_position(self, start_time: datetime) -> int:
        """
        Find the index where a new booking should be inserted so that
        the list stays sorted by start_time.

        Instead of checking every booking one by one from the start,
        binary search repeatedly cuts the search space in half.

        Example:
            If bookings are at 09:00, 11:00, 14:00
            and the new booking starts at 12:00,
            this method returns index 2,
            so the booking gets inserted before 14:00.

        Returns:
            The correct list index for insertion.
        """

        # lo = lowest possible index where the new booking could go
        # hi = one past the highest possible index
        lo, hi = 0, len(self.bookings)

        # Keep searching until lo and hi meet.
        while lo < hi:
            # Find the middle index of the current search range.
            mid = (lo + hi) // 2

            # If the middle booking starts before the new start time,
            # the insert position must be to the RIGHT of mid.
            if self.bookings[mid].start_time < start_time:
                lo = mid + 1
            else:
                # Otherwise, the insert position is at mid or to the LEFT of mid.
                hi = mid

        # When the loop ends, lo is the correct insertion position.
        return lo

    def add_booking(self, booking: Booking) -> bool:
        """
        Add a new booking to the list, keeping the list sorted.

        Rules:
        1. The booking must end after it starts.
        2. The booking must not overlap with existing bookings.
        3. If valid, it is inserted in the correct sorted position.

        Returns:
            True  -> booking was added successfully
            False -> booking was rejected
        """

        # Reject impossible bookings, like:
        # start = 14:00, end = 13:00
        # or start = 14:00, end = 14:00
        if booking.end_time <= booking.start_time:
            return False

        # Find where this booking should go in the sorted list.
        pos = self._find_insert_position(booking.start_time)

        # Because the list is sorted, the only bookings that could overlap
        # are the one just before the insert position and the one currently
        # at the insert position.
        #
        # Check the booking immediately before the new one.
        if pos > 0 and self.bookings[pos - 1].overlaps(booking):
            return False

        # Check the booking immediately after / at the insert position.
        if pos < len(self.bookings) and self.bookings[pos].overlaps(booking):
            return False

        # If no conflicts were found, insert the booking into the list
        # at the correct position.
        self.bookings.insert(pos, booking)

        return True

    def remove_booking(self, booking_id: str) -> bool:
        """
        Remove a booking by its unique booking_id.

        We go through the list one by one until we find the booking
        with the matching ID.

        enumerate(self.bookings) gives us:
        - i       -> the index in the list
        - booking -> the Booking object at that index

        Returns:
            True  -> booking found and removed
            False -> booking_id not found
        """

        for i, booking in enumerate(self.bookings):
            if booking.booking_id == booking_id:
                del self.bookings[i]
                return True

        # If the loop ends, no matching booking was found.
        return False

    def get_booking_by_id(self, booking_id: str) -> Optional[Booking]:
        """
        Find and return a booking with a matching booking_id.

        Returns:
            Booking object -> if found
            None           -> if not found
        """

        for booking in self.bookings:
            if booking.booking_id == booking_id:
                return booking

        return None
