from django.conf.urls.defaults import *
from django.contrib import admin

from settings import MEDIA_ROOT

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'terra.main.views.index', name="index"),
    url(r'^upload/$', 'terra.main.views.upload', name='upload'),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT}),
    (r'^(?P<path>video/.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT}),
    (r'^admin/(.*)', admin.site.root),
)
