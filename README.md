sager_client
============

Instructions for installing the polarmeter client:

1) Add current user (alex in my case) to dialout group:

  usermod -a -G dialout alex

2) Logout and log back in for the change to take effect, the groups are
initialized at login.

3) Install python-setuptools (debian-based instructions):

sudo apt-get install python-setuptools

4) Install the library from the sager_client folder:

sudo python setup.py install
