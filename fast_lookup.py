class HashTable:
    # initializing the hash map by size and 2d arrays
    def __init__(self, size = 200):
        self.size = size
        self.hash_table = [[] for _ in range (size)]

    def insert(self, key, value):
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
        # getting the index where the value should be stored
        hash_key = hash(key) % self.size
        bucket = self.hash_table[hash_key]

        # loops through the bucket to find the key
        for record_key, record_val in bucket:
            if record_key == key:
                # if the key is found, the value of the key is returned
                return record_val
        # if the key is not found, returns false
        return False

    def __str__(self):
        # delete this later
        return "".join(str(bucket) for bucket in self.hash_table)

class FastLookup:
    # initializes values 100 and 200 into buildings and room hashmaps
    def __init__(self, building_number = 100, room_number = 200):
        self.buildings_id = HashTable(building_number)
        self.buildings_name = HashTable(building_number)
        self.rooms_id = HashTable(room_number)
    
    #---- BUILDING FUNCTIONS ----
    def add_building(self, building):
        # adding the building to the respective hashmaps
        self.buildings_id.insert(building.building_id, building)
        self.buildings_name.insert(building.name.lower(), building)
    
    def find_building_id(self, building_id):
        # returning the building found from id prompt
        return self.buildings_id.lookup(building_id)
    
    def find_building_name(self, building_name):
        # returning the building found from building name
        return self.buildings_name.lookup(building_name.lower())
    
    def delete_building_id(self, building_id):
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
        # finding the building from building name
        building = self.buildings_id.lookup(building_name.lower())

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
    
    # ---- ROOM FUNCTIONS ----
    def add_room(self, building_id, room):
        # finding the building from the inputted building id
        building = self.find_building_id(building_id)

        # if building is not found, will return false
        if building is None:
            return False
        
        # adding a room to the building object
        building.rooms[room.room_id] = room

        # inserting the room into the room hash map
        self.rooms_id.insert(room.room_id, room)
    
    def find_room(self, room_id):
        # using the hash map function lookup to find the room info
        return self.rooms_id.lookup(room_id)
    
    def delete_room_id(self, building_id, room_id):
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



