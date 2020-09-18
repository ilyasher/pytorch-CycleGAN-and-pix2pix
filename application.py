# [START gae_python38_render_template]
import datetime
import os
import io
import requests
from PIL import Image, UnidentifiedImageError

from flask import Flask, render_template, send_file, request, redirect, flash

import apply_model

access_token = ''
with open('access_token', 'r') as f:
    access_token = f.readline().strip()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16MB upload limit
app.secret_key = os.urandom(16)

application = app

IMG_PATH = '/tmp/full.png'
IMG_TRIMMED_PATH = '/tmp/trimmed.png'
IMG_TMP_PATH = '/tmp/tmp.png'

# Setup
model = apply_model.Model()

def reset():
    img = Image.open('./static/example.png')
    img.save(IMG_PATH)
    apply_model.trim_img(img).save(IMG_TRIMMED_PATH)
    model.get_heightmap()

reset()

def preprocess(crop_watermark=False):
    img = Image.open(IMG_TMP_PATH)
    os.remove(IMG_TMP_PATH)

    w, h = img.size
    crop_p = 0.9 if crop_watermark else 1
    min_dim = int(min(w, h) * crop_p)
    img = img.crop((0, 0, min_dim, min_dim))
    img = img.resize((256, 256), Image.ANTIALIAS)

    img.save(IMG_PATH)
    apply_model.trim_img(img).save(IMG_TRIMMED_PATH)

@app.route('/')
def root():
    reset()
    return render_template('index.html', heights=model.heights_list(), token=access_token)

@app.route('/img/<imgname>')
def get_image(imgname):
    output = io.BytesIO()
    Image.open('/tmp/'+imgname).save(output, format='PNG')
    output.seek(0, 0)
    return output.getvalue()

@app.route("/map")
def incorrect_map():
    return redirect("/")

@app.route("/map/<long>/<lat>/<zoom>")
def upload_image_from_map(long, lat, zoom):

    url = 'https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/'+ \
        long + ',' + lat + ',' + zoom + '/500x500?access_token=' + access_token;

    r = requests.get(url, allow_redirects=False)
    f = open(IMG_TMP_PATH, 'wb')
    f.write(r.content)
    f.close()

    try:
        preprocess(crop_watermark=True)

        model.get_heightmap()
    except UnidentifiedImageError:
        flash('Invalid Image')
        return redirect("/")

    return render_template('index.html', heights=model.heights_list(),
        token=access_token, long=long, lat=lat, zoom=zoom, scrolldown='true')

@app.route("/upload-image", methods=["GET", "POST"])
def upload_image():

    if request.method == "POST":

        if request.files:
            image = request.files["image"]

            if image.filename != "":
                image.save(IMG_TMP_PATH)
                try:
                    preprocess()

                    model.get_heightmap()
                except UnidentifiedImageError:
                    flash('Invalid Image')

    return render_template('index.html', heights=model.heights_list(), token=access_token)

@app.errorhandler(413)
def request_entity_too_large(error):
    return f"File Too Large (limit {int(app.config['MAX_CONTENT_LENGTH']/1024/1024)}MB)", 413

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.


    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python38_render_template]
