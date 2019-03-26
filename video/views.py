from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .forms import UploadFileForm
import os
from .models import Movie
from .models import AccessLog as Log
import subprocess
import threading
import urllib.parse
import pandas as pd
from uuid import uuid4
from os.path import expanduser as eu
from datetime import datetime
import hashlib
from datetime import timedelta
import logging
import imghdr

# Create your views here.

def rootdir(request):
    return HttpResponse('<h1>hello world!</h1>')

def movie(request):
    logger = logging.getLogger('command')
    logger.info('a')
    
    domain = request.META['HTTP_HOST']
    try:
        userhash = hashlib.sha256(request.META['HTTP_X_FORWARDED_FOR'].encode('utf-8')).hexdigest()
    except:
        userhash = 'localhost'
    ls, msg, mid, title, o = [[], '', None, None, None]
    
    if 'id' in request.GET:
        mid = request.GET['id']
        try:
            movie = Movie.objects.get(movieid=mid)
        except:
            pass
        else:
            if 'remove' in request.GET:
                Movie.objects.filter(movieid=mid).update(remove=True)
    else:
        mid, title = [None, None]
        movie = None
    
    log = Log.objects.filter(userid=str(userhash))
    log = log.filter(movieid=mid).order_by('-at')
    if len(log) != 0:
        if False:
            delta = datetime.now() - log[0].at
            if delta > timedelta(hours=6):
                Log(movieid=mid, userid=userhash).save()
                if movie is not None:
                    movie.playcount += 1
                    movie.save()
    else:
        Log(movieid=mid, userid=userhash).save()
        if movie is not None:
            movie.playcount += 1
            movie.save()
        delta = None
        
    return render(request, 'video/video.html', dict(
        msg='', ls=Movie.objects.filter(remove=False).order_by('-posted_at'), mid=mid, domain=domain, title=title,
        movie=movie
    ))




def func11(file_name, mid):
    if imghdr.what(file_name) in [None, 'gif']:
        path = eu('~/www/media/storage/movie/') + f'{mid}.jpg'
        subprocess.run(
            ['ffmpeg', ] + \
            '-ss 7 -t 1 -r 1'.split(' ') + \
            ['-i', file_name] + \
            f'-f image2 -s 320x240'.split(' ') +\
            [path]
        )
        path = eu('~/www/media/storage/movie/')
        cmd = ["ffmpeg", "-i", file_name] + \
        '-map 0 -f segment -vcodec libx264 -acodec aac -strict experimental'.split(' ') + \
            '-vf scale=640:-1 -vb 512k'.split(' ') + \
        ["-segment_list", f'{path}ts/{mid}.m3u8', '-segment_time', '2', f'{path}ts/{mid}-%03d.ts']
        subprocess.run(cmd)
    else:
        path = eu('~/www/media/storage/movie/') + f'{mid}.jpg'
        subprocess.run(
            ['ffmpeg', ] + \
            '-ss 7 -t 1 -r 1'.split(' ') + \
            ['-i', file_name] + \
            f'-f image2 -s 3200x2400'.split(' ') +\
            [path]
        )
    os.remove(file_name)
        
def upload(request):
    base = os.path.dirname(os.path.abspath(__file__))
    
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        file_obj = request.FILES['file']
        if form.is_valid():
            try:
                userhash = hashlib.sha256(request.META['HTTP_X_FORWARDED_FOR'].encode('utf-8')).hexdigest()
            except:
                userhash = 'localhost'
            mid = str(uuid4())
            file_name = os.path.join('ignore', 'temp', f'{mid}.tmp')
            if not os.path.exists(file_name):
                with open(file_name, 'wb+') as output:
                    for chunk in file_obj.chunks():
                        output.write(chunk)
                thread_1 = threading.Thread(target=func11, args=(file_name, mid))
                thread_1.start()
                msg = 'Success!'
                title = request.POST['title']
                if title == '':
                    title = os.path.basename(file_obj.name)
                Movie(
                    title=title,
                    playcount=0,
                    movieid=mid,
                    userid=userhash,
                    filetype=imghdr.what(file_name),
                ).save()
                return redirect('video')
            else:
                msg = 'file already uploaded'
        else:
            msg = 'invalid form'
    else:
        form = UploadFileForm()
        msg = ''
    return render(request, 'video/upload.html', dict(form=form, msg=msg))