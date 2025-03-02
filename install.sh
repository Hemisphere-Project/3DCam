#!/bin/bash

# TODO
# - install SDK ? or ./Redist enough ? => TerraBee 80x60

BASEPATH="$(dirname "$(readlink -f "$0")")"
cd "$BASEPATH"

# Dependencies
# sudo apt-get install python3-opencv python3-numpy python3-protobuf python3-venv  

# Venv (legacy mode, now using poetry)
# python3 -m venv --system-site-packages venv
# source venv/bin/activate
# pip install setuptools
# pip install -r requirements.txt


# TerraBee SDK :: TODO
# wget https://www.terabee.com/wp-content/uploads/2020/06/TerraBee-SDK-1.0.0-Linux.zip OR use ./Redist

# RealSense SDK
apt install -y automake libtool cmake libusb-1.0-0-dev python3-protobuf libtbb-dev clang
git clone https://github.com/IntelRealSense/librealsense.git --depth 1
cd librealsense
./scripts/setup_udev_rules.sh
udevadm control --reload-rules
udevadm trigger

export CC=/usr/bin/clang
export CXX=/usr/bin/clang++
mkdir build && cd build
cmake .. -DBUILD_EXAMPLES=false -DCMAKE_BUILD_TYPE=Release -DFORCE_LIBUVC=true -DOTHER_LIBS="-latomic"
make -j4 && make install
cmake .. -DBUILD_PYTHON_BINDINGS=bool:true -DPYTHON_EXECUTABLE=$(which python3)
make -j4 && make install
# Link pyrealsense2.so to python3 site-packages
cd Release
for libfile in pyrealsense2.cpython-*.so; do
    ln -sf "$PWD/$libfile" /usr/lib/python3/dist-packages/pyrealsense2/
done
cd "$BASEPATH"
unset CC
unset CXX


# Poetry
poetry install
poetry run pip install opencv-python-headless




# ln -sf "$BASEPATH/3dcam" /usr/local/bin/
# ln -sf "$BASEPATH/3dcam.service" /etc/systemd/system/
# systemctl daemon-reload

echo "3dcam INSTALLED"
echo
