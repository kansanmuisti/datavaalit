import requests

from django.conf import settings
from social.models import ApiToken
from pyfaceb import FBGraph

TOKEN_URL = "https://graph.facebook.com/oauth/access_token?" + \
        "client_id=%s&client_secret=%s&grant_type=client_credentials"

def get_facebook_token():
    try:
        token = ApiToken.objects.get(type='FB')
        return token.token
    except ApiToken.DoesNotExist:
        pass

    r = requests.get(TOKEN_URL % (settings.FACEBOOK_APP_ID, settings.FACEBOOK_API_SECRET))
    arr = r.text.split('=')
    if arr[0] != 'access_token':
        raise Exception("FB returned invalid access token")
    ApiToken.objects.filter(type='FB').delete()
    token = ApiToken(type='FB', token=arr[1])
    token.save()
    return token.token

def get_facebook_graph(graph_id):
    token = get_facebook_token()
    fbg = FBGraph(token)
    return fbg.get(graph_id)

