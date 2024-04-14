import argparse
from lib.video_texts import update_config_file
from lib.core import making_video

parser = argparse.ArgumentParser(description='long video')
parser.add_argument('-topic', dest='topic', type=str, help='Enter video topic. Example: survival video game')
parser.add_argument('-general_topic', dest='general_topic', type=str, help='general topic you want to make a video about.Example: video game, food, city, person and...')
parser.add_argument('-time', dest='time', type=str, help='video time in minute')
parser.add_argument('-intro_video', dest='intro_video', type=str, help='do you want intro with video instead photo?')
parser.add_argument('-pexels_api', dest='pexels_api', type=str, help='get API from www.pexels.com')
parser.add_argument('-language', dest='language', type=str, help='video language')
parser.add_argument('-multi_speaker', dest='multi_speaker', type=str, help='Use multiple speakers in video')

args = parser.parse_args()

if (args.general_topic != None):
	update_config_file('config.txt', 'general_topic', args.general_topic)
if (args.time != None):
	update_config_file('config.txt', 'time', args.time)
if (args.intro_video != None):	
	update_config_file('config.txt', 'intro_video', args.intro_video)
if (args.pexels_api != None):
	update_config_file('config.txt', 'pexels_api', args.pexels_api)
if (args.language != None):
	update_config_file('config.txt', 'language', args.language)
if (args.multi_speaker != None):
	update_config_file('config.txt', 'multi_speaker', args.multi_speaker)


if (args.topic != None):
	making_video(args.topic)
else:
	print('Please enter a topic with "-topic"')		