import os
import shutil
import sys

from lib.video_texts import get_names,process_text,getyamll,read_config_file,read_random_line
from lib.image_procces import getim,delete_invalid_images,sortimage,shape_error
from lib.APIss import download_file,chatgpt,translateto
from lib.video_editor import mergevideo
from lib.voices import generate_voice
from lib.language import get_language_code

def intro(title):
  introtext = chatgpt(getyamll("intro_prompt").format(title=title,language=read_config_file()["language"]))
  introtext = process_text(introtext, ":")
  print(introtext)
  try:
      os.makedirs("tempfiles/11")
  except FileExistsError:
      pass  
  except Exception as e:
      print(f"Error: {e}")
  generate_voice(introtext, "tempfiles/11/11.mp3",get_language_code(read_config_file()["language"]))

def top10s(top10,genre,title):
  num = 1
  for top in top10:
    imagepath=str(num)
    npath = "tempfiles/" + imagepath
    mp3file = npath + "/" + imagepath + ".mp3"

    getim(top+" "+genre,npath)
    delete_invalid_images(npath)
    sortimage(npath)
    delete_invalid_images(npath)
    shape_error(npath)
    sortimage(npath)

    time = int(read_config_file()["time"]) * 60 / 10
    time = int(time)
    text = chatgpt(getyamll("text_prompt").format(title=title,top=top,genre=genre,time=str(time),language=read_config_file()["language"]))
    text = translateto("number " + imagepath +" " + top, get_language_code(read_config_file()["language"])) +",,.."+ text
    lines = text.strip().split('\n')
    if "sure" in lines[0]:
        lines.pop()
    if "assist" in lines[-1]:
        lines.pop()
    text = '\n'.join(lines)

    print(text)

    generate_voice(text, mp3file,get_language_code(read_config_file()["language"]))

    print("--------------------------")
    num = num + 1

def outro():
  if not os.path.exists("tempfiles/0"):
      os.mkdir("tempfiles/0")
  download_file(read_random_line("download_list/outro_pic.txt"), "tempfiles/0/1.jpg")
  generate_voice(translateto(getyamll("outro_text"),get_language_code(read_config_file()["language"])), "tempfiles/0/0.mp3",get_language_code(read_config_file()["language"]))


def delete_directories_and_file(start, end, base_directory="tempfiles/"):
    try:
        for i in range(start, end + 1):
            directory_path = os.path.join(base_directory, str(i))
            if os.path.exists(directory_path) and os.path.isdir(directory_path):
                shutil.rmtree(directory_path)
                print(f"Directory {i} deleted successfully.")
            else:
                print(f"Directory {i} not found.")

        song_file_path = os.path.join(base_directory, "song.mp3")
        if os.path.exists(song_file_path) and os.path.isfile(song_file_path):
            os.remove(song_file_path)
            print("File 'song.mp3' deleted successfully.")
        else:
            print("File 'song.mp3' not found.")

        print("All directories and the file 'song.mp3' deleted successfully.")
    except Exception as e:
        print(f"Error while deleting directories and file: {e}")

def making_video(title,genre=""):
  genre = read_config_file()["general_topic"]
  print("--------------------------")
  print(title)
  print("--------------------------")
  top10=get_names(title)
  print(top10)
  print("--------------------------")
  intro(title)
  print("--------------------------")
  top10s(top10,genre,title)
  outro()

  download_file(read_random_line("download_list/background_music.txt"), "tempfiles/song.mp3")
  mergevideo(title,"tempfiles/song.mp3",top10,title)
  delete_directories_and_file(0, 11)
  if os.path.exists("temp.txt"):
    os.remove("temp.txt")
  sys.exit()
