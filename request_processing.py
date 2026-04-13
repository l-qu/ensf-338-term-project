import fast_lookup

class Node:
    def __init__ (self, data):
        self.data = data
        self.next = None

class RequestList:
    def __init__ (self):
        # initializing the list
        self.front = None
        self.rear = None
    
    def enqueue (self, request):
        # making a new node for the 
        new_node = Node(request)

        # checking if the back is none and changes pointers
        if self.rear is None:
            self.front = new_node
            self.rear = new_node
            return
        
        # changing the rear to the new node
        self.rear.next = new_node
        self.rear = new_node
    
    def dequeue (self):
        # check if the list is empty
        if self.is_empty():
            return None
        
        # assigning the temporary pointer to list
        temp = self.front

        # putting the new front to the next node
        self.front = self.front.next

        # checking if the front is now none, if so the rear is then none 
        if self.front is None:
            self.rear = None
        
        # temp is now the first in
        return temp.data

    def is_empty (self):
        # check if the list is empty
        return self.front is None
    
    def peek(self):
        # checking if the list is empty 
        if self.is_empty():
            return None
        
        # returns the data but doesn't change the list
        return self.front.data
    
    # not sure if we need this? I keep for now.
    def display(self):
        current = self.front

        if current is None:
            print("Queue is empty.")
            return
        
        while current is not None:
            print(current.data)
            current = current.next

class Request:
    def __init__ (self, id, type, description):
        # initializing the request
        self.id = id
        self.type = type
        self.description = description
    
    def __str__ (self):
        # printing request formatting
        return f"Request #{self.id} | Type: {self.type} | {self.description}"
    
def process_request(request):
    # different print statements to process.. might need more code after other classes are finished
    if (request.type == "navigation"):
        print(f"Processing nagivation request: {request.description}")
    elif (request.type == "service"):
        print(f"Processing service request: {request.description}")
    else:
        print(f"Processing unknown request type: {request.description}")   


def process_request_all(list):
    # going through all requests
    while not list.is_empty():
        request = list.dequeue()
        process_request(request)
