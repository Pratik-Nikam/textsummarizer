from django.db import models
from django.utils.translation import gettext_lazy as _
from .utils import file_uploaded_path
# Create your models here.

class SourceType(models.TextChoices):
   URL = "url", _("URL")
   VIDEO_FILE = "video_file", _("Video File")
   AUDIO_FILE = "audio_file", _("Audio File")
   TEXT_FILE = "text_file", _("Text File")


class Summarizer(models.Model):
    source = models.CharField(choices=SourceType.choices, max_length=20, 
                                null=False, blank=False, 
                                default=SourceType.VIDEO_FILE)
    source_data = models.TextField()
    uploaded_file = models.FileField(upload_to=file_uploaded_path, null=True, blank=True)
    file_name = models.CharField(max_length=255)
    summerized_data = models.TextField()
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
   #  file_meta_data = models.JSONField(default=dict)


