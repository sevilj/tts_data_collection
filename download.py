from bs4 import BeautifulSoup
import os, sys, re
import requests
from urllib.request import urlretrieve
import time, random
import librosa
import soundfile as sf
import numpy as np

def listToString(s):   
    str1 = " "
    return (str1.join(s)) 

def has_cyrillic(text):
    return bool(re.search('[\u0400-\u04FF]', text))

def splitBySilence (audio, maxSilence=1530, silenceDur=.33):
    '''
    Spliting audio by silence

    audio - path to the audio
    maxSilence - maximum number of the sample anplitude 
    silenceDur - duration of the silence in seconds
    '''

    data, sr = librosa.load(audio, sr=16000)                        # reading file and taking samples and change sample rate to 16 kHz
    t = librosa.get_duration(y=data,sr=sr)                          # audio duration in seconds
    time = np.arange(0, t, t/len(data))                             # arange the time accroding to samples' size

    silenceP = []                                                   # list to store our points of silence begining on the audio                             
    silence = 0                                                     # variable to calculate if it is silence or not
    i = 0
    while i < len(time):
        if np.abs(data[i]*sr) < maxSilence:                       # if the amplitude of the voice is not bigger than given value
            silence += int((len(time)*.01)/(int(t)))                # starting calculating silence time by adding 0.01 second 
            if silence >= int((len(time)*silenceDur)/(int(t))):     # if it is bigger than 0.03 seconds => silence
                silenceP.append(i - silenceDur*len(time)/t)         # adding the beginning of the silence
                silence = 0                                         # after considiration that it is silince we are starting again to calculate silence point
        else:    
            silence = 0                                             # in case if this wasn't silence we begin to calculate it from 0
        i += int((len(time)*.01)/(int(t)))                          # checking each 0.01 of the second

    newSilence = []                                                 # list of the real silence point
    for j in range(len(silenceP)): 
        if j+1 == len(silenceP): break                              

        if round(silenceP[j+1]-silenceP[j],1) > (silenceDur+0.1)*len(time)/t:    # if the difference of the neighbor silence points are bigger than the silenc min+0.01 second
            if newSilence:                                                       # Then it was actually not the silence     
                if newSilence[len(newSilence)-1] == silenceP[j]:                 # In case if the beginning of the silence equal to the end of the previous silence part                 
                    newSilence.remove(silenceP[j])
                    newSilence.append(silenceP[j+1])
                else:
                    newSilence.append(silenceP[j])
                    newSilence.append(silenceP[j+1])
            else:
                newSilence.append(silenceP[j])
                newSilence.append(silenceP[j+1])
    
    dividedData, durations = [], []
    j = 0
    while j < len(newSilence):
        if j+1 != len(newSilence): 
            print (int(newSilence[j]),int(newSilence[j+1]))
            durations.append((newSilence[j+1]-newSilence[j])*t/len(time))              # adding to the list of the durations of non-silent parts
            dividedData.append(data [int(newSilence[j]+100):int(newSilence[j+1])])    # completeng list of the new data of samples
        j+=2


    return dividedData, durations, sr

if len(sys.argv) != 2:
    print('Usage: download_audio.py {number_of_audios_to_download}')
    quit()

if not os.path.exists('audios'):
    os.makedirs('audios')

if not os.path.exists('splitted'):
    os.makedirs('splitted')

if not os.path.exists('texts'):
    os.makedirs('texts')

# Gets list of already checked news
checked = []
if os.path.exists('checked.txt'):
    fp = open('checked.txt','r+')
    line = fp.readline()
    while line:
        checked.append(line)
        line = fp.readline()
    f = lambda x: x.replace("\n", "")
    checked = list(map(f, checked))
else:
    fp = open('checked.txt','a')

count, k, collected = 1, 1, 0
while os.path.exists('./audios/audio_' + str(count) + '.wav'):
    count += 1	
while os.path.exists('./splitted/splitted_' + str(k) + '.wav'):
    k += 1

news = str(373557)


while collected != int(sys.argv[1]):

    # Get the not checked news
    while news in checked:
        news = str(int(news)-1)
    checked.append(news)
    fp.write(news+'\n')        

    rulingpage = requests.get("https://oxu.az/world/" + news, timeout=5).text
    soup = BeautifulSoup(rulingpage, 'html.parser')
    doctext = soup.find('div', class_='news-inner')
    
    # If the news exists
    if doctext != None:
        text = re.sub(r'[^\w\s]','',listToString(doctext.text.split('\n')[1:]))
        
        # If the news not in russian
        if not has_cyrillic(text):

            print("Found right news:", news, ". Searching for audio...",)
            print ('Downloading...')

            audio_link = soup.find('audio')
            
            if audio_link != None:
                audio_link = audio_link.get("src")
                urlretrieve(audio_link, './audios/audio_' + str(count) + '.mp3')

                audio_duration = librosa.get_duration(filename='./audios/audio_' + str(count) + '.mp3')

                # Transform mp3 to wav format
                os.popen('sox ' + './audios/audio_' + str(count) + '.mp3' + ' -e signed-integer -c 1 -b 16 -r 22050 ' + './audios/audio_' + str(count) + '.wav')
                time.sleep(1)
                os.remove('./audios/audio_' + str(count) + '.mp3')

                # Downloads text of the audio
                f = open('./texts/audio_text_' + str(count) +'.txt', "a")
                f.write(re.sub(r'[^\w\s]','',listToString(doctext.text.split('\n')[1:])))

                divided, durations, s = splitBySilence('./audios/audio_' + str(count) + '.wav', maxSilence=250, silenceDur=0.045)


                for i in range(len(divided)):
                    name = './splitted/splitted_' + str(k)+'.wav'          # naming audio chunk
                    sf.write(name, divided[i],s,subtype='PCM_16')               # write it first and changing bit rate
                    k+=1

                count += 1
                collected += 1

        news = str(int(news)-1)
