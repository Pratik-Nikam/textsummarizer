from email import message
from django.shortcuts import render
from .models import SourceType, Summarizer
from .services import SummarizerService, sendMail
# Create your views here.
from django.views import View
from django.http import JsonResponse

class SummarizerView(View, SummarizerService):
    template_name = 'summarizer.html'
    context = {"source_type": dict(SourceType.choices)}
    
    def get(self, request):
        data = Summarizer.objects.all()
        self.context['data'] = data
        return render(request, self.template_name, context=self.context)

    def post(self, request):
        print(request.FILES)
        file = request.FILES['uploaded_file']
        file_name = file.name
        summarizer_obj = self.save_uploaded_data(request=request)
        print(summarizer_obj.uploaded_file, "*"*10)
        print(summarizer_obj.uploaded_file.name)
        # self.speech_to_text(summarizer_obj.uploaded_file, summarizer_obj.uploaded_file.name)
        if summarizer_obj.source == 'text_file':
            summary_data, source_data = self.read_text_file(summarizer_obj.uploaded_file) 

        else:
            summary_data, source_data = self.convert_video_to_wav(summarizer_obj.uploaded_file, summarizer_obj.uploaded_file.name)

        summarizer_obj.summerized_data = summary_data
        summarizer_obj.source_data = source_data
        summarizer_obj.file_name = file_name
        summarizer_obj.save()

        data = Summarizer.objects.all()
        self.context['data'] = data

        return render(request, self.template_name, context=self.context)



class EmailSummary(View):

    def post(self, request):
        data = dict(request.POST.items())
        print(data)
        recipients = request.POST.get('email_receiver')
        message = request.POST.get('email_body')
        
        subject = f"Summary for the input file {request.POST.get('file_name')}"
        print(recipients, type(recipients))

        sendMail([recipients], subject, message)

        return JsonResponse({'status':"success"})

