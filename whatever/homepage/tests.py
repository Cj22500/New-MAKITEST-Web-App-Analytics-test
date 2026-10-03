from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class SignUpTests(TestCase):
    def test_signup_page_renders(self):
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create your account")
        # Both password fields must be present exactly once: a stray {{ form }}
        # in the template once rendered the whole form a second time.
        self.assertEqual(response.content.count(b'name="password1"'), 1)
        self.assertEqual(response.content.count(b'name="password2"'), 1)

    def test_signup_creates_account_and_redirects_to_login(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "student1",
                "email": "student1@htw-berlin.de",
                "role": "student",
                "password1": "exam-Pass-2026",
                "password2": "exam-Pass-2026",
            },
        )
        self.assertRedirects(response, reverse("login"))

        user = User.objects.get(username="student1")
        self.assertEqual(user.email, "student1@htw-berlin.de")
        # Signing up must not sign you in — the login step is the next one.
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_signup_rejects_mismatched_passwords(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "student2",
                "email": "student2@htw-berlin.de",
                "role": "student",
                "password1": "exam-Pass-2026",
                "password2": "different-Pass-2026",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="student2").exists())

    def test_signup_rejects_duplicate_email(self):
        User.objects.create_user("taken", "shared@htw-berlin.de", "exam-Pass-2026")
        response = self.client.post(
            reverse("signup"),
            {
                "username": "student3",
                "email": "shared@htw-berlin.de",
                "role": "student",
                "password1": "exam-Pass-2026",
                "password2": "exam-Pass-2026",
            },
        )
        self.assertContains(response, "already exists")
        self.assertFalse(User.objects.filter(username="student3").exists())


class LoginTests(TestCase):
    def setUp(self):
        self.password = "exam-Pass-2026"
        self.user = User.objects.create_user(
            "student1", "student1@htw-berlin.de", self.password
        )

    def test_login_with_registered_credentials(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "student1",
                "password": self.password,
            },
        )
        self.assertRedirects(response, reverse("student_home"))
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.user.pk)

    def test_login_with_wrong_password_fails(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "student1",
                "password": "not-the-password",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_honours_safe_next(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "student1",
                "password": self.password,
                "next": reverse("my_scores"),
            },
        )
        self.assertRedirects(response, reverse("my_scores"))

    def test_login_ignores_offsite_next(self):
        """An open redirect here would let someone bounce a student off-site."""
        response = self.client.post(
            reverse("login"),
            {
                "username": "student1",
                "password": self.password,
                "next": "https://example.com/phish",
            },
        )
        self.assertRedirects(response, reverse("student_home"))

    def test_logout_requires_post(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)
        self.assertRedirects(
            self.client.post(reverse("logout")), reverse("landing_page")
        )
        self.assertNotIn("_auth_user_id", self.client.session)


class StudentAccessTests(TestCase):
    """Every student page, including the proctoring view, requires a login."""

    protected = ("student_home", "exam_details", "home")

    def test_anonymous_is_redirected_to_login(self):
        for name in self.protected:
            with self.subTest(view=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertRedirects(response, f"{reverse('login')}?next={url}")

    def test_signed_in_student_requires_exam_context_for_setup(self):
        user = User.objects.create_user(
            "student1", "student1@htw-berlin.de", "exam-Pass-2026"
        )
        self.client.force_login(user)
        self.assertEqual(self.client.get(reverse("student_home")).status_code, 200)
        self.assertEqual(self.client.get(reverse("exam_details")).status_code, 404)
        self.assertEqual(self.client.get(reverse("home")).status_code, 404)
