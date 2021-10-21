#!/usr/bin/env bash
set -e

echo "export PATH=$PATH:/esp32-bin:/root/.espressif/tools/xtensa-esp32-elf/esp-2021r1-8.4.0/xtensa-esp32-elf/bin/:/xtensa-esp32-elf/bin/" >> /root/.bashrc
bash

chmod +x /esp32-bin/execute.sh
chmod +x /esp32-bin/make-flash-img.sh

#/usr/local/bin/arduino
tail -f /dev/null