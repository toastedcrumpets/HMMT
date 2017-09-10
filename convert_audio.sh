#!/bin/bash
unzip -o ~/Downloads/audio.zip && for f in *.wav; do ffmpeg -y -i "$f" -c:a libvorbis -q:a 4 "${f/%wav/ogg}"; done && rm *.wav && rm ~/Downloads/audio.zip
