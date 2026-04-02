class Priority:
    EMERGENCY = 3
    STANDARD = 2
    LOW = 1

class ServiceRequest:
    def __init__(self, request_id, description, priority):
        self.request_id = request_id
        self.description = description
        self.priority = priority

    def display_request(self):
        return f"Request ID: {self.request_id} | {self.description} (Priority: {self.priority})"
    
class PriorityQueue:
    def __init__(self):
        self.heap = []

    def peek(self):
        if not self.heap:
            return None
        else:
            return self.heap[0]
    
    def enqueue(self, service_request):
        self.heap.append(service_request)
        self._heapify_up(len(self.heap) - 1)
    
    def dequeue(self):
        if not self.heap:
            return None
        top_request = self.heap[0]
        last_request = self.heap.pop()
        if self.heap:
            self.heap[0] = last_request
            self._heapify_down(0)
        return top_request

    def _heapify_up(self, index):
        parent_index = (index - 1) // 2
        while index > 0 and self.heap[index].priority > self.heap[parent_index].priority:
            self.heap[index], self.heap[parent_index] = self.heap[parent_index], self.heap[index]
            index = parent_index
            parent_index = (index - 1) // 2
    
    def _heapify_down(self, index):
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
        for request in self.heap:
            request.display_request()
