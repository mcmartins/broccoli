# download prover9 software
wget https://www.cs.unm.edu/~mccune/prover9/download/LADR-2009-11A.tar.gz
# unpack
tar -xzf LADR-2009-11A.tar.gz
# remove tar
rm LADR-2009-11A.tar.gz
# go to folder and compile
cd LADR-2009-11A/
make all
# as root add prover9 to path (change path to prover9 accordingly)
su -
echo 'pathmunge /home/mcmartins/LADR-2009-11A/bin' > /etc/profile.d/LADR.sh
chmod +x /etc/profile.d/LADR.sh
# install module with setup.py
sudo python setup.py clean build install
# execute module
python -m broccoli -v -i /path/to/input.json
# or
python -m broccoli -v -i '<JSON>'

