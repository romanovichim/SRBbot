

import xml.etree.ElementTree as XmlElementTree
import subprocess
import httplib2
import tempfile
import settings
import requests
import logging
import json
import os
from extentions import EnumHelper, FileHelper, TextHelper
from signal import signal, SIGINT, SIGTERM, SIGABRT
from pyvona import create_voice as ivona_voice
# noinspection PyPackageRequirements
#from telegram.ext.dispatcher import run_async
from pymongo import MongoClient
from random import SystemRandom
from enum import Enum, unique
from time import time, sleep
# noinspection PyPackageRequirements
#from telegram import Chat

random = SystemRandom()

class FfmpegWrap(object):
    @staticmethod
    def __convert__(command, in_filename: str = None, in_content: bytes = None):
        with tempfile.TemporaryFile() as temp_out_file:
            temp_in_file = None

            if in_content:
                temp_in_file = tempfile.NamedTemporaryFile(delete=False)
                temp_in_file.write(in_content)
                in_filename = temp_in_file.name
                temp_in_file.close()
            if not in_filename:
                raise Exception('Neither input file name nor input bytes is specified.')

            proc = subprocess.Popen(command(in_filename), stdout=temp_out_file, stderr=subprocess.DEVNULL,shell = True)
            proc.wait()

            if temp_in_file:
                os.remove(in_filename)

            temp_out_file.seek(0)
            return temp_out_file.read()

    @staticmethod
    def convert_to_ogg(in_filename: str = None, in_content: bytes = None):
        command = lambda f: [
            os.path.join(settings.Ffmpeg.DIRECTORY, 'ffmpeg'),
            '-loglevel', 'quiet',
            '-i', f,
            '-f', 'ogg',
            '-acodec', 'libopus',
            '-'
        ]

        return FfmpegWrap.__convert__(command, in_filename, in_content)

    @staticmethod
    def convert_to_mp3(in_filename: str = None, in_content: bytes = None):
        command = lambda f: [
            os.path.join(settings.Ffmpeg.DIRECTORY, 'ffmpeg'),
            '-loglevel', 'quiet',
            '-i', f,
            '-f', 'mp3',
            '-acodec', 'libmp3lame',
            '-'
        ]

        return FfmpegWrap.__convert__(command, in_filename, in_content)

    @staticmethod
    def convert_to_pcm16b16000r(in_filename: str = None, in_content: bytes = None):
        command = lambda f: [
            os.path.join(settings.Ffmpeg.DIRECTORY, 'ffmpeg'),
            '-loglevel', 'quiet',
            '-i', f,
            '-f', 's16le',
            '-acodec', 'pcm_s16le',
            '-ar', '16000',
            '-'
        ]

        return FfmpegWrap.__convert__(command, in_filename, in_content)

    @staticmethod
    def get_duration(file_path: str = None, audio_content: bytes = None):
        temp_file = None

        if audio_content:
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            temp_file.write(audio_content)
            temp_file.close()

            file_path = temp_file.name

        ffmpeg_proc = subprocess.Popen(
            [os.path.join(settings.Ffmpeg.DIRECTORY, 'ffprobe'), file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

        output = ffmpeg_proc.communicate()[0].decode('utf-8')
        duration = None
        for o in output.split('\n'):
            if 'Duration' in o and 'misdetection' not in o:
                duration = o.split()[1][:-1].split(':')  # here goes magic => time['h', 'm', 's']
                break
        if duration:
            duration = float(duration[0]) * 3600 + float(duration[1]) * 60 + float(duration[2])
            if duration < 1:
                duration = 1
        else:
            duration = 0

        if temp_file:
            os.remove(file_path)

        return duration


class Speech(object):
    # noinspection PyProtectedMember
    @staticmethod
    def stt(filename: str = None, content: bytes = None, request_id: str = None, topic: str = 'notes',
            lang: str = 'ru-RU', key: str = settings.Speech.Yandex.API_KEY):
        if filename is not None:
            file = open(filename, 'br')
            content = file.read()
            file.close()
        if content is None:
            raise Exception('No file name or content provided.')

        #content = FfmpegWrap.convert_to_pcm16b16000r(in_content=content)
        content = FfmpegWrap.convert_to_mp3(in_content=content)
        
        if request_id is not None:
            uuid = TextHelper.get_md5(request_id)
        else:
            uuid = TextHelper.get_md5(str(time()))

        url = settings.Speech.Yandex.STT_PATH + '?uuid=%s&key=%s&topic=%s&lang=%s' % (
            uuid,
            key,
            topic,
            lang
        )
        chunks = FileHelper.read_chunks(settings.Speech.Yandex.CHUNK_SIZE, content=content)

        connection = httplib2.HTTPConnectionWithTimeout(settings.Speech.Yandex.STT_HOST)

        connection.connect()
        connection.putrequest('POST', url)
        connection.putheader('Transfer-Encoding', 'chunked')
        connection.putheader('Content-Type', 'audio/x-mpeg-3')
        connection.endheaders()

        
        
        for chunk in chunks:
            connection.send(('%s\r\n' % hex(len(chunk))[2:]).encode('utf-8'))
            connection.send(chunk)
            connection.send('\r\n'.encode('utf-8'))
            sleep(1)

        connection.send('0\r\n\r\n'.encode('utf-8'))
        ''' 
        print('do response')
        uuid = TextHelper.get_md5(str(time()))
        key='3b714925-a4a2-48da-8a6d-8c8907b8fb0a' 
        #uuid = 'eb6dc985-5b3c-46ab-a73b-6db5d18b5c2a'
        url = 'https://asr.yandex.net/asr_xml?key=' + key + '&uuid=' + uuid + '&topic=queries&lang=ru-RU'
        headers = {"Content-Type": 'audio/x-mpeg-3'}
        data = open('rectry4.mp3', 'rb').read()
        tmp = requests.post(url, headers=headers, data=data)
        '''
        
        response = connection.getresponse()
        if response.code == 200:
            response_text = response.read()
            xml = XmlElementTree.fromstring(response_text)

            if int(xml.attrib['success']) == 1:
                max_confidence = - float("inf")
                text = ''

                for child in xml:
                    if float(child.attrib['confidence']) > max_confidence:
                        text = child.text
                        max_confidence = float(child.attrib['confidence'])

                if max_confidence != - float("inf"):
                    return text
                else:
                    raise Exception(
                        'STT: No text found.\n\nResponse:\n%s\n\nRequest id: %s' % (
                            response_text,
                            request_id if request_id is not None else 'None'
                        )
                    )
        else:
            raise Exception('STT: Yandex ASR bad response.\nCode: %s\n\n%s' % (response.code, response.read()))
        

# Adds 'id' property to record
class IdFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, 'id'):
            record.id = 'None'
        return True


class UpdatersStack(object):
    def __init__(self, *updaters):
        self.updaters = list(updaters)

    def add_handlers(self, *handlers):
        for updater in self.updaters:
            for handler in handlers:
                updater.dispatcher.add_handler(handler)

    def idle(self, stop_signals=(SIGINT, SIGTERM, SIGABRT)):
        for updater in self.updaters:
            for sig in stop_signals:
                signal(sig, updater.signal_handler)
            updater.is_idle = self.is_idle

        while self.is_idle():
            sleep(1)

    def is_idle(self):
        is_idle = False
        for updater in self.updaters:
            if updater.is_idle:
                is_idle = True
                break

        return is_idle

    def start_polling(self, poll_interval=0.0, timeout=10, network_delay=5., clean=False, bootstrap_retries=0):
        for updater in self.updaters:
            updater.start_polling(poll_interval, timeout, network_delay, clean, bootstrap_retries)
