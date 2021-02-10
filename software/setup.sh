#!/bin/bash

# Copyright 2021 Google LLC

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     https://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


install_deps() {
    echo 'Installing dependencies'
    apt-get update
    apt-get install -y python3-picamera python3-pigpio python3-rpi.gpio
}


install_edgetpu() {
    if ! pip3 freeze | grep -q edgetpu
    then
        echo 'Installing edgetpu module'
        pushd /tmp
        wget --content-disposition https://github.com/google-coral/edgetpu-platforms/releases/download/v1.9.2/edgetpu_api_1.9.2.tar.gz
        tar xvf edgetpu_api_1.9.2.tar.gz
        cd edgetpu_api
        yes n | bash install.sh
        popd
    fi
}


setup_camera() {
    if ! grep -q '^start_x=1' /boot/config.txt
    then
        echo 'Enabling camera - reboot required'
        printf "\n# Enable camera\nstart_x=1\ngpu_mem=128" >> /boot/config.txt
    fi
}


setup_services() {
    svc=/etc/systemd/system/alto.service
    if ! [ -e ${svc} ]
    then
        echo 'Installing alto service'

        # Copy the service and change the working directory to ../app.
        appdir=$(cd $(dirname $0)/../app; pwd)
        sed -e "s:\\(WorkingDirectory=\\).*:\\1${appdir}:" $(dirname $0)/alto.service > ${svc}

        # Reduce pigpiod sample rate to reduce CPU usage.
        sed -i -e 's/-l$/-l -s 10/' /lib/systemd/system/pigpiod.service

        echo 'Starting pigpiod and alto'
        systemctl enable pigpiod
        systemctl enable alto

        systemctl start pigpiod
        systemctl start alto
    fi
}


if [ "$(whoami)" = "root" ]
then
    install_deps
    install_edgetpu
    setup_services
    setup_camera
else
    sudo bash $0
fi
