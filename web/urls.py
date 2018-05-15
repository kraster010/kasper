"""
Url definition file to redistribute incoming URL requests to django
views. Search the Django documentation for "URL dispatcher" for more
help.

"""
from django.conf.urls import url, include

# default evennia patterns
from evennia.web.urls import urlpatterns

# eventual custom patterns
custom_patterns = [
    # webclient
    url(r'^play', include('web.portals.webclient.urls', namespace='webclient', app_name='webclient')),
]



# this is required by Django.
urlpatterns = custom_patterns