import os
import sys
import random
import shutil
import datetime
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import imageio_ffmpeg


TMP_DIR = Path("tmp")
OUT_DIR = Path("out")
AUDIO_PARENT_DIR = Path("vendoring") / "lib"
AUDIO_FORMATS = [p.name for p in AUDIO_PARENT_DIR.iterdir() if p.is_dir()]
DICTIONARY_NAME = "japanese-vocabulary-pronunciation-audio-master-{{AUDIO_FORMAT}}"
INDEX_FILE_NAME = "yomitan_index.json"

# Our own Opus build, encoded from the mp3 build: upstream's ogg build lacks
# 894 of the mp3 build's 6,355 words.
OPUS_SOURCE_FORMAT = "mp3"
OPUS_BITRATE = "32k"
ENCODED_DIR = TMP_DIR / "encoded"

SAMPLES_DIR = TMP_DIR / "samples"
SAMPLE_COUNT = 12
SAMPLE_BITRATES = ["24k", "32k", "48k", "64k"]



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


def encode_opus(source : Path, target : Path, bitrate : str):

    # -vn drops the cover art some mp3s embed, -map_metadata -1 their tags.
    subprocess.run(
        [
            imageio_ffmpeg.get_ffmpeg_exe(), "-nostdin", "-loglevel", "error", "-y",
            "-i", str(source),
            "-vn", "-map_metadata", "-1",
            "-ac", "1", "-c:a", "libopus", "-b:a", bitrate,
            str(target),
        ],
        check=True,
    )

def encode_audio_files(source_dir : Path, target_dir : Path, bitrate : str):

    os.makedirs(target_dir, exist_ok=True)
    sources = sorted(source_dir.iterdir())
    with ThreadPoolExecutor() as pool:
        list(pool.map(
            lambda source: encode_opus(source, target_dir / f"{source.stem}.opus", bitrate),
            sources,
        ))

def write_samples():

    source_dir = AUDIO_PARENT_DIR / OPUS_SOURCE_FORMAT
    sources = random.Random(0).sample(sorted(source_dir.iterdir()), SAMPLE_COUNT)
    shutil.rmtree(SAMPLES_DIR, ignore_errors=True)
    for source in sources:
        sample_dir = SAMPLES_DIR / source.stem
        os.makedirs(sample_dir)
        shutil.copy(source, sample_dir / f"original{source.suffix}")
        for bitrate in SAMPLE_BITRATES:
            encode_opus(source, sample_dir / f"{bitrate}.opus", bitrate)
    print(f"samples in {SAMPLES_DIR}")


def main():

    if "--samples" in sys.argv:
        write_samples()
        return

    shutil.rmtree(ENCODED_DIR, ignore_errors=True)
    encode_audio_files(AUDIO_PARENT_DIR / OPUS_SOURCE_FORMAT, ENCODED_DIR / "opus", OPUS_BITRATE)

    source_dirs = {audio_format: AUDIO_PARENT_DIR / audio_format for audio_format in AUDIO_FORMATS}
    source_dirs["opus"] = ENCODED_DIR / "opus"

    for audio_format, source_dir in source_dirs.items():
        dict_title = DICTIONARY_NAME.replace("{{AUDIO_FORMAT}}", audio_format)
        tmp_dir = TMP_DIR / dict_title
        out_dir = OUT_DIR / dict_title
        
        create_dict_dir(tmp_dir)
        write_index_file(tmp_dir, dict_title)
        copy_audio_files(tmp_dir, source_dir)
        create_zip_file(out_dir, dict_title)
        

if __name__ == "__main__":
    main()
