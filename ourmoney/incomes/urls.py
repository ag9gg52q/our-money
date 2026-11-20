from django.urls import path

from . import views

urlpatterns = [
    path('', views.IncomeListView.as_view(), name='income-list'),
    path('<uuid:pk>/', views.IncomeDetailView.as_view(), name='income-detail'),
]
