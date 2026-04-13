import fast_lookup
import service_queue

class Node:
    """
    A node in a singly linked list used for the request queue
    """
    def __init__ (self, data):
        """
        Initializes a node with the given data

        Parameters:
            data: Request to store in the node
        """
        self.data = data
        self.next = None

class RequestList:
    """
    A FIFO queue using a singly linked list
    """
    
    def __init__ (self):
        """
        Initializes an empty request queue

        Attributes:
            front (Node): Points to the first node in the queue
            rear (Node): Points to the last node in the queue
        """
        # initializing the list
        self.front = None
        self.rear = None
    
    def enqueue (self, request):
        """
        Adds a request to the end of queue

        Parameters:
            request (Request): The request to be added

        Returns:
            None
        """

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
        """
        Removes and returns request at the front of the queue

        Returns:
            Request: Request at the front of the queue
        """
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
        """
        Cheks if the queue is empty

        Returns:
            bool: True if the queue is empty, false if it is not
        """
        # check if the list is empty
        return self.front is None
    
    def peek(self):
        """
        Returns the front request without removing it

        Returns:
            Request: Request at the front of the queue
        """
        # checking if the list is empty 
        if self.is_empty():
            return None
        
        # returns the data but doesn't change the list
        return self.front.data
    
    # not sure if we need this? I keep for now.
    def display(self):
        """
        Prints all requests currently in the queue from front to rear

        Returns:
            None
        """
        current = self.front

        if current is None:
            print("Queue is empty.")
            return
        
        while current is not None:
            print(current.data)
            current = current.next

class Request:
    """
    Represents requests and their types

    """
    def __init__ (self, id, type, description):
        """
        Initializes a request object

        Parameters: 
            id (int): Unique identifier for request
            type (str): Type of request
            description (str): Description of request
        """

        self.id = id
        self.request_type = type
        self.description = description
    
    def __str__ (self):
        """
        Returns a formatted string representation of the requests
        
        Returns:
            str: Formatted request string
        """
        return f"Request #{self.id} | Type: {self.request_type} | {self.description}"
    
def process_request(request):
    """
    Processes a request based on its type

    Parameters:
        request (Request): Request to process
    
    Returns:
        None
    """
    # different print statements to process.. might need more code after other classes are finished
    if (request.request_type == "navigation"):
        print(f"Processing nagivation request: {request.description}")
    elif (request.request_type == "service"):
        print(f"Processing service request: {request.description}")
    else:
        print(f"Processing unknown request type: {request.description}")   


def process_request_all(list):
    """
    Processes all requests in FIFO order

    Parameters:
        list (RequestList): Queue of requests
    
    Returns:
        None
    """
    # going through all requests
    while not list.is_empty():
        request = list.dequeue()
        process_request(request)
