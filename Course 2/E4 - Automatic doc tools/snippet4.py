def find_max(numbers):
    """
    Finds the largest number in a list of numbers.

    :param numbers: A non-empty list of numbers to evaluate.
    :type numbers: list of (int or float)
    :returns: The maximum number found in the list.
    :rtype: int or float
    :raises IndexError: If the input list is empty.
    """
    max_number = numbers[0]
    for number in numbers:
        if number > max_number:
            max_number = number
    return max_number