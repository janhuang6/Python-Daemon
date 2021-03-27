#!/usr/bin/python3

import os
import time
import os.path
import glob
import logging
import sys
import shutil

USER = os.environ['USER']
src_dir = '/nfs_snc/data/projects/ferm/slam/profile/'
#src_dir  = '/home/'+USER+'/profile/'
haps_dir = '/home/'+USER+'/HAPS/'

if not os.path.isdir(haps_dir):
    os.mkdir(haps_dir)

if not os.path.isdir(haps_dir+'dsp-hex/'):
    os.mkdir(haps_dir+'dsp-hex/')

if not os.path.isdir(haps_dir+'profile/'):
    os.mkdir(haps_dir+'profile/')

# Modification datetime stamp
moddate_vio_pre = moddate_dsp_pre = moddate_com_pre = 0
moddate_vio_cur = moddate_dsp_cur = moddate_com_cur = 0

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

while True:
    if os.path.isfile(src_dir+'viocommands.bin'):
        moddate_vio_cur = os.stat(src_dir+'viocommands.bin')[8]
    if os.path.isfile(src_dir+'vio-replay-haps-dsp.hex.iss'):
        moddate_dsp_cur = os.stat(src_dir+'vio-replay-haps-dsp.hex.iss')[8]
    if os.path.isfile(src_dir+'commmit_info.txt'):
        moddate_com_cur = os.stat(src_dir+'commmit_info.txt')[8]

    if moddate_vio_pre != moddate_vio_cur and moddate_dsp_pre != moddate_dsp_cur and moddate_com_pre != moddate_com_cur:
        logger.info('==================== Detected new files for processing... ====================')
        timestr = time.strftime('%Y%m%d_%H%M%S')
        logger.info("Current time is "+timestr)
        target_vio = haps_dir+'profile/'+timestr+'_viocommands.bin'
        target_dsp = haps_dir+'profile/'+timestr+'_dsp10.hex'
        os.system('cp -rf '+src_dir+'viocommands.bin '+target_vio)
        os.system('cp -rf '+src_dir+'vio-replay-haps-dsp.hex.iss '+target_dsp)
        os.system('sed -i "s/@28/@78/g" '+target_dsp)
        os.system('sed -i "s/@3/@8/g" '+target_dsp)
        os.system('rm -r '+haps_dir+'viocommands.bin')
        os.system('ln -s '+target_vio+' '+haps_dir+'viocommands.bin')
        os.system('rm -r '+haps_dir+'dsp-hex/dsp10.hex')
        os.system('ln -s '+target_dsp+' '+haps_dir+'dsp-hex/dsp10.hex')
        logger.info('Start to run source_haps.sh')
        os.system('/bin/csh -c "source '+haps_dir+'source_haps.sh"')

        moddate_vio_pre = moddate_vio_cur
        moddate_dsp_pre = moddate_dsp_cur
        moddate_com_pre = moddate_com_cur
        for file in glob.glob(haps_dir+'Clock_count_Haps/clock_count_haps_*.csv'):
            logger.info('Push '+file+' through shoebox')
            os.system('shoebox put -f /teams/ferm-vio-haps/ '+file+' -o -y')
            logger.info('Move '+file+' to pushed/ folder. Done!')
            shutil.move(file, haps_dir+'Clock_count_Haps/pushed/'+os.path.basename(file))
        logger.info('============================== Finish processing. ============================')
        timestr = time.strftime('%Y%m%d_%H%M%S')
        logger.info("Current time is "+timestr)
    time.sleep(10) #sleep 10 seconds
