"""
This is the test file contains all
test cases of modules, views, middleware
"""
import unittest
from django.core import mail
from django.test import TestCase, modify_settings
from selenium import webdriver
from survey.models import Organization, Employee, User, Question


@modify_settings(MIDDLEWARE_CLASSES={
        'append': 'django.middleware.cache.FetchFromCacheMiddleware',
        'prepend': 'django.middleware.cache.UpdateCacheMiddleware',
})
class MiddlewareTestCase(TestCase):
    """
    This is Middleware Test Case
    """

    @modify_settings(MIDDLEWARE_CLASSES={
        'append': 'django.middleware.cache.FetchFromCacheMiddleware',
        'prepend': 'django.middleware.cache.UpdateCacheMiddleware',
    })
    def test_cache_middleware(self):
        """
        Testing middleware cache
        """
        with self.modify_settings(MIDDLEWARE_CLASSES={
                'append': 'django.middleware.cache.FetchFromCacheMiddleware',
                'prepend': 'django.middleware.cache.UpdateCacheMiddleware',
                'remove': [
                    'django.contrib.sessions.middleware.SessionMiddleware',
                    'django.contrib.auth.middleware.AuthenticationMiddleware',
                    'django.contrib.messages.middleware.MessageMiddleware',
                ],
        }):
            self.client.get('/')


class EmailTest(TestCase):
    """
    This is Email Test Case
    """
    def test_send_email(self):
        """
        Testing outbox sending count
        """
        # Send message.
        mail.send_mail('Subject here', 'Here is the message.',
                       'from@example.com', ['to@example.com'],
                       fail_silently=False)

        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)

        # Verify that the subject of the first message is correct.
        self.assertEqual(mail.outbox[0].subject, 'Subject here')


class ModelsTest(TestCase):
    """
    Model Test Cases
    """

    @staticmethod
    def create_organization(company_name='Harbinger',
                            location='Pune', description='Innovate'):
        """
        Method for create organization
        :param company_name:
        :param location:
        :param description:
        """
        return Organization.objects.create(company_name=company_name,
                                           location=location, description=description)

    @staticmethod
    def create_employee(emp_name='shradha',
                        emp_username='shradha@gmail.com',
                        emp_password='Shradha@1234',
                        emp_designation='Software Engineer',
                        emp_address='Pune', organization=None):
        """
        Method for create employee
        :param emp_name:
        :param emp_username:
        :param emp_password:
        :param emp_designation:
        :param emp_address:
        :param organization:
        """
        return Employee.objects.create(emp_name=emp_name,
                                       emp_username=emp_username,
                                       emp_password=emp_password,
                                       emp_designation=emp_designation,
                                       emp_address=emp_address,
                                       organization=organization)

    @staticmethod
    def create_user(organization=None, is_active=True, is_staff=False):
        """
        Method for create user
        :param organization:
        :param is_active:
        :param is_staff:
        """
        return User.objects.create(organization=organization,
                                   is_active=is_active,
                                   is_staff=is_staff)

    @staticmethod
    def create_question(question='How was CSR ?',
                        is_required=True, question_type='text',
                        choices='good, bad, very good',
                        organization=Organization.objects.get(id=1)):
        """
        Method for create question
        :param question:
        :param is_required:
        :param question_type:
        :param choices:
        :param organization:
        """
        return Question.objects.create(question=question,
                                       is_required=is_required,
                                       question_type=question_type,
                                       choices=choices,
                                       organization=organization)

    def test_all(self):
        """
        testing all test cases simultaneously
        """
        org = self.create_organization()
        self.assertTrue(isinstance(org, Organization))
        self.assertEqual(org.__str__(), org.company_name)

        emp = self.create_employee()
        self.assertTrue(isinstance(emp, Employee))
        self.assertEqual(emp.__str__(), emp.emp_name)
        self.assertEqual(str(Employee._meta.verbose_name_plural), "Employees")

        user = self.create_user()
        self.assertTrue(isinstance(user, User))

        question = self.create_question()
        self.assertTrue(isinstance(question, Question))
        self.assertEqual(question.__str__(), question.question)


class TestLogin(unittest.TestCase):
    """
    Testing Using Selenium
    """

    def setUp(self):
        """
        Setting up web driver
        """
        self.driver = webdriver.Firefox()

    def test_login_gateway_fire(self):
        """
        Testing Login for both admin and user
        """
        self.driver.get("http://127.0.0.1:8000/")
        self.assertIn("http://127.0.0.1:8000/", self.driver.current_url)

    def test_login_fire(self):
        """
        Authenticating Login credentials
        """
        self.driver.get("http://127.0.0.1:8000/login/")
        self.driver.find_element_by_id('id_username').send_keys("shradha@gmail.com")
        self.driver.find_element_by_id('id_password').send_keys("Shradha@1234")
        self.driver.find_element_by_id('submit').click()
        self.assertIn("http://127.0.0.1:8000/", self.driver.current_url)

    def test_login_url_fire(self):
        """
        Testing Login url
        """
        self.driver.get("http://127.0.0.1:8000/login/")
        self.assertIn("http://127.0.0.1:8000/login/", self.driver.current_url)

    def tearDown(self):
        self.driver.quit()


if __name__ == '__main__':
    unittest.main()
