from pstats import Stats
from django.shortcuts import render
import json
import requests, random, re
from django.http import HttpResponse, JsonResponse
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .logic import LOGIC_RESPONSES
from decouple import config
# Create your views here.
def home(request):
    return render(request, 'home.html')

VERIFY_TOKEN = "b56148e7b0fb9de35aefc00f462e531f29b7f8196814bd89ca"

# FB_ENDPOINT = "https://graph.facebook.com/v2.6/me/messages"
FB_ENDPOINT = "https://graph.facebook.com/v13.0/"
PAGE_ACCESS_TOKEN = "EAAPpMq2g9B8BAEtTkGwl2YtOsxBvxoBmd8fie0VR996ghaz1VZC75E3OHRjczyi7ahD3RdiZCVStMOcZB2q4nZBpygutZBCzYqvf9VaMwiIqyyDCanXWqBj8ob29LXTC16sHMbQ8B9ZCPELr0nwzjuvDc2L2bkUcQYhVHgZBkwVm7qwUiRx6Tzb"

def parse_and_send_fb_message(fbid, received_message):
     # Remove all punctuations, lower case the text and split it based on space
    tokens = re.sub(r"[^a-zA-Z0-9\s]",' ',received_message).lower().split()
    msg = None
    for token in tokens:
        if token in LOGIC_RESPONSES:
            msg = random.choice(LOGIC_RESPONSES[token])
            break
        
    if msg is not None:                 
        endpoint = f"{FB_ENDPOINT}/me/messages?access_token={PAGE_ACCESS_TOKEN}"
        response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":msg}})
        status = requests.post(
            endpoint, 
            headers={"Content-Type": "application/json"},
            data=response_msg)
        print(status.json())
        return Stats.json()
    return None

class FacebookWebhookView(View):
    @method_decorator(csrf_exempt) # required
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs) #python3.6+ syntax
    
    '''
    hub.mode
    hub.verify_token
    hub.challenge
    Are all from facebook..
    '''
    def get(self, request, *args, **kwargs):
        hub_mode   = request.GET.get('hub.mode')
        hub_token = request.GET.get('hub.verify_token')
        hub_challenge = request.GET.get('hub.challenge')
        if hub_token != VERIFY_TOKEN:
            return HttpResponse('Error, invalid token', status_code=403)
        return HttpResponse(hub_challenge)
            

    def post(self, request, *args, **kwargs):
        incoming_message = json.loads(request.body.decode('utf-8'))
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                if 'message' in message:
                    fb_user_id = message['sender']['id'] # sweet!
                    fb_user_txt = message['message'].get('text')
                    if fb_user_txt:
                        parse_and_send_fb_message(fb_user_id, fb_user_txt)
        return HttpResponse("Success", status=200)