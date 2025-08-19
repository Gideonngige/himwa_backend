
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('himwa_app.urls')),
    path('admin/', admin.site.urls),
]
