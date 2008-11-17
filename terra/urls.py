from django.conf.urls.defaults import *

from settings import MEDIA_ROOT
# Uncomment the next two lines to enable the admin:
from django.contrib import admin


admin.autodiscover()



urlpatterns = patterns('',
    # Example:
    # (r'^vidsample/', include('vidsample.foo.urls')),
    url(r'^$', 'terra.main.views.index', name="index"),
    url(r'^upload/$', 'terra.main.views.upload', name='upload'),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^(?P<path>static/.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT}),
    (r'^(?P<path>yvideo/.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT}),
    (r'^(?P<path>video/.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT}),
    # Uncomment the next line to enable the admin:
    (r'^admin/(.*)', admin.site.root),
)
