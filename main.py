import os
import shutil
import datetime
from pathlib import Path


TMP_DIR = Path("tmp")
OUT_DIR = Path("out")
AUDIO_PARENT_DIR = Path("vendoring") / "lib"
AUDIO_FORMATS = [p.name for p in AUDIO_PARENT_DIR.iterdir() if p.is_dir()]
DICTIONARY_NAME = "japanese-vocabulary-pronunciation-audio-master-{{AUDIO_FORMAT}}"
INDEX_FILE_NAME = "yomitan_index.json"



def create_dict_dir(target_dir : Path):

    if not os.path.exists(target_dir):
        os.makedirs(target_dir, exist_ok=True)
        os.makedirs(target_dir / "audios", exist_ok=True)

def write_index_file(target_dir : Path, dict_title : str):

    with open(INDEX_FILE_NAME, mode="r") as f:
        index_file_content = f.read()

    with open(target_dir / INDEX_FILE_NAME, mode="w") as f:
        index_file_content = index_file_content.replace("{{DICT_TITLE}}", dict_title)
        index_file_content = index_file_content.replace("{{REVISION}}", datetime.datetime.now().strftime("%Y.%m.%d"))
        f.write(index_file_content)

def copy_audio_files(target_dir : Path, source_dir : Path):

    shutil.copytree(
        source_dir,
        target_dir / "audios",
        dirs_exist_ok=True
    )

def create_zip_file(target_dir : Path, dict_title : str):

    shutil.make_archive(
        base_name=target_dir,
        format="zip",
        root_dir=str(TMP_DIR),
        base_dir=dict_title,
    )


def main():

    for audio_format in AUDIO_FORMATS:
        dict_title = DICTIONARY_NAME.replace("{{AUDIO_FORMAT}}", audio_format)
        source_dir = AUDIO_PARENT_DIR / audio_format
        tmp_dir = TMP_DIR / dict_title
        out_dir = OUT_DIR / dict_title
        
        create_dict_dir(tmp_dir)
        write_index_file(tmp_dir, dict_title)
        copy_audio_files(tmp_dir, source_dir)
        create_zip_file(out_dir, dict_title)
        

if __name__ == "__main__":
    main()
