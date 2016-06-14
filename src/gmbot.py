import requests
import json
import thread
import socket

class Gmbot(object):
    def __init__(self, bot_id = 'e18f0a0d058420de66f2e2a387'):
        self.bot_id = bot_id

    def on_chat(self, fbid, who, msg):
        wrbcommands.handle(str(who), msg, self)

    # Send a text message as a GroupMe bot
    def send(self,message):
        url = 'https://api.groupme.com/v3/bots/post'
        text = message;
        payload = {'bot_id': self.bot_id, 'text': text}
        requests.post(url, data=json.dumps(payload))

    # Send an image message as a GroupMe bot
    def sendImage(self, image_url, message = ''):
        url = 'https://api.groupme.com/v3/bots/post'
        text = message;
        payload = {'bot_id': self.bot_id, 'text': text,
        'attachments': [
        {
                'type': 'image',
                'url': image_url
        }]}
        requests.post(url, data=json.dumps(payload))

    def listen(self, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('0.0.0.0', port))
        sock.listen(0) 
        while True:
            client, address = sock.accept()
            thread.start_new_thread(Gmbot.handle, (self, client, ))

    def handle(self, client):
        stream = client.makefile('w+')

        data = []
        dataIn = stream.readline()
        while dataIn != '' and dataIn != '\r\n':
            data.append(dataIn)
            dataIn = stream.readline()

        print data[0].split()[1]

        stream.write('\r\n')
        stream.flush()

        while dataIn != '':
            data.append(dataIn)
            dataIn = stream.readline()

        print data[len(data)-1]
        stream.close()