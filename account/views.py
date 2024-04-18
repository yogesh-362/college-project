from django.shortcuts import render
from .models import Employee, Issue_Ticket, Holiday, Employee_Task, In_Out, Events, SalaryStructure, EmployeeStatus, \
    EmpContract, RulesCategory, Rule, EmployeePaySlip, EmployeePaySlipLines, EmployeeLeave
from .serializers import (EmployeeSerializer, EmployeeRegistrationSerializer, EmployeeLoginSerializer,
                          In_Out_serializer, EmployeeProfileSerializer, EmployeeChangePasswordSerializer,
                          UserPasswordResetSerializer,
                          SendPasswordResetSerializer, IssueTicketSerializer, HolidaySerializer, EmployeeTaskSerializer,
                          SalaryStructureSerializer,
                          EmployeeStatusSerializer, EmpContractSerializer, RuleCategorySerializer, RuleSerializer,
                          EmployeePaySlipSerializer, EmployeePaySlipLinesSerializer, EmployeeLeaveSerializer,
                          )
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view
from django.http import HttpResponse, JsonResponse
from rest_framework.filters import SearchFilter
from rest_framework import filters
import qrcode
from datetime import datetime, timedelta
# from datetime import timedelta
from rest_framework.decorators import api_view, permission_classes
import re
import inflect
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.db.models import Q
from django.core.mail import send_mail
import math






def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class EmployeeViewSet(ModelViewSet):
    # permission_classes = [IsAuthenticated]
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class EmployeeTaskViewSet(ModelViewSet):
    queryset = Employee_Task.objects.all()
    serializer_class = EmployeeTaskSerializer

