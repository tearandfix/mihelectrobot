#!/usr/bin/env python

import OPi.GPIO as GPIO
import telegram
import os.path
import logging as log
from time import sleep
import config
import datetime
import sys

LINE_SENSE_PIN = 7
STORE_STATE_FILE = '/var/mihelectro_state'


def get_last_state():
    if not os.path.isfile(STORE_STATE_FILE):
        log.info('Storage file does not exist')
        return None
    with open(STORE_STATE_FILE, 'r') as f:
        data = f.read()
        if not data:
            log.info('Storage file is empty')
            return None
        if data == '1':
            log.info('Stored online')
            return True
        elif data == '0':
            log.info('Stored offline')
            return False
        else:
            log.info('Invalid data')
            return None


def get_time_since_last_state():
    if not os.path.isfile(STORE_STATE_FILE):
        log.info('Storage file does not exist')
        return None
    mtime = datetime.datetime.fromtimestamp(os.path.getmtime(STORE_STATE_FILE))
    log.info(f'Last state changed: {mtime}')
    delta = datetime.datetime.now() - mtime
    log.info(f'Time difference: {delta}')
    return delta


def make_time_number(n, text1, text2, text3):
    """Make linguistically correct time string from the provided number and text forms
    """
    def parse_digit(d, n):
        if d == 0:
            return f'{n} {text3}'
        elif d == 1:
            return f'{n} {text1}'
        elif d > 1 and d < 5:
            return f'{n} {text2}'
        else:
            return f'{n} {text3}'
    if n < 21:
        return parse_digit(n, n)
    else:
        return parse_digit(n % 10, n)


def format_time_delta(delta):
    """Make textual time delta representation
    """
    text = []
    if delta.days:
        text.append(make_time_number(delta.days, 'день', 'дні', 'днів'))
    h, rem = divmod(delta.seconds, 3600)
    m, sec = divmod(rem, 60)
    if h or delta.days:     # also include hours if days are present
        text.append(make_time_number(h, 'годину', 'години', 'годин'))
    text.append(make_time_number(m, 'хвилину', 'хвилини', 'хвилин'))
    return ', '.join(text)


def save_state(state):
    with open(STORE_STATE_FILE, 'w') as f:
        f.write('1' if state else '0')


def get_line_state():
    value = GPIO.input(LINE_SENSE_PIN)
    return value == 0


def send_notification(bot, online, delta=None):
    log.info(f'Sending notification, online={online}')
    try:
        msg = '✅ Електропостачання відновлено' if online else '❌ Відключено електропостачання'
        if delta is not None:
            msg += '.\n'
            msg += 'Світла не було ' if online else 'Світло було '
            msg += format_time_delta(delta) + '.'
        bot.sendMessage(chat_id=config.chat_id, text=msg)
        return True
    except Exception:
        log.error('Failed to send telegram notification')
        return False


def notify(bot, online, delta=None):
    for i in range(150):        # 5 minutes retries
        if send_notification(bot, online, delta):
            save_state(online)
            break
        sleep(2)
        log.info(f'Retrying sending notification {i}')
    else:
        log.error('Failed to send notification. Terminating')
        sys.exit(1)


def wait_state_change(last_state):
    while True:
        online = get_line_state()
        if online != last_state:
            stabilize_count = 5
            for i in range(stabilize_count):
                if online == get_line_state():
                    stabilize_count -= 1
                sleep(1)
            if stabilize_count != 0:
                log.warn('State is not stable')
                continue
            log.info('State is stable')
            return online
        sleep(2)


def main():
    log.info('GPIO initialization')
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(LINE_SENSE_PIN, GPIO.IN)

    log.info('Telegram bot initialization')
    bot = telegram.Bot(token=config.bot_token)

    online = get_line_state()

    last_state = get_last_state()
    if last_state is None:
        log.info('No last state information')
        notify(bot, online)
    else:
        if online != last_state:
            log.info('State has changed since the last time')
            delta = get_time_since_last_state()
            notify(bot, online, delta)

    last_state = online
    while True:
        online = wait_state_change(last_state)
        log.info(f'State has changed, online={online}')
        if online != last_state:
            log.info('State has changed')
            delta = get_time_since_last_state()
            notify(bot, online, delta)
        last_state = online
        sleep(1)        # to prevent fast state changes


if __name__ == "__main__":
    log.basicConfig(level=log.DEBUG)
    main()
