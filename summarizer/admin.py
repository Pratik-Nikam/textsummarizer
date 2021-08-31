from django.contrib import admin
from summarizer.models import Summarizer


class SummarizerAdmin(admin.ModelAdmin):
    pass
admin.site.register(Summarizer, SummarizerAdmin)

# Register your models here.
