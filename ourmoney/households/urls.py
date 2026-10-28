from django.urls import path

from . import views

urlpatterns = [
    path('', views.HouseholdCreateView.as_view(), name='household-create'),
    path('join/', views.HouseholdJoinView.as_view(), name='household-join'),
]
