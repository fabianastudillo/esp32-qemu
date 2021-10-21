FROM python:3.7.11-bullseye
LABEL Fabian Astudillo-Salinas <fabian.astudillos@ucuenca.edu.ec>

RUN apt-get update
RUN apt-get install -y git
RUN apt-get install -y build-essential zlib1g-dev pkg-config libglib2.0-dev binutils-dev libboost-all-dev autoconf libtool libpixman-1-dev
RUN apt-get install -y wget flex bison gperf cmake ninja-build ccache libffi-dev libssl-dev dfu-util
#RUN python -m pip install requests==2.26.0 elasticsearch==7.14.0 pandas==1.3.2 pysocks==1.7.1
#RUN python -m pip install -U scikit-learn
#RUN python -m pip install matplotlib==1.16.0
#RUN python -m pip install plotly chart_studio

RUN mkdir esp32-qemu
WORKDIR /esp32-qemu
RUN git clone https://github.com/Ebiroll/qemu-xtensa-esp32 -b esp-develop esp-develop
RUN mkdir qemu_espressif
WORKDIR /esp32-qemu/qemu_espressif
RUN ../esp-develop/configure --target-list=xtensa-softmmu --enable-debug --enable-sanitizers --disable-strip --disable-capstone --disable-vnc
RUN make
RUN pwd
RUN cp ../esp-develop/pc-bios/esp32-r0-rom.bin .
WORKDIR /esp32-qemu
RUN mkdir -p esp
WORKDIR /esp32-qemu/esp
RUN git clone --recursive https://github.com/espressif/esp-idf.git
WORKDIR /esp32-qemu/esp/esp-idf
RUN ./install.sh
RUN export IDF_PATH=/esp32-qemu/esp/esp-idf
#RUN . ./export.sh
WORKDIR /root
RUN wget https://downloads.arduino.cc/arduino-1.8.16-linux64.tar.xz
RUN tar -Jxvf arduino-1.8.16-linux64.tar.xz
WORKDIR /root/arduino-1.8.16
RUN ./install.sh
#RUN usermod -a -G dialout $USER
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python get-pip.py
RUN pip install pyserial
RUN mkdir -p /root/Arduino/hardware/espressif
WORKDIR /root/Arduino/hardware/espressif
RUN git clone https://github.com/espressif/arduino-esp32.git esp32
WORKDIR /root/Arduino/hardware/espressif/esp32
RUN git submodule update --init --recursive
WORKDIR /root/Arduino/hardware/espressif/esp32/tools
RUN python get.py
RUN apt-get install -y libxtst6
RUN apt install -y xauth
ADD ./cli_interface /root/cli_interface
RUN cd /root/cli_interface; \
    pip install -r requirements.txt; \
    python -m pip install --editable .

RUN pip install future==0.15.2 cryptography==2.1.4 gdbgui==0.13.2.0 pygdbmi==0.9.0.2 \
    pip install pyparsing==2.0.3 pyelftools==0.22 idf-component-manager==0.2.99-beta \
    pip install python-socketio==4 kconfiglib==13.7.1 reedsolo==1.5.3 bitstring==3.1.6 \
    pip install ecdsa==0.16.0 construct==2.10.54
#ADD make-flash-img.sh /bin/make-flash-img.sh
#ADD execute.sh /bin/execute.sh
#RUN chmod +x /bin/make-flash-img.sh
#RUN chmod +x /bin/execute.sh
RUN mkdir /esp32-bin
RUN rm /root/arduino-1.8.16-linux64.tar.xz
#CMD ["/usr/local/bin/arduino"]
#RUN echo "export PATH=$PATH:/esp32-bin" >> /root/.bashrc
RUN cd /root/

ENTRYPOINT [ "/bin/bash", "/esp32-bin/entrypoint.sh" ]

#CMD [ "python", "./fingerprint_generator.py" ]
