#!/usr/bin/env bash
set -e

folder="$1"

if [ -z "$1" ]; then
  echo "Usage: execute.sh project_directory"
  exit 1
fi

if [ ! -d "${folder}" ]; then
  echo "<project_directory> does no exist"
  exit 1
fi

/esp32-qemu/qemu_espressif/xtensa-softmmu/qemu-system-xtensa -nographic -M esp32 -drive file="/root/${folder}/${folder}img.bin,if=mtd,format=raw" -nic user,model=open_eth,hostfwd=tcp::80-:80 -s