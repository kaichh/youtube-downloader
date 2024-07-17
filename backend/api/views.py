import yt_dlp
from django.http import JsonResponse, FileResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

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
    url = request.data.get('url')
    format_type = request.data.get('format', 'mp4')

    if not url:
        return Response({'error': 'URL is required'}, status=400)

    try:
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': '%(title)s.%(ext)s',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        response = FileResponse(open(filename, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    except Exception as e:
        return Response({'error': str(e)}, status=400)