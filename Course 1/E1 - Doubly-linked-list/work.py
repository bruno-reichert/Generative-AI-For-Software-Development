"""
This module provides a thread-safe implementation of a Doubly Linked List.

A doubly linked list is a linear data structure where each element (Node) 
contains a reference to both the next node and the previous node. This allows 
for efficient bidirectional traversal and constant-time O(1) appends.
"""

import threading  # Used to make the LinkedList class thread-safe
import time       # Used for performance testing


class Node:
    """
    Represents a single node in a doubly linked list.

    Attributes:
        data: The value stored within the node (can be of any type).
        next (Node | None): Reference to the next node in the list.
        prev (Node | None): Reference to the previous node in the list.
    """

    def __init__(self, data):
        """Initializes a Node with data and empty next/prev pointers."""
        self.data = data
        # Type hints let tools like Pylance know these can be Node objects or None
        self.next: Node | None = None
        self.prev: Node | None = None


class LinkedList:
    """
    A thread-safe Doubly Linked List.

    Supports O(1) appends at the tail and bidirectional traversal.

    Attributes:
        head (Node | None): The first node in the list.
        tail (Node | None): The last node in the list.
        size (int): The current number of nodes in the list.
        max_size (int | None): The maximum capacity allowed, or None for unlimited.
        lock (threading.Lock): Mutex lock used to ensure thread safety.
    """

    def __init__(self, max_size=None):
        """Initializes an empty Doubly Linked List with optional size limit."""
        self.head: Node | None = None
        self.tail: Node | None = None
        self.size = 0
        self.max_size = max_size  
        self.lock = threading.Lock()

    def append(self, data):
        """
        Appends a new node containing data to the end of the list.

        This method is thread-safe and runs in O(1) time.

        Args:
            data: The value to append to the list.

        Raises:
            ValueError: If the data size exceeds 1000 items (for sequence types).
            ValueError: If the list is full based on max_size limits.
        """
        # Validate input data size only if the data type supports the len() function
        if hasattr(data, "__len__") and len(data) > 1000:  
            raise ValueError("Data size exceeds maximum limit")
            
        # Acquire the lock to ensure only one thread modifies the structure at a time
        with self.lock:           
            if self.max_size is not None and self.size >= self.max_size:
                raise ValueError("Linked list is full")
            
            new_node = Node(data)
            
            # If the list is empty, the new node becomes both the head and the tail
            if self.tail is None:
                self.head = new_node
                self.tail = new_node
            else:
                # If the list has nodes, link the new node to the current tail
                new_node.prev = self.tail  # Set backward link from new node to old tail
                self.tail.next = new_node  # Set forward link from old tail to new node
                self.tail = new_node       # Reassign the tail pointer to the new node
                
            self.size += 1

    def print_list(self):
        """Prints the elements of the list sequentially from head to tail."""
        current = self.head
        while current:
            print(current.data, end=" ")
            current = current.next

    def print_list_reverse(self):
        """Prints the elements of the list in reverse order from tail to head."""
        # Start traversal from the tail
        current = self.tail
        
        # Follow the prev pointers backward
        while current:
            print(current.data, end=" ")
            current = current.prev
        print()  # Ensure a newline is printed at the end of the output


# =====================================================================
# Verification and Tests
# =====================================================================

# Test 1 - Append Multiple Data Types
# Verifies that integers, floats, and strings can all be appended safely.
print("--- Test 1: Appending Multiple Data Types ---")
linked_list = LinkedList()
linked_list.append("A")
linked_list.append(1)
linked_list.append(0.1)
linked_list.print_list()
print("\nExpected Output: A 1 0.1\n")


# Test 2 - Print the Linked List in Reverse
# Verifies that the backward traversal utilizing prev pointers works.
print("--- Test 2: Printing in Reverse ---")
linked_list = LinkedList()
linked_list.append("A")
linked_list.append("B")
linked_list.append(10)
linked_list.append(20)
linked_list.print_list_reverse()
print("Expected Output: 20 10 B A\n")


# Test 3 - Append 10,000 items rapidly
# Measures execution time to ensure O(1) performance of the refactored append.
print("--- Test 3: Rapid Appends Performance Test ---")
linked_list = LinkedList()

start_time = time.perf_counter()
for i in range(10000):
    linked_list.append("A")
end_time = time.perf_counter()

print(f"Time taken: {end_time - start_time:.6f} seconds")