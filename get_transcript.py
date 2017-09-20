from datetime import datetime
import os
import sys
import requests
import json

def requestError(request):
    print (request.status_code)
    print (request.headers)
    print (request.text)
    sys.exit(2)

def get_transcript(id, token):

    # get group name
    name_endpoint = 'https://api.groupme.com/v3/groups/'+id+'?token='+token
    name_res = requests.get(name_endpoint)
    if name_res.status_code is not 200:
        requestError(name_res)
    name_json = name_res.json()['response']
    group_name = (name_json['name']).replace(' ', '_')
    transcript_filename = group_name + '_transcript.json'

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
            requestError(messages_res)

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
            print('Done!\n')


    pulled_messages = sorted(pulled_messages, key=lambda k: k['created_at'])
    print 'Pulled {0} new messages from {1} to {2} to transcript file'.format(
        len(pulled_messages),
        datetime.fromtimestamp(pulled_messages[0]['created_at']),
        datetime.fromtimestamp(pulled_messages[-1]['created_at']),
    )

    transcript_file = open(transcript_filename, 'w+')
    transcript_file.write(json.dumps(pulled_messages))
    transcript_file.close()


def main():
    if len(sys.argv) != 3:
        print "\nPlease execute using the following example format:\n"
        print "             argv[0]         argv[1]        argv[2]"
        print "$ python get_transcript.py   GROUP_ID   YOUR_ACCESS_TOKEN\n"
        sys.exit(1)

    group_id = sys.argv[1]
    token = sys.argv[2]
    get_transcript(group_id, token)

if __name__ == '__main__':
    main()
