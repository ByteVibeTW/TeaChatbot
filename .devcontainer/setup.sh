#!/bin/bash
set -e

echo 'Dir::Cache::archives "";' > /etc/apt/apt.conf.d/no-cache
apt-get update
apt-get install -y wget nano vim curl

# CUDA
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
dpkg -i cuda-keyring_1.1-1_all.deb
apt-get update
apt-get -y install cuda-toolkit-12-5
rm -rf /var/lib/apt/lists/*

# cuDNN
wget https://developer.download.nvidia.com/compute/cudnn/9.3.0/local_installers/cudnn-local-repo-ubuntu2204-9.3.0_1.0-1_amd64.deb
dpkg -i cudnn-local-repo-ubuntu2204-9.3.0_1.0-1_amd64.deb
cp /var/cudnn-local-repo-ubuntu2204-9.3.0/cudnn-*-keyring.gpg /usr/share/keyrings/
cd /var/cudnn-local-repo-ubuntu2204-9.3.0 && dpkg -i libcudnn9-cuda-12_9.3.0.75-1_amd64.deb
cd /var/cudnn-local-repo-ubuntu2204-9.3.0 && dpkg -i libcudnn9-dev-cuda-12_9.3.0.75-1_amd64.deb
apt-get -y install cudnn-cuda-12
rm -rf /var/lib/apt/lists/*

# 驗證
nvidia-smi || echo "nvidia-smi not found"
nvcc --version || echo "nvcc not found"