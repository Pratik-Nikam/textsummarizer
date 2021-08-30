from django.shortcuts import render
from .models import SourceType
from .services import SummarizerService
# Create your views here.
from django.views import View


class SummarizerView(View, SummarizerService):
    template_name = 'summarizer.html'
    context = {"source_type": dict(SourceType.choices)}
    
    def get(self, request):
        return render(request, self.template_name, context=self.context)

    def post(self, request):
        print(request.FILES)
        file = request.FILES['uploaded_file']
        # print(type(file))
        summarizer_obj = self.save_uploaded_data(request=request)
        print(summarizer_obj.uploaded_file, "*"*10)
        print(summarizer_obj.uploaded_file.name)
        self.speech_to_text(summarizer_obj.uploaded_file, summarizer_obj.uploaded_file.name)
        # self.convert_video_to_wav(summarizer_obj.uploaded_file, summarizer_obj.uploaded_file.name)
        return render(request, self.template_name, context=self.context)





