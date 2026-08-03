def bubble_sort(arr):
    """
    Sort an array in ascending order using the bubble sort algorithm.

    This is an in-place sorting algorithm that repeatedly steps through 
    the list, compares adjacent elements, and swaps them if they are in 
    the incorrect order.

    :param arr: The list of comparable elements to be sorted in-place.
    :type arr: list
    :returns: The sorted list.
    :rtype: list
    """
    # Get the total number of elements in the array
    n = len(arr)
    
    # Outer loop: Controls how many passes we make over the array.
    # Each pass guarantees that the next largest element finds its correct position.
    for i in range(n):
        
        # Inner loop: Compares adjacent elements.
        # We stop at 'n - i - 1' because the last 'i' elements have already
        # been sorted and placed in their final positions in previous passes.
        for j in range(0, n - i - 1):
            
            # Compare the current element with its neighbor on the right
            if arr[j] > arr[j + 1]:
                
                # If the left element is larger than the right, swap them.
                # Python allows us to swap variables in one line without a temporary variable.
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                
    # Return the fully sorted array
    return arr