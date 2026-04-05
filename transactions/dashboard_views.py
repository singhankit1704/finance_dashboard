from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth, TruncWeek
from datetime import date, timedelta

from .models import Transaction
from users.permissions import IsAnyRole, IsAnalystOrAdmin


def success_response(data=None, message="Success"):
    return Response({"success": True, "message": message, "data": data}, status=status.HTTP_200_OK)


class DashboardSummaryView(APIView):
    """
    GET /api/dashboard/summary/
    Returns total income, total expenses, net balance.
    Accessible by: viewer, analyst, admin.
    Admins see global totals; others see their own.
    """
    permission_classes = [IsAnyRole]

    def get(self, request):
        qs = Transaction.objects.filter(is_deleted=False)
        if not request.user.is_admin:
            qs = qs.filter(user=request.user)

        totals = qs.aggregate(
            total_income=Sum('amount', filter=Q(type='income')),
            total_expense=Sum('amount', filter=Q(type='expense')),
        )

        total_income = float(totals['total_income'] or 0)
        total_expense = float(totals['total_expense'] or 0)
        net_balance = total_income - total_expense

        return success_response({
            "total_income": total_income,
            "total_expenses": total_expense,
            "net_balance": net_balance,
        }, "Dashboard summary fetched.")


class CategoryBreakdownView(APIView):
    """
    GET /api/dashboard/categories/
    Returns category-wise income and expense totals.
    Accessible by: analyst, admin.
    """
    permission_classes = [IsAnalystOrAdmin]

    def get(self, request):
        qs = Transaction.objects.filter(is_deleted=False)
        if not request.user.is_admin:
            qs = qs.filter(user=request.user)

        breakdown = (
            qs.values('category', 'type')
            .annotate(total=Sum('amount'), count=Count('id'))
            .order_by('category', 'type')
        )

        # Restructure: {category: {income: X, expense: Y, count: N}}
        result = {}
        for item in breakdown:
            cat = item['category']
            if cat not in result:
                result[cat] = {'income': 0.0, 'expense': 0.0, 'count': 0}
            result[cat][item['type']] = float(item['total'])
            result[cat]['count'] += item['count']

        return success_response(result, "Category breakdown fetched.")


class MonthlyTrendsView(APIView):
    """
    GET /api/dashboard/trends/monthly/
    Returns monthly income vs expense for the last 12 months.
    Accessible by: analyst, admin.
    """
    permission_classes = [IsAnalystOrAdmin]

    def get(self, request):
        qs = Transaction.objects.filter(is_deleted=False)
        if not request.user.is_admin:
            qs = qs.filter(user=request.user)

        monthly = (
            qs.annotate(month=TruncMonth('date'))
            .values('month', 'type')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )

        result = {}
        for item in monthly:
            key = item['month'].strftime('%Y-%m')
            if key not in result:
                result[key] = {'income': 0.0, 'expense': 0.0}
            result[key][item['type']] = float(item['total'])

        return success_response(result, "Monthly trends fetched.")


class WeeklyTrendsView(APIView):
    """
    GET /api/dashboard/trends/weekly/
    Returns weekly income vs expense for the last 8 weeks.
    Accessible by: analyst, admin.
    """
    permission_classes = [IsAnalystOrAdmin]

    def get(self, request):
        eight_weeks_ago = date.today() - timedelta(weeks=8)
        qs = Transaction.objects.filter(is_deleted=False, date__gte=eight_weeks_ago)
        if not request.user.is_admin:
            qs = qs.filter(user=request.user)

        weekly = (
            qs.annotate(week=TruncWeek('date'))
            .values('week', 'type')
            .annotate(total=Sum('amount'))
            .order_by('week')
        )

        result = {}
        for item in weekly:
            key = item['week'].strftime('%Y-%m-%d')
            if key not in result:
                result[key] = {'income': 0.0, 'expense': 0.0}
            result[key][item['type']] = float(item['total'])

        return success_response(result, "Weekly trends fetched.")


class RecentActivityView(APIView):
    """
    GET /api/dashboard/recent/
    Returns the last 10 transactions.
    Accessible by: viewer, analyst, admin.
    """
    permission_classes = [IsAnyRole]

    def get(self, request):
        from .serializers import TransactionSerializer
        qs = Transaction.objects.filter(is_deleted=False)
        if not request.user.is_admin:
            qs = qs.filter(user=request.user)

        recent = qs.order_by('-date', '-created_at')[:10]
        return success_response(
            TransactionSerializer(recent, many=True).data,
            "Recent activity fetched."
        )
