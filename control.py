from transcribe import *
from multiprocessing import Process

p = Process(target=main)

while True:
    try:
        p.start()
        p.join()
    except Exception as e:
        p.start()
        p.join()