from processor.views import process_image_api
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/process-image/', process_image_api, name='process-image'),
]
