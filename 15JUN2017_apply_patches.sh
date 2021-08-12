#!/bin/bash

# scp /Users/wendel/odoo/patches/15JUN2017/Archive.zip centos@172.31.48.13:/tmp
# odoo-prod
# sudo su - root
# cd /opt/odoo/odoo
# cp /tmp/Archive.zip .
# unzip Archive.zip && rm -f Archive.zip && rm -rf __MACOSX
# sh 15JUN2017_apply_patches.sh

patch -p0 -f < ./ODOO-SA-2017-06-15-1_10.0.patch
patch -p0 -f < ./ODOO-SA-2017-06-15-2_10.0.patch
patch -p0 -f < ./ODOO-SA-2017-06-15-3_10.0.patch
patch -p0 -f < ./ODOO-SA-2017-06-15-4_10.0.patch
