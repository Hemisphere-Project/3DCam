#!/bin/bash

# TODO
# - install SDK ? or ./Redist enough ? => TerraBee 80x60

BASEPATH="$(dirname "$(readlink -f "$0")")"
cd "$BASEPATH"

# Dependencies
sudo apt install -y automake libtool cmake libusb-1.0-0-dev python3-protobuf libtbb-dev clang python3-opencv python3-flask-socketio python3-eventlet

# TerraBee SDK :: TODO
# wget https://www.terabee.com/wp-content/uploads/2020/06/TerraBee-SDK-1.0.0-Linux.zip OR use ./Redist

# RealSense SDK
git clone https://github.com/IntelRealSense/librealsense.git --depth 1
cd librealsense
./scripts/setup_udev_rules.sh
udevadm control --reload-rules
udevadm trigger
export CC=/usr/bin/clang
export CXX=/usr/bin/clang++
mkdir build && cd build
cmake .. -DBUILD_EXAMPLES=false -DCMAKE_BUILD_TYPE=Release -DFORCE_LIBUVC=true -DOTHER_LIBS="-latomic"
make -j4 && sudo make install
cmake .. -DBUILD_PYTHON_BINDINGS=bool:true -DPYTHON_EXECUTABLE=$(which python3)
make -j4 && sudo make install
cd Release
for libfile in pyrealsense2.cpython-*.so; do
    ln -sf "$PWD/$libfile" "$BASEPATH"/
done
unset CC
unset CXX
cd "$BASEPATH"

# Service
ln -sf "$BASEPATH/3dcam" /usr/local/bin/
ln -sf "$BASEPATH/3dcam.service" /etc/systemd/system/
systemctl daemon-reload

echo "3dcam INSTALLED"
echo
