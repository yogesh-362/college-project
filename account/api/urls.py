from django.urls import path, include
from account.views import (EmployeeViewSet, IssueTicketViewSet,holidayViewSet,
                    EmployeeTaskViewSet, inoutViewSet,
                    SalaryStructureViewSet, EmployeeStatusViewSet, EmpContractViewSet, RuleCategoryViewSet, RuleViewSet,
                    EmployeePaySlipViewSet, EmployeePaySlipLinesViewSet, EmployeeLeaveViewSet, IssueTicketUserViewSet)
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()

router.register(r"emp-list", EmployeeViewSet, basename="Employee List")
router.register(r"emp-task", EmployeeTaskViewSet, basename="Employee task")
router.register(r"issue-ticket", IssueTicketViewSet, basename="Issue Ticket")
router.register(r"holidays", holidayViewSet, basename="holidays")
router.register(r"in-out", inoutViewSet, basename="in-out")
router.register(r"employee-leave", EmployeeLeaveViewSet, basename="employee_leave")
router.register("salary-structure", SalaryStructureViewSet, basename="salary_structure")
router.register("employee-status", EmployeeStatusViewSet, basename="employee_status")
router.register("emp-contract", EmpContractViewSet, basename="emp_contract")
router.register("rule-category", RuleCategoryViewSet, basename="rule_category")
router.register("rule", RuleViewSet, basename="rule")
router.register('employee-pay-slip', EmployeePaySlipViewSet, basename="employee_pay_slip")
router.register('employee-pay-slip-lines', EmployeePaySlipLinesViewSet, basename="employee_pay_slip_lines")


urlpatterns = [
                  path('', include(router.urls)),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
