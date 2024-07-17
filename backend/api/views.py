import os
import yt_dlp
from django.conf import settings
from django.http import FileResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.signals import request_finished
from django.dispatch import receiver
from threading import Timer

# Global variable to store the path of the file to be deleted
file_to_delete = None

def delete_file(file_path):
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"File deleted: {file_path}")
        except Exception as e:
            print(f"Error deleting file {file_path}: {str(e)}")

@api_view(['GET'])
def ping(request):
    return Response({"message": "pong"})

@api_view(['POST'])
def get_video_info(request):
    url = request.data.get('url')
    
    if not url:
        return Response({'error': 'URL is required'}, status=400)

    try:
        ydl_opts = {}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
        video_info = {
            'title': info['title'],
            'author': info['uploader'],
            'description': info['description'],
            'thumbnail': info['thumbnail'],
            'duration': info['duration'],
        }
        return Response(video_info)
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['POST'])
def download_video(request):
    global file_to_delete
    url = request.data.get('url')

    if not url:
        return Response({'error': 'URL is required'}, status=400)

    try:
        download_path = os.path.join(settings.MEDIA_ROOT, 'downloads')
        os.makedirs(download_path, exist_ok=True)

        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        file_to_delete = filename  # Store the filename for later deletion
        response = FileResponse(open(filename, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(filename)}"'
        return response

    except Exception as e:
        if file_to_delete:
            delete_file(file_to_delete)
        return Response({'error': str(e)}, status=400)

@receiver(request_finished)
def schedule_file_deletion(sender, **kwargs):
    global file_to_delete
    if file_to_delete:
        file_path = file_to_delete
        file_to_delete = None  # Reset the global variable
        # Schedule file deletion after a delay
        Timer(7.0, delete_file, args=(file_path,)).start()