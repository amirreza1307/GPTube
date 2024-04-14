import moviepy.editor as mp
import moviepy.editor as mpe
from moviepy.editor import *
import cv2
import os
import requests

from lib.APIss import get_videos,download_file
from lib.image_procces import resize_and_add_borders
from lib.video_texts import read_config_file
from lib.image_procces import getim,delete_invalid_images,sortimage,shape_error

def create_video_with_images_and_audio(image_folder, audio_file, text, audio_volume=1.0):
  audio_clip = mp.AudioFileClip(audio_file)
  audio_clip = audio_clip.volumex(audio_volume)
  desired_duration = audio_clip.duration + 1
  image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
  image_duration = desired_duration / len(image_files)
  video_clips = []

  for idx, image_file in enumerate(image_files):
    try:
      image_path = os.path.join(image_folder, image_file)
      img = cv2.imread(image_path)
      resized_img = resize_and_add_borders(img, 1920, 1080)
      img_rgb = cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB)

      if idx == 0:
          font = cv2.FONT_ITALIC
          font_scale = 2
          font_color = (255, 255, 255)
          font_thickness = 10
          text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
          text_x = 100
          text_y = img_rgb.shape[0] - 100
          cv2.putText(img_rgb, text, (text_x, text_y), font, font_scale, font_color, font_thickness, cv2.LINE_AA)

      video_clip = mp.ImageClip(img_rgb).set_duration(image_duration)
      video_clips.append(video_clip)
    except Exception as e:
      print(f"Error processing image {image_file}: {e}")
      continue

  final_clip = mp.concatenate_videoclips(video_clips, method="compose")
  final_clip = final_clip.set_audio(audio_clip)
  final_clip.fps = 24
  return final_clip

def make_intro(title):
  withvideo= read_config_file()["intro_video"]
  if(withvideo == "yes" or withvideo == "Yes" or withvideo == "YES"):
    
    links = get_videos(title)

    videos_count = 0
    video_times = 0
    final_videos = []

    audio_clip = AudioFileClip("tempfiles/11/11.mp3")

    while(video_times < audio_clip.duration + 1):
      subvideo_path = "tempfiles/11/"+str(videos_count)+".mp4"
      download_file(links[videos_count],subvideo_path)
      video_clip = VideoFileClip(subvideo_path)
      video_times += video_clip.duration
      videos_count += 1
      width = video_clip.size[0]
      height = video_clip.size[1]
      odd = 1.0
      while(int(height * odd) < 1080 or int(width * odd) < 1920):
          odd+=0.1
      newwidth = int(width * odd) + 1
      newheight = int(height * odd) + 1
      video_clip = video_clip.resize((newwidth, newheight))
      x = (newwidth - 1920)/2
      y = (newheight - 1080)/2
      video_clip = video_clip.crop(x1=x,y1=y,x2=x+1920,y2=y+1080)
      final_videos.append(video_clip)

    final_video = concatenate_videoclips(final_videos)
    if final_video.duration > audio_clip.duration + 1:
      final_video = final_video.subclip(0, audio_clip.duration + 1)
    final_video = final_video.set_audio(audio_clip)
    return final_video

  else:

    npath = "tempfiles/11"
    getim(title,npath)
    delete_invalid_images(npath)
    sortimage(npath)
    delete_invalid_images(npath)
    shape_error(npath)
    sortimage(npath)
    video_clip = create_video_with_images_and_audio("tempfiles/11", "tempfiles/11/11.mp3", "")

    return video_clip



def mergevideo(videoname, audio_file,tops,title):
  video_clips = []

  video_clip = make_intro(title)
  video_clips.append(video_clip)
  for i in range(10,-1,-1):
    ir = str(i)
    if(i!=0 and i!=11):
      top = ir+"."+tops[i-1]
    else:
      top = ""

    video_clip = create_video_with_images_and_audio("tempfiles/"+ir, "tempfiles/"+ir+"/"+ir+".mp3", top)
    video_clips.append(video_clip)

  chapter_text = "00:00 intro\n"
  sum = 0
  for i in range(1,11):
     sum += video_clips[i-1].duration
     minutee = int(sum/60)
     secc = int(sum%60)
     if 0 <= minutee < 10:
        strmi = f'0{minutee}'
     else:
        strmi = str(minutee)
     if 0 <= secc < 10:
        strse = f'0{secc}'
     else:
        strse = str(secc)

     chapter_text += strmi + ":" + strse + " " + tops[10-i] + "\n"

  sum += video_clips[10].duration

  minutee = int(sum/60)
  secc = int(sum%60)
  if 0 <= minutee < 10:
    strmi = f'0{minutee}'
  else:
    strmi = str(minutee)
  if 0 <= secc < 10:
    strse = f'0{secc}'
  else:
    strse = str(secc)

  chapter_text += strmi + ":" + strse + " outro\n"

  with open(videoname+".txt", "w", encoding="utf-8") as file:
      file.write(chapter_text)

  final_video = concatenate_videoclips(video_clips)
  audio_clip = AudioFileClip(audio_file)
  if final_video.duration < audio_clip.duration:
      audio_clip = audio_clip.subclip(0, final_video.duration)
  adjusted_audio_clip = CompositeAudioClip([audio_clip.volumex(0.05),final_video.audio])
  final_video = final_video.set_audio(adjusted_audio_clip)
  final_video.write_videofile(videoname+".mp4", audio_codec='aac')
