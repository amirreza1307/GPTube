import argparse
from lib.video_texts import update_config_file
from lib.shortcore import final_video

parser = argparse.ArgumentParser(description='short video')
parser.add_argument('-topic', dest='topic', type=str, help='Enter video topic. Example: top 10 survival video game')
parser.add_argument('-time', dest='time', type=str, help='video time in second')
parser.add_argument('-language', dest='language', type=str, help='video language')
parser.add_argument('-multi_speaker', dest='multi_speaker', type=str, help='Use multiple speakers in video')
parser.add_argument('-pexels_api', dest='pexels_api', type=str, help='get API from www.pexels.com')


args = parser.parse_args()

if (args.topic != None):
	if(args.time != None):
		time = 	args.time
	else:
		time = "30"

	if(args.language != None):
		language = 	args.language
	else:
		language = "english"

	if(args.multi_speaker != None):
		multi_speaker = args.multi_speaker
		update_config_file('config.txt', 'multi_speaker', multi_speaker)
	else:
		multi_speaker = "no"
	if(args.pexels_api != None):
		pexels_api = args.pexels_api
		update_config_file('config.txt', 'pexels_api', pexels_api)
		
	final_video(args.topic,time,language,multi_speaker)	
else:
	print('Please enter a topic with "-topic"')	