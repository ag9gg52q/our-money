from django.urls import path

from . import views

urlpatterns = [
    path('', views.CategoryListView.as_view(), name='category-list'),
    path('<uuid:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),
]