class EmployeeTaskView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request):
        print(request.user.id)
        instance = Employee_Task.objects.filter(employee=request.user.id)
        serializer = EmployeeTaskSerializer(instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
class EmployeeRegistrationView(APIView):
    def post(self, request, format=None):
        serializer = EmployeeRegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployeeLoginView(APIView):
    def post(self, request, format=None):
        serializer = EmployeeLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.data.get("email")
            password = serializer.data.get("password")
            user = authenticate(emp_email=email, password=password)
            print(user)
            if user:
                login(request, user)
                token = get_tokens_for_user(user)
                return Response(token, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Email or Password is not valid"}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({"error": "Email or Password is not valid"}, status=status.HTTP_400_BAD_REQUEST)


class TokenRefreshView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({"error": "Refresh Token Not Provided"}, status=status.HTTP_400_BAD_REQUEST)

            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)
            return Response({"access": new_access_token}, status=status.HTTP_200_OK)
        except:
            return Response({"error": "Invalid Data"})


class EmployeeLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({"error": "Refresh token not provided"}, status=status.HTTP_400_BAD_REQUEST)

            else:
                token = RefreshToken(refresh_token)
                token.blacklist()
                logout(request)
                return Response({"message": "Logout Successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class EmployeeProfileView(APIView):
    def get(self, request, format=None):
        try:
            serializer = EmployeeProfileSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({"error": "Anonymous User"}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, format=None):
        try:
            user_profile = request.user
            serializer = EmployeeProfileSerializer(user_profile, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"error": "Anonymous User"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        try:
            request.user.delete()
            return Response({"message": "User Deleted Successfully"}, status=status.HTTP_200_OK)
        except:
            return Response({"Error": "User is not Logged In"}, status=status.HTTP_400_BAD_REQUEST)


class EmployeeChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            serializer = EmployeeChangePasswordSerializer(data=request.data, context={'user': request.user})
            if serializer.is_valid():
                # Call save() method of the serializer and pass the instance argument
                serializer.save(instance=request.user)
                return Response({'detail': "Password Updated Successfully"}, status=status.HTTP_200_OK)
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SendPasswordResetEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        serializer = SendPasswordResetSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            uid = serializer.validated_data.get('uid')
            token = serializer.validated_data.get('token')
            link = serializer.validated_data.get('link')
            return Response({"message": "Password Reset Link Is Been Send", "uid": uid, "token": token, "link": link})
        return Response({"message": "There was an unexpected error"})


class UserPasswordResetView(APIView):
    def post(self, request, uid, token, format=None):
        serializer = UserPasswordResetSerializer(data=request.data, context={'uid': uid, 'token': token})
        if serializer.is_valid(raise_exception=True):
            return Response({'message': "Password Reset Successfully"})
        return Response(serializer.errors)


@api_view(['GET'])
def generate_qr_code(request):
    try:
        # Assuming you have only one employee for simplicity
        employee = Employee.objects.get(id=1)

        # Generate QR code data based on employee ID
        qr_code_data = f"employee_id:{employee.id}"

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_code_data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        response = HttpResponse(content_type="image/png")
        img.save(response, "PNG")
        return response

    except Employee.DoesNotExist:
        return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
# @permission_classes([IsAuthenticated])

def scan_qr_code(request):
    try:
        qr_code_data = request.data.get('qr_code_data')
        employee_id = int(qr_code_data.split(":")[1])

        # Lookup employee by employee_id
        employee = Employee.objects.get(id=employee_id)

        # Update time entry based on employee's current status
        current_time = datetime.now().time()
        total_worked_hours = timedelta()

        if employee.status:
            # This is an out-time scan
            if employee.last_scan_in_time:
                employee.last_scan_out_time = current_time
                if employee.last_scan_in_time > employee.last_scan_out_time:
                    # Swap in and out times if out time is earlier than in time
                    employee.last_scan_in_time, employee.last_scan_out_time = employee.last_scan_out_time, employee.last_scan_in_time

                # Calculate time difference as timedelta
                time_difference = datetime.combine(datetime.today(), employee.last_scan_out_time) - datetime.combine(datetime.today(), employee.last_scan_in_time)

                # Update total worked hours
                employee.total_worked_hours += time_difference
                employee.last_scan_out_time = current_time
            else:
                # If there's no previous in-time, we can't calculate worked hours
                employee.last_scan_in_time = current_time
        else:
            # This is an in-time scan
            if employee.last_scan_out_time:
                # If there's a previous out-time, update the last scan in-time
                employee.last_scan_in_time = current_time
            else:
                # If there's no previous out-time, set the current time as the last scan in-time
                employee.last_scan_in_time = current_time

        # Toggle employee status
        employee.status = not employee.status
        employee.save()

        # Format total worked hours
        total_worked_hours_with_units = format_total_worked_hours(employee.total_worked_hours)

        # Update the response with the formatted total worked hours
        return Response({"message": "Time entry updated successfully",
                         "id": employee_id,
                         "total_worked_hours": total_worked_hours_with_units},
                        status=status.HTTP_200_OK)

    except (Employee.DoesNotExist, ValueError, IndexError):
        return Response({"error": "Invalid QR code data or Employee does not exist"},
                        status=status.HTTP_400_BAD_REQUEST)

def format_total_worked_hours(total_worked_hours):
    # Convert total worked hours to hours and minutes format
    hours = total_worked_hours.seconds // 3600
    minutes = (total_worked_hours.seconds // 60) % 60
    return f"{hours} hours {minutes} minutes"




class IssueTicketUserViewSet(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request):
        instance = Issue_Ticket.objects.filter(ticket_email=request.user)
        serializer = IssueTicketSerializer(instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class IssueTicketViewSet(ModelViewSet):
    serializer_class = IssueTicketSerializer
    queryset = Issue_Ticket.objects.all()

    def create(self, request, *args, **kwargs):
        # Call the create method of the parent class
        response = super().create(request, *args, **kwargs)

        # Send email to admin
        if response.status_code == 201:  # Only send email if the ticket was successfully created
            ticket_data = response.data
            subject = 'New Ticket Submitted'
            message = f'A new ticket has been submitted.\n\nIssue: {ticket_data["ticket_issue"]}\nEmployee ID: {ticket_data["ticket_emp_id"]}\nDate: {ticket_data["ticket_date"]}'
            from_email = 'yogeshgoswami0306@gmail.com'  # Sender's email address
            recipient_list = ['yogesh.pranshtech@gmail.com']  # Admin's email address

            send_mail(subject, message, from_email, recipient_list, fail_silently=False)

        return response

class holidayViewSet(ModelViewSet):
    # permission_classes = [IsAuthenticated]
    serializer_class = HolidaySerializer
    queryset = Holiday.objects.all()


class inoutViewSet(ModelViewSet):
    # permission_classes = [IsAuthenticated]
    serializer_class = In_Out_serializer
    queryset = In_Out.objects.all()



class EmployeeInOutView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request):
        print(request.user.id)
        instance = In_Out.objects.filter(employee=request.user.id)
        serializer = In_Out_serializer(instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

def home(request):
    return render(request, 'account/authentication.html')


def issue_ticket(request):
    return render(request, 'account/issue_ticket.html')


def forgot(request):
    return render(request, 'account/forgot.html')


def changepassword(request):
    return render(request, 'account/changepassword.html')


def dashboard(request):
    return render(request, 'account/dashboard.html')


def employee_list(request):
    return render(request, 'account/new_emp_list.html')


def holidayView(request):
    form = Holiday.objects.all()
    print(form)
    return render(request, 'account/holidays.html', {'form': form})


def employee_task_View(request):
    return render(request, 'account/employee_task.html')


def leave(request):
    return render(request, 'account/emp_leave.html')

class EmployeeLeaveView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request):
        print(request.user.id)
        instance = EmployeeLeave.objects.filter(employee=request.user.id)
        serializer = EmployeeLeaveSerializer(instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

def inout_view(request):
    form = In_Out.objects.all()
    print(form)
    return render(request, 'account/in-out.html', {'form': form})


def Calendar(request):
    all_events = Events.objects.all()
    context = {
        "events": all_events,
    }
    return render(request, 'account/calendar.html', context)


def all_events(request):
    all_events = Events.objects.all()
    out = []
    for event in all_events:
        out.append({
            'title': event.name,
            'id': event.id,
            'start': event.start.strftime("%m/%d/%Y, %H:%M:%S"),
            'end': event.end.strftime("%m/%d/%Y, %H:%M:%S"),
        })

    return JsonResponse(out, safe=False)


def add_event(request):
    start = request.GET.get("start", None)
    end = request.GET.get("end", None)
    title = request.GET.get("title", None)
    event = Events(name=str(title), start=start, end=end)
    event.save()
    data = {}
    return JsonResponse(data)


def update(request):
    start = request.GET.get("start", None)
    end = request.GET.get("end", None)
    title = request.GET.get("title", None)
    id = request.GET.get("id", None)
    event = Events.objects.get(id=id)
    event.start = start
    event.end = end
    event.name = title
    event.save()
    data = {}
    return JsonResponse(data)


def remove(request):
    id = request.GET.get("id", None)
    event = Events.objects.get(id=id)
    event.delete()
    data = {}
    return JsonResponse(data)


class SalaryStructureViewSet(ModelViewSet):
    queryset = SalaryStructure.objects.all()
    serializer_class = SalaryStructureSerializer


class EmployeeStatusViewSet(ModelViewSet):
    queryset = EmployeeStatus.objects.all()
    serializer_class = EmployeeStatusSerializer


class EmpContractViewSet(ModelViewSet):
    queryset = EmpContract.objects.all()
    serializer_class = EmpContractSerializer


class RuleCategoryViewSet(ModelViewSet):
    queryset = RulesCategory.objects.all()
    serializer_class = RuleCategorySerializer


class RuleViewSet(ModelViewSet):
    queryset = Rule.objects.all()
    serializer_class = RuleSerializer


class EmployeePaySlipViewSet(ModelViewSet):
    queryset = EmployeePaySlip.objects.all()
    serializer_class = EmployeePaySlipSerializer


@api_view(['GET', 'POST'])
def compute_employee(request, payslip_id):
    try:
        payslip = EmployeePaySlip.objects.get(pk=payslip_id)
        payslip.employee_pay_slip_lines.all().delete()
        # variable that can be used in python code
        employee = payslip.emp_id
        contract = employee.emp_contract.latest("id")
        contra = f"EmployeePaySlip.objects.get(pk={str(payslip_id)}).emp.emp_contract.latest('id')"
        ordered_rules = contract.salary_structure.rules.order_by("sequence")
        # basic_total = sum(payslip.employee_pay_slip_lines.filter(category_id__rule_category_code__in=['BASIC']).values_list('rate', flat=True))
        # allowance = sum(payslip.employee_pay_slip_lines.filter(category_id__rule_category_code__in=['ALW']).values_list('rate', flat=True))

        # import pdb; pdb.set_trace()
        print(ordered_rules)
        for rule in ordered_rules:
            local_var = {}
            if rule.amount_type == 'Python Code':
                # print(basic_total)
                python_code = rule.amount_value
                python_code = python_code.replace('contract', contra)
                matches = re.findall(r'rules\.\w*', python_code)
                # if contract.salary_structure.structure_name == "Regular Salary":
                #     matches = re.findall(r'rules\.\w*', python_code)
                # elif contract.salary_structure.structure_name == "Salary Without PF":
                #     matches = re.findall(r'rules\.(?!HRA|PFEN1|PFEPS|PFEMP)\w*', python_code)
                for match in matches:
                    temp_rule = f"EmployeePaySlip.objects.get(pk={str(payslip_id)}).employee_pay_slip_lines.get(code='RULE_CODE').rate"
                    code = match.split('.')[-1]
                    if code:
                        temp_rule = temp_rule.replace('RULE_CODE', code)
                        python_code = python_code.replace(match, temp_rule)

                exec(python_code, globals(), local_var)
                print(local_var)
                if local_var == {}:
                    res = eval(python_code)
                else:
                    res = local_var['result']
            else:
                res = rule.amount_value

            total_days = payslip.total_payable_days()[0]
            worked_days = payslip.total_payable_days()[1]

            if total_days == worked_days:
                final_total = res
            else:
                oneday_amount = float(res) / total_days
                final_total_value = float(oneday_amount) * float(worked_days)
                formatted_final_total = f"{final_total_value:.2f}"
                final_total = float(formatted_final_total)

            result = EmployeePaySlipLines.objects.create(
                slip_id=payslip,
                name=contract.first_name,
                code=rule.code,
                category_id=rule.category_id,
                amount_type=rule.amount_type,
                amount_value=rule.amount_value,
                rate=res,
                final=final_total
            )
            print(result)

        payslip_lines = payslip.employee_pay_slip_lines.all()
        # if contract.out_from
        serializer = EmployeePaySlipLinesSerializer(payslip_lines, many=True)
        return Response({"data": serializer.data})

        # return JsonResponse({"data": json_data}, content_type='application/json')
    except EmployeePaySlip.DoesNotExist:
        return Response({"error": "Not Exist"}, status=status.HTTP_404_NOT_FOUND)


class EmployeePaySlipLinesViewSet(ModelViewSet):
    queryset = EmployeePaySlipLines.objects.all()
    serializer_class = EmployeePaySlipLinesSerializer


@api_view(['GET'])
def print_payslip(request, payslip_id):
    # import pdb;
    # pdb.set_trace()
    try:
        payslip = EmployeePaySlip.objects.get(pk=payslip_id)
        print(payslip.emp_id.emp_name)
    except EmployeePaySlip.DoesNotExist:
        return HttpResponse({"error": "Not Exist"}, status=status.HTTP_404_NOT_FOUND)

    net_amount = math.ceil(sum(
        payslip.employee_pay_slip_lines.filter(category_id__rule_category_code__in=['BASIC', 'ALW']).values_list(
            'final', flat=True)) - sum(
        payslip.employee_pay_slip_lines.filter(category_id__rule_category_code__in=['DED']).values_list('final',
                                                                                                        flat=True)))
    net_amount_data = '{:.2f}'.format(math.ceil(sum(
        payslip.employee_pay_slip_lines.filter(category_id__rule_category_code__in=['BASIC', 'ALW']).values_list(
            'final', flat=True)) - sum(
        payslip.employee_pay_slip_lines.filter(category_id__rule_category_code__in=['DED']).values_list('final',
                                                                                                        flat=True))))

    net_amount_total = '{:.2f}'.format(math.ceil(sum(
        payslip.employee_pay_slip_lines.filter(category_id__rule_category_code__in=['BASIC', 'ALW']).values_list('rate',
                                                                                                                 flat=True)) - sum(
        payslip.employee_pay_slip_lines.filter(category_id__rule_category_code__in=['DED']).values_list('rate',
                                                                                                        flat=True))))

    std_days = payslip.total_payable_days()[0]
    worked_days = payslip.total_payable_days()[1]
    lop = std_days - worked_days
    emp_birth_day = payslip.emp_id.emp_birthday
    emp_desig = payslip.emp_id.emp_designation
    emp_personal_no = payslip.emp_id
    emp_bank_name = payslip.emp_id.bank_name
    emp_pf_number = payslip.emp_id.pf_number
    emp_bank_account_number = payslip.emp_id.bank_account_number
    emp_uan_no = payslip.emp_id. emp_uan

    ctc = payslip.emp_id.emp_contract.latest("id").ctc
    print(ctc)
    total_val = math.floor(sum(
            payslip.employee_pay_slip_lines.filter(category_id__rule_category_code__in=['BASIC', 'ALW']).values_list(
                'rate', flat=True)))
    if ctc < total_val:
        total_val = ctc

    payslip_template = get_template('payslip.html')
    context = {
        'payslip': payslip,
        "first_name": payslip.emp_id.emp_contract.latest("id").first_name,
        "last_name": payslip.emp_id.emp_contract.latest("id").last_name,
        "ctc": payslip.emp_id.emp_contract.latest("id").ctc,
        "month": payslip.get_month_name(),
        "data": {payslip_data.code: '{:.2f}'.format(round(payslip_data.final)) for payslip_data in payslip.employee_pay_slip_lines.all()},
        "rate": {payslip_data.code: '{:.2f}'.format(round(payslip_data.rate)) for payslip_data in payslip.employee_pay_slip_lines.all()},
        "gross_earnings": '{:.2f}'.format(math.floor(sum(
            payslip.employee_pay_slip_lines.filter(category_id__rule_category_code__in=['BASIC', 'ALW']).values_list(
                'final', flat=True)))),
        "gross_deductions": '{:.2f}'.format(math.ceil(sum(
            payslip.employee_pay_slip_lines.filter(category_id__rule_category_code__in=['DED']).values_list('final',
                                                                                                            flat=True)))),
        "net_amount": net_amount_data,
        "gross_earnings_total": total_val,
        "gross_deductions_total": '{:.2f}'.format(math.ceil(sum(
            payslip.employee_pay_slip_lines.filter(category_id__rule_category_code__in=['DED']).values_list('rate',
                                                                                                            flat=True)))),
        "net_amount_total": net_amount_total,
        "net_amount_words": payslip.number_to_words(net_amount),
        "std_days": std_days,
        "worked_days": worked_days,
        "lop": lop,
        "emp_birth_day": emp_birth_day,
        "emp_desig" : emp_desig,
        "emp_personal_no" : emp_personal_no,
        "emp_bank_name" : emp_bank_name,
        "emp_pf_number" : emp_pf_number,
        "emp_bank_account_number" : emp_bank_account_number,
        "emp_uan_no" : emp_uan_no,
    }

    html = payslip_template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="payslip.pdf"'

    # Generate PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')

    return response



class EmployeeLeaveViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeLeaveSerializer
    queryset = EmployeeLeave.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['start_date']

    def create(self, request, *args, **kwargs):
        # Call the create method of the parent class
        response = super().create(request, *args, **kwargs)

        # Send email to admin
        if response.status_code == 201:  # Only send email if the ticket was successfully created
            ticket_data = response.data
            subject = 'New leave'
            message = f'A new Leave has been submitted.\n\nname: foram'
            from_email = 'yogeshgoswami0306@gmail.com'  # Sender's email address
            recipient_list = ['yogesh.pranshtech@gmail.com']  # Admin's email address

            send_mail(subject, message, from_email, recipient_list, fail_silently=False)

        return response


    def get_queryset(self):
        queryset = super().get_queryset()
        month = self.request.query_params.get('month')
        if month:
            try:
                month = int(month)
                queryset = queryset.filter(
                    Q(start_date__month=month) | Q(end_date__month=month)
                )
            except ValueError:
                # Handle invalid month value
                queryset = EmployeeLeave.objects.none()  # Return an empty queryset
        return queryset


def in_out_list(request):
    return render(request, 'account/in-out-list.html')
