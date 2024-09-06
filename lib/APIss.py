import re
import requests
import urllib.parse
from deep_translator import GoogleTranslator

def read_config_file(file_path="config.txt"):
    config = {}
    with open(file_path, 'r') as file:
        for line in file:
            key, value = line.strip().split(' = ')
            config[key.strip()] = value.strip()
    return config

#images API (Bing)
def _extractBingImages(html):
    pattern = r'mediaurl=(.*?)&.*?expw=(\d+).*?exph=(\d+)'
    matches = re.findall(pattern, html)
    result = []

    for match in matches:
        url, width, height = match
        if url.endswith('.jpg') or url.endswith('.jpeg'):
            result.append({'url': urllib.parse.unquote(url), 'width': int(width), 'height': int(height)})

    return result

def getBingImages(texts, retries=5):
    texts = texts + " Quality image"
    texts = texts.replace(" ", "+")
    images = []
    tries = 0
    while(len(images) == 0 and tries < retries):
        response = requests.get(f"https://www.bing.com/images/search?q={texts}&first=1")
        if(response.status_code == 200):
            images = _extractBingImages(response.text)
        else:
            print("Error While making bing image searches", response.text)
            raise Exception("Error While making bing image searches")
    if(images):
        return images
    raise Exception("Error While making bing image searches")

#video API (Pexels)
#def get_api():


def get_videos(title):
  url = "https://api.pexels.com/videos/search"
  headers = {
      "Authorization": read_config_file()["pexels_api"]
  }
  params = {
      "query": title,
      "orientation": "landscape",
      "per_page": 30
  }

  response = requests.get(url, headers=headers, params=params)
  json_data = response.json()

  links = []
  for i in range(30):
    link = json_data['videos'][i]['video_files'][0]['link']
    links.append(link)

  return links

#ai API (chatgpt)
def chatgpt(prompt):
    api_url = f"https://llm.sswsuport.workers.dev/?query={prompt}"
    response = requests.get(api_url)
    return response.text

#downlaod any file
def download_file(url, save_path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(8192):
                file.write(chunk)
        print("file downloaded successfully.")
    else:
        print("Failed to download the file.")


def translateto(text,language):
    translator = GoogleTranslator(target=language)
    return translator.translate(text)
