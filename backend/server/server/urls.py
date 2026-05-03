from django.urls import path, include, re_path
from django.contrib import admin 

from apps.endpoints.urls import urlpatterns as endpoints_urlpatterns 

urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns += [
    path('api/v1/', include('apps.endpoints.urls')),
]
