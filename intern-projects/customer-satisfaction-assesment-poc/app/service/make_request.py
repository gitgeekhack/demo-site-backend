import json
import requests


def fetch_data_from_url(time):
    url = "http://35.222.102.114:9200/wot_conversation_index/_search/?size=100000"
    payload = json.dumps({
        "query": {
            "range": {
                "created_at": {
                    "gte": "now-" + str(time)
                }
            }
        }
    })
    headers = {
        'Authorization': 'Basic cmVhZG9ubHk6YmEyRTUzU21JZG5lOG0=',
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.text

def fetch_data_using_thread_id(thread_id):
    url = "http://35.222.102.114:9200/wot_conversation_index/_search/?size=100000"
    payload = json.dumps({
        "query": {
            "bool": {
                "must": [
                    {
                        "match_phrase": {
                            "thread_id": thread_id
                        }
                    }
                ]
            }
        }
    })

    headers = {
        'Authorization': 'Basic cmVhZG9ubHk6YmEyRTUzU21JZG5lOG0=',
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.text
