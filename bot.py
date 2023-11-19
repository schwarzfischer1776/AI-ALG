# bot.py
import os
import random

import discord
from dotenv import load_dotenv
import upload 
import story_to_movie_functor as movie_creator 

load_dotenv()

load_dotenv()
#TOKEN = 'MTE3NTQ3OTAxMjQ1MDEyNzkzMw.GKmi-b.2fvSydMPqV6lm_Gh33zOeW9DQ_YEabmh_JiCV0'

TOKEN = 'MTE3NTU4OTk5MTczMzI3MjU3Ng.Gyhhf9.d_cuiuT2mIOrD0p5PbLRqsEYeLJtanlUfSUns8'

client=discord.Client(intents=discord.Intents.all())

def parse_text_into_sentences(text):
    sentences = []
    current_sentence = ""

    for char in text:
        if char in ['|']:
            sentences.append(current_sentence.strip())
            current_sentence = ""
        current_sentence += char
    # Add the last sentence if the text doesn't end with punctuation
    if current_sentence:
        sentences.append(current_sentence.strip())

    return sentences


@client.event
async def on_message(message):
    order = message.content 
    order = order.split("|")
    video_path = movie_creator.create_video_from_story(*order) 
    
    url = upload.upload_to_youtube(video_path, order[0])

    #if message.author == client.user:
    #    return

    #if message.content.startswith('generate:'):
    response = "enjoy your video! access the following link:  " + url # upload.test_function(message.content[9:])
    await message.channel.send(response)

client.run(TOKEN)