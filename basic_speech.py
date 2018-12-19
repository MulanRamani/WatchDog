import calendar
import time
import math
import re
import requests
import pygame
from random import randint
from string import Template
from gtts import gTTS
from gtts_token.gtts_token import Token

def _patch_faulty_function(self):
    if self.token_key is not None:
        return self.token_key

    timestamp = calendar.timegm(time.gmtime())
    hours = int(math.floor(timestamp / 3600))

    results = requests.get("https://translate.google.com/")
    tkk_expr = re.search("(tkk:*?'\d{2,}.\d{3,}')", results.text).group(1)
    tkk = re.search("(\d{5,}.\d{6,})", tkk_expr).group(1)
    
    a , b = tkk.split('.')

    result = str(hours) + "." + str(int(a) + int(b))
    self.token_key = result
    return result

# Monkey patch faulty function.
Token._get_token_key = _patch_faulty_function

hubdog_greeting_array = ['%s, Your smile is proof that the best things in life are free',
'You look great today, %s!',
'%s, Happiness looks great on you!',
'%s, You bring out the best in people',
"%s, You're the kind of person who could make even Kanye smile",
"You're really fun to be around, %s",
'%s, You have a great sense of style',
'Thank you for giving a shit, %s',
'%s, Thank you for making Hubdoc such a great place to work at',
'Good Morning, %s',
'Hi %s, you have a great sense of humor'
'I love your enthusiasm, %s'
'%s your positive attitude is infectious'
'Thanks for being so reliable, %s'
'You’re so great to work with, %s'
]

jokes_array = [
'How do construction workers party? They raise the roof',
'What’s a snowman’s favourite breakfast?  Frosted Flakes',
'How do you get a Canadian to apologize?  Step on their foot.',
"what’s the tallest building in the city? The library, because it has so many stories",
'Where do programmers go to take a vacation from School? String break',
'As a programmer, sometimes I Feel a void.  And I know I’ve reached the point of no return.',
'Why don’t bachelors like Git? Because they are afraid to commit.']

general_greeting_array = ['Welcome to Hubdoc']

def main(names):
    if names[0] == "Unknown":
        unknown_hubdog()
    else:
        known_hubdog(names[0])

def known_hubdog(hubdog_name):
  
    index = randint(0, len(hubdog_greeting_array)-1)
    print(index)
    greeting_string = hubdog_greeting_array[index] % hubdog_name
    tts = gTTS(greeting_string)
    tts.save('known.mp3')
    print('saved mp3 file')
    pygame.init()
    pygame.mixer.music.load('known.mp3')
    pygame.mixer.music.play()
    time.sleep(5)
    print('played mp3')
    time.sleep(5)
    say_joke()


def unknown_hubdog():
    index = randint(0, len(general_greeting_array)-1)
    greeting_string = general_greeting_array[index] + '. What is your name?'
    tts = gTTS(greeting_string)
    tts.save('unknown.mp3')
    print('saved mp3 file')
    pygame.init()
    pygame.mixer.music.load('unknown.mp3')
    pygame.mixer.music.play()
    time.sleep(5)
    print('played mp3')

    #hasn't been implemented yet
    # listen()
    
    # return_string = 'And who are you here to see?'
    # tts = gTTS(return_string)
    # tts.save('hello.mp3')
    # listen()
def say_joke():
    index = randint(0, len(jokes_array)-1)
    joke_string = "Here's a fun joke. " + jokes_array[index]
    tts = gTTS(greeting_string)
    tts.save('joke.mp3')
    print('saved mp3 file')
    pygame.init()
    pygame.mixer.music.load('joke.mp3')
    pygame.mixer.music.play()
    time.sleep(5)
    print('played mp3')

if __name__ == "__main__":
    main([])
