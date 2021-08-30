
import datetime

def file_uploaded_path(instance, file_name):
    source_type = instance.source
    return '{0}'.format(file_name)