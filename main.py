import os

import datetime
from pathlib import Path


audio_formats = ["mp3", "ogg"]
dictionary_name = "japanese-vocabulary-pronunciation-audio-master-{{AUDIO_FORMAT}}"
index_file_name = "yomitan_index.json"


def write_index_file(target_dir : Path, dict_title : str):

    with open(index_file_name, mode="r") as f:
        index_file_content = f.read()

    with open(target_dir / index_file_name, mode="w") as f:
        index_file_content = index_file_content.replace("{{DICT_TITLE}}", dict_title)
        index_file_content = index_file_content.replace("{{REVISION}}", datetime.datetime.now().strftime("%Y.%m.%d"))
        f.write(index_file_content)


def main():

    for audio_format in audio_formats:
        dict_title = dictionary_name.replace("{{AUDIO_FORMAT}}", audio_format)
        
        target_dir = Path("tmp") / dict_title
        if not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)

        write_index_file(target_dir, dict_title)

        

if __name__ == "__main__":
    main()
