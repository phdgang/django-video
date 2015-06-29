# Requirements: #
  * mencoder
  * mtn (movie thumbnailer)
  * python imaging library
  * python-magic
  * parallel python
  * yamdi

# Configuration #

In the `default.py` file all default values for parameters which can be altered. To specify your own value for any of parameters you should define new value in your `settings.py` adding `TERRA_` prefix to the name of paramter. For instance, if you wanted to change video encoding bitrate you would add something like `TERRA_ENCODING_VBITRATE = 1000` to your `settings.py` file.

## Brief explanation of parameters meaning ##

### Player parameters ###
`PLAYER_WIDTH, PLAYER_HEIGHT` - default width and height of player
`PLAYER_VOLUME` - default volume (per cents)
`PLAYER_AUTOPLAY` - whether playback should begin right after page loading
`PLAYER_LOOP` - whether player have to loop movie playback:
`PLAYER_MUTE` - whether player will be muted by default
`PLAYER_THUMBNAILS` - whether movie thumbnails should be displayed along with player
`PLAYER_EMBED_CODE` - whether player embed code should be displayed:

`VIDEO_DIR` - directory in which video is stored. Time formatting can be used as usual.
`TEMP_VIDEO_DIR` - directory for temporary video files

### Encoding related parameters ###

`ENCODING_AFREQ` - audio frequency
`ENCODING_ABITRATE` - audio bitrate
`ENCODING_FRAMERATE` - video framerate
`ENCODING_VBITRATE` - video bitrate
`ENCODING_WIDTH` - encoded video width
`ENCODING_HEIGHT` - encoded video height
`ENCODING_LOG_FILE` - encoding log file. This file is separate for every video. If you do not want to have this type of log you can specify '/dev/null' on Unix system or possibly 'nul' on Windows (the latter was not tested). For some videos this file can become unreasonably big so it can safely be deleted after encoding using `clean_auxiliarry_files` method of video object.

### Thumbnail generation related parameters ###

`THUMBNAIL_TIMESTEP` - this specifies an interval of time between two thumbnails
`THUMBNAIL_WIDTH` - this parameters can be used to resize thumbnails (keeping aspect) to the specified width. If it's `None` (which is default) then thumbnails are of the video size.
`THUMBNAIL_MINIMUM_NUMBER` - this defines the minimum quantity of thumbnails to be generated. So you will have at least `THUMBNAIL_MINIMUM_NUMBER` of thumbnails for every video which is useful for tiny videos with duration less then `THUMBNAIL_TIMESTEP * THUMBNAIL_MINIMUM_NUMBER`.
`THUMBNAIL_LOG_FILE` - the save as `ENCODING_LOG_FILE` but for thumbnails. And it does not have a size issue.
`THUMBNAIL_DIR` - the name of directory for thumbnails in every video directory

### Debug options ###
`LOG_FUNCTION` - function which is used to log on errors.

# Uploading #
You can upload videos using something similar to the following. UploadForm is in `video/forms.py`. It's capable of filtering out invalid videos or non-videos at all. This form uses magics to tell apart videos on non-videos. So you've got to have up to date magic database.
```
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
```

# Templatetags #

Parameters to templatetag a provided as following:
`{% tag par1=value1 par2=value2 %}`

## Player templatetag ##
To embed a player in your page you should make use of `player` templatetag. Possible parameters to this templatetag are: `width`, `height`, `autoplay`, `volume`, `loop`, `mute`, `thumbnails`, `embed_code`. Meaning of this parameters is quite obvious.

## Thumbnails templatetag ##
You can display thumbnails of the certain video separately from player. To fulfill that goal you can use `thumbnails` templattag. It understands only two parameters: `width`, `player`. The latter is the name of javascript variable representing player. You can use this parameter if you want for user to have a possibility of jumping through the movie just by clicking on thumbnails.

# Bugs and issues #

In order to generate thumbnails our application uses mtn. But mtn in some cases may be imprecise in detecting a position of thumbnail in a movie. So jumping to the certain place in a video by clicking on thumbnails sometimes is buggy either.