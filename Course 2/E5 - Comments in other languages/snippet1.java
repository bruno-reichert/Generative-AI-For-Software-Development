/**
 * A utility class providing an implementation of the Bubble Sort algorithm.
 * 
 * Bubble Sort is an in-place sorting algorithm that repeatedly steps through 
 * the list, compares adjacent elements, and swaps them if they are in 
 * the incorrect order.
 * 
 * @author Bruno Benno Reichert
 * @version 1.0
 */
public class BubbleSort { // In Java, all code must reside inside a class

    /**
     * Sorts an array of integers in ascending order in-place using Bubble Sort.
     *
     * @param arr the array of integers to be sorted
     */
    public static void bubbleSort(int[] arr) {
        // 'public': accessible from other classes.
        // 'static': can be called directly without creating a 'new BubbleSort()' object.
        // 'void': means this method does not return any value.
        // 'int[] arr': tells Java this method expects an array of integers as input.

        // Get the total number of elements in the array. 
        // In Java, arrays have a built-in '.length' property.
        int n = arr.length;
        
        // Outer loop: Controls how many passes we make over the array.
        // Java 'for' loop syntax: (initial variable; loop condition; step increment)
        // 'i++' is shorthand for 'i = i + 1'
        for (int i = 0; i < n; i++) {
            
            // Inner loop: Compares adjacent elements.
            // We stop at 'n - i - 1' because the last 'i' elements are already sorted.
            for (int j = 0; j < n - i - 1; j++) {
                
                // Compare the element at index 'j' with the one next to it at 'j + 1'
                if (arr[j] > arr[j + 1]) {
                    
                    // Since Java doesn't support swapping in a single line like Python,
                    // we must use a temporary variable ('temp') to safely swap them.
                    
                    int temp = arr[j];       // 1. Save the value at index j in temp
                    arr[j] = arr[j + 1];     // 2. Overwrite index j with the value at j + 1
                    arr[j + 1] = temp;       // 3. Put the saved temp value into index j + 1
                }
            }
        }
    }

    /**
     * The main entry point of the program.
     * Every standalone Java program must have a 'main' method with this exact signature.
     *
     * @param args the command-line arguments (not used)
     */
    public static void main(String[] args) {
        // Initialize an array of integers using the curly-brace shortcut syntax
        int[] arr = {64, 34, 25, 12, 22, 11, 90};
        
        // Call our static bubbleSort method, passing the array we just created
        bubbleSort(arr);
        
        // 'println' prints the text and automatically moves the cursor to a new line
        System.out.println("Sorted array is:");
        
        // Loop through the sorted array to print each element
        for (int i = 0; i < arr.length; i++) {
            // 'print' prints the value on the same line without starting a new line,
            // appending a space after each number.
            System.out.print(arr[i] + " ");
        }
    }
}