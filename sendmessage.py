import urllib3
import json
from config import *

TG_URL = "https://api.telegram.org/bot{botToken}/sendMessage"

def sendMessage(message):
    return sendMessageTG(message,TG_TOKEN,TG_CHATID)

def sendMessageTG(message,botToken,chatID):

    headers = {
        'Content-Type': 'application/json'
    }

    data = {
        "chat_id": chatID,
        "text": message
    }

    http = urllib3.PoolManager()

    url = TG_URL.format(botToken=botToken)

    response = http.request('POST', url, headers=headers, body=json.dumps(data))
    return response.status


if __name__=="__main__":
    sendMessage("testing")