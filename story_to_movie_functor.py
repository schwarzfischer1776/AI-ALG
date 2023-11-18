import os
from datetime import datetime
import json

#Preparation 
language_codes = [
    "af-ZA", "ar-XA", "bg-BG", "bn-IN", "ca-ES",
    "cmn-CN", "cmn-TW", "cs-CZ", "da-DK", "de-DE",
    "el-GR", "en-AU", "en-GB", "en-IN", "en-US",
    "es-ES", "es-US", "eu-ES", "fi-FI", "fil-PH",
    "fr-CA", "fr-FR", "gl-ES", "gu-IN", "he-IL",
    "hi-IN", "hu-HU", "id-ID", "is-IS", "it-IT",
    "ja-JP", "kn-IN", "ko-KR", "lt-LT", "lv-LV",
    "ml-IN", "mr-IN", "ms-MY", "nb-NO", "nl-BE",
    "nl-NL", "pa-IN", "pl-PL", "pt-BR", "pt-PT",
    "ro-RO", "ru-RU", "sk-SK", "sr-RS", "sv-SE",
    "ta-IN", "te-IN", "th-TH", "tr-TR", "uk-UA",
    "vi-VN", "yue-HK"
]

def parse_text_into_sentences(text):
    sentences = []
    current_sentence = ""

    for char in text:
        current_sentence += char
        if char in ['.', '!', '?']:
            sentences.append(current_sentence.strip())
            current_sentence = ""

    # Add the last sentence if the text doesn't end with punctuation
    if current_sentence:
        sentences.append(current_sentence.strip())

    return sentences

### IMAGE CREATION ### 
'''
DALL-E image generation example for openai>1.2.3, saves requested images as files
-- not a code utility, has no input or return

# example pydantic models returned by client.images.generate(**img_params):
## - when called with "response_format": "url":
images_response = ImagesResponse(created=1699713836, data=[Image(b64_json=None, revised_prompt=None, url='https://oaidalleapiprodscus.blob.core.windows.net/private/org-abcd/user-abcd/img-12345.png?st=2023-11-11T13%3A43%3A56Z&se=2023-11-11T15%3A43%3A56Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2023-11-10T21%3A41%3A11Z&ske=2023-11-11T21%3A41%3A11Z&sks=b&skv=2021-08-06&sig=%2BUjl3f6Vdz3u0oRSuERKPzPhFRf7qO8RjwSPGsrQ/d8%3D')])

requires:
pip install --upgrade openai
pip install pillow
'''
import os
from io import BytesIO
import openai                  # for handling error types
from datetime import datetime  # for formatting date returned with images
import base64                  # for decoding images if recieved in the reply
import requests                # for downloading images from URLs
from PIL import Image          # pillow, for processing image types
import tkinter as tk           # for GUI thumbnails of what we got
from PIL import ImageTk        # for GUI thumbnails of what we got

def old_package(version, minimum):  # Block old openai python libraries before today's
    version_parts = list(map(int, version.split(".")))
    minimum_parts = list(map(int, minimum.split(".")))
    return version_parts < minimum_parts

if old_package(openai.__version__, "1.2.3"):
    raise ValueError(f"Error: OpenAI version {openai.__version__}"
                     " is less than the minimum version 1.2.3\n\n"
                     ">>You should run 'pip install --upgrade openai')")

file = open("JSON/openai_key.json")
key  = json.load(file)
openai_api_key = key['key']
file.close()

os.environ["OPENAI_API_KEY"] = openai_api_key

