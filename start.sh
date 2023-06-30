#! /bin/sh

cd ~/airplane-notify
touch nohup.out
rm nohup.out
nohup python3 -u airplane-notify.py --config ./config.json  &
sleep 2
tail -f nohup.out