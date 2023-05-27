from flask import Blueprint, request, current_app, send_file, url_for, after_this_request, jsonify, \
    make_response, Response
from app.models import Track, User
from app import db
import secrets
import string
from pathlib import Path
from datetime import datetime
# pydub REQUIRES sudo apt-get install ffmpeg
from pydub import AudioSegment
from werkzeug.datastructures.file_storage import FileStorage
import json
import os
from flask_cors import cross_origin
from typing import Callable

app_route = Blueprint('route', __name__)
REMOVE_AFTER_DOWNLOADING = True


def makename(user_uid: str, time: str, mp3filename: str) -> str:
    """
    :param user_uid: owner uid
    :param time: unix timestamp
    :param mp3filename: file name
    :return: unique file name
    """
    return ":".join([str(user_uid), time, mp3filename])


def response_msg(message: str, status: int, logger: Callable = None) -> Response:
    """
    Make response for abort function
    """
    logger(message)
    return make_response(jsonify(message=message), status)


@app_route.route('/')
def index():
    return "WAV to MP3 service"


@app_route.route('/api/signup', methods=['POST'])
@app_route.route('/api/signup/<string:username>', methods=['POST'])
@cross_origin()
def create_user(username: str = None) -> Response:
    unique_name: str = ""

    def random_string(length: int = 8) -> str:
        """
        Returns random string for generating unique user's names
        :param length: length of random string
        :return: rendom string with letters and numbers
        """
        letters_and_digits = string.ascii_letters + string.digits
        rand_string = ''.join(secrets.choice(letters_and_digits) for i in range(length))
        return rand_string

    # * get request user's name
    if username:  # if username in url
        unique_name = username
    else:  # if username in json parameters
        try:
            payload = json.loads(request.data)
            if not payload or not (unique_name := payload.get('username')):
                raise Exception("The key \'username\' is wrong")
        except Exception as e:
            return response_msg(f'{e} Problem with request data', 401, current_app.logger.error)

    # * generate unique user's name
    name_exists = User.query.with_entities(User.unique_name).filter_by(unique_name=unique_name).first()
    while name_exists:
        unique_name = f'{username}_{random_string()}'
        name_exists = User.query.with_entities(User.unique_name).filter_by(unique_name=unique_name).first()

    # * create user in database
    try:
        new_user: User = User(name=username, unique_name=unique_name)
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f'{e} Error during user {username} creation')
        return response_msg(f'{e} Error during user {username} creation', 500, current_app.logger.error)

    current_app.logger.debug(f'User {new_user.name} was created')
    return make_response(new_user.as_dict(), 201)


@app_route.route('/api/record', methods=['GET'])
def record() -> Response:
    """
    send file to user
    :return:
    """
    # get request parameters
    track_id: int = int(request.args.get('id'))
    user_unique_name: str = request.args.get('user')
    print(track_id, user_unique_name)
    # * get track info from database
    track: Track = Track.query.filter_by(id=track_id).first()
    # if track really belongs to user
    if track and track.owner.unique_name == user_unique_name:
        # get file's unique name for getting it from storage
        mp3_name: str = makename(track.owner.uuid, track.timestamp, track.name)
        mp3_path: Path = current_app.config['UPLOAD_FOLDER'] / 'mp3' / mp3_name

        # * remove after downloading if REMOVE_AFTER_DOWNLOADING = True
        @after_this_request
        def remove_file(response):
            if REMOVE_AFTER_DOWNLOADING:
                try:
                    os.remove(mp3_path)
                except Exception as e:
                    current_app.logger.error("Error removing mp3 file", e)
                try:
                    db.session.delete(track)
                    db.session.commit()
                except Exception as e:
                    current_app.logger.error("Error removing track object", e)
            return response

        # * send file to user
        current_app.logger.debug(f'File {mp3_name} will be sent')
        return send_file(mp3_path, mimetype='audio/mpeg',  download_name=track.name, as_attachment=True), 200
    else:
        return response_msg(f'File {track_id=} {user_unique_name=} not found',
                            404, current_app.logger.error)


@app_route.route('/api/convert', methods=['POST'])
@cross_origin()
def convert() -> Response:
    """
    Convert file from wav to mp3
    :return:
    """
    wav_folder: Path = current_app.config['UPLOAD_FOLDER'] / 'wav'
    mp3_folder: Path = current_app.config['UPLOAD_FOLDER'] / 'mp3'
    ALLOWED_EXTENSIONS: set = {'.wav'}
    current_app.config['MAX_CONTENT_LENGTH'] = 20 * 1000 * 1000

    file: FileStorage = None
    mp3filename: str = ""
    url: str = ""

    # * get user's data and file from request

    user_name: str = request.authorization.get("username")
    user_uid: str = request.authorization.get("password")
    if (not user_name) or (not user_uid):
        return response_msg('No authorization in request', 400, current_app.logger.error)

    if not (file := request.files.get('file')):
        return response_msg('No file part in request', 400, current_app.logger.error)

    # find user in database
    user: User = User.query.filter_by(unique_name=user_name, uuid=user_uid).first()
    if not user:
        return response_msg("Unknown user", 401, current_app.logger.error)

    filename: Path = Path(file.filename)
    # if filename is correct and its extension is .wav
    if not filename or not (filename.suffix in ALLOWED_EXTENSIONS):
        return response_msg("Wrong file name of file format", 400, current_app.logger.error)

    current_app.logger.info(f'file {filename} was recieved')
    # * save wav file in upload folder
    time: str = str(datetime.utcnow().timestamp())  # timestamp for unique filenames
    filepath: Path = wav_folder / makename(user.uuid, time, filename.name)  # .name clears filename from unsecure path
    file.save(filepath)
    # * convert wav file to mp3
    try:
        mp3filename = str(filename.with_suffix(".mp3"))
        audio: AudioSegment = AudioSegment.from_wav(filepath)
        audio = audio.set_frame_rate(44100)
        audio.export(mp3_folder / makename(user_uid, time, mp3filename), format="mp3")
    except Exception as e:
        return response_msg(f'Error with convertation: {e}', 500, current_app.logger.error)
    finally:
        try:
            # * remove wav file
            os.remove(filepath)
        except Exception as e:
            current_app.logger.error(f'Error removing uploaded file {filepath}: {e}')
    # * create track object in database
    try:
        track: Track = Track(name=str(mp3filename), user=user, timestamp=time)
        db.session.add(track)
        db.session.commit()
    except Exception as e:
        # remove mp3 file
        os.remove(mp3_folder / makename(user_uid, time, mp3filename))
        return response_msg(f'{e} Error while writing track {mp3filename} object to database',
                            500, current_app.logger.error)
    else:
        # * create url for downloading
        url: str = f'{request.root_url}api/record?id={track.id}&user={user.unique_name}'
        current_app.logger.debug(f'url for file: {url}')

    return make_response(jsonify(url=url), 201)
