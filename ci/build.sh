#!/usr/bin/bash
set -e
set +x

echo "Building"
cd firmware/micropython

DOCKER="docker run --rm -v $HOME:$HOME -u $UID -w $PWD larsks/esp-open-sdk"
echo $DOCKER

NPROC=$(nproc)

$DOCKER make -C mpy-cross -j $NPROC
$DOCKER make submodules -C ports/esp8266 -j $NPROC
$DOCKER make axtlc -C ports/esp8266 -j $NPROC
$DOCKER make -C ports/esp8266 -j $NPROC

FIRMWARE=ports/esp8266/build-GENERIC/firmware-combined.bin
mv $FIRMWARE ../
echo "Build firmware is at firmware/$FIRMWARE"
cd ../../
