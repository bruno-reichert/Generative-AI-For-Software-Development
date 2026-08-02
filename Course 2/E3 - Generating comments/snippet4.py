def find_max(numbers):
    """
    Finds the largest number in a list of numbers.

    Args:
        numbers (list of (int or float)): A non-empty list of numbers.

    Returns:
        int or float: The maximum number found in the list.

    Raises:
        IndexError: If the input list is empty.
    """
    max_number = numbers[0]
    for number in numbers:
        if number > max_number:
            max_number = number
    return max_number