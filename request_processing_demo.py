from request_processing import RequestList, Request, process_request
import time
from random import randint

def demo_20_requests():
    """
    Demo for request processing
    """
    queue = RequestList()

    print("--- Enqueuing 20 requests ---")
    for i in range(1, 21):
        number = randint(1, 3)
        if (number == 1):
            req_type = "navigation"
        elif (number == 2):
            req_type = "service"
        elif (number == 3):
            req_type = "other"

        request = Request(i, req_type, f"Demo request {i}")
        queue.enqueue(request)
        print(f"Enqueued: {request}")
        time.sleep(0.25)

    print("\n--- Dequeuing and processing 20 requests in arrival order ---")
    order = 1
    while not queue.is_empty():
        request = queue.dequeue()
        print(f"Dequeued #{order}: {request}")
        process_request(request)
        print("\n")
        time.sleep(0.25)

demo_20_requests()