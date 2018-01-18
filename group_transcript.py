from datetime import datetime
import os
import sys
import requests
import json

def get_group_name(id, token):

    # get group name
    name_endpoint = 'https://api.groupme.com/v3/groups/'+id+'?token='+token
    name_response = requests.get(name_endpoint)

    if name_response.status_code is not 200:
        print "\nHTTP error code " + str(groups_response.status_code) + "\n"
        sys.exit(2)

    name_json = name_response.json()['response']
    group_name = (name_json['name']).replace(' ', '_')
    transcript_filename = group_name + '_transcript.json'
    return transcript_filename

def get_transcript(id, token, outfile):

    # initialize vars
    messages_endpoint = 'https://api.groupme.com/v3/groups/'+id+'/messages'
    pulled_messages = []
    beforeId = None
    done = False
    soFar = 0

    # continuously pull messages until entire transcript has been fetched
    while not done:
        params = {'token': token, 'limit': 100}

        if beforeId is not None:
            params['before_id'] = str(beforeId)

        messages_res = requests.get(messages_endpoint, params=params)
        if messages_res.status_code is not 200:
            print "\nHTTP error code " + str(groups_response.status_code) + "\n"
            sys.exit(2)

        messages_json = messages_res.json()
        messages_list = messages_json['response']['messages']
        for message in messages_list:
            pulled_messages.append(message)

        if len(messages_list) is 100:
            soFar = soFar + 100
            beforeId = messages_list[-1]['id']
            if (soFar % 1000 is 0):
                print str(soFar) + ' messages loaded so far!'
        else:
            done = True
            print('Done!')

    # sort messages and write to transcript file
    pulled_messages = sorted(pulled_messages, key=lambda k: k['created_at'])
    oldest_msg_date = datetime.fromtimestamp(pulled_messages[0]['created_at'])
    newest_msg_date = datetime.fromtimestamp(pulled_messages[-1]['created_at'])

    print "\nPulled " + str(len(pulled_messages)) + " messages\n" \
          "from: " + str(oldest_msg_date) + "\n" \
          "to:   " + str(newest_msg_date) + "\n"

    outfile.write(json.dumps(pulled_messages))

def main():
    if len(sys.argv) != 3:
        print "\nPlease execute using the following example format:\n" \
              "             argv[0]         argv[1]        argv[2]\n" \
              "$ python group_transcript.py   GROUP_ID   YOUR_ACCESS_TOKEN\n"
        sys.exit(1)

    group_id = sys.argv[1]
    token = sys.argv[2]
    transcript_filename = get_group_name(group_id, token)
    transcript_file = open(transcript_filename, 'w+')
    get_transcript(group_id, token, transcript_file)
    transcript_file.close()

if __name__ == '__main__':
    main()
