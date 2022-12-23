#!/usr/bin/env python

import OPi.GPIO as GPIO
import telegram
import os.path
import logging as log
from time import sleep
import config
import datetime

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


def format_time_delta(delta):
    text = []
    if delta.days == 1:
        text.append('один день')
    elif delta.days > 1 and delta.days <= 4:
        text.append(f'{delta.days} дні')
    elif delta.days > 4:
        text.append(f'{delta.days} днів')

    h, rem = divmod(delta.seconds, 3600)
    m, sec = divmod(rem, 60)
    if h == 1:
        text.append('одну годину')
    elif h > 1 and h <= 4:
        text.append(f'{h} години')
    elif h > 4:
        text.append(f'{h} годин')

    if m == 1:
        text.append('одну хвилину')
    elif m > 1 and m <= 4:
        text.append(f'{m} хвилини')
    else:
        text.append(f'{m} хвилин')
    return ', '.join(text)


def save_state(state):
    with open(STORE_STATE_FILE, 'w') as f:
        f.write('1' if state else '0')


def get_line_state():
    value = GPIO.input(LINE_SENSE_PIN)
    return value == 0


def notify(bot, online, delta=None):
    log.info(f'Sending notification, online={online}')
    try:
        msg = '✅ Електропостачання відновлено' if online else '❌ Відключено електропостачання'
        if delta is not None:
            msg += '\n'
            msg += 'Світла не було ' if online else 'Світло було '
            msg += format_time_delta(delta)
        bot.sendMessage(chat_id=config.chat_id, text=msg)
        return True
    except Exception:
        log.error('Failed to send telegram notification')
        return False


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
        save_state(online)
        notify(bot, online)
    else:
        if online != last_state:
            log.info('State has changed since the last time')
            delta = get_time_since_last_state()
            save_state(online)
            notify(bot, online, delta)

    last_state = online
    while True:
        while (online := get_line_state()) == last_state:
            sleep(1)
        log.info(f'State has changed, online={online}')
        if online != last_state:
            log.info('State has changed')
            delta = get_time_since_last_state()
            save_state(online)
            for i in range(60):
                if notify(bot, online, delta):
                    break
                sleep(1)
                log.info(f'Retrying sending notification {i}')
        last_state = online
        sleep(1)        # to prevent fast state changes


if __name__ == "__main__":
    log.basicConfig(level=log.DEBUG)
    main()
