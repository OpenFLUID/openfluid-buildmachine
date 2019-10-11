# $1 is the name of the directory that will be created, contain every necessary code and be shared with docker images
# $2 is the sourcesup username
# $3 is the github username

# AUTOMBMBUILD athoni Arthoni

# check args number

mkdir $1
cd $1
chmod 777 .

mkdir GitRepositories
cd GitRepositories

git clone git+ssh://$2@git.renater.fr:2222/scmrepos/git/openfluid/openfluid-devtools.git
git clone https://github.com/$3/openfluid-buildmachine.git

cd openfluid-buildmachine
git checkout MBM
pip3 install -e .

#python3 setup.py test
python3 tests/02mbm.py MainTest.test_mbm

cd ../../

echo "Settings can be changed in openfluid-buildmachine/mbm/settings.py"
echo "Existing yml for multi-build config is in openfluid-buildmachine/mbm/basicConf.yml"
echo ""
echo "Multi-build machine can be launched with 'mbm (-c [config yaml file])'"
