"""
This is views file contains business logic
"""
import logging
from smtplib import SMTPAuthenticationError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_date
from django.utils.timezone import now
from django.core.mail import EmailMessage
from .models import Employee, Survey, Question, SurveyFeedback, User


LOGGER = logging.getLogger(__name__)


def login_gateway(request):
    return render(request, 'survey/login_gateway.html')


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


def logout(request):
    """
    user logging out from system and deleting session
    :param request:
    """
    try:
        LOGGER.info("%s trying to log out from employee dashboard ",
                    request.session['username'])
        del request.session['username']
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

        if name != "csrfmiddlewaretoken" and name != 'btn_response':
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


# def assign_survey(request, survey_id):
#     """
#     displaying list of assigned surveys to logged in user
#     :param request:
#     :param survey_id:
#     """
#     user_list = Employee.objects.filter(
#         organization_id=request.user.organization)
#     return render(request,
#                   'survey/survey_assign.html',
#                   {"user_list": user_list, "survey_id": survey_id})
#

# def assign_question(request, survey_id):
#     """
#     displaying question list of particular survey
#     :param request:
#     :param survey_id:
#     """
#     try:
#         if request.user.organization is None:
#             raise ConnectionError
#         questions = Question.objects.filter(organization=request.user.organization)
#         return render(request, 'survey/question_assign.html',
#                       {"question_list": questions, "survey_id": survey_id})
#     except ConnectionError:
#         LOGGER.error("organization admin not in session")
#
#
# def save_assign_survey(request):
#     """
#     Saving assigned survey of employee and sending mail to him
#     :param request:
#     """
#
#     if request.POST.getlist('emp_id'):
#         for employee_id in request.POST.getlist('emp_id'):
#             survey_employee = SurveyEmployee.objects.filter(
#                 survey_id=request.POST['survey_id'],
#                 employee_id=employee_id)
#             if not survey_employee:
#                 survey_employee_map_obj = SurveyEmployee()
#                 survey_employee_map_obj.survey = get_object_or_404(
#                     Survey, pk=request.POST['survey_id'])
#                 survey_employee_map_obj.employee = get_object_or_404(
#                     Employee, pk=employee_id)
#                 survey_employee_map_obj.organization = request.user.organization
#                 survey_employee_map_obj.startDatetime = parse_date(
#                     request.POST.getlist('start-date')[1])
#                 survey_employee_map_obj.endDatetime = parse_date(
#                     request.POST.getlist('end-date')[1])
#                 survey_employee_map_obj.save()
#                 user_obj = get_object_or_404(Employee, pk=employee_id)
#                 to_email = user_obj.emp_username
#                 try:
#                     email_body = "Hi, \n Your Survey Link\n"\
#                                  + request.build_absolute_uri('/')[:-1].strip("/")\
#                                  + "/employee"
#                     email = EmailMessage(
#                         'Survey Assign', email_body, to=[to_email]
#                     )
#                     email.send()
#                     LOGGER.info("Email has been send to %s ", to_email)
#                 except SMTPAuthenticationError:
#                     LOGGER.exception("Email Error")
#                 finally:
#                     return redirect('surveyList')
#     return redirect('surveyList')
#
#
# def save_assign_question(request):
#     """
#     saving assigned questions
#     :param request:
#     """
#     try:
#         if request.POST.getlist('question_id'):
#             for question_id in request.POST.getlist('question_id'):
#                 survey_question = SurveyQuestion.objects.filter(
#                     survey_id=request.POST['survey_id'],
#                     question_id=question_id)
#                 if not survey_question:
#                     survey_question_map_obj = SurveyQuestion()
#                     survey_question_map_obj.survey = get_object_or_404(
#                         Survey, pk=request.POST['survey_id'])
#                     survey_question_map_obj.organization = request.user.organization
#                     survey_question_map_obj.question = get_object_or_404(
#                         Question, pk=question_id)
#                     survey_question_map_obj.save()
#         return redirect('surveyList')
#     except ConnectionError:
#         LOGGER.log("Something went wrong")
#
#
# def survey_lists(request):
#     """
#     displaying survey list assigned to current user
#     :param request:
#     """
#     survey_list = Survey.objects.filter(organization=request.user.organization)
#     return render(request, 'survey/survey_employee.html', {"survey_list": survey_list})
#
#
# def survey_questions(request, survey_id):
#     """
#     displaying questions and employees list to which survey has been assigned
#     :param request:
#     :param survey_id:
#     """
#     survey_questions_list = SurveyQuestion.objects.filter(survey_id=survey_id,
#                                                           organization=request.user.organization)
#     survey_employee_list = SurveyEmployee.objects.filter(
#         survey_id=survey_id,
#         organization=request.user.organization)
#     return render(request, 'survey/survey_questions_list.html',
#                   {"survey_questions_list": survey_questions_list,
#                    "survey_employee_list": survey_employee_list})
#
#
# @login_required(login_url='login')
# def report(request):
#     """
#     displaying report for each and every employee of respective organization
#     :param request:
#     """
#     survey_data = SurveyEmployee.objects.filter(organization_id=request.user.organization)
#     context = {'survey': survey_data}
#     return render(request, 'survey/report.html', context)
