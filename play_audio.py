#!usr/bin/env python  
#coding=utf-8  

import pyaudio  
import wave

#define stream chunk   
chunk = 1024  

def play_audio_file(filename):

    #open a wav format music
    f = wave.open(filename,"rb")
    #instantiate PyAudio
    p = pyaudio.PyAudio()
    #open stream
    stream = p.open(format = p.get_format_from_width(f.getsampwidth()),
                    channels = f.getnchannels(),
                    rate = f.getframerate(),
                    output = True)
    #read data
    data = f.readframes(chunk)

    #play stream
    while data:
        stream.write(data)
        data = f.readframes(chunk)

    #stop stream
    stream.stop_stream()
    stream.close()

    #close PyAudio
    p.terminate()

#
# play_audio_file("output0.wav")
# play_audio_file("output1.wav")