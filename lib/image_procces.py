import os
from PIL import Image
import cv2
import requests
import json
import hashlib

from lib.APIss import getBingImages


def getim(top, paths):
    links = getBingImages(top)
    result = []
    for link in links:
        width = link["width"]
        height = link["height"]
        ratio = width / height
        result.append(link["url"])
    result = json.loads(json.dumps(result))
    if not os.path.exists(paths):
        os.mkdir(paths)
    for link in result:
        filename = hashlib.sha1(link.encode()).hexdigest() + ".jpg"
        filepath = os.path.join(paths, filename)
        #print("downloading "+link)
        requests.max_redirects = 30
        try:
          response = requests.get(link, timeout=2)
        except requests.exceptions.Timeout:
          continue
        except requests.exceptions.SSLError:
          continue
        except requests.exceptions.TooManyRedirects:
          continue
        except requests.exceptions.ConnectionError:
          continue
        except requests.exceptions.RequestException:
          continue
        with open(filepath, "wb") as f:
            f.write(response.content)

def is_image_valid(filepath):
    try:
        img = Image.open(filepath)
        img.close()
        return True
    except:
        return False

def delete_image(filepath):
    os.remove(filepath)

def get_all_images(path):
    files = os.listdir(path)
    images = []
    for file in files:
        if file.endswith(".jpg"):
            images.append(file)
    return images

def delete_invalid_images(path):
    images = get_all_images(path)
    for image in images:
        filepath = os.path.join(path, image)
        if not is_image_valid(filepath):
            delete_image(filepath)
def shape_error(path):
    images = get_all_images(path)
    for image in images:
      filepath = os.path.join(path, image)
      try:
        img = cv2.imread(filepath)
        height, width, _ = img.shape
      except Exception as e:
        delete_image(filepath)
        print(image + " delete:shape error")
        continue

def sortimage(path):
  files = os.listdir(path)
  counter = 1
  for file in files:
      if file.endswith((".jpg", ".jpeg", ".png")):
          os.rename(os.path.join(path, file), os.path.join(path, str(counter) + "q.jpg"))
          counter += 1
  files = os.listdir(path)
  counter = 1
  for file in files:
      if file.endswith(".jpg"):
          os.rename(os.path.join(path, file), os.path.join(path, str(counter) + ".jpg"))
          counter += 1


def resize_and_add_borders(img, target_width, target_height):
    height, width, _ = img.shape
    odd = 1.0
    while(int(height * odd) < target_height or int(width * odd) < target_width):
      odd += 0.1
    new_width = int(width * odd) + 1
    new_height = int(height * odd) + 1
    resized_img = cv2.resize(img, (new_width, new_height))
    #print(str(resized_img.shape[0])+" "+str(resized_img.shape[1]))
    extra_height = resized_img.shape[0] - target_height
    extra_width = resized_img.shape[1] - target_width
    top_crop = extra_height // 2
    bottom_crop = extra_height - top_crop
    left_crop = extra_width // 2
    right_crop = extra_width - left_crop
    cropped_img = resized_img[top_crop:-bottom_crop, left_crop:-right_crop]
    return cropped_img