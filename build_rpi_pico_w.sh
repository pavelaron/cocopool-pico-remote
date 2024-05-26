#!/bin/sh
# Command example: ./build_rpi_pico_w.sh v1.22.2 PicoWExample

HOSTNAME=Cocopool
MPCONFIG_PATH=./micropython/ports/rp2/boards/RPI_PICO_W/mpconfigboard.h

git clone --depth 1 --branch $1 https://github.com/micropython/micropython.git

if [[ "$OSTYPE" == "darwin"* ]]; then
  sed -i '' 's/\(#define MICROPY_PY_NETWORK_HOSTNAME_DEFAULT.*\)".*"/\1"'$HOSTNAME'"/g' $MPCONFIG_PATH
else
  sed -ri 's/(#define MICROPY_PY_NETWORK_HOSTNAME_DEFAULT.*)".*"/\1"'$HOSTNAME'"/g' $MPCONFIG_PATH
fi

make -C ./micropython/mpy-cross/ -j 16
make -C ./micropython/ports/rp2 BOARD=RPI_PICO_W clean
make -C ./micropython/ports/rp2 BOARD=RPI_PICO_W submodules
make -C ./micropython/ports/rp2 BOARD=RPI_PICO_W -j 16
