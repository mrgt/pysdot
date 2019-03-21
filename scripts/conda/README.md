---------- Complete process:
git clone http://github.com/sd-ot/pysdot.git
cd pysdot/conda

conda install anaconda anaconda-client conda-build
conda build . --output
anaconda login
anaconda upload -u sdot xxx.tar.bz2

---------- Complete process for windows
download visual studio
download miniconda
launch anaconda prompt
conda install git

---------- To test if it works (e.g. from a docker instance)
# docker run -it debian /bin/bash
cd
apt-get update && apt-get upgrade -y -q && apt-get dist-upgrade -y -q && apt-get -y -q autoclean && apt-get -y -q autoremove
apt-get install -y -q curl bzip2 git
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
chmod 777 Miniconda3-latest-Linux-x86_64.sh
./Miniconda3-latest-Linux-x86_64.sh -b
. /root/miniconda3/etc/profile.d/conda.sh

conda install -c hugo_lec sdot
conda activate

