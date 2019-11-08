# Deeplens functions

I am doing an internship in which the AWS DeepLens is an essential part. I will be posting my finished code here.

## Prototype 1: doorman

I have made an application that is able to detect and recognise faces. Users can interact with the application through a slack chat.

### Prerequisites
Python 3.6 (Do it in an environment just to be safe)
AWS DeepLens (obviously)
Pip (used to install requirements.txt)
A slack app with permission to edit, look at and edit the chat

### How to
Install the requirements using pip install -r requirements.txt (this will take a while)
Check if the camera is set up correctly using stream.py
Export your slack app token using "export SLACK_BOT_TOKEN="xoxb-< your token here >"
Export the slack channel you want the app to post in using "export SLACK_CHANNEL=< channel >", if you dont know the channel_id you can check it by running app.py.

Run app.py and slack_doorman.py in separate terminals. Start with at least one picture containing a face in /faces, otherwise it will not start.

React to unknown faces by saying "The person is < name >" in the slack channel to inform the app who the person is.
