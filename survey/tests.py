import unittest
from django.core import mail
from django.test import TestCase, modify_settings
from selenium import webdriver
from survey.models import Organization, Employee, Survey, User, Question


@modify_settings(MIDDLEWARE_CLASSES={
    'append': 'django.middleware.cache.FetchFromCacheMiddleware',
    'prepend': 'django.middleware.cache.UpdateCacheMiddleware',
})
class MiddlewareTestCase(TestCase):

    @modify_settings(MIDDLEWARE_CLASSES={
        'append': 'django.middleware.cache.FetchFromCacheMiddleware',
        'prepend': 'django.middleware.cache.UpdateCacheMiddleware',
    })
    def test_cache_middleware(self):
        with self.modify_settings(MIDDLEWARE_CLASSES={
            'append': 'django.middleware.cache.FetchFromCacheMiddleware',
            'prepend': 'django.middleware.cache.UpdateCacheMiddleware',
            'remove': [
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
                'django.contrib.messages.middleware.MessageMiddleware',
            ],
        }):
            response = self.client.get('/')


class EmailTest(TestCase):
    def test_send_email(self):
        # Send message.
        mail.send_mail('Subject here', 'Here is the message.',
                       'from@example.com', ['to@example.com'],
                       fail_silently=False)

        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)

        # Verify that the subject of the first message is correct.
        self.assertEqual(mail.outbox[0].subject, 'Subject here')

# models test


class ModelsTest(TestCase):

    @staticmethod
    def create_organization(company_name='Harbinger', location='Pune', description='Innovate'):
        return Organization.objects.create(company_name=company_name, location=location, description=description)

    @staticmethod
    def create_employee(emp_name='mona', emp_username='mona@gmail.com', emp_password='mona@123',
                        emp_designation='Software Engineer',
                        emp_address='Pune', organization=None):
        return Employee.objects.create(emp_name=emp_name, emp_username=emp_username, emp_password=emp_password,
                                       emp_designation=emp_designation, emp_address=emp_address,
                                       organization=organization)

    @staticmethod
    def create_survey(survey_name='CSR Activity', description='CSR for harbinger',
                      organization=Organization.objects.get(id=1), question=Question.objects.get(id=1),
                      employee=Employee.objects.get(id=1),
                      start_date_time='2019-02-28',
                      end_date_time='2019-02-28', flag=True):
        return Survey.objects.create(survey_name=survey_name, description=description,
                                     organization=organization, question=question, employee=employee,
                                     startDatetime=start_date_time, endDatetime=end_date_time, flag=flag)

    @staticmethod
    def create_user(organization=None, is_active=True, is_staff=False):
        return User.objects.create(organization=organization, is_active=is_active, is_staff=is_staff)

    @staticmethod
    def create_question(question='How was CSR ?', is_required=True, question_type='text',
                        choices='good, bad, very good', organization=Organization.objects.get(id=1)):
        return Question.objects.create(question=question, is_required=is_required, question_type=question_type,
                                       choices=choices, organization=organization)

    def test_all(self):
        org = self.create_organization()
        self.assertTrue(isinstance(org, Organization))
        self.assertEqual(org.__str__(), org.company_name)

        emp = self.create_employee()
        self.assertTrue(isinstance(emp, Employee))
        self.assertEqual(emp.__str__(), emp.emp_name)
        self.assertEqual(str(Employee._meta.verbose_name_plural), "Employees")

        user = self.create_user()
        self.assertTrue(isinstance(user, User))

        survey = self.create_survey()
        self.assertEqual(survey.__str__(), survey.survey_name)
        self.assertTrue(isinstance(survey, Survey))
        self.assertEqual(str(Survey._meta.verbose_name_plural), "surveys")

        question = self.create_question()
        self.assertTrue(isinstance(question, Question))
        self.assertEqual(question.__str__(), question.question)


# views test using selenium

class TestLogin(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Firefox()

    def test_homepage_fire(self):
        self.driver.get("http://127.0.0.1:8000/")
        self.assertIn("http://127.0.0.1:8000/", self.driver.current_url)

    def test_login_fire(self):
        self.driver.get("http://127.0.0.1:8000/login/")
        self.driver.find_element_by_id('id_username').send_keys("shradha@gmail.com")
        self.driver.find_element_by_id('id_password').send_keys("Shradha@1234")
        self.driver.find_element_by_id('submit').click()
        self.assertIn("http://127.0.0.1:8000/", self.driver.current_url)

    def test_login_url_fire(self):
        self.driver.get("http://127.0.0.1:8000/login/")
        self.assertIn("http://127.0.0.1:8000/login/", self.driver.current_url)

    def test_report_url_fire(self):
        self.driver.get('http://127.0.0.1:8000/report/')
        self.assertIn('http://127.0.0.1:8000/report/', self.driver.current_url)

    def tearDown(self):
        self.driver.quit()


if __name__ == '__main__':
    unittest.main()
