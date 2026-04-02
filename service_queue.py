class Priority:
    """
    Represents priority levels for incoming requests.
    Attributes: 
        EMERGENCY (int): highest priority level
        STANDARD (int): middle priority level
        LOW (int): lowest priority level
    """
    EMERGENCY = 3
    STANDARD = 2
    LOW = 1

class ServiceRequest:
    """
    Represents a service request.
    Parameters:
        request_id (int): request id number
        description (String): description of the request
        priority (int): priority level of the request
    """
    def __init__(self, request_id, description, priority):
        """
        Initializes a service request.
        Parameters:
            request_id (int): request id number
            description (String): description of the request
            priority (int): priority level of the request
        Returns:
            new ServiceRequest object
        """
        self.request_id = request_id
        self.description = description
        self.priority = priority

    def display_request(self):
        """
        Formats request details.
        Parameters:
            None
        Returns:
            str: formatted request details
        """
        return f"Request ID: {self.request_id} | {self.description} (Priority: {self.priority})"
    
class PriorityQueue:
    """
    A max heap priority queue for ServiceQueue objects.
    """
    def __init__(self):
        """
        Initializes a new empty priority queue.
        """
        self.heap = []

    def peek(self):
        """
        Returns the highest priority request without removing it.
        Parameters: 
            None
        Returns: 
            ServiceRequest: the top request, or none if queue is empty
        """
        if not self.heap:
            return None
        else:
            return self.heap[0]
    
    def enqueue(self, service_request):
        """
        Adds a new request in priority order.
        Parameters:
            service_request (ServiceRequest): new request to be added
        Returns:
            Nothing
        """
        self.heap.append(service_request)
        self._heapify_up(len(self.heap) - 1)
    
    def dequeue(self):
        """
        Removes the highest priority request
        Parameters:
            None
        Returns: 
            top_request (ServiceRequest): the top request, or none if the queue is empty
        """
        if not self.heap:
            return None
        top_request = self.heap[0]
        last_request = self.heap.pop()
        if self.heap:
            self.heap[0] = last_request
            self._heapify_down(0)
        return top_request

    def _heapify_up(self, index):
        """
        Restores heap property by moving the element upward
        Parameters:
            index (int): the index of the element to heapify
        Returns: 
            Nothing
        """
        parent_index = (index - 1) // 2
        while index > 0 and self.heap[index].priority > self.heap[parent_index].priority:
            self.heap[index], self.heap[parent_index] = self.heap[parent_index], self.heap[index]
            index = parent_index
            parent_index = (index - 1) // 2
    
    def _heapify_down(self, index):
        """
        Restores heap property by moving the element downward
        Parameters:
            index (int): the index of the element to heapify
        Returns:
            Nothing
        """
        n = len(self.heap)
        while True:
            largest = index
            left = 2 * index + 1
            right = 2 * index + 2
            if left < n and self.heap[left].priority > self.heap[largest].priority:
                largest = left
            if right < n and self.heap[right].priority > self.heap[largest].priority:
                largest = right
            if largest == index:
                break
            self.heap[index], self.heap[largest] = self.heap[largest], self.heap[index]
            index = largest

    def display_queue(self):
        """
        Displays all requests in queue (heap, not sorted order)
        """
        for request in self.heap:
            request.display_request()
