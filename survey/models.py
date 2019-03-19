"""
This is the database structure of survey application
"""
import logging
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.db import models

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


class Organization(models.Model):
    """
    This the organization class
    """
    company_name = models.CharField(max_length=200)
    location = models.CharField(max_length=100)
    description = models.CharField(max_length=200)

    def __str__(self):
        return self.company_name


class User(AbstractUser):
    """
    This is user class which overrides Abstract User
    """
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)


class Employee(models.Model):
    """
    This is Employee class
    """
    emp_name = models.CharField(max_length=200)
    emp_username = models.CharField(max_length=100, unique=True,
                                    error_messages=
                                    {'required': 'Please provide your email address.',
                                     'unique': 'An account with this email exist.'},)
    emp_password = models.CharField(max_length=100)
    emp_designation = models.CharField(max_length=100)
    emp_address = models.CharField(max_length=200)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.emp_name

    class Meta:
        """
        this shows class in plural form
        """
        verbose_name_plural = 'Employees'


class Question(models.Model):
    """
    This is question class
    """
    TEXT = 'text'
    RADIO = ' radio '
    SELECT = 'select'
    SELECT_MULTIPLE = 'select-multiple'
    INTEGER = 'integer'

    Question_types = (
        (TEXT, 'text'),
        (RADIO, 'radio'),
        (SELECT, 'select'),
        (SELECT_MULTIPLE, 'Select Multiple'),
        (INTEGER, 'integer'),
    )
    question = models.TextField()
    is_required = models.BooleanField(default=False)
    question_type = models.CharField(max_length=200, choices=Question_types, default=TEXT)
    choices = models.TextField(blank=True, null=True,
                               help_text='if the question type is "radio," "select," or "select multiple"'
                                         ' provide a comma-separated list of options for this question .')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    # noinspection PyUnresolvedReferences
    def get_choice(self):
        if self.choices is not None:
            return self.choices.split(',')

    def __str__(self):
        return self.question


class Survey(models.Model):
    """
    This is Survey class
    """
    survey_name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    question = models.ManyToManyField(Question)
    employee = models.ManyToManyField(Employee)
    startDatetime = models.DateField(blank=True, null=True)
    endDatetime = models.DateField(blank=True, null=True)
    flag = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return self.survey_name

    class Meta:
        """
              this shows class in plural form
        """
        verbose_name_plural = 'surveys'


def validate_list(value):
    """takes a text value and verifies
     that there is at least one comma"""
    values = value.split(',')
    if len(values) < 2:
        raise ValidationError(
            "The selected field requires an "
            "associated list of choices. "
            "Choices must contain more"
            " than one item.")


class SurveyFeedback(models.Model):
    """
    Survey Feedback model
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    response = models.TextField(blank=True, null=True)
    flag = models.BooleanField()
    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now_add=True)


