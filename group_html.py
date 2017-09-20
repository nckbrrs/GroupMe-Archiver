import json
import requests
import datetime
import os.path
import sys
import shutil
import re
import string
from UserDict import UserDict
from inspect import cleandoc

_HTML_HEADER = """
<!doctype html>
<html>
\t<head>
\t\t<meta charset="UTF-8">
\t\t<link rel="stylesheet" type="text/css" href="transcript.css"/>
\t\t<title>GroupMe Transcript</title>
\t</head>
\t<body>
\t\t<div class="container">
\t\t\t<h1 style="font-family:sans-serif;">Messages from """

_HTML_FOOTER = """
\t\t\t</div>
\t\t</div>
\t</body>
</html>
"""

class ImageCache(UserDict):

    def __init__(self, folder, initial_data={}):
        UserDict.__init__(self, initial_data)
        self._folder = folder

    def __getitem__(self, key):
        try:
            return UserDict.__getitem__(self, key)
        except KeyError:
            local_filename = self._save_image(key)
            self[key] = local_filename
            return local_filename

    def _save_image(self, url):
        local_filename= os.path.join('attachments', (url.split('/')[-1]))
        local_filepath = os.path.join(self._folder, local_filename)

        if os.path.exists(local_filepath):
            return local_filename

        try:
            response = requests.get(url, stream=True)
        except:
            # attachment could not be found, download dummy image instead
            dummy_img_url = "https://pbs.twimg.com/profile_images/600060188872155136/st4Sp6Aw.jpg"
            response = requests.get(dummy_img_url, stream=True)

        with open(local_filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()

        return local_filename

def write_html_transcript(messages, folder, outfiles, image_cache):
    current_year = 0
    current_filename = ""
    current_file = None

    # build HTML for each message
    for n, message in enumerate(messages):
        time = datetime.datetime.fromtimestamp(message["created_at"])
        name = message["name"]
        text = message["text"] if (not (message["text"] is None)) else ""
        system = message["system"]
        avi = message["avatar_url"] if (not (message["avatar_url"] is None)) else "https://pbs.twimg.com/profile_images/600060188872155136/st4Sp6Aw.jpg"
        if (len(message["attachments"]) != 0):
            if (message["attachments"][0]["type"] == 'image'):
                pic = message["attachments"][0]["url"]
        else:
            pic = None

        if (time.year > current_year):
            current_year = time.year
            current_filename = str(time.year) + "_messages.html"
            current_file = open(os.path.join(folder, current_filename), 'w')
            current_file.write(_HTML_HEADER)
            current_file.write(str(time.year) + '</h1>\n')
            current_file.write('\t\t\t<div class="chat">')
            outfiles.append(current_file)

        # write avi
        if avi is not None:
            current_file.write('<table><tr><td style="vertical-align: top;"><div class="avi">')
            # change "avi" to "image_cache[avi] for offline access
            current_file.write('<img src="' + avi + '"style="width:70px;"/></td></div>')

        # surround message with message-container div class
        current_file.write("<td>")
        current_file.write('<div class="message-container')
        if system:
            current_file.write(' system')
        current_file.write('">')

        # write date
        current_file.write('<div class="datetime">')
        current_file.write((time.strftime('%Y-%m-%d %H:%M')).encode('utf-8'))
        current_file.write('</div>')

        # write sender's name
        current_file.write('<div class="author">')
        current_file.write(name.encode('utf-8'))
        current_file.write('</div>')

        # look for URLs in message and replace those detected with HTML link
        urls_in_text = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        plain_text = text
        for url in urls_in_text:
            html_url = "<a href='" + url + "'>" + url + "</a>"
            text = string.replace(text, url, html_url)

        current_file.write('<div class="message"><span class="message-span" title="%s">' % (time.strftime('%Y-%m-%d %H:%M')))
        current_file.write(text.encode('utf-8'))
        current_file.write('</br></br>')
        current_file.write('</span></div>')

        # save and display images sent as links, rather than uploaded from device
        if (plain_text.endswith(".jpg") or plain_text.endswith(".png") or plain_text.endswith(".jpeg") or plain_text.endswith(".gif")):
            # change "urls_in_text[0]" to "image_cache[urls_in_text[0]]" for offline access
            for url in urls_in_text:
                current_file.write('<img src="' + urls_in_text[0] + '" style="width: 50%; height: 50%"/>')
                current_file.write('</br></br>')

        # save and display videos
        if (plain_text.endswith(".mp4")):
            for url in urls_in_text:
                current_file.write('<video width="500" height="300" controls>')
                # change "urls_in_text[0]" to "image_cache[urls_in_text[0]]" for offline access
                current_file.write('<source src="' + urls_in_text[0]+ '" type="video/mp4"></video>')

        # save and display images uploaded from device
        if pic:
            # change "pic" to "image_cache[pic]" for offline access
            current_file.write('<img src="' + pic + '" style="width: 50%; height: 50%"/>')
            current_file.write('</br></br>')

        # close messsage-container
        current_file.write('</div></td></tr></table>\n')

        if (n % 1000 == 0):
            print '%04d/%04d messages processed' % (n, len(messages))

def write_html(transcript, folder):
    shutil.copyfile('resources/transcript.css', os.path.join(folder, 'transcript.css'))

    #image_cache = ImageCache(folder)
    image_cache = 0
    html_files = []
    write_html_transcript(transcript, folder, html_files, image_cache)

    for file in html_files:
        file.write(_HTML_FOOTER)
        file.close()

def main():

    # print error message if not executed correctly
    if len(sys.argv) != 2:
        print "\nUSAGE ERROR! Execution example format:\n"
        print "             argv[0]               argv[1]"
        print "$ python html_transcript.py transcript_filename.json\n"
        sys.exit(1)

    # make folder that will contain written html file (argv[2] should be desired name of folder)
    output_folder_name = (sys.argv[1]).replace('_transcript.json', '_html')
    if not os.path.exists(output_folder_name):
        os.mkdir(output_folder_name)

    # make folder that will contain pic/vid attachments
    attachments_folder = os.path.join(output_folder_name, 'attachments')
    if not os.path.exists(attachments_folder):
        os.mkdir(attachments_folder)

    # argv[1] should be name of transcript file
    transcript_file = open(sys.argv[1])
    transcript_data = json.load(transcript_file)
    transcript_file.close()

    # actually write the html
    write_html(transcript_data, output_folder_name)

if __name__ == '__main__':
    main()
