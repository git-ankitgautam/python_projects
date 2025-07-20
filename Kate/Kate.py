import pyttsx3
import speech_recognition as sr
import datetime
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import re, requests, subprocess, urllib.parse, urllib.request
from bs4 import BeautifulSoup

import pafy

import threading as th

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)


def say(audio):
    engine.say(audio)
    engine.runAndWait()


def YTvideourl(search_term):
    query_string = urllib.parse.urlencode({"search_query": search_term})
    formatUrl = urllib.request.urlopen("https://www.youtube.com/results?" + query_string)
    search_results = re.findall(r"watch\?v=(\S{11})", formatUrl.read().decode())

    video_url = "https://www.youtube.com/watch?v=" + "{}".format(search_results[0])

    return video_url


"""def check():
    file_check = os.path.isfile('C:\\Python \\Projects \\Python projects\\User_data')
    if "flase" in file_check:
        p = input("Please Enter your password here:-")
        w = open('User_data', 'wt')
        w.write(p)"""

"""file_check = os.path.isfile('G:\\Python projects\\User_data')
print(file_check)"""

def Gui():
    import GUI


def wishMe():
    hour = int(datetime.datetime.now().hour)
    say("the time is")
    say(datetime.datetime.now().strftime("%H:%M"))
    if 0 <= hour < 12:
        say("Good Morning!")

    elif 12 <= hour < 18:
        say("Good Afternoon!")

    else:
        say("Good Evening!")

    say(" I am Kate. How may I help you?")


def takecommand():
    # It takes microphone input from the user and returns string output
    query = input()
    """r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")    
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")

    except Exception as e:
        # print(e)    
        print("Say that again please...")  
        return "None"
        """
    return query


def sendEmail(to, content):
    import smtplib
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    say("enter your email password for login")
    e_pass = input()
    server.login('ankitgautam485@gmail.com', e_pass)
    server.sendmail('ankitgautam485@gmail.com', to, content)
    server.close()


wishMe()


if __name__ == "__main__":
    
    # check()
    while True:
        query = takecommand().lower()

        # Logic for executing tasks based on query
        if 'wikipedia' in query:
            import wikipedia
            say('Searching Wikipedia...')
            query = query.replace("wikipedia", "")
            results = wikipedia.summary(query, sentences=5)
            say("According to Wikipedia")
            print(results)
            say(results)

        elif 'email' and 'send' in query:
            try:
                say("enter their email address please")
                to = input() 
                say("What should I say?")
                content = takecommand()
                sendEmail(to, content)
                say("Email has been sent!")
            except Exception as e:
                print(e)
                say("Sorry, I was not able to send this email") 
        
        
        elif 'youtube' and 'play' in query:
            import vlc
            query = query.replace("on youtube", "")
            query0 = query.replace("play", "")
            video_url = YTvideourl(query0)
            import urllib.request
            say("playing")
            say(query0)
            say("on youtube")


            video = pafy.new(video_url)
            best = video.getbest()
            playurl = best.url
            ins = vlc.Instance()
            player = ins.media_player_new()

            code = urllib.request.urlopen(video_url).getcode()
            if str(code).startswith('2') or str(code).startswith('3'):
                print('Stream is working')
            else:
                print('Stream is dead')

            Media = ins.media_new(playurl)
            Media.get_mrl()
            player.set_media(Media)
            player.play()
            good_states = ["State.Playing", "State.NothingSpecial", "State.Opening"]
            while str(player.get_state()) in good_states:
                time.sleep(2)
            player.stop()
            

        elif 'search' and 'google' in query:
            browser = webdriver.Chrome('C:\Python\Projects\chromedriver')
            browser.get("https://www.google.com")
            search_bar = browser.find_element_by_name('q')
            query0 = query.replace("search", "")
            query1 = query0.replace("on google", "")
            search_bar.send_keys(query1)
            search_bar.send_keys(Keys.ENTER)
            

        elif 'play music' in query:
            import os
            say("accessing your playlist")
            os.startfile(
                'E:\\Data\\Samsung galaxy m20\\Documents\\Music\\Playlists\\Playlist.wpl')

        elif "bye" in query:
            say("goodbye")
            exit()
