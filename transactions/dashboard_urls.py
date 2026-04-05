from django.urls import path
from .dashboard_views import (
    DashboardSummaryView, CategoryBreakdownView,
    MonthlyTrendsView, WeeklyTrendsView, RecentActivityView
)

urlpatterns = [
    path('summary/', DashboardSummaryView.as_view(), name='dashboard-summary'),
    path('categories/', CategoryBreakdownView.as_view(), name='dashboard-categories'),
    path('trends/monthly/', MonthlyTrendsView.as_view(), name='dashboard-monthly'),
    path('trends/weekly/', WeeklyTrendsView.as_view(), name='dashboard-weekly'),
    path('recent/', RecentActivityView.as_view(), name='dashboard-recent'),
]
