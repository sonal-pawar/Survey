"""
This is views file contains business logic
"""
import logging
from smtplib import SMTPAuthenticationError

from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.core.mail import EmailMessage
from .models import Employee, Survey, Question, SurveyFeedback


LOGGER = logging.getLogger(__name__)


def login_gateway(request):
    """
    Login gateway for admin and employee
    """
    return render(request, 'survey/login_gateway.html')


@login_required(login_url='login')
def question_list(request, survey_id):
    """
    displaying questions on the screen
    :param request:
    :param survey_id:
    """
    try:
        # This view Displaying survey questions of particular survey
        if request.session['username'] is None:
            raise ConnectionError
        session_name = request.session['username']
        emp = Employee.objects.get(emp_username=session_name)
        LOGGER.info("This is the survey question view and current user is %s", session_name)
        survey = Survey.objects.filter(id=survey_id)
        survey_data = Survey.objects.filter(id=survey_id).values('question')
        count = 0
        que_id1 = ()
        for questions in survey_data:
            print(questions)
            que_id = survey_data[count]['question']
            que_id1 += (que_id,)
            count += 1

        question_data = Question.objects.filter(id__in=que_id1)
        ans_data = SurveyFeedback.objects.filter(survey_id=survey_id, employee_id=emp.id)
        LOGGER.info("ans data : %s ", ans_data)
        context = {'question_list': question_data, 'survey_id': survey_id,
                   'response': ans_data, 'employee': emp, 'survey': survey}
        return render(request, 'survey/question_list.html', context)
    except ConnectionError:
        LOGGER.error("something went wrong")


@login_required(login_url='login')
def employee(request):
    """
    Displaying Survey details of logged in user
    :param request:
    """
    try:
        if 'username' not in request.session:
            raise ConnectionError
        # survey details of logged in user displaying on this view
        if 'username' in request.session:
            session_name = request.session['username']
            emp = Employee.objects.get(emp_username=session_name)
            employee_data = Employee.objects.filter(id=emp.id)
            survey_emp_data = Survey.objects.filter(employee=emp.id, startDatetime__lte=now(),
                                                    endDatetime__gte=now())
            upcoming_surveys = Survey.objects.filter(employee=emp.id, startDatetime__gt=now(),
                                                     endDatetime__gte=now())
            expired_surveys = Survey.objects.filter(employee=emp.id, startDatetime__lt=now(),
                                                    endDatetime__lte=now())
            current_surveys = Survey.objects.filter(employee=emp.id, startDatetime__lte=now(),
                                                    endDatetime__gte=now())
            LOGGER.info("you are now in employee dashboard view ")

            completed_survey = list()
            assigned_survey = list()
            incomplete_survey = list()

            for survey in survey_emp_data:
                survey_feedback = SurveyFeedback.objects.filter(
                    employee_id=emp.id, survey_id=survey.id).count()
                if survey_feedback:
                    if SurveyFeedback.objects.filter(
                            survey_id=survey.id, employee_id=emp.id, flag=True):
                        completed_survey.append(survey)
                    else:
                        incomplete_survey.append(survey)
                else:
                    assigned_survey.append(survey)

            pending_survey_count = len(assigned_survey)
            completed_survey_count = len(completed_survey)
            context = {'session': session_name, 'survey_list': survey_emp_data,
                       'employee': employee_data,
                       'completed_survey': completed_survey,
                       'assigned_survey': assigned_survey,
                       'upcoming_surveys': upcoming_surveys,
                       'expired_surveys': expired_surveys,
                       'current_surveys': current_surveys,
                       'completed_survey_count': completed_survey_count,
                       'pending_survey_count': pending_survey_count,
                       'incomplete_survey': incomplete_survey}
            return render(request, "survey/survey.html", context)
        return redirect('login')
    except ConnectionError:
        LOGGER.error("something went wrong")
    return redirect('login')


def login(request):
    """
    User can Log in using credential provided by admin
    :param request:
    """
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        LOGGER.info("Employee Authentication")
        try:
            if Employee.objects.get(emp_username=username, emp_password=password):
                request.session['username'] = username
                if request.session is None:
                    raise Exception
                LOGGER.info("%s is just logged in into the employee dashboard :", username)
                return redirect('employee')
        except Employee.DoesNotExist:
            LOGGER.error(" Wrong details are entered ")
            return render(request, "survey/login.html")
    return render(request, "survey/login.html")


def user_logout(request):
    """
    user logging out from system and deleting session
    :param request:
    """
    try:
        LOGGER.info("%s trying to log out from employee dashboard ",
                    request.session['username'])
        del request.session['username']
        logout(request)
        LOGGER.info("logged out......")
    except KeyError:
        LOGGER.error("Error occur :  employee can't logged out ")
    return redirect('login_gateway')


@login_required(login_url='login')
def save(request, survey_id):
    """
    This view saving questions response
    :param request:
    :param survey_id:
    """
    session_name = request.session['username']
    emp = Employee.objects.get(emp_username=session_name)
    LOGGER.info("%s is saving question answers into the system ", session_name)
    for name in request.POST:
        all_answers = SurveyFeedback.objects.filter(survey=Survey.objects.get(id=survey_id),
                                                    employee=Employee.objects.get(id=emp.id))

        if name not in ('csrfmiddlewaretoken', 'btn_response'):
            is_record = SurveyFeedback.objects.filter(survey=Survey.objects.get(id=survey_id),
                                                      employee=Employee.objects.get(id=emp.id),
                                                      question=Question.objects.get(id=name))
            if not is_record:
                if request.POST[name]:
                    if request.POST.getlist(name):
                        survey_result_obj = SurveyFeedback()
                        survey_result_obj.survey = Survey.objects.get(id=survey_id)
                        survey_result_obj.employee = Employee.objects.get(id=emp.id)
                        survey_result_obj.question = Question.objects.get(id=name)
                        survey_result_obj.organization = request.user.organization
                        survey_result_obj.response = ', '.join(
                            request.POST.getlist(name))
                        survey_status = Survey.objects.get(
                            employee=Employee.objects.get(id=emp.id),
                            id=survey_id,
                            organization=request.user.organization)
                        if request.POST["btn_response"] == "Finish":
                            survey_result_obj.flag = True
                            LOGGER.info("Result data : %s", survey_result_obj)
                            survey_result_obj.save()
                            survey_status.flag = True
                            survey_status.save()

                        else:
                            survey_result_obj.flag = False
                            survey_result_obj.save()
                            survey_status.flag = False
                            survey_status.save()
        elif name == 'btn_response' and request.POST["btn_response"] == "Finish":

            for record in all_answers:
                record.flag = True
                record.save()
            try:
                email_body = "Hi, \n Your have completed the survey \n" + \
                             request.build_absolute_uri('/')[:-1].strip("/") \
                             + "/employee"
                email = EmailMessage(
                    'Survey Feedback ', email_body, to=[session_name]
                )
                email.send()
                LOGGER.info("Email has been sent to : %s", session_name)
            except SMTPAuthenticationError:
                LOGGER.exception("Email error : ")

    return redirect("employee")
