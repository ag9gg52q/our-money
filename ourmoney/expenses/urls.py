from django.urls import path

from . import views

urlpatterns = [
    path('', views.ExpenseListView.as_view(), name='expense-list'),
    path('debts/', views.OpenDebtListView.as_view(), name='debt-list'),
    path('debts/<uuid:pk>/settle/', views.DebtSettleView.as_view(), name='debt-settle'),
    path('debts/<uuid:pk>/cancel/', views.DebtCancelView.as_view(), name='debt-cancel'),
    path('<uuid:pk>/', views.ExpenseDetailView.as_view(), name='expense-detail'),
]
