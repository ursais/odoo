#!/bin/bash

# scp /Users/wendel/odoo/patches/02JUN2017/Archive.zip centos@172.31.48.13:/tmp
# odoo-prod
# sudo su - root
# cd /opt/odoo/odoo
# cp /tmp/Archive.zip .
# unzip Archive.zip && rm -f Archive.zip && rm -rf __MACOSX
# sh 02JUN2017_apply_patches.sh

patch -p0 -f < ./2017-06-02-1-10.0.patch
