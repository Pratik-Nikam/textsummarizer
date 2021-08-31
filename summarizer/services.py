from .models import Summarizer
import speech_recognition as sr
import subprocess
from django.conf import settings
import os
from textsummarizer.settings import BASE_DIR
import subprocess

from ibm_watson import SpeechToTextV1

from ibm_watson.websocket import RecognizeCallback, AudioSource

from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from pydub import AudioSegment
from pydub.silence import split_on_silence
import math
class SummarizerService:

    def save_uploaded_data(self, request):
        print(request.POST)
        uploaded_file = request.FILES['uploaded_file']
        print(uploaded_file)
        data = dict(request.POST.items())
        del data['csrfmiddlewaretoken']
        summarizer_obj = Summarizer.objects.create(**data, uploaded_file=uploaded_file)
        return summarizer_obj

    def convert_video_to_wav(self, video_path, file_name):
        print(file_name)
        video_path = os.path.join(settings.MEDIA_ROOT, str(video_path))
        media_path = os.path.join(BASE_DIR, "media")
        print(media_path, file_name)
        print("video path", video_path)
        # final_path = media_path, 
        # ffmpeg -i aud_rec_2.mp4 aak-swa-conv.wav
        output_path = os.path.join(settings.MEDIA_ROOT, str(file_name)+".wav")
        print("output path", output_path)
        command = f"ffmpeg -i {video_path} {output_path}"
        proc = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        out, err = proc.communicate()
        self.convert_wav_to_text(output_path)
        return output_path

    def convert_wav_to_text(self, file_path):
        
        r = sr.Recognizer()
        with sr.WavFile(file_path) as source:
            audio = r.record(source)

        # try:
        print("Transcription: " + r.recognize_google(audio))
        # except (LookupError, Exception) as e:
        #     print("Could not understand audio", e)



    def speech_to_text(self, video_path, file_name):
        video_path = os.path.join(settings.MEDIA_ROOT, str(video_path))
        output_path = os.path.join(settings.MEDIA_ROOT, str(file_name)+".wav")
        command = f'ffmpeg -i {video_path} -ab 160k -ar 44100 -vn {output_path}'

        subprocess.call(command, shell=True)

        apikey = 'H6GW5-S_Hu1MtIyHtQ2SiU0UyJSyV7G8eXJLdglH8KFv'

        url = 'https://api.au-syd.speech-to-text.watson.cloud.ibm.com/instances/56bff63d-0da7-49c6-b4e9-f74a5f7b2de3'

        authenticator = IAMAuthenticator(apikey)

        stt = SpeechToTextV1(authenticator=authenticator)
        print(output_path)
        stt.set_service_url(url)
 
        # open the audio file using pydub
        obj = SplitWavAudioMubin(filepath=output_path)
        obj.multiple_split(1)



        # with open(output_path,'rb') as f:
           
        #     res = stt.recognize(audio=f,content_type='audio/wav',model='en-AU_NarrowbandModel',continuous=True).get_result()
        #     print(res)
        # text = [result['alternatives'][0]['transcript'].rstrip() + '.\n' for result in res['results']]
            
        # print(text)




class SplitWavAudioMubin():
    def __init__(self, filepath):
        self.folder = "audio_chunks"
        self.filepath = filepath
        print(self.filepath, "*********")
        self.audio = AudioSegment.from_wav(self.filepath)

    def get_duration(self):
        return self.audio.duration_seconds

    def single_split(self, from_min, to_min, split_filename):
        t1 = from_min * 60 * 1000
        t2 = to_min * 60 * 1000
        split_audio = self.audio[t1:t2]
        split_audio.export(self.folder + '\\' + split_filename, format="wav")

    def multiple_split(self, min_per_split):
        total_mins = math.ceil(self.get_duration() / 60)
        for i in range(0, total_mins, min_per_split):
            split_fn = str(i) + '_' + "chunk.wav"
            self.single_split(i, i+min_per_split, split_fn)
            print(str(i) + ' Done')
            if i == total_mins - min_per_split:
                print('All splited successfully')
            # file_path = os.path.join(settings.BASE_DIR, "\\"+'audio_chunks'+"\\"+split_fn)
            file_path = str(settings.BASE_DIR)+"\\"+'audio_chunks'+"\\"+split_fn
            print(file_path, "--------------->", settings.BASE_DIR) 
            self.convert_wav_to_text(file_path=file_path)
            
    def convert_wav_to_text(self, file_path):
        
        r = sr.Recognizer()
        with sr.WavFile(file_path) as source:
            audio = r.record(source)

        # try:
        print("Transcription: " + r.recognize_google(audio))