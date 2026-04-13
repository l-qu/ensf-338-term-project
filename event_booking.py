# event_booking.py
# Room and Event Booking System

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, time, datetime

# List and Optional are type hints:
# - List[Booking] means "a list of Booking objects"
# - Optional[Booking] means "either a Booking or None"
from typing import List, Optional

import uuid  # This is used to generate unique IDs for each booking.


@dataclass(order=True)
class Booking:
    start_time: datetime
    end_time: datetime

    # booking_id gets a default value automatically.
    # default_factory means "run this function each time a new Booking is made".
    # str(uuid.uuid4()) creates a unique random ID as a string.
    #
    # compare=False means this field is NOT used when comparing bookings.
    booking_id: str = field(default_factory=lambda: str(uuid.uuid4()), compare=False)
    title: str = field(default="", compare=False)
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

        lo, hi = 0, len(self.bookings)

        # Keep searching until lo and hi meet.
        while lo < hi:
            mid = (lo + hi) // 2

            if self.bookings[mid].start_time < start_time:
                lo = mid + 1
            else:
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

        # Reject impossible bookings.
        if booking.end_time <= booking.start_time:
            return False

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

    def get_bookings_in_range(
        self, range_start: datetime, range_end: datetime
    ) -> List[Booking]:
        """
        Return all bookings that happen during a given time range.

        A booking should be included if it overlaps the range at all.

        That means a booking counts if:
            booking starts before the range ends
            AND
            booking ends after the range starts

        Example:
            booking: 09:30 to 10:30
            range:   10:00 to 12:00

        This booking should still be returned, even though it started before 10:00.
        """

        result: List[Booking] = []

        if range_end <= range_start:
            return result

        # Find where a booking with start_time = range_start would be inserted.
        #
        # Since self.bookings is sorted by start_time, this gives us a useful
        # starting point for the search.
        pos = self._find_insert_position(range_start)

        # The booking just before the insert position may still overlap the range
        # if it started earlier but has not ended yet.
        if pos > 0:
            prev = self.bookings[pos - 1]
            if prev.end_time > range_start:
                result.append(prev)

        i = pos

        while i < len(self.bookings) and self.bookings[i].start_time < range_end:

            # This booking overlaps the range if it ends after range_start.
            # If so, include it.
            if self.bookings[i].end_time > range_start:
                result.append(self.bookings[i])

            i += 1

        return result

    def get_events_on_day(self, target_day: date) -> List[Booking]:
        """
        Return all bookings that happen on one specific day.

        Instead of writing completely new logic, we reuse get_bookings_in_range().

        We convert the day into:
            start of day -> 00:00:00
            end of day   -> 23:59:59.999999

        Then we ask for all bookings in that full-day range.
        """

        # time.min == 00:00:00
        day_start = datetime.combine(target_day, time.min)

        # time.max == 23:59:59.999999
        day_end = datetime.combine(target_day, time.max)

        # Reuse the range-query method.
        return self.get_bookings_in_range(day_start, day_end)

    def next_upcoming_event(self, now: datetime) -> Optional[Booking]:
        """
        Return the next relevant booking at a given moment.

        This does one of two things:
        1. If an event is happening right now, return that current event.
        2. Otherwise, return the next future event.
        3. If there is nothing current or upcoming, return None.

        Optional[Booking] means:
            - it returns a Booking if one exists
            - otherwise it returns None
        """

        # Find where 'now' would be inserted in the sorted list.
        pos = self._find_insert_position(now)

        # First check the booking just before that position.
        if pos > 0 and self.bookings[pos - 1].end_time > now:
            return self.bookings[pos - 1]

        # If there is no current booking, then the booking at position 'pos'
        # is the next booking that starts at or after 'now'.
        if pos < len(self.bookings):
            return self.bookings[pos]

        # If pos is at the end of the list, there are no more bookings.
        return None

    def all_bookings(self) -> List[Booking]:
        """
        Return a copy of the full bookings list.

        list(self.bookings) creates a shallow copy.
        """
        return list(self.bookings)
