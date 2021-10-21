#!/usr/bin/env bash
set -e

BOOTLOADER="/root/Arduino/hardware/espressif/esp32/tools/sdk/esp32/bin/bootloader_dout_40m.bin"
DEFAULTBIN="/root/Arduino/hardware/espressif/esp32/tools/partitions/default.bin"
folder=`basename $(pwd)`
arg_projname="${folder}" # Appname has to be the same name of folder
arg_flashimg="${folder}.bin" # Flass img file
#if [ -z "$1" ]; then
#  echo "Usage: make-flash-img.sh project_directory"
#  exit 1
#fi

#if [ ! -d "/${folder}" ]; then
#  echo "<project_directory> does no exist"
#  exit 1
#fi

dd if=/dev/zero bs=1024 count=4096 of="${arg_flashimg}"
dd if="${BOOTLOADER}" bs=1 seek=$((0x1000)) of="${arg_flashimg}" conv=notrunc
dd if="${DEFAULTBIN}" bs=1 seek=$((0x8000)) of="${arg_flashimg}" conv=notrunc
dd if="${arg_projname}.ino.esp32.bin" bs=1 seek=$((0x10000)) of="${arg_flashimg}" conv=notrunc
cp ${arg_flashimg} /root/workspace/current/flash_image.bin