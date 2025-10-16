from django.http import FileResponse, HttpResponse, HttpResponseNotFound
import os
from django.conf import settings

def stream_audio(request, path):
    file_path = os.path.join(settings.MEDIA_ROOT, path)

    if not os.path.exists(file_path):
        return HttpResponseNotFound("Файл не найден")

    file_size = os.path.getsize(file_path)
    range_header = request.headers.get('Range')

    if range_header:
        start, end = range_header.replace('bytes=', '').split('-')
        start = int(start)
        end = int(end) if end else file_size - 1
        length = end - start + 1

        with open(file_path, 'rb') as f:
            f.seek(start)
            data = f.read(length)

        response = HttpResponse(data, status=206)
        response['Content-Type'] = 'audio/mpeg'
        response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
        response['Accept-Ranges'] = 'bytes'
        return response

    return FileResponse(open(file_path, 'rb'), content_type='audio/mpeg')