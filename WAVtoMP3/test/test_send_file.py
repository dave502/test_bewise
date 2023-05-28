import base64
import json
import os
import random
import re
import urllib
from pathlib import Path
import requests as requests


def main():
    test_user_file: Path = Path("./test_user_file.json")
    if test_user_file.is_file():
        with open(test_user_file) as json_file:
            data = json.load(json_file)
            print(data)
    else:
        test_user_url: str = 'http://127.0.0.1:5000/api/signup/test_user'
        response = requests.post(test_user_url)
        if response.status_code == 201 and (data := response.json()):
            with open(test_user_file, 'w') as json_file:
                json_file.write(json.dumps(data))

    if data:
        url: str = 'http://127.0.0.1:5000/api/convert'
        user: str = data.get("unique_name")
        uuid: str = data.get("uuid")
        headers = {"Authorization": "Basic {}".format(base64.b64encode(bytes(f"{user}:{uuid}", "utf8")).decode("utf8"))}
        wav_path_folder: Path = Path(os.path.abspath(os.path.dirname(__file__))) / 'wav_samples'
        wav_file: str = random.choice(os.listdir(wav_path_folder))
        print(f'File "{wav_file}" will be sent')
        files = {'file': (wav_file, open(wav_path_folder / wav_file, 'rb'), {'Expires': '0'})}

        # * make request for convertation
        response = requests.post(url, files=files, headers=headers)
        if not response.ok:
            print(response.json().get('message'))
            return
        file_url: str = json.loads(response.content).get("url")
        print(f"Link for download {file_url=}")

        # * make request to download converted mp3 file
        response = requests.get(file_url)
        cont_disp = response.headers['content-disposition']
        # decode filename if it's cyrillic
        if cont_disp.find("filename*=UTF-8") >= 0:
            filename = urllib.parse.unquote(re.findall("filename\*=UTF-8''(.+)", cont_disp)[0])
        else:
            filename = re.findall("filename=(.+)", cont_disp)[0]

        if response.status_code == 200:
            print(f'file "{filename}" was received')
            open(Path.cwd() / Path("mp3") / filename, 'wb').write(response.content)
        else:
            print("Error")
    else:
        print("Error! Application can't receive authorization data.")


if __name__ == "__main__":
    main()
