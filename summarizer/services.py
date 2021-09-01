# from transformers.tokenization_utils_base import TruncationStrategy
from .models import Summarizer
import speech_recognition as sr
import subprocess
from django.conf import settings
import os
from textsummarizer.settings import BASE_DIR
import subprocess

from email.utils import formataddr
import email
import smtplib
from email.mime.text import MIMEText
import traceback

from ibm_watson import SpeechToTextV1

from ibm_watson.websocket import RecognizeCallback, AudioSource

from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from pydub import AudioSegment
from pydub.silence import split_on_silence
import math

from .models import SourceType

# from transformers import BartForConditionalGeneration, BartTokenizer, BartConfig

# Loading the model and tokenizer for bart-large-cnn

import shutil

class SummaryGeneration:

    def __init__(self) -> None:
        self.tokenizer=BartTokenizer.from_pretrained('facebook/bart-large-cnn')
        self.model=BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')

    def generate_summart(self, original_text):

        # tokenizer=BartTokenizer.from_pretrained('facebook/bart-large-cnn')
        # model=BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')

        # print(original_text)
        # original_text = ""

        # Encoding the inputs and passing them to model.generate()
        inputs = self.tokenizer.batch_encode_plus([original_text],return_tensors='pt',truncation=True)
        print(inputs)
        summary_ids = self.model.generate(inputs['input_ids'], early_stopping=True)
        # print(summary_ids, '============')

        # Decoding and printing the summary
        bart_summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        # print(bart_summary)

        return bart_summary


class SummarizerService:

    def save_uploaded_data(self, request):
        print(request.POST)
        uploaded_file = request.FILES['uploaded_file']
        print(uploaded_file)
        data = dict(request.POST.items())
        del data['csrfmiddlewaretoken']
        summarizer_obj = Summarizer.objects.create(**data, uploaded_file=uploaded_file)
        # if data.get('source') == SourceType.TEXT_FILE:


        return summarizer_obj

    def read_text_file(self, file_path):


        file_path = os.path.join(settings.MEDIA_ROOT, str(file_path))
        # media_path = os.path.join(BASE_DIR, "media")
        print(file_path, "---------------------------")

        with open(file_path, 'r') as f:
            data = f.read()



        n_obj = SummaryGeneration()

        summary_data = n_obj.generate_summart(data)

        return summary_data, data

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

        chunks_path = str(settings.MEDIA_ROOT) +str(file_name)
        print(chunks_path)
        summary_data, source_data = self.process_wav_to_text(output_path,chunks_path)
        return summary_data, source_data

    def process_wav_to_text(self, file_path, chunks_path):
        obj = SplitWavAudioMubin(filepath=file_path, folder=chunks_path)
        source_data = obj.multiple_split(1)
        print("--",source_data)
        n_obj = SummaryGeneration()
        summary_data = n_obj.generate_summart(source_data)
        print(summary_data, "final_summary================")
        print(chunks_path, "chunls ",file_path, "file path----------" )


        try:
            shutil.rmtree(chunks_path)
            # os.remove(chunks_path)
        except Exception as err:
            print(err)

        return summary_data, source_data

    # def get_summary(self):

    #     summary = self.generate_summart()

class SplitWavAudioMubin():
    def __init__(self, filepath, folder="audio_chunks"):
        try:
            os.mkdir(folder)
        except OSError as error:
            pass
        self.folder = folder
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
        text_data = ""
        for i in range(0, total_mins, min_per_split):
            split_fn = str(i) + '_' + "chunk.wav"
            self.single_split(i, i+min_per_split, split_fn)
            print(str(i) + ' Done')
            if i == total_mins - min_per_split:
                print('All splited successfully')
            # file_path = os.path.join(settings.BASE_DIR, "\\"+'audio_chunks'+"\\"+split_fn)
            file_path = str(settings.BASE_DIR)+"\\"+ self.folder +"\\"+split_fn

            path_ = self.folder + "\\"+ split_fn
            print(file_path, "--------------->", settings.BASE_DIR, "path===", path_)
            text_data += self.convert_wav_to_text(file_path=path_)
        return text_data

    def convert_wav_to_text(self, file_path):
        r = sr.Recognizer()
        with sr.WavFile(file_path) as source:
            audio = r.record(source)
        # print("Transcription: " + r.recognize_google(audio))
        return r.recognize_google(audio)


def sendMail(recipients, subject, message): # recipients - list of emails. Eg: ['john.doe@example.com', 'john.smith@example.co.uk']
    server = None
    if recipients == None or len(recipients) <= 0:
        raise ValueError("No recipients: {}".format(recipients))
    try:
        server = smtplib.SMTP('outbound.cisco.com', 25)
        # server.set_debuglevel(True) # show communication with the server
        EMAIL_FROM_NAME = 'TextSummarizer'
        EMAIL_FROM_ADDRESS = 'textsummarizer@cisco.com'
        message = MIMEText(message, "html")
        message["To"] = ", ".join(recipients) #email.utils.formataddr(("", toEmail))
        message["From"] = email.utils.formataddr((EMAIL_FROM_NAME, EMAIL_FROM_ADDRESS))
        message["Subject"] = subject
    
        print("Recipients: {}".format(message["To"]), flush=True)
        server.sendmail(EMAIL_FROM_ADDRESS, recipients, message.as_string())
        return 0
    except Exception:
        print("Exception while sending mail to: {}".format(recipients))
        traceback.print_exc()
        return -1
    finally:
        if server != None: server.quit()
        

