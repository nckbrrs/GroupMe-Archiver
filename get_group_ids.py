import os
import sys
import requests
import json

def get_groups(token, outfile):
    groups_endpoint = 'https://api.groupme.com/v3/groups?token=' + token
    groups_response = requests.get(endpoint)

    if response.status_code is not 200:
        print response.status_code
        print response.headers
        print response.text
        sys.exit(2)

    groups_json = groups_response.json()
    for group in groups_json['response']:
        outfile.write('Group Name: ' + group['name'] + '\n')
        outfile.write('Group ID: ' + group['id'] + '\n\n')

def main():
    if len(sys.argv) != 2:
        print "\nPlease execute using the following example format:\n" \
              "             argv[0]               argv[1]\n" \
              "$ python get_group_ids.py YOUR_ACCESS_TOKEN\n"
        sys.exit(1)

    token = sys.argv[1]
    groups_file = open('my_group_ids.txt', 'w+')
    get_groups(token, groups_file)
    groups_file.close()
    print "\nA text file, 'my_group_ids.txt' has been created that holds" \
          "the names of the groups that you are in as well as their" \
          "associated unique Group IDs!\n"

if __name__ == '__main__':
    main()
