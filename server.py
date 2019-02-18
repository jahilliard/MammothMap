import io
import PIL.Image
from io import BytesIO
from flask import Flask, send_file, request, make_response, Response
from manager import Manager

app = Flask(__name__)
manager = Manager()

@app.route('/api/v1/map', methods=['GET'])
def map_image():
    arr, checksum = manager.refresh_map_and_etag()
    if request.headers['If-None-Match'] == checksum:
        return Response(status=304)
    img = PIL.Image.fromarray(arr)
    img_io = BytesIO()
    img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    response = make_response(send_file(img_io, mimetype='image/jpeg'))
    response.headers['Etag'] = checksum
    return response


if __name__ == '__main__':
    app.run(debug=True)
