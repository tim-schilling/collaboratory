import json
import random
import string
from django.conf import settings
from django.template import RequestContext
from django.http import HttpResponse
from django.shortcuts import redirect, render_to_response
from django.core.files.temp import NamedTemporaryFile
from django.core.files import File
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
import pusher


def pushit(channel, event, data):
    """
    generic utility function to push data to pusher
    expects:
        'channel name'
        'event name'
        'data'
    """
    pusher.app_id = settings.PUSHER_API_ID
    pusher.key = settings.PUSHER_KEY
    pusher.secret = settings.PUSHER_SECRET_KEY
    p = pusher.Pusher()
    p[channel].trigger(event, data)

@csrf_exempt
def auth_user(request):
    socket_id = request.POST.get('socket_id')
    channel_name = request.POST.get('channel_name')
    pusher.app_id = settings.PUSHER_API_ID
    pusher.key = settings.PUSHER_KEY
    pusher.secret = settings.PUSHER_SECRET_KEY
    p = pusher.Pusher()
    auth = p[channel_name].authenticate(socket_id)
    return HttpResponse(json.dumps(auth), mimetype="application/json")


def share_file(request):
    invitee = False
    file_data = None
    if 'key' in request.GET:
        key = request.GET.get('key')
    elif 'key' in request.POST:
        key = request.GET.get('key')
    else:
        key = None
    if 'shared_file' in request.FILES:
        shared_file = request.FILES['shared_file']
        file_data = shared_file.read()
        shared_file.flush()
        key = ''.join(random.choice(string.letters+string.digits+"_") for i in xrange(16))
        channel_id = "private-"+key
        pushit(channel_id, 'new_file', json.dumps({'file_data': file_data}))

    return render_to_response(
        'share.html',
        {
            'SITE_PATH': settings.SITE_PATH,
            'file_data': file_data,
            'invitee': invitee,
            'key': key,
        }, RequestContext(request)
    )