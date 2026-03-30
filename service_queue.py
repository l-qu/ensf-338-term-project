class ServiceRequest:
    def __init__(self, request_id, descrpition, priority):
        self.request_id = request_id
        self.description = descrpition
        self.priority = priority

    def display_request(self):
        return f"Request ID: {self.request_id} | {self.description} (Priority: {self.priority})"
    
class PriorityQueue:
    def __init__(self):
        self.heap = []