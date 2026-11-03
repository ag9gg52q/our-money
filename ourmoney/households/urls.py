from django.urls import path

from . import views

urlpatterns = [
    path('', views.HouseholdCreateView.as_view(), name='household-create'),
    path('join/', views.HouseholdJoinView.as_view(), name='household-join'),
    path('current/', views.CurrentHouseholdView.as_view(), name='household-current'),
    path(
        'current/members/<uuid:pk>/make-admin/',
        views.MakeAdminView.as_view(),
        name='household-member-make-admin',
    ),
]
