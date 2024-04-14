import asyncio
import random
import os
from concurrent.futures import ThreadPoolExecutor
import edge_tts
from edge_tts import VoicesManager
from lib.video_texts import read_config_file

def generate_voice(text, outputfile,lang):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        with ThreadPoolExecutor() as executor:
            loop.run_in_executor(executor, run_async_func, loop, async_generate_voice, text, outputfile,lang)
    finally:
        loop.close()

    if not os.path.exists(outputfile):
        print("An error happened during edge_tts audio generation, no output audio generated")
        raise Exception("An error happened during edge_tts audio generation, no output audio generated")

    return outputfile
async def async_generate_voice(text, outputfile,lang):
    try:
        voices = await VoicesManager.create()
        if (lang == "en"):
            voice = voices.find(Locale="en-US")
        else:
            voice = voices.find(Language = lang)
        multi = read_config_file()["multi_speaker"]
        if(multi=="yes" or multi=="Yes" or multi=="YES"): 
            speaker = random.choice(voice)["Name"]
        else:      
            try:
                speaker = read_config_file("temp.txt")["speaker"]
            except:
                speaker = random.choice(voice)["Name"]
                with open("temp.txt", "w") as file:
                    file.write("speaker = " + speaker)
                    
        communicate = edge_tts.Communicate(text, speaker)
        submaker = edge_tts.SubMaker()
        with open(outputfile, "wb") as file:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    file.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    submaker.create_sub((chunk["offset"], chunk["duration"]), chunk["text"])

    except Exception as e:
        print("Error generating audio using edge_tts", e)
        raise Exception("An error happened during edge_tts audio generation, no output audio generated", e)

    return outputfile
def run_async_func(loop, func, *args):
    return loop.run_until_complete(func(*args))

