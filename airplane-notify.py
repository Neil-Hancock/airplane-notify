#!/usr/bin/env python

import argparse
import json
import logging
import sys
import requests
import time

from os import path
from pushbullet import Pushbullet

def notify_pushbullet(settings, msg):
    push = pb.push_note("Airplane of Interest in the Area", msg)


def main(settings):
    try:
        # obtain the json from the web url
        data: dict = requests.get(settings['dump1090_endpoint']).json()

        # parse the json
        if not data:
            logging.info('No airplanes in the sky.')
            return

        # current_apt = datetime.strptime(settings['current_interview_date_str'], '%B %d, %Y')

        # hash = hashlib.md5(''.join(dates) + current_apt.strftime('%B %d, %Y @ %I:%M%p')).hexdigest()
        # fn = "goes-notify_{0}.txt".format(hash)
        # if settings.get('no_spamming') and os.path.exists(fn):
        #     return
        # else:
        #     for f in glob.glob("goes-notify_*.txt"):
        #         os.remove(f)
        #     f = open(fn, "w")
        #     f.close()

    except OSError:
        logging.critical("Something went wrong when trying to obtain the openings")
        return

    for registration in settings['registration_numbers']:
        if registration in str(data):
            msg = f'Found registration number {registration} in the area'
            logging.info(f'{msg}, adsb airplane data: {data}')
            notify_pushbullet(settings, msg)


def _check_settings(config):
    required_settings = (
        'dump1090_endpoint',
        'pushbullet_api_key',
        'registration_numbers'
    )

    for setting in required_settings:
        if not config.get(setting):
            raise ValueError('Missing setting %s in config.json file.' % setting)


if __name__ == '__main__':

    # Configure Basic Logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(levelname)s: %(asctime)s %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        stream=sys.stdout,
    )

    pwd = path.dirname(sys.argv[0])

    # Parse Arguments
    parser = argparse.ArgumentParser(description="Command line script to check for airplanes with a given registration.")
    parser.add_argument('--config', dest='configfile', default='%s/config.json' % pwd,
                        help='Config file to use (default is config.json)')
    arguments = vars(parser.parse_args())
    logging.info("config file is:" + arguments['configfile'])
    # Load Settings
    try:
        with open(arguments['configfile']) as json_file:
            settings = json.load(json_file)

            # merge args into settings IF they're True
            for key, val in arguments.items():
                if not arguments.get(key): continue
                settings[key] = val

            settings['configfile'] = arguments['configfile']
            _check_settings(settings)
    except Exception as e:
        logging.error('Error loading settings from config.json file: %s' % e)
        sys.exit()

    # Configure File Logging
    if settings.get('logfile'):
        handler = logging.FileHandler('%s/%s' % (pwd, settings.get('logfile')))
        handler.setFormatter(logging.Formatter('%(levelname)s: %(asctime)s %(message)s'))
        handler.setLevel(logging.DEBUG)
        logging.getLogger('').addHandler(handler)

    # Configur Push Bullet
    pb = Pushbullet(settings['pushbullet_api_key'])

    logging.debug('Running job with arguments: %s' % arguments)

    while True:
        main(settings)
        time.sleep(120)

