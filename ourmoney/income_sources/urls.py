from django.urls import path

from . import views

urlpatterns = [
    path('', views.IncomeSourceListView.as_view(), name='income-source-list'),
    path('<uuid:pk>/', views.IncomeSourceDetailView.as_view(), name='income-source-detail'),
]
