import unittest
from one_correct import TaskManager

class TestTaskManager(unittest.TestCase):

    def setUp(self):
        """Runs before EVERY test. Instantiates a fresh, isolated manager."""
        self.manager = TaskManager()

    def test_add_valid_task(self):
        """Test that we can add a normal task successfully."""
        result = self.manager.add_task("Buy groceries")
        self.assertIn("Buy groceries", result)
        self.assertEqual(len(result), 1)

    def test_add_empty_task_raises_error(self):
        """Test that adding an empty string raises a ValueError."""
        with self.assertRaises(ValueError):
            self.manager.add_task("")

    def test_add_whitespace_task_should_raise_error(self):
        """Test that adding a whitespace-only task correctly raises a ValueError."""
        with self.assertRaises(ValueError):
            self.manager.add_task("   ")

    def test_remove_nonexistent_task_should_raise_error(self):
        """Test that removing a missing task raises a ValueError."""
        # Add a dummy task first
        self.manager.add_task("Wash car")
        with self.assertRaises(ValueError):
            self.manager.remove_task("Clean room")

    def test_remove_valid_task(self):
        """Test that we can successfully remove an existing task."""
        self.manager.add_task("Read book")
        result = self.manager.remove_task("Read book")
        self.assertNotIn("Read book", result)
        self.assertEqual(len(result), 0)


if __name__ == "__main__":
    unittest.main()