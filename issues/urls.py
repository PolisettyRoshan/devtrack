from django.urls import path

from .views import issues, reporters


urlpatterns = [
    path("reporters/", reporters),
    path("issues/", issues),
]
