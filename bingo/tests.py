# ============================
# Django Test Suite for API and Models
# ============================

# Import necessary modules for testing
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile

# Import models and views for testing
from .models import Profile, Task, UserTask, Leaderboard
from .views import email_validation, get_client_ip, user_rank

# Retrieve the custom User model
User = get_user_model()

# ============================
# Client IP Address Tests
# ============================

class ClientIPTests(TestCase):
    """
    Tests the functionality of retrieving client IP addresses in different scenarios.
    """
    def setUp(self):
        self.factory = RequestFactory()

    def test_get_client_ip_with_forwarded_for(self):
        """Test if the function correctly extracts the first IP from 'X-Forwarded-For'."""
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1, 192.168.1.2'
        self.assertEqual(get_client_ip(request), '192.168.1.1')

    def test_get_client_ip_without_forwarded_for(self):
        """Test if the function correctly falls back to 'REMOTE_ADDR'."""
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '192.168.1.100'
        self.assertEqual(get_client_ip(request), '192.168.1.100')

    def test_get_client_ip_empty(self):
        """Test when there is no IP information in the request headers."""
        request = self.factory.get('/')
        request.META.pop('REMOTE_ADDR', None)
        request.META.pop('HTTP_X_FORWARDED_FOR', None)
        self.assertIsNone(get_client_ip(request))

# ============================
# User Profile Tests
# ============================

class ProfileTests(TestCase):
    """
    Tests for updating and retrieving user profiles.
    """
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

# ============================
# Email Validation Tests
# ============================

class EmailValidationTests(TestCase):
    """
    Tests for validating email addresses.
    """
    def test_email_validation_valid(self):
        """Test a valid university email address."""
        self.assertTrue(email_validation("user@exeter.ac.uk"))

    def test_email_validation_invalid_domain(self):
        """Test invalid email domains."""
        self.assertFalse(email_validation("user@gmail.com"))
        self.assertFalse(email_validation("user@exeter.com"))

# ============================
# User Registration Tests
# ============================

class RegisterUserTests(TestCase):
    """
    Tests for user registration.
    """
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('register')

    def test_register_valid_user(self):
        """Test registering a new user successfully."""
        data = {
            "username": "newuser",
            "password": "password123",
            "passwordagain": "password123",
            "email": "newuser@exeter.ac.uk",
            "gdprConsent": True
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_password_mismatch(self):
        """Test registration fails if passwords do not match."""
        data = {
            "username": "newuser",
            "password": "password123",
            "passwordagain": "password456",
            "email": "newuser@exeter.ac.uk",
            "gdprConsent": True
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

# ============================
# Task Completion Tests
# ============================

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
        self.assertIn("Task completed!", response.data["message"])
        self.leaderboard.refresh_from_db()
        self.assertEqual(self.leaderboard.points, self.task.points)

# ============================
# Leaderboard Tests
# ============================

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

# ============================
# User Rank Tests
# ============================

class UserRankTests(TestCase):
    """
    Tests the ranking system based on user points.
    """
    def test_user_rank_beginner(self):
        """Test that users with 0-49 points are ranked as 'Beginner'."""
        self.assertEqual(user_rank(10), "Beginner")
        self.assertEqual(user_rank(0), "Beginner")

    def test_user_rank_intermediate(self):
        """Test that users with 50-1250 points are ranked as 'Intermediate'."""
        self.assertEqual(user_rank(100), "Intermediate")

    def test_user_rank_expert(self):
        """Test that users with more than 1250 points are ranked as 'Expert'."""
        self.assertEqual(user_rank(1300), "Expert")