from openai import OpenAI
#client = OpenAI(api_key="")  # don't do this, OK?
client = OpenAI()  # will use environment variable "OPENAI_API_KEY"
def create_image(text, style, filename):
    
    prompt = (
     "Subject:" + text + ". Style:" + style + "."
    )

    image_params = {
     "model": "dall-e-3",  # Defaults to dall-e-2
     "n": 1,               # Between 2 and 10 is only for DALL-E 2
     "size": "1024x1024",  # 256x256, 512x512 only for DALL-E 2 - not much cheaper
     "prompt": prompt,     # DALL-E 3: max 4000 characters, DALL-E 2: max 1000
     "user": "myName",     # pass a customer ID to OpenAI for abuse monitoring
    }

    ## -- You can uncomment the lines below to include these non-default parameters --

    image_params.update({"response_format": "b64_json"})  # defaults to "url" for separate download

    ## -- DALL-E 3 exclusive parameters --
    #image_params.update({"model": "dall-e-3"})  # Upgrade the model name to dall-e-3
    #image_params.update({"size": "1792x1024"})  # 1792x1024 or 1024x1792 available for DALL-E 3
    #image_params.update({"quality": "hd"})      # quality at 2x the price, defaults to "standard" 
    #image_params.update({"style": "natural"})   # defaults to "vivid"

    # ---- START
    # here's the actual request to API and lots of error catching
    try:
        images_response = client.images.generate(**image_params)
    except openai.APIConnectionError as e:
        print("Server connection error: {e.__cause__}")  # from httpx.
        raise
    except openai.RateLimitError as e:
        print(f"OpenAI RATE LIMIT error {e.status_code}: (e.response)")
        raise
    except openai.APIStatusError as e:
        print(f"OpenAI STATUS error {e.status_code}: (e.response)")
        raise
    except openai.BadRequestError as e:
        print(f"OpenAI BAD REQUEST error {e.status_code}: (e.response)")
        raise
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise

    # make a file name prefix from date-time of response
    images_dt = datetime.utcfromtimestamp(images_response.created)
    img_filename = filename #images_dt.strftime('DALLE-%Y%m%d_%H%M%S')  # like 'DALLE-20231111_144356'

    # get the prompt used if rewritten by dall-e-3, null if unchanged by AI
    revised_prompt = images_response.data[0].revised_prompt

    # get out all the images in API return, whether url or base64
    # note the use of pydantic "model.data" style reference and its model_dump() method
    image_url_list = []
    image_data_list = []
    for image in images_response.data:
        image_url_list.append(image.model_dump()["url"])
        image_data_list.append(image.model_dump()["b64_json"])
    #Here choose one image only, this can be modified in future, if one wants to have all 4 images possibly.
    image_url_list = image_url_list[0:1]
    image_data_list = image_data_list[0:1]

    # Initialize an empty list to store the Image objects
    image_objects = []

    # Check whether lists contain urls that must be downloaded or b64_json images
    if image_url_list and all(image_url_list):
        # Download images from the urls
        for i, url in enumerate(image_url_list):
            while True:
                try:
                    print(f"getting URL: {url}")
                    response = requests.get(url)
                    response.raise_for_status()  # Raises stored HTTPError, if one occurred.
                except requests.HTTPError as e:
                    print(f"Failed to download image from {url}. Error: {e.response.status_code}")
                    retry = input("Retry? (y/n): ")  # ask script user if image url is bad
                    if retry.lower() in ["n", "no"]:  # could wait a bit if not ready
                        raise
                    else:
                        continue
                break
            image_objects.append(Image.open(BytesIO(response.content)))  # Append the Image object to the list
            image_objects[i].save(f"images/{img_filename}_{i}.png")
            image_objects[i].save(f"permanent_files/images/{img_filename}_{i}.png")
            print(f"{img_filename}_{i}.png was saved")
    elif image_data_list and all(image_data_list):  # if there is b64 data
        # Convert "b64_json" data to png file
        for i, data in enumerate(image_data_list):
            image_objects.append(Image.open(BytesIO(base64.b64decode(data))))  # Append the Image object to the list
            image_objects[i].save(f"images/{img_filename}_{i}.png")
            image_objects[i].save(f"permanent_files/images/{img_filename}_{i}.png")
            print(f"{img_filename}_{i}.png was saved")
    else:
        print("No image data was obtained. Maybe bad code?")

    ## -- extra fun: pop up some thumbnails in your GUI if you want to see what was saved

def create_images(story_list, style):
    for i, sentence in enumerate(story_list):
        create_image(sentence, style, "image_" + str(i))


###TEXT TO SPEECH GENERATION ### 

import os
from google.cloud import texttospeech
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="JSON/rugged-plane-405515-b94dcdd9aa32.json"

audios_path = os.path.join(os.getcwd(), "audios")


