from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from video.forms import UploadForm

from video.models import Video

def index(request):
    form = UploadForm()
    video = get_object_or_404(Video, pk=int(request.GET.get('video', 1)))
    return render_to_response('index.html',
                              {'video' : video,
                               'form' : form,
                               'videos' : Video.objects.encoded()},
                              context_instance = RequestContext(request))



def upload(request):
    if request.method == 'GET':
        form = UploadForm()
    else:
        form = UploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('index'))

    return render_to_response('upload.html',
                              {'form' : form,
                               'videos' : Video.objects.encoded()},
                              context_instance = RequestContext(request))
