"""
URL configuration for the SpendWise expenses app.

All paths are namespaced under the 'expenses' app label.
"""

from django.urls import path

from . import views

urlpatterns = [
    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------
    path('register/', views.register_view, name='register'),
    path('login/',    views.login_view,    name='login'),
    path('logout/',   views.logout_view,   name='logout'),

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------
    path('', views.dashboard_view, name='dashboard'),

    # ------------------------------------------------------------------
    # Categories
    # ------------------------------------------------------------------
    path('categories/',             views.category_list_view,   name='category_list'),
    path('categories/add/',         views.category_create_view, name='category_create'),
    path('categories/<int:pk>/delete/', views.category_delete_view, name='category_delete'),

    # ------------------------------------------------------------------
    # Transactions
    # ------------------------------------------------------------------
    path('transactions/',                    views.transaction_list_view,   name='transaction_list'),
    path('transactions/add/',                views.transaction_create_view, name='transaction_create'),
    path('transactions/<int:pk>/',           views.transaction_detail_view, name='transaction_detail'),
    path('transactions/<int:pk>/edit/',      views.transaction_update_view, name='transaction_update'),
    path('transactions/<int:pk>/delete/',    views.transaction_delete_view, name='transaction_delete'),

    # ------------------------------------------------------------------
    # Settings
    # ------------------------------------------------------------------
    path('settings/', views.settings_view, name='settings'),

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------
    path('export/csv/',     views.export_transactions_csv, name='export_csv'),
    path('api/chart-data/', views.dashboard_chart_data,    name='chart_data'),
]
