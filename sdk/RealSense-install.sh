#!/bin/bash
sudo apt-get update && sudo apt-get dist-upgrade

sudo apt-get install -y automake python3-protobuf libtbb-dev libtool cmake libusb-1.0-0-dev libx11-dev xorg-dev libglu1-mesa-dev libssl-dev clang llvm libatlas-base-dev python3-opencv

cd ~
git clone https://github.com/IntelRealSense/librealsense.git
cd librealsense
sudo cp config/99-realsense-libusb.rules /etc/udev/rules.d/ 
sudo udevadm control --reload-rules 
sudo udevadm trigger

echo "
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=cpp
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION_VERSION=3
export PYTHONPATH=$PYTHONPATH:/usr/local/lib:/home/pi/librealsense/build/wrappers/python:/home/pi/librealsense/build/Release
" >> .bashrc
source ~/.bashrc

export CC=/usr/bin/clang
export CXX=/usr/bin/clang++

cd ~/librealsense
mkdir  build  && cd build
cmake .. -DBUILD_EXAMPLES=false -DCMAKE_BUILD_TYPE=Release -DFORCE_LIBUVC=true -DOTHER_LIBS="-latomic"
make -j4
sudo make install

cd ~/librealsense/build
cmake .. -DBUILD_PYTHON_BINDINGS=bool:true -DPYTHON_EXECUTABLE=$(which python3)
make -j4
sudo make install

unset CC
unset CXX



