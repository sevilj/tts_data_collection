
import os, re,shutil
from numhandle import replaceNumberstoWords
import librosa


#List all files in the directory
def list_all_files_in_dir(path_to_audio_folder):
    files = os.listdir(path_to_audio_folder)
    return files


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

# Get the indexes of audios which are less than 15 secs (the duration can be changed to your preference)

#Copy those audios from direcotry with mixed audios to clear/wavs directory

def get_audio_indexes(audio_files):
    global audio_indexes_less_than_15
    audio_indexes_less_than_15 = []
    for audio in audio_files:
        if (librosa.get_duration(filename='/Users/sevil/Desktop/mixed/wavs/' + audio)) <= 15:
            shutil.copy("/Users/sevil/Desktop/mixed/wavs/" + audio, "/Users/sevil/Desktop/clear/wavs")
            get_index_of_audio = audio[6:-4]
            audio_indexes_less_than_15.append(get_index_of_audio)
    return audio_indexes_less_than_15

# Get indexes of text_files


def get_text_indexes(text_files):
    text_indexes = []
    for texts in text_files:
        get_index_of_text = texts[11:-4]
        text_indexes.append(get_index_of_text)
    return text_indexes

# Find texts that match audio_indexes_less_than_15 secs

# Copy those text files from directory with mixed text_files to clear/texts directory


def match_audio_and_texts():
    global to_path
    from_path = "/Users/sevil/Desktop/mixed/texts/"
    to_path = "/Users/sevil/Desktop/clear/texts/"
    for i in range(len(get_text_indexes(text_files))):
        for j in range(len(audio_indexes_less_than_15)):
            if audio_indexes_less_than_15[j] == get_text_indexes(text_files)[i]:
                shutil.copy(from_path +"audio_text_" + get_text_indexes(text_files)[i] +".txt", to_path)

# Concatenate texts of all text_files to one metadata.txt file

# The format is : audios_id|text with numbers as numbers|text with numbers as words


def metadata(text_files_after_filter):
    for texts in text_files_after_filter:
        with open(to_path + texts) as f:
            for line in f.readlines():
                # count += 1
                filehandle.write("audio_" + texts[11:-4] + "|" + line + "|" +replaceNumberstoWords(line) +'\n')


path_to_audio_folder = '/Users/sevil/Desktop/mixed/wavs'
audio_files = list_all_files_in_dir(path_to_audio_folder)
audio_files.sort(key=natural_keys)

print(get_audio_indexes(audio_files))

path_to_text_folder = '/Users/sevil/Desktop/mixed/texts'
text_files = list_all_files_in_dir(path_to_text_folder)
text_files.sort(key=natural_keys)

print(get_text_indexes(text_files))

match_audio_and_texts()

path_to_matched_text_folder = "/Users/sevil/Desktop/clear/texts"
text_files_after_match = (list_all_files_in_dir(path_to_matched_text_folder))
text_files_after_match.sort(key=natural_keys)
filehandle = open("metadata.txt",'w')

metadata(text_files_after_match)

