# Django Test Suite for API and Models
# Run Test: python manage.py test

from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework import status
from rest_framework.test import APIClient

from unittest.mock import patch, mock_open, MagicMock

# Import models and views for testing
from bingo.models import Profile, Task, UserTask, Leaderboard
from bingo.views import user_rank, load_initial_tasks, login_user, tasks, get_user_profile, check_developer_role

import os
import json

# Retrieve the custom User model
User = get_user_model()


# Load Initial Tasks Tests

class LoadInitialTasksTestCase(TestCase):
    @patch("builtins.open", new_callable=mock_open, read_data='[{"pk": 2, "fields": {"description": "New Task", "points": 15, "requires_upload": false, "requires_scan": true}}]')
    @patch("os.path.join", return_value="mocked_path/initial_data.json")
    @patch("bingo.models.Task.objects.exists", return_value=False)
    @patch("bingo.models.Task.objects.create")
    def test_load_initial_tasks(self, mock_create, mock_exists, mock_path, mock_file):
        """Test loading initial tasks when no tasks exist"""
        load_initial_tasks()
        mock_create.assert_called_once_with(
            id=2,
            description="New Task",
            points=15,
            requires_upload=False,
            requires_scan=True
        )
        self.assertTrue(mock_create.called)

    @patch("builtins.open", new_callable=mock_open, read_data='[]')
    @patch("os.path.join", return_value="mocked_path/initial_data.json")
    @patch("bingo.models.Task.objects.exists", return_value=False)
    @patch("bingo.models.Task.objects.create")
    def test_load_initial_tasks_empty_file(self, mock_create, mock_exists, mock_path, mock_file):
        """Test loading initial tasks when JSON file is empty"""
        load_initial_tasks()
        mock_create.assert_not_called()

    @patch("os.path.join", return_value="mocked_path/initial_data.json")
    @patch("bingo.models.Task.objects.exists", return_value=True)
    @patch("builtins.open", new_callable=mock_open)
    def test_load_initial_tasks_already_exists(self, mock_file, mock_exists, mock_path):
        """Test loading initial tasks when tasks already exist"""
        load_initial_tasks()
        mock_file.assert_not_called()


# User Profile Tests

class ProfileTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="profileuser", email="profile@exeter.ac.uk", password="testpass")
        self.client.force_authenticate(user=self.user)
        Profile.objects.create(user=self.user)

    def test_update_user_profile(self):
        """Test updating the user's username."""
        url = reverse('update_user_profile')
        data = {"username": "updateduser"}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "updateduser")

    def test_update_user_profile_with_picture(self):
        """Test updating the user's profile picture."""
        url = reverse('update_user_profile')
        image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        data = {"profile_picture": image}
        response = self.client.put(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        profile = Profile.objects.get(user=self.user)
        self.assertTrue(profile.profile_picture)

    def test_update_user_profile_unsupported_picture_format(self):
        """Test updating the profile with an unsupported image format."""
        url = reverse('update_user_profile')
        unsupported_image = SimpleUploadedFile("test.gif", b"file_content", content_type="image/gif")
        data = {"profile_picture": unsupported_image}
        response = self.client.put(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

# User Registration Tests

class RegisterUserTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('register_user')

    def test_register_valid_user(self):
        """Test registering a valid user."""
        data = {
            "username": "newuser",
            "password": "Str0ngP@ssw0rd123",
            "passwordagain": "Str0ngP@ssw0rd123",
            "email": "newuser@example.com",
            "gdprConsent": True
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_password_mismatch(self):
        """Test registering a user with mismatched passwords."""
        data = {
            "username": "newuser",
            "password": "Str0ngP@ssw0rd123",
            "passwordagain": "DifferentP@ss456",
            "email": "newuser@example.com",
            "gdprConsent": True
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_fields(self):
        """Test registering a user with missing required fields."""
        data = {"username": "user1"}  
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_existing_username(self):
        """Test registering a user with an already existing username."""
        User.objects.create_user(username="existinguser", email="existing@example.com", password="password123")
        data = {
            "username": "existinguser",
            "password": "Str0ngP@ssw0rd123",
            "passwordagain": "Str0ngP@ssw0rd123",
            "email": "newuser@example.com",
            "gdprConsent": True
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_existing_email(self):
        """Test registering a user with an already existing email."""
        User.objects.create_user(username="user2", email="existing@example.com", password="Str0ngP@ssw0rd123")
        data = {
            "username": "newuser",
            "password": "Str0ngP@ssw0rd123",
            "passwordagain": "Str0ngP@ssw0rd123",
            "email": "existing@example.com",
            "gdprConsent": True
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_without_gdpr_consent(self):
        """Test registering a user without GDPR consent."""
        data = {
            "username": "newuser",
            "password": "Str0ngP@ssw0rd123",
            "passwordagain": "Str0ngP@ssw0rd123",
            "email": "newuser@example.com",
            "gdprConsent": False
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

# User Login Tests

class LoginUserTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='Str0ngP@ssw0rd123')

    def test_login_user_success(self):
        """Test logging in with correct credentials."""
        response = self.client.post(reverse('login_user'), {"username": "testuser", "password": "Str0ngP@ssw0rd123"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.json())
        self.assertIn("refresh", response.json())

    def test_login_user_invalid_credentials(self):
        """Test logging in with incorrect password."""
        response = self.client.post(reverse('login_user'), {"username": "testuser", "password": "wrongpassword"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()["error"], "Invalid username or password")

    def test_login_user_missing_fields(self):
        """Test logging in with missing fields."""
        response = self.client.post(reverse('login_user'), {"username": ""}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["error"], "Username and password are required.")

    def test_login_user_nonexistent_username(self):
        """Test logging in with a username that does not exist."""
        response = self.client.post(reverse('login_user'), {"username": "nonexistent", "password": "Str0ngP@ssw0rd123"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()["error"], "Invalid username or password")

    def test_login_user_blank_password(self):
        """Test logging in with a blank password."""
        response = self.client.post(reverse('login_user'), {"username": "testuser", "password": ""}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["error"], "Username and password are required.")

    def test_login_user_case_sensitivity(self):
        """Test login with different case in username."""
        response = self.client.post(reverse('login_user'), {"username": "TESTUSER", "password": "Str0ngP@ssw0rd123"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()["error"], "Invalid username or password")

# Task Tests

class TasksTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='Str0ngP@ssw0rd123')
        self.task = Task.objects.create(id=1, description='Test Task', points=10, requires_upload=False, requires_scan=False)

    @patch("bingo.views.load_initial_tasks", autospec=True)
    def test_tasks_retrieval(self, mock_load_initial_tasks):
        """Test retrieving tasks and ensuring task preloading is called."""
        mock_load_initial_tasks.return_value = None  
        response = self.client.get(reverse('tasks'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.json()), 1)
        self.assertTrue(mock_load_initial_tasks.called) 

    @patch("bingo.views.load_initial_tasks", autospec=True)
    def test_tasks_retrieval_no_tasks(self, mock_load_initial_tasks):
        """Test retrieving tasks when no tasks exist in the database."""
        Task.objects.all().delete()
        response = self.client.get(reverse('tasks'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 0)

    @patch("bingo.views.load_initial_tasks", autospec=True)
    def test_tasks_retrieval_error_handling(self, mock_load_initial_tasks):
        """Test error handling when an exception occurs in task retrieval."""
        mock_load_initial_tasks.side_effect = Exception("Task loading error")
        with self.assertRaises(Exception) as context:
            self.client.get(reverse('tasks'))
        self.assertEqual(str(context.exception), "Task loading error")

# Task Completion Tests

class CompleteTaskTests(TestCase):
    """
    Tests for completing tasks and updating leaderboard scores.
    """
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="taskuser", email="task@exeter.ac.uk", password="testpass")
        self.client.force_authenticate(user=self.user)
        self.task = Task.objects.create(description="Test Task", points=10)
        self.leaderboard = Leaderboard.objects.create(user=self.user, points=0)

    def test_complete_task_success(self):
        """Test successfully completing a task."""
        url = reverse('complete_task')
        data = {"task_id": self.task.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Task submitted successfully and awaiting GameKeeper approval!", response.data["message"])
        #self.leaderboard.refresh_from_db()
        #self.assertEqual(self.leaderboard.points, self.task.points)

    def test_complete_task_already_completed(self):
        """Test completing a task that was already completed."""
        UserTask.objects.create(user=self.user, task=self.task, completed=True)
        url = reverse('complete_task')
        data = {"task_id": self.task.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Task already completed and approved!", response.data["message"])


# Leaderboard Tests

class LeaderboardTests(TestCase):
    """
    Tests for retrieving and ordering leaderboard entries.
    """
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username="leaderuser1", email="leader1@exeter.ac.uk", password="testpass")
        self.user2 = User.objects.create_user(username="leaderuser2", email="leader2@exeter.ac.uk", password="testpass")
        self.client.force_authenticate(user=self.user1)
        Leaderboard.objects.create(user=self.user1, points=100)
        Leaderboard.objects.create(user=self.user2, points=200)

    def test_leaderboard_ordering(self):
        """Test if the leaderboard is sorted correctly."""
        url = reverse('leaderboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data[0]["points"], response.data[1]["points"])

    def test_leaderboard_empty(self):
        """Test leaderboard when no users exist."""
        Leaderboard.objects.all().delete()
        url = reverse('leaderboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_leaderboard_ties(self):
        """Test leaderboard when multiple users have the same score."""
        user3 = User.objects.create_user(username="leaderuser3", email="leader3@exeter.ac.uk", password="testpass")
        Leaderboard.objects.create(user=user3, points=200)
        url = reverse('leaderboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["points"], response.data[1]["points"])

# Check Developer Role Tests

class CheckDeveloperRoleTestCase(TestCase):
    """
    Tests for checking the developer role status of a user.
    """
    def setUp(self):
        self.client = APIClient()
        self.developer_user = User.objects.create_user(username='developeruser', email='dev@example.com', password='password123', role='Developer')
        self.regular_user = User.objects.create_user(username='regularuser', email='user@example.com', password='password123', role='User')

    def test_check_developer_role_true(self):
        """Test if a user with Developer role is correctly identified."""
        self.client.force_authenticate(user=self.developer_user)
        response = self.client.get(reverse('check_developer_role'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["is_developer"])

    def test_check_developer_role_false(self):
        """Test if a user without Developer role is correctly identified."""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(reverse('check_developer_role'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.json()["is_developer"])

#Retrieve User Profile Test

class GetUserProfileTestCase(TestCase):
    """
    Tests for retrieving user profile details.
    """
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')
        self.profile = Profile.objects.create(user=self.user, rank="Intermediate")
        self.leaderboard = Leaderboard.objects.create(user=self.user, points=51)
        self.client.force_authenticate(user=self.user)

    def test_get_user_profile(self):
        """Test retrieving user profile details."""
        response = self.client.get(reverse('get_user_profile'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["username"], "testuser")
        self.assertEqual(response.json()["email"], "test@example.com")
        self.assertEqual(response.json()["total_points"], 51)
        self.assertEqual(response.json()["rank"], "Intermediate")

    def test_get_user_profile_no_leaderboard_entry(self):
        """Test retrieving user profile when leaderboard entry does not exist."""
        Leaderboard.objects.filter(user=self.user).delete()
        response = self.client.get(reverse('get_user_profile'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["total_points"], 0)
        self.assertEqual(response.json()["rank"], "Beginner")

# User Rank Tests

class UserRankTests(TestCase):
    """
    Tests the ranking system based on user points.
    """
    def test_user_rank_beginner(self):
        """Test that users with 0-50 points are ranked as 'Beginner'."""
        self.assertEqual(user_rank(10), "Beginner")
        self.assertEqual(user_rank(0), "Beginner")
        self.assertEqual(user_rank(49), "Beginner")

    def test_user_rank_intermediate(self):
        """Test that users with 51-1250 points are ranked as 'Intermediate'."""
        self.assertEqual(user_rank(50), "Intermediate")
        self.assertEqual(user_rank(99), "Intermediate")
        self.assertEqual(user_rank(99), "Intermediate")

    def test_user_rank_expert(self):
        """Test that users with more than 1251 points are ranked as 'Expert'."""
        self.assertEqual(user_rank(100), "Expert")
        self.assertEqual(user_rank(5000), "Expert")
        self.assertEqual(user_rank(1251), "Expert")

    def test_user_rank_boundary_cases(self):
        """Test boundary cases to ensure correct ranking transitions."""
        self.assertEqual(user_rank(49), "Beginner")
        self.assertEqual(user_rank(50), "Intermediate")
        self.assertEqual(user_rank(99), "Intermediate")
        self.assertEqual(user_rank(100), "Expert")