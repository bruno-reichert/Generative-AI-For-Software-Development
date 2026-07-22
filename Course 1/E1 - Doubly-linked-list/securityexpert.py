import threading # Used to make the class thread-safe

class Node:
    def __init__(self, data):
        self.data = data
        self.next: Node | None = None
        self.prev: Node | None = None  # Added to point to the previous node

class LinkedList:
    def __init__(self, max_size=None):
        self.head: Node | None = None  # Points to the first node
        self.tail: Node | None = None  # Points to the last node (New!)
        self.size = 0
        self.max_size = max_size  
        self.lock = threading.Lock()

    def append(self, data):
        # Validate input data (using the fix from Step 1)
        if hasattr(data, "__len__") and len(data) > 1000:  
            raise ValueError("Data size exceeds maximum limit")
            
        with self.lock:           
            if self.max_size is not None and self.size >= self.max_size:
                raise ValueError("Linked list is full")
            
            new_node = Node(data)
            
            # If the list is empty
            if self.tail is None:
                self.head = new_node
                self.tail = new_node
            else:
                # Pylance now knows for certain that self.tail is NOT None in this block
                new_node.prev = self.tail
                self.tail.next = new_node
                self.tail = new_node
                
            self.size += 1

    def print_list(self):
        current = self.head
        while current:
            print(current.data, end=" ")
            current = current.next

    def print_list_reverse(self):
        # Start at the very end of the list
        current = self.tail
        
        # Traverse backward using the prev pointers
        while current:
            print(current.data, end=" ")
            current = current.prev
        print()  # Print a new line at the end

# Test 1 - Append Multiple Data Types
# As initially designed not all data types can be added to the linked list.
# Update the code to allow for additional data types.

linked_list = LinkedList()
linked_list.append("A")
linked_list.append(1)
linked_list.append(0.1)
linked_list.print_list()

# Expected Output:
# A 1 0.1

# Test 2 - Print the Linked List in Reverse
# Write the print_list_reverse method. Once your list is doubly linked
# this should be a much easier method to write

linked_list = LinkedList()
linked_list.append("A")
linked_list.append("B")
linked_list.append(10)
linked_list.append(20)
linked_list.print_list_reverse()

# Expected Output:
# 20 10 B A

# Test 3 - Append 10,000 items rapidly
# As initially written this is a very slow process. Your updated class
# should be able to find the tail of your linked list (the last node)
# very quickly, significantly speeding up this process.
# Runtimes will vary substantially but as initially written the append method
# will take well more than a second. A refactored doubly linked list class
# should take significantly less than a second.

import time

linked_list = LinkedList()

start_time = time.perf_counter()
for i in range(10000):
    linked_list.append("A")
end_time = time.perf_counter()

print(f"Time taken: {end_time - start_time:.6f} seconds")