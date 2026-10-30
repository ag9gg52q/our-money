from django.urls import path

from . import views

urlpatterns = [
    path(
        'categories/<uuid:category_id>/subcategories/',
        views.SubcategoryListView.as_view(),
        name='subcategory-list',
    ),
    path(
        'subcategories/<uuid:pk>/', views.SubcategoryDetailView.as_view(), name='subcategory-detail'
    ),
]
