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
        self.buildings_name.delete(building_name.lower())

        # deleting all rooms from the building as well
        for room_id in building.rooms:
            self.rooms_id.delete(room_id)
        return True
    
    def get_building_location(self, building_id):
        """
        Gets the location of a building by its id

        Parameters:
            building_id (int): The ID of the building 

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
            building_id (int): The ID of the building 
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
        
        # adding a room to the building object
        building.rooms[room.room_id] = room

        # inserting the room into the room hash map
        self.rooms_id.insert(room.room_id, room)
        self.rooms_id.insert(room.room_id, room)
        self.rooms_capacity.insert(room.room_id, room.capacity)
        self.rooms_type.insert(room.room_id, room.room_type)
        self.rooms_bookings.insert(room.room_id, room.bookings)
    
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
        return True
    




