import timeit

class HashTable:
    """
    Hash table using seperate chaining for collisions

    """
    def __init__(self, size = 200):
        """
        Initializes the hash map with the fixed number of buckets.

        Parameters:
            size(int): number of buckets in hash table.
                       defaults to 200.

        Attributes:
            size (int): size of the hash table
            hash_table ()
        """

        self.size = size
        self.hash_table = [[] for _ in range (size)]

    def insert(self, key, value):
        """
        Inserts a key-value pair into the map.
        If key exists, the value is updated

        Parameters:
            key: Key used to insert
            value: Value associated with key

        returns:
            None
        """

        # getting the index where the value should be stored
        hash_key = hash(key) % self.size
        bucket = self.hash_table[hash_key]

        # loop checks if the key is already in the bucket/hash map
        for index, (record_key, _) in enumerate(bucket):
            if record_key == key:
                # if the key exists, update the value
                bucket[index] = (key, value)
                return
        # if the key doesn't exist, it is appended to the bucket/hash map
        bucket.append((key, value))
        
    def delete(self, key):
        """
        Deletes a value in the hashmap from a key

        Parameters:
            key: Key associated with the value

        returns:
            True if delete was successful
            False if delete was not successful
        """
        # getting the index where the value should be stored
        hash_key = hash(key) % self.size
        bucket = self.hash_table[hash_key]

        # looping through the bucket to find the key to delete
        for index, (record_key, _) in enumerate(bucket):
            if record_key == key:
                # if the key is found, delete it and return True as in it is completed
                bucket.pop(index)
                return True
        # If nothing was found, return false
        return False
            
    def lookup(self, key):
        """
        Looks up a value from a key in the hash map

        Parameters:
            key: Key associated with value to find

        returns:
            record_val: value associated with the key
            None if value was not found
        """
        # getting the index where the value should be stored
        hash_key = hash(key) % self.size
        bucket = self.hash_table[hash_key]

        # loops through the bucket to find the key
        for record_key, record_val in bucket:
            if record_key == key:
                # if the key is found, the value of the key is returned
                return record_val
        # if the key is not found, returns false
        return None

    def __str__(self):
        """
        Prints out the items in the hash table

        returns:
            String of all the items in the hash table
        """

        return "".join(str(bucket) for bucket in self.hash_table)

