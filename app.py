
import os, shutil
import logging
import slack
import ssl as ssl_lib
import certifi
# ================= Welcome Event ================= #
# When somebody new joins a channel, say hi to em!
@slack.RTMClient.run_on(event="member_joined_channel")
def welcome(**payload):
    """Create and send an onboarding welcome message to new users. Save the
    time stamp of this message so we can update this message in the future.
    """
    # Get WebClient and channel_id so you can communicate back to Slack.
    web_client = payload["web_client"]
    data = payload["data"]
    
    # Get the id of the Slack user associated with the incoming event
    user_id = data["user"]
    channel_id = data["channel"]

    # Open a DM with the new user.
    web_client.chat_postMessage(channel=channel_id, text="Hey everyone, say hi to <@{}> :wave:".format(user_id))


# ============== Message Events ============= #
# When a user sends a DM, the event type will be 'message'.
# Here we'll link some message callbacks to the 'message' event.
@slack.RTMClient.run_on(event="message")
def message(**payload):
    """Display the onboarding welcome message after receiving a message
    that contains "start".
    """
    data = payload["data"]
    web_client = payload["web_client"]
    channel_id = data.get("channel")
    #user_id = data.get("user")
    text = data.get("text")

    print(data)

    if text and text.lower() == "intruder?":
        web_client.chat_postMessage(
            channel=channel_id,
            blocks=[
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*I HAVE DETECTED AN INTRUDER*"
			}
		},
		{
			"type": "image",
			"title": {
				"type": "plain_text",
				"text": "CHRONOS-CAM-AVOND",
			},
			"image_url": "https://www.parkeer24.nl/static/site/img/module/content/article/25138/header.jpg",
			"alt_text": "CHRONOS-CAM-AVOND"
		}
	]   
        )

    elif text and text.lower() == "why?":
        web_client.chat_postMessage(channel=channel_id, text="42")
    
    elif text and 'unknown' in text.lower() and "files" in data:
        web_client.chat_postMessage(channel=channel_id, text="Who is this person at the door?")

    elif text and 'the person is' in text.lower():
          new_name = text[14:]
          web_client.chat_postMessage(channel=channel_id, text="{} registered!".format(new_name))
          for files in os.listdir("."):
              if files.startswith("unknown@"):
                  new_path = "faces/{}.jpg".format(new_name)
                  os.rename(files, new_path)
                  web_client.chat_postMessage(channel=channel_id, text="Restart the app to save changes.")

    # elif "files" in data:
        # web_client.chat_postMessage(channel=channel_id, text="*How insightful!*")

if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
    print(ssl_context)
    slack_token = os.environ["SLACK_BOT_TOKEN"]
    rtm_client = slack.RTMClient(token=slack_token, ssl=ssl_context)
    status = rtm_client.start()
