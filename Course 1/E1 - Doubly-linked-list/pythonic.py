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
        self.lock = threading.RLock()

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

    def __iter__(self):
        """Allows 'for data in linked_list:' forward iteration."""
        with self.lock:
            current = self.head
            while current:
                yield current.data
                current = current.next

    def __reversed__(self):
        """Allows 'for data in reversed(linked_list):' backward iteration."""
        with self.lock:
            current = self.tail
            while current:
                yield current.data
                current = current.prev

    def __len__(self):
        """Allows 'len(linked_list)' to retrieve size."""
        with self.lock:
            return self.size

    def __repr__(self):
        """Provides an official string representation of the object."""
        with self.lock:
            # We can use our new __iter__ internally to collect the elements
            elements = list(self)
            return f"LinkedList({elements})"

    def __contains__(self, item):
        """Allows 'if "A" in linked_list:' syntax."""
        with self.lock:
            current = self.head
            while current:
                if current.data == item:
                    return True
                current = current.next
            return False

# Creating the list
linked_list = LinkedList()
linked_list.append("A")
linked_list.append("B")
linked_list.append(10)

# Native Python interactions:
print(linked_list)                   # Output: LinkedList(['A', 'B', 10])
print(len(linked_list))              # Output: 3
print("B" in linked_list)            # Output: True

# Native iteration:
for item in linked_list:
    print(item)

# Native reverse iteration:
for item in reversed(linked_list):
    print(item)