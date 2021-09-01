

from django.urls import path
from .views import SummarizerView, EmailSummary
urlpatterns = [
    path("", SummarizerView.as_view(), name="summarizer_view"),
    path("email/", EmailSummary.as_view(), name="email_view")

]