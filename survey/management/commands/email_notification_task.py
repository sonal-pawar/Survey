import datetime
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from survey.models import Survey, Employee


class Command(BaseCommand):
    help = 'Type the help text here'

    def handle(self, *args, **options):
        self.send_notification_one_day_prior()
        self.send_notification_on_start_date()
        self.send_notification_one_day_before_end_date()
        self.send_notification_after_end_date()

    @staticmethod
    def send_notification_one_day_prior():
        upcoming = Survey.objects.filter(startDatetime=datetime.date.today() + datetime.timedelta(days=1))
        for employee in upcoming:
            emp = Employee.objects.get(pk=employee.employee_id)
            subject = 'You have a new survey coming tomorrow.'
            body = "Hello {}<br><br> ".format(emp.emp_name)
            body += "You have a new survey coming tomorrow.<br>"
            body += "Please login to survey management and complete your survey.<br><br>"
            body += "Thanks,<br>{}".format("Survey Management Team")
            send_mail(subject, body, 'sonal.pawar@harbingergroup.com', [emp.emp_username],
                      html_message=body)

    @staticmethod
    def send_notification_on_start_date():
        started = Survey.objects.filter(startDatetime=datetime.date.today())
        for employee in started:
            emp = Employee.objects.get(pk=employee.employee_id)
            subject = 'You have a new survey in your dashboard.'
            body = "Hello {}<br><br> ".format(emp.emp_name)
            body += "You have a new survey in your dashboard.<br>"
            body += "Please login to survey management and complete your survey.<br><br>"
            body += "Thanks,<br>{}".format("Survey Management Team")
            send_mail(subject, body, 'sonal.pawar@harbingergroup.com', [emp.emp_username],
                      html_message=body)

    @staticmethod
    def send_notification_one_day_before_end_date():
        started = Survey.objects.filter(endDatetime=datetime.date.today() + datetime.timedelta(days=1))
        for employee in started:
            emp = Employee.objects.get(pk=employee.employee_id)
            subject = 'Survey assigned to you ending tomorrow.'
            body = "Hello {}<br><br> ".format(emp.emp_name)
            body += "Survey in your dashboard ending tomorrow.<br>"
            body += "Please login to survey management and complete your survey.<br><br>"
            body += "Thanks,<br>{}".format("Survey Management Team")
            send_mail(subject, body, 'sonal.pawar@harbingergroup.com', [emp.emp_username],
                      html_message=body)

    @staticmethod
    def send_notification_after_end_date():
        started = Survey.objects.filter(endDatetime__lt=datetime.date.today())
        for employee in started:
            emp = Employee.objects.get(pk=employee.employee_id)
            subject = 'Survey assigned to you was ended.'
            body = "Hello {}<br><br> ".format(emp.emp_name)
            body += "Survey in your dashboard ended.<br>"
            body += "Please login to survey management and complete your survey.<br><br>"
            body += "Thanks,<br>{}".format("Survey Management Team")
            send_mail(subject, body, 'sonal.pawar@harbingergroup.com', [emp.emp_username],
                      html_message=body)
