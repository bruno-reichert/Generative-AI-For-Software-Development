class TaskManager:
    """
    Manages a simple list of tasks.
    
    This class is encapsulated, preventing global state contamination 
    and ensuring consistent, predictable error handling.
    """

    def __init__(self):
        # State is now safely contained inside each instance of TaskManager
        self.tasks = []

    def add_task(self, task):
        """Adds a task after validating that it is not empty or whitespace."""
        # Check if the task is None, empty, or consists only of spaces
        if not task or not task.strip():
            raise ValueError("Task cannot be empty.")
            
        self.tasks.append(task)
        return self.tasks

    def remove_task(self, task):
        """Removes a task from the list. Raises ValueError if missing."""
        if task in self.tasks:
            self.tasks.remove(task)
            return self.tasks
        else:
            # Consistent API: Raising an exception on failure
            raise ValueError("Task not found.")

    def list_tasks(self):
        """Returns the current list of tasks."""
        return self.tasks

    def clear_tasks(self):
        """Clears all tasks from the list without side-effects."""
        self.tasks.clear()
        return "Tasks cleared."