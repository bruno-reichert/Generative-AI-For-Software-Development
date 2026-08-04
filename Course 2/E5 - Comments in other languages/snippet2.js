/**
 * Sorts an array of numbers in ascending order in-place using the Bubble Sort algorithm.
 *
 * @param {number[]} arr - The array of numbers to be sorted.
 * @returns {void} This function modifies the array in-place and does not return a value.
 */
function bubbleSort(arr) {
    // Get the total number of elements in the array
    let n = arr.length;
    
    // Outer loop: Controls the number of passes over the array
    for (let i = 0; i < n; i++) {
        
        // Inner loop: Compares adjacent items, ignoring already sorted ones at the end
        for (let j = 0; j < n - i - 1; j++) {
            
            // If the left item is larger than the right, they are out of order
            if (arr[j] > arr[j + 1]) {
                
                // Save current item in a temporary variable
                let temp = arr[j];
                
                // Overwrite current item with the next item's value
                arr[j] = arr[j + 1];
                
                // Move the saved value into the next item's position
                arr[j + 1] = temp;
            }
        }
    }
}

let arr = [64, 34, 25, 12, 22, 11, 90];
console.log("Unsorted array:", arr);
bubbleSort(arr);
console.log("Sorted array is:", arr);