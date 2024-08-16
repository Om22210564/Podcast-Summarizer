import requests
from apisecrets import API_KEY_ASSEMBLYAI,API_KEY_LISTENNOTES
import time 
import json
import pprint
import os
#upload
trancript_endpoint = "https://api.assemblyai.com/v2/transcript"
assemblyai_headers = {'authorization': API_KEY_ASSEMBLYAI}
listennotes_episode_endpoint = "https://listen-api.listennotes.com/api/v2/episodes"
listennotes_headers = {'X-ListenAPI-Key': API_KEY_LISTENNOTES}

def get_episode_audio_url(episode_id):
    url = listennotes_episode_endpoint + "/" + episode_id
    response = requests.request('Get',url,headers=listennotes_headers)

    data = response.json()
    # pprint.pprint(data)
    audio_url = data['audio']
    episode_thumbnail = data['thumbnail']
    podcast_title = data['podcast']['title']
    episode_title = data['title']
    return audio_url,episode_thumbnail,episode_title,podcast_title
#transcribe
def transcribe(audio_url,auto_chapters):
    trancript_request = {"audio_url": audio_url,'auto_chapters':auto_chapters}
    transcript_response = requests.post(trancript_endpoint,json=trancript_request , headers =assemblyai_headers)

    job_id = transcript_response.json()['id']
    return job_id



#poll 
def poll(trancript_id):
    polling_endpoint = trancript_endpoint + '/' + trancript_id
    polling_response = requests.get(polling_endpoint,headers=assemblyai_headers)
    return polling_response.json()
    

def get_trancription_result_url(audio_url,auto_chapters):
    transcript_id = transcribe(audio_url,auto_chapters)
    while True:
        data = poll(transcript_id)
        if data['status'] == 'completed':
            return data,None
        elif data['status'] == 'error':
            return data,data['error']
        print("Waiting 60 seconds....")
        time.sleep(60)

# def save_trancript(episode_id):
#     audio_url,episode_thumbnail,episode_title,podcast_title = get_episode_audio_url(episode_id)
#     data, error = get_trancription_result_url(audio_url,auto_chapters=True)
#     pprint.pprint(data)
#     if data:
#         text_filename = episode_id + ".txt"
#         with open(text_filename,"w") as f:
#             f.write(data['text'])
#         chapters_filename = episode_id + '_chapters.json'
#         with open(chapters_filename,'w') as f:
#             chapters = data['chapters']
#             episode_data = {'chapters': chapters}
#             episode_data['episode_thumbnail'] = episode_thumbnail
#             episode_data['episode_title'] = episode_title
#             episode_data['podcast_title'] = podcast_title

#             json.dump(episode_data,f)
#             print("Transcript saved")
#             return True
#     elif error:
#         print("error!!",error)
#         return False
def save_trancript(episode_id):
    # Check if the JSON file already exists
    chapters_filename = episode_id + '_chapters.json'
    if os.path.exists(chapters_filename):
        print(f"File '{chapters_filename}' already exists. Loading data from file.")
        with open(chapters_filename, 'r') as f:
            episode_data = json.load(f)
        return episode_data
    
    # If the file doesn't exist, proceed with the transcription process
    audio_url, episode_thumbnail, episode_title, podcast_title = get_episode_audio_url(episode_id)
    data, error = get_trancription_result_url(audio_url, auto_chapters=True)
    pprint.pprint(data)
    
    if data:
        text_filename = episode_id + ".txt"
        with open(text_filename, "w") as f:
            f.write(data['text'])
        
        # Save the transcription data and additional episode information
        with open(chapters_filename, 'w') as f:
            chapters = data['chapters']
            episode_data = {'chapters': chapters}
            episode_data['episode_thumbnail'] = episode_thumbnail
            episode_data['episode_title'] = episode_title
            episode_data['podcast_title'] = podcast_title
            
            json.dump(episode_data, f)
            print("Transcript saved")
        return episode_data
    
    elif error:
        print("Error!!", error)
        return False

