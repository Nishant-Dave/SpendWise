"""
Root URL configuration for the SpendWise project.
"""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),

    # All expenses app routes (mounted at root so '/' is the dashboard)
    path('', include('backend.expenses.urls')),
]

# Global LOGIN_URL used by @login_required redirects
# (also set in settings.py via LOGIN_URL if preferred)
