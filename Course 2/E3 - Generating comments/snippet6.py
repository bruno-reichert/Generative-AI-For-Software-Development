def bubble_sort(arr):
    """
    Sort an array in ascending order using the bubble sort algorithm.

    This is an in-place sorting algorithm that repeatedly steps through 
    the list, compares adjacent elements, and swaps them if they are in 
    the incorrect order.

    :param arr: The list of comparable elements to be sorted in-place.
    :type arr: list
    :returns: The sorted list (the same list object passed as the parameter).
    :rtype: list
    """
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr