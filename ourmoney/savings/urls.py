from django.urls import path

from . import views

urlpatterns = [
    path('', views.SavingsEntryListView.as_view(), name='savings-entry-list'),
    path('<uuid:pk>/', views.SavingsEntryDetailView.as_view(), name='savings-entry-detail'),
]
