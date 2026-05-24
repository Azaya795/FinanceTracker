import os
import unittest

# Configure the application to use a local SQLite database for test isolation
os.environ['SQLITE_DB'] = 'test.db'
# Ensure PostgreSQL credentials are wiped during testing so it always uses SQLite
os.environ.pop('DB_HOST', None)

from app.app import app, init_db, execute_query

class FlaskAppTestCase(unittest.TestCase):

    def setUp(self):
        """Set up test client and initialize the database schema."""
        self.app = app.test_client()
        self.app.testing = True
        
        # Initialize database schema before each test
        init_db()

    def tearDown(self):
        """Clean up database tables and remove the test file after each test."""
        try:
            execute_query("DROP TABLE IF EXISTS tasks", commit=True)
        except Exception:
            pass
        # Remove the test SQLite file to guarantee clean states between runs
        if os.path.exists('test.db'):
            try:
                os.remove('test.db')
            except OSError:
                pass

    def test_home_page(self):
        """Test that the index home page loads correctly."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'SWE 2026', response.data)
        self.assertIn(b'MVP Template', response.data)

    def test_health_endpoint(self):
        """Test the Docker/orchestration health check api."""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['database'], 'active')

    def test_get_tasks_empty(self):
        """Test retrieving tasks when database is empty."""
        response = self.app.get('/api/tasks')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 0)

    def test_create_task_success(self):
        """Test successfully creating a new task entry."""
        payload = {
            "title": "Build Test Suite",
            "description": "Ensure code coverage is greater than 70%."
        }
        response = self.app.post('/api/tasks', json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['message'], "Task created successfully")

        # Verify task is inside database
        tasks = execute_query("SELECT title, description, status FROM tasks")
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]['title'], "Build Test Suite")
        self.assertEqual(tasks[0]['description'], "Ensure code coverage is greater than 70%.")
        self.assertEqual(tasks[0]['status'], "todo")

    def test_create_task_validation_error(self):
        """Test input validation on task creation."""
        # Test case: Empty title
        payload = {
            "title": "  ",
            "description": "Should fail validation."
        }
        response = self.app.post('/api/tasks', json=payload)
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data['error'], "Title is required")

    def test_toggle_task_status(self):
        """Test securely toggling a task status between 'todo' and 'done'."""
        # Insert initial task
        execute_query(
            "INSERT INTO tasks (title, description, status) VALUES (?, ?, ?)",
            ("Sample Task", "For toggling", "todo"),
            commit=True
        )
        tasks = execute_query("SELECT id, status FROM tasks")
        task_id = tasks[0]['id']
        self.assertEqual(tasks[0]['status'], "todo")

        # Toggle to 'done'
        response = self.app.post(f'/api/tasks/{task_id}/toggle')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], "Task marked as done")

        # Check in DB
        db_tasks = execute_query("SELECT status FROM tasks WHERE id = ?", (task_id,))
        self.assertEqual(db_tasks[0]['status'], "done")

        # Toggle back to 'todo'
        response = self.app.post(f'/api/tasks/{task_id}/toggle')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], "Task marked as todo")

        db_tasks = execute_query("SELECT status FROM tasks WHERE id = ?", (task_id,))
        self.assertEqual(db_tasks[0]['status'], "todo")

    def test_toggle_nonexistent_task(self):
        """Test toggling a task ID that doesn't exist."""
        response = self.app.post('/api/tasks/9999/toggle')
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertEqual(data['error'], "Task not found")

    def test_delete_task_success(self):
        """Test deleting a task entry successfully."""
        # Insert initial task
        execute_query(
            "INSERT INTO tasks (title, description, status) VALUES (?, ?, ?)",
            ("Task to delete", "Will be removed", "todo"),
            commit=True
        )
        tasks = execute_query("SELECT id FROM tasks")
        task_id = tasks[0]['id']

        # Delete task
        response = self.app.delete(f'/api/tasks/{task_id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], "Task deleted successfully")

        # Verify database is empty
        db_tasks = execute_query("SELECT id FROM tasks")
        self.assertEqual(len(db_tasks), 0)

    def test_delete_nonexistent_task(self):
        """Test deleting a task ID that doesn't exist."""
        response = self.app.delete('/api/tasks/9999')
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertEqual(data['error'], "Task not found")

if __name__ == '__main__':
    unittest.main()
