#slack integration for photos
import requests
import json
import dropbox
import re


def main(path):
    dbx = dropbox.Dropbox("tzFkehmTQlAAAAAAAAAFOmBxALEDa2fe11LtnWJFMsfxvbStGD0gZQLQ3xhHL4Hb")
    shared_link_metadata = dbx.sharing_create_shared_link_with_settings(path)
    dropbox_url = shared_link_metadata.url
    dropbox_url = re.sub(r".{4}$","raw=1",dropbox_url)

    slack_webhook_url = 'https://hooks.slack.com/services/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'
    slack_data = {
        "attachments": [
            {
                "fallback": "Required plain-text summary of the attachment.",
                "image_url": dropbox_url
            }
        ]
    }


    response = requests.post(
        slack_webhook_url, data=json.dumps(slack_data),
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code != 200:
        raise ValueError(
            'Request to slack returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
        )

# if __name__ == "__main__":
#     main()