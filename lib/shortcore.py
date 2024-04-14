import os
import shutil
import sys
import re
import requests
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, CompositeAudioClip

from lib.video_texts import getyamll,read_config_file,read_random_line
from lib.APIss import download_file,chatgpt,translateto
from lib.voices import generate_voice
from lib.language import get_language_code

def get_video(prompt,videoname):
    url = "https://api.pexels.com/videos/search"
    headers = {
        "Authorization": read_config_file()["pexels_api"]
    }
    params = {
        "query": prompt,
        "per_page": 1
    }

    response = requests.get(url, headers=headers, params=params)
    json_data = response.json()


    link = json_data['videos'][0]['video_files'][0]['link']

    download_file(link,videoname)


def resize_and_text(videopath,targetwidth=1080,targetheight=1920):
    video_clip = VideoFileClip(videopath+".mp4")
    width = video_clip.size[0]
    height = video_clip.size[1]
    odd = 1.0

    while(int(height * odd) < targetheight or int(width * odd) < targetwidth):
        odd+=0.1

    newwidth = int(width * odd) + 1
    newheight = int(height * odd) + 1

    video_clip = video_clip.resize((newwidth, newheight))

    x = (newwidth - targetwidth)/2
    y = (newheight - targetheight)/2

    video_clip = video_clip.crop(x1=x,y1=y,x2=x+targetwidth,y2=y+targetheight)
    newclip = video_clip

    audio_clip = AudioFileClip(videopath+".mp3")
    audioduration = audio_clip.duration

    while(audioduration > video_clip.duration):
        videos = []
        videos.append(video_clip)
        videos.append(newclip)
        video_clip = concatenate_videoclips(videos)

    video_clip = video_clip.subclip(0,audioduration)
    video_clip = video_clip.set_audio(audio_clip)

    return video_clip


def final_video(title,time,language,multi_speaker):
    if not os.path.exists("temp"):
        os.mkdir("temp")
    
    print("--------------------------------")
    print(title + " in " + time + " second"+", "+language+", multi speaker : "+multi_speaker)
    print("--------------------------------")
    original_text = chatgpt(getyamll("short_prompt")).format(title=title,time=time)
    print(original_text)
    print("--------------------------------")
    download_file(read_random_line("download_list/background_music.txt"), "temp/song.mp3")
    videoprompts = re.findall(r'\[([^\]]+)\]', original_text)
    if "Text" in original_text:
        texts = re.findall(r'Text:\s+"([^"]+)"', original_text)
    else:
        texts = re.findall(r'text:\s+"([^"]+)"', original_text)
    print(videoprompts)
    print(texts)
    print("--------------------------------")
    videos = []
    i = 0
    if not os.path.exists("temp"):
        os.mkdir("temp")
    for text,prompt in zip(texts,videoprompts):
        get_video(prompt,"temp/"+str(i)+".mp4")
        print("video download")
        generate_voice(translateto(text,get_language_code(language)),"temp/"+str(i)+".mp3",get_language_code(language))
        print("speech make")
        videos.append(resize_and_text("temp/"+str(i)))
        i+=1

    final_video = concatenate_videoclips(videos)
    audio_clip = AudioFileClip("temp/song.mp3")
    if final_video.duration < audio_clip.duration:
        audio_clip = audio_clip.subclip(0, final_video.duration)

    adjusted_audio_clip = CompositeAudioClip([audio_clip.volumex(0.12),final_video.audio])
    final_video = final_video.set_audio(adjusted_audio_clip)
    final_video.write_videofile("short.mp4", audio_codec='aac')

    if os.path.exists("temp.txt"):
        os.remove("temp.txt")
    if os.path.exists("temp") and os.path.isdir("temp"):
        shutil.rmtree("temp")
        print(f"Directory temp deleted successfully.")
    else:
        print(f"Directory temp not found.")
    sys.exit()