def synthesize_text(text, language_code, file_name):
    """Synthesizes speech from the input string of text."""

    client = texttospeech.TextToSpeechClient()

    input_text = texttospeech.SynthesisInput(text=text)

    # Note: the voice can also be specified by name.
    # Names of voices can be retrieved with client.list_voices().
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        #name="en-US-Standard-C",
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate = 0.75
    )

    response = client.synthesize_speech(
        request={"input": input_text, "voice": voice, "audio_config": audio_config}
    )

    # The response's audio_content is binary.
    with open(audios_path + "/" + file_name + ".mp3", "wb") as out:
        out.write(response.audio_content)
        #print('Audio content written to file "output.mp3"')
    
def create_audiofiles(story_list, language_code):
    for i, sentence in enumerate(story_list):
        synthesize_text(sentence, language_code, "audio_" + str(i))
        


### CREATE VIDEO BY MERGING AUDIO AND IMAGES ###

#Finally merge to one Video 
from mutagen.mp3 import MP3 
from PIL import Image 
from pathlib import Path 
import os 
import imageio 
from moviepy import editor 
from moviepy.editor import * 

audios_path = os.path.join(os.getcwd(), "audios")
video_path = os.path.join(os.getcwd(), "videos") 
images_path = os.path.join(os.getcwd(), "images") 

#return the global path to the video being created. 
def create_video():
    #Create the lists of audio and images, corresponding to the sentences in the story      
    list_of_audios = []
    for audio_file in sorted(os.listdir(audios_path)): 
        if audio_file.endswith('.mp3'):
            audio_path = os.path.join(audios_path, audio_file) 
            audio = AudioFileClip(audio_path) 
            list_of_audios.append(audio)


    list_of_images = [] 
    prelim_list_of_images = [path for path in sorted(os.listdir(images_path)) if path.endswith('jpeg') == True or path.endswith('png') == True or path.endswith('jpg') == True ]
    for i, image_file in enumerate(prelim_list_of_images): 
        if image_file.endswith('.png') or image_file.endswith('.jpg') or image_file.endswith('.jpeg'): 
            image_path = os.path.join(images_path, image_file) 
            image = ImageClip(image_path).set_duration(list_of_audios[i].duration) #Image.open(image_path) #.resize((400, 400), Image.ANTIALIAS) 
            list_of_images.append(image) 

    #Here some intermediate steps, since o/w moviepy won't save a audio recording
    audio = concatenate_audioclips(list_of_audios)
    final_video = concatenate_videoclips(list_of_images, method = 'compose')
    final_video.write_videofile(fps=5, codec="libx264", filename="videos/video_lemma.mp4")

    #Finally create the resulting movie 
    video = editor.VideoFileClip("videos/video_lemma.mp4") 
    audio = audio.subclip(0,video.duration)
    final_video = video.set_audio(audio) 

    current_datetime_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = current_datetime_str + "_video.mp4"

    final_video.write_videofile(fps=5, codec="libx264", audio_codec="aac",filename= "videos/" + filename)
    
    return video_path + "/" + filename


### CLEANUP MODULE ###

#Flush all the folders to avoid overflooding. If time allows make this more error resistant... 
def delete_all_files_in_folder(folder_path):
    try:
        # Check if the folder exists
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            # Iterate through each file in the folder and delete them
            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"Deleted file: {file_path}")
            print(f"All files in the folder '{folder_path}' have been deleted.")
        else:
            print(f"The specified path '{folder_path}' is not a valid folder.")
    except Exception as e:
        print(f"An error occurred: {e}")


### FINALLY COMPOSITE FUNCTION OF ALL OF THE ABOVE ####

audios_path = os.path.join(os.getcwd(), "audios")
images_path = os.path.join(os.getcwd(), "images")

def create_video_from_story(story, style, language_code):
    delete_all_files_in_folder(audios_path)
    delete_all_files_in_folder(images_path)
    
    story_list = parse_text_into_sentences(story)
    
    create_images(story_list, style)
    
    create_audiofiles(story_list, language_code)
    
    video_path = create_video()
    
    return video_path 
    
    
#video_path = create_video_from_story("Zwei Hunde spielen miteinander. Eine Katze springt zwischen die zwei Hunde. Die drei Tiere machen einen Mittagsschlaf", "charcoal and pencil drawing", "de-DE")
    