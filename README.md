# japanese-vocabulary-pronunciation-audio-DaDb

Vendoring + Bundling of the japanese-vocabulary-pronunciation-audio to import into DaKanji

## Installation

Make sure uv is installed on your system and run

``` bash
uv sync
```

## Usage

Run this command to bundle data and convert it to a DaDb audio dictionary.

``` bash
uv run main.py
```

After running this script the dictionaries will be availalbe in `./out`

## Original data

https://github.com/tofugu/japanese-vocabulary-pronunciation-audio/tree/master