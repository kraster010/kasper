"""
This structures the (simple) structure of the
webpage 'application'.
"""
from django.conf.urls import *
from web.portals.webclient import views as webclient_views

urlpatterns = [
    url(r'^$', webclient_views.webclient, name="index")]
