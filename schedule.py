#!/usr/bin/env python

from datetime import timedelta, datetime
from time_utils import make_hour_text
import logging as log

_timetable = {0: '___   xxx___   xxx___   ',
              1: 'xxx___   xxx___   xxx___',
              2: '   xxx___   xxx___   xxx',
              3: '___   xxx___   xxx___   ',
              4: 'xxx___   xxx___   xxx___',
              5: '   xxx___   xxx___   xxx',
              6: '___   xxx___   ___   xxx'}

_delta_error = timedelta(minutes=20)


def _get_rounded_time(time):
    """Round to the closest hour using margin of 25 minutes"""
    t = None
    if time.minute >= 35:
        t = time + timedelta(minutes=(60-time.minute))
        t = datetime(t.year, t.month, t.day, t.hour)
    elif time.minute <= 25:
        t = datetime(time.year, time.month, time.day, time.hour)
    return t


def _get_next_switch(current_online, day, hour):
    next_switch = []
    flat_timetable = ''.join([_timetable[i] for i in range(7)])
    flat_h = day * 24 + hour
    prev_state = flat_timetable[flat_h]
    for i in range(1, 24*7):
        h = (flat_h + i) % (24*7)
        if current_online:      # looking for next ('_' and 'x') or just 'x'
            if flat_timetable[h] == 'x':
                next_switch.append(i)
                break
            if flat_timetable[h] == '_' and prev_state != '_':
                next_switch.append(i)
            prev_state = flat_timetable[h]
        else:       # looking for next '_' or ' '
            if flat_timetable[h] == ' ':
                next_switch.append(i)
                break
            if flat_timetable[h] == '_' and prev_state != '_':
                next_switch.append(i)
                prev_state = '_'
    return next_switch


def get_schedule_info(time, to_online):
    time, next_switches = _get_scheduled_switches(time, to_online)
    if not next_switches:
        return None
    next_times = [time + timedelta(hours=h) for h in next_switches]
    next_times = [t.strftime("%-H:%M") for t in next_times]
    next_periods = [make_hour_text(h) for h in next_switches]
    lines = []
    if to_online:
        lines.append('\nЧас включення збігається з графіком.\n')
        lines.append(f'\nℹ️ Наступне відключення в {next_times[0]}, через {next_periods[0]}.')
        if len(next_switches) == 2:
            lines.append(f' Або в {next_times[1]}, через {next_periods[1]}.')
    else:
        lines.append('\nЧас відключення збігається з графіком.\n')
        lines.append(f'\nℹ️ Наступне включення в {next_times[0]}, через {next_periods[0]}.')
        if len(next_switches) == 2:
            lines.append(f' Або в {next_times[1]}, через {next_periods[1]}.')
    return ''.join(lines)


def _get_timetable_switch_state(time):
    day = time.weekday()
    hour = time.hour
    prev_day = day
    prev_hour = hour - 1
    if prev_hour < 0:
        if prev_day == 0:
            prev_day = 6
        else:
            prev_day -= 1
        prev_hour = 23
    state = _timetable[day][hour]
    prev_state = _timetable[prev_day][prev_hour]
    if state != prev_state:
        return state
    return None


def _get_scheduled_switches(time, to_online):
    time = _get_rounded_time(time)
    if time is None:
        log.warning('Time can not be rounded')
        return (None, None)
    state = _get_timetable_switch_state(time)
    if state is None:
        log.info('No distinct state swich in the timetable')
        return (None, None)
    next_switches = None
    if to_online and (state == ' ' or state == '_'):
        log.info('Switching to online timetable match')
        next_switches = _get_next_switch(True, time.weekday(), time.hour)
    elif (not to_online) and (state == 'x' or state == '_'):
        log.info('Switching to offline timetable match')
        next_switches = _get_next_switch(False, time.weekday(), time.hour)
    if not next_switches:
        log.warning('Failed to determine next switch time')
        return (None, None)
    return (time, next_switches)