class FastLookup:
    def __init__(self, building_number = 100, room_number = 200):
        """
        Initializes hash tabled for the fast lookup system

        Parameters:
            building_number (int): Initial capacity for building hash table
            room_number (int): Initial capacity for room hash table 
        
        Attributes:
            building_id (HashTable): maps building IDs to building objects
            buildings_name (HashTable): maps building names to building objects
            rooms_id (HashTable): map room IDs to room object
            rooms_capacity (HashTable): map room capacities to room objects
            rooms_type (HashTable): map rooms types to room objects
            self.room_bookings (HashTable): map room bookings to room objects
        """

        self.buildings_id = HashTable(building_number)
        self.buildings_name = HashTable(building_number)
        self.rooms_id = HashTable(room_number)
        self.rooms_capacity = HashTable(room_number)
        self.rooms_type = HashTable(room_number)
        self.rooms_bookings = HashTable(room_number)
    
    #---- BUILDING FUNCTIONS ----
    def add_building(self, building):
        """
        Adds a building to the id and name hash tables

        Parameters:
            building (Building): The building object to add

        Returns:
            None
        """
        self.buildings_id.insert(building.building_id, building)
        self.buildings_name.insert(building.name.lower(), building)
    
    def find_building_id(self, building_id):
        """
        Adds a building to the id and name hash tables.

        Parameters:
            building_id (str): The ID of the building

        Returns:
            Building: The building object associated with building_id
        """

        return self.buildings_id.lookup(building_id)
    
    def find_building_name(self, building_name):
        """
        Finds a building's name using its ID

        Parameters:
            building_name (str): The name of the building

        Returns:
            Building: The building object associated with building_name
        """

        return self.buildings_name.lookup(building_name.lower())
    
    def list_buildings(self):
        """
        Lists all buildings

        Returns:
            list: All building objects
        """
        buildings = []
        for bucket in self.buildings_id.hash_table:
            for _building_id, building in bucket:
                buildings.append(building)
        
        return buildings
    
    def list_building_rooms(self, building_id):
        """
        Lists all rooms inside one building

        Parameters:
            building_id (str): ID of the building

        Returns:
            list: All room objects in the building
        """
        building = self.find_building_id(building_id)
        if building is None:
            return []

        return list(building.rooms.values())  
    
    def delete_building_id(self, building_id):
        """
        Deletes a building using its ID and removes associated roooms

        Parameters:
            building_id (str): The ID of the building to delete

        Returns:
            bool: True if the building was successfully deleted
                  False if the building was not found
        """

        # finding the building from building id
        building = self.buildings_id.lookup(building_id)

        # if it isn't found, return false for not found
        if building is None:
            return False
        
        # if it is, then the building in id and name hash maps will be deleted
        self.buildings_id.delete(building_id)
        self.buildings_name.delete(building.name.lower())

        # deleting all rooms from the building as well
        for room_id in building.rooms:
            self.rooms_id.delete(room_id)
            self.rooms_capacity.delete(room_id)
            self.rooms_type.delete(room_id)
            self.rooms_bookings.delete(room_id)
        building.rooms.clear()
        return True
    
    def delete_building_name(self, building_name):
        """
        Deletes a building using its name and removes associated roooms

        Parameters:
            building_name (str): The name of the building to delete

        Returns:
            bool: True if the building was successfully deleted
                  False if the building was not found
        """
        
        # finding the building from building name
        building = self.buildings_name.lookup(building_name.lower())

        # if it isn't found, return false for not found
        if building is None:
            return False
        
        # if it is, then the building in id and name hash maps will be deleted
        self.buildings_id.delete(building.building_id)
        self.buildings_name.delete(building.name.lower())

        # deleting all rooms from the building as well
        for room_id in list(building.rooms):
            self.rooms_id.delete(room_id)
            self.rooms_capacity.delete(room_id)
            self.rooms_type.delete(room_id)
            self.rooms_bookings.delete(room_id)
        building.rooms.clear()
        return True
    
    def find_building_location(self, building_id):
        """
        Gets the location of a building by its id

        Parameters:
            building_id (str): The ID of the building 

        Returns:
            tuple: (latitude, longitude) or coordinates if found
        """

        # finding the building from inputted building id
        building = self.find_building_id(building_id)

        # if building is not found, will return false
        if building is None:
            return False
        
        return building.location

    def update_building_location(self, building_id, new_location):
        """
        Updates location of building

        Parameters:
            building_id (str): The ID of the building 
            new_location (tuple): New (lat, lon) or coordinates

        Returns:
            bool: True if updated successfully
        """
        # finding the building from inputted building id
        building = self.find_building_id(building_id)

        # if building is not found, will return false
        if building is None:
            return False
        
        building.location = new_location
        return True

    def update_building_name(self, building_id, new_name):
        """
        Updates building name

        Parameters: 
            building_id (str): The ID of the building
            new_name (str): New name of the building
        
        Returns:
            bool: True if updated successfully
        """
        # check if the name exists already
        existing = self.find_building_name(new_name.lower().strip())
        if existing and existing is not building:
            return False
        
        # finding the building from inputted building id
        building = self.find_building_id(building_id)

        # if building is not found, will return false
        if building is None:
            return False
        
        building.name = new_name
        return True

    def update_building_id(self, building_name, new_id):
        """
        Updates building ID

        Parameters: 
            building_name (str): The name of the building
            new_id (str): New ID of the building
        
        Returns:
            bool: True if updated successfully
        """
        # check if the id exists already
        existing = self.find_building_name(new_id.lower().strip())
        if existing and existing is not building:
            return False
        
        # finding the building from inputted building name
        building = self.find_building_name(building_name)

        # if building is not found, will return false
        if building is None:
            return False
        
        building.name = new_id
        return True
    
    def update_building(self, building_id, new_name = None, new_location = None, new_building_id = None):
        """
        Updates building name

        Parameters: 
            building_id (str): The ID of the building
            new_name (str)
        
        Returns:
            bool: True if updated successfully
        """
        #finding the building and checking if it exists
        building = self.find_building_id(building_id)
        if building is None:
            return False

        update_building_id = building_id
        if new_building_id is not None:
            existing = self.find_building_id(new_building_id.lower().strip())
            if existing_building is not None and existing_building is not building:
                return False
            update_building_id = new_building_id.strip()

        if new_name is not None:
            existing_building = self.find_building_name(new_name.strip())
            if existing_building is not None and existing_building is not building:
                return False

        if new_building_id is not None and not self.update_building_id(building_id, update_building_id):
            return False
        if new_name is not None and not self.update_building_name(update_building_id, new_name):
            return False
        if new_location is not None and not self.update_building_location(update_building_id, new_location):
            return False
        return True
    
    # ---- ROOM FUNCTIONS ----
    def add_room(self, building_id, room):
        """
        Adds a room to a building and inserts it into the room hash table

        Parameters:
            building_id (str): The ID of the building to add the room into
            room (Room): The room object to add

        Returns:
            bool: True if the room was successfully added.
                  False if the building does not exist.
        """
        # finding the building from the inputted building id
        building = self.find_building_id(building_id)

        # if building is not found, will return false
        if building is None:
            return False
        
        # checking if it already exists
        if self.find_room(room.room_id) is not None:
            return False
        
        # adding a room to the building object
        building.rooms[room.room_id] = room

        # inserting the room into the room hash map
        self.rooms_id.insert(room.room_id, room)
        self.rooms_capacity.insert(room.room_id, room.capacity)
        self.rooms_type.insert(room.room_id, room.room_type)
        self.rooms_bookings.insert(room.room_id, room.bookings)
        return True
    
    def find_room_building (self, room_id):
        """
        Finds the building inc which the room belongs
        
        Parameters:
            room_id (str): Room ID to search for building it's in

        Returns:
            Building: The building it is housed in
        """
        for building in self.list_buildings():
            if room_id in building.rooms:
                return building
        return None
    
    def find_room(self, room_id):
        """
        Finds a room using its ID

        Parameters:
            room_id (str): The ID of the room

        Returns:
            Room: The room object if found
        """

        # using the hash map function lookup to find the room info
        return self.rooms_id.lookup(room_id)
    
    def find_room_capacity(self, room_id):
        """
        Finds a room's capacity using its ID

        Parameters:
            room_id (str): The ID of the room

        Returns:
            Capacity: Capacity of room if it is found
        """

        return self.rooms_capacity.lookup(room_id)

    def find_room_type(self, room_id):
        """
        Finds a room's type using its ID

        Parameters:
            room_id (str): The ID of the room

        Returns:
            Type: Type of room if it is found
        """

        return self.rooms_type.lookup(room_id)

    def find_room_bookings(self, room_id):
        """
        Finds a room's bookings using its ID

        Parameters:
            room_id (str): The ID of the room

        Returns:
            Bookings: Bookings of a room if it is found
        """
        return self.rooms_bookings.lookup(room_id)
        
    def delete_room_id(self, building_id, room_id):
        """
        Deletes a room from a building using building id and room id

        Parameters:
            building_id (str): ID of the building where the room will be deleted
            room_id (str): ID of the room to be deleted

        Returns:
            bool: True if the room was successfully deleted.
                  False if the building or room does not exist.
        """

        # finding the building by its id 
        building = self.find_building_id(building_id)
        
        # returning false is building doesnt exist
        if building is None:
            return False
        
        # returning false if room doesnt exist
        if room_id not in building.rooms:
            return False
        
        # deleting room from the building and deleting room from hash map of rooms
        del building.rooms[room_id]
        self.rooms_id.delete(room_id)
        self.rooms_capacity.delete(room_id)
        self.rooms_type.delete(room_id)
        self.rooms_bookings.delete(room_id)
        return True
    
    def delete_room_name(self, building_name, room_id):
        """
        Deletes a room from a building using building name and room id

        Parameters:
            building_name (str): Name of the building where the room will be deleted
            room_id (str): ID of the room to be deleted.

        Returns:
            bool: True if the room was successfully added.
                  False if the building does not exist.
        """

        # finding the building by its name
        building = self.find_building_name(building_name.lower())
        
        # returning false is building doesnt exist
        if building is None:
            return False
        
        # returning false if room doesnt exist
        if room_id not in building.rooms:
            return False
        
        # deleting room from the building and deleting room from hash map of rooms
        del building.rooms[room_id]
        self.rooms_id.delete(room_id)
        self.rooms_capacity.delete(room_id)
        self.rooms_type.delete(room_id)
        self.rooms_bookings.delete(room_id)
        return True
    
    def update_room_id(self, building_id, room_id, new_room_id):
        """
        Updates room's ID 

        Parameters: 
            building_id (str): The ID of the building
            room_id (str): Current room ID
            new_room_id (str): 
        
        Returns:
            bool: True if updated successfully
        """

        # finding if the building exists
        building = self.find_building_id(building_id)
        if building is None or room_id not in building.rooms:
            return False

        # finding the room in the building
        room = building.rooms[room_id]

        # finding if a room with that id exists already
        existing_room = self.find_room(new_room_id.strip())
        if existing_room is not None and existing_room is not room:
            return False

        # if they are the same already, done
        if new_room_id.strip() == room.room_id:
            return True

        # deleting the room information
        self.rooms_id.delete(room_id)
        self.rooms_capacity.delete(room_id)
        self.rooms_type.delete(room_id)
        self.rooms_bookings.delete(room_id)
        del building.rooms[room_id]

        # putting the new id and old info back in
        room.room_id = new_room_id.strip()
        building.rooms[new_room_id.strip()] = room
        self.rooms_id.insert(new_room_id.strip(), room)
        self.rooms_capacity.insert(new_room_id.strip(), room.capacity)
        self.rooms_type.insert(new_room_id.strip(), room.room_type)
        self.rooms_bookings.insert(new_room_id.strip(), room.bookings)
        return True
    
    def update_room_type(self, room_id, new_room_type):
        """
        Updates a room's type.

        Parameters:
            room_id (str): The room ID to update.
            new_room_type (str): The replacement room type.

        Returns:
            bool: True if updated successfully.
        """

        # checking if the room exists or not
        room = self.find_room(room_id)
        if room is None:
            return False
        
        # assigning the new room type
        room.room_type = new_room_type.strip()
        self.rooms_type.insert(room.room_id, room.room_type)
        return True

    def update_room_capacity(self, room_id, new_capacity):
        """
        Updates a room's capacity.

        Parameters:
            room_id (str): The room ID to update.
            new_capacity (int): The replacement room capacity.

        Returns:
            bool: True if updated successfully.
        """

        # checking if the room exists or not and error checks for capacity
        room = self.find_room(room_id)
        if room is None or not isinstance(new_capacity, int) or new_capacity < 0:
            return False

        # setting new capasity
        room.capacity = new_capacity
        self.rooms_capacity.insert(room.room_id, room.capacity)
        return True

    def update_room_booking(self, room_id, new_booking):
        """
        Replaces a room's bookings.
        ****** REPLACE WITH ACTUAL BOOKING????? ********

        Parameters:
            room_id (str): The room ID to update.
            new_booking: A booking value or iterable of booking values.

        Returns:
            bool: True if updated successfully.
        """

        # checking if room exists
        room = self.find_room(room_id)
        if room is None or new_booking is None:
            return False

        # assigning bookings
        room.bookings = list(new_booking)
        self.rooms_bookings.insert(room.room_id, room.bookings)
        return True

    def update_room(self, building_id, room_id, new_room_id = None, new_capacity = None, new_room_type = None, new_bookings = None, new_room_name = None):
        """
        Updates one or more room fields.

        Parameters:
            building_id (str): The building that owns the room.
            room_id (str): The current room ID.
            new_room_id (str | None): The replacement room ID.
            new_capacity (int | None): The replacement room capacity.
            new_room_type (str | None): The replacement room type.
            new_bookings (iterable | None): The replacement bookings list.
            new_room_name (str | None): The replacement room name.

        Returns:
            bool: True if every requested update succeeds.
        """

        # making sure room exists
        building = self.find_building_id(building_id)
        if building is None or room_id not in building.rooms:
            return False

        # room id to update
        active_room_id = room_id

        # updating room id if it is inputted
        if new_room_id is not None:
            if not self.update_room_id(building_id, room_id, new_room_id):
                return False
            active_room_id = new_room_id.strip()

        # updating the rest
        if new_capacity is not None and not self.update_room_capacity(active_room_id, new_capacity):
            return False
        if new_room_type is not None and not self.update_room_type(active_room_id, new_room_type):
            return False
        if new_bookings is not None and not self.update_room_booking(active_room_id, new_bookings):
            return False
        return True

    def list_rooms(self, building_id):
        """
        Lists all rooms of a building

        Parameters:
            building_id (str): ID of the building to list rooms of

        Returns:
            Rooms: List of all the rooms in the building
        """
        rooms = []

        for bucket in self.rooms_id.hash_table:
            for _room_id, room in bucket:
                rooms.append(room)

        return rooms

    # ---------- PERFORMANCE DEMO ----------

    def benchmark_lookup(self, sizes=None, repeats=1000):
        """
        Benchmark lookup time using timeit to demonstrate near O(1) performance.

        Parameters:
            sizes (list[int]): Different dataset sizes to test
            repeats (int): Number of repeated lookups per test

        Returns:
            list of (size, avg_time)
        """

        if sizes is None:
            sizes = [100, 1000, 5000, 10000, 20000]

        results = []

        class DemoBuilding:
            def __init__(self, building_id, name):
                self.building_id = building_id
                self.name = name
                self.location = (0, 0)
                self.rooms = {}

        for size in sizes:
            lookup = FastLookup(size * 2, size * 2)

            # populate hash table
            for i in range(size):
                lookup.add_building(DemoBuilding(f"B{i}", f"Building {i}"))

            target_key = f"B{size // 2}"

            # time only the lookup
            time_taken = timeit.timeit(
                stmt=lambda: lookup.find_building_id(target_key),
                number=repeats
            )

            avg_time = time_taken / repeats
            results.append((size, avg_time))

        return results


if __name__ == "__main__":
    fl = FastLookup()
    results = fl.benchmark_lookup()

    print("Lookup Benchmark (timeit):")
    for size, t in results:
        print(f"{size:>6} records -> {t:.10f} seconds per lookup")