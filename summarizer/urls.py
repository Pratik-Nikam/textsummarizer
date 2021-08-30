

from django.urls import path
from .views import SummarizerView
urlpatterns = [
    path("", SummarizerView.as_view(), name="summarizer_view")
]