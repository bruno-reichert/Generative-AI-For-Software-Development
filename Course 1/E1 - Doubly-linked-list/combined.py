"""
This module provides a production-grade, thread-safe, and highly pythonic 
implementation of a Doubly Linked List.

By combining robust concurrency protections (RLock) with standard Python dunder 
protocols, this implementation behaves like a built-in Python collection while 
remaining safe for multi-threaded execution.
"""

import threading
import time


class Node:
    """
    Represents an individual node within a doubly linked list.

    Attributes:
        data: The value stored within the node (any Python object).
        next (Node | None): Link to the next node in sequence.
        prev (Node | None): Link to the previous node in sequence.
    """

    def __init__(self, data):
        self.data = data
        self.next: Node | None = None
        self.prev: Node | None = None


class LinkedList:
    """
    A thread-safe, double-linked list supporting native Python protocols.

    Implements standard iteration, length tracking, membership testing, 
    and efficient O(1) tail insertion.

    Attributes:
        head (Node | None): The first node in the list.
        tail (Node | None): The last node in the list.
        size (int): Current count of nodes.
        max_size (int | None): Capacity limit, or None if unlimited.
        lock (threading.RLock): Reentrant lock for safe multi-threaded mutations.
    """

    def __init__(self, max_size=None):
        self.head: Node | None = None
        self.tail: Node | None = None
        self.size = 0
        self.max_size = max_size  
        # Using RLock to support reentrant dunder operations safely (e.g., __repr__)
        self.lock = threading.RLock()

    def append(self, data):
        """
        Appends data to the tail of the list in O(1) time.

        Args:
            data: The value to append.

        Raises:
            ValueError: If the data size exceeds 1000 items (for sequence types).
            ValueError: If the list has reached its max_size capacity.
        """
        # Validate data size outside of the lock to minimize contention
        if hasattr(data, "__len__") and len(data) > 1000:  
            raise ValueError("Data size exceeds maximum limit")
            
        with self.lock:           
            if self.max_size is not None and self.size >= self.max_size:
                raise ValueError("Linked list is full")
            
            new_node = Node(data)
            
            # Identify if list is empty by checking tail (satisfies type checkers)
            if self.tail is None:
                self.head = new_node
                self.tail = new_node
            else:
                new_node.prev = self.tail
                self.tail.next = new_node
                self.tail = new_node
                
            self.size += 1

    def __iter__(self):
        """Allows forward iteration (e.g., 'for x in linked_list:')."""
        with self.lock:
            current = self.head
            while current:
                yield current.data
                current = current.next

    def __reversed__(self):
        """Allows backward iteration (e.g., 'for x in reversed(linked_list):')."""
        with self.lock:
            current = self.tail
            while current:
                yield current.data
                current = current.prev

    def __len__(self):
        """Allows query using 'len(linked_list)'."""
        with self.lock:
            return self.size

    def __repr__(self):
        """Provides a clear, print-friendly representation of the object."""
        with self.lock:
            # Safely triggers __iter__ internally without deadlocking due to RLock
            elements = list(self)
            return f"LinkedList({elements})"

    def __contains__(self, item):
        """Allows search using the 'in' operator (e.g., 'if item in linked_list:')."""
        with self.lock:
            current = self.head
            while current:
                if current.data == item:
                    return True
                current = current.next
            return False


# =====================================================================
# Lead Programmer's Verified Test Suite
# =====================================================================

# Test 1 - Append and Print Multiple Data Types Natively
print("--- Test 1: Native Print & Multi-Type Support ---")
linked_list = LinkedList()
linked_list.append("A")
linked_list.append(1)
linked_list.append(0.1)

# Using standard print triggers __repr__ under the hood
print(linked_list)                   
print("Expected Output: LinkedList(['A', 1, 0.1])\n")


# Test 2 - Print the Linked List in Reverse utilizing the reversed protocol
print("--- Test 2: Native Reverse Iteration ---")
linked_list = LinkedList()
linked_list.append("A")
linked_list.append("B")
linked_list.append(10)
linked_list.append(20)

# Print components utilizing Pythonic unpacking and reversed iterator
print(*(item for item in reversed(linked_list)))
print("Expected Output: 20 10 B A\n")


# Test 3 - Performance benchmark with 10,000 rapid appends
print("--- Test 3: Rapid Appends Performance Test ---")
benchmark_list = LinkedList()

start_time = time.perf_counter()
for i in range(10000):
    benchmark_list.append("A")
end_time = time.perf_counter()

print(f"Time taken: {end_time - start_time:.6f} seconds")
print(f"Final list size: {len(benchmark_list)} items")