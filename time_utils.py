#!/usr/bin/env python


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


def make_day_text(days):
    return make_time_number(days, 'день', 'дні', 'днів')


def make_hour_text(hours):
    return make_time_number(hours, 'годину', 'години', 'годин')


def format_time_delta(delta):
    """Make textual time delta representation
    """
    text = []
    if delta.days:
        text.append(make_day_text(delta.days))
    h, rem = divmod(delta.seconds, 3600)
    m, sec = divmod(rem, 60)
    if h or delta.days:     # also include hours if days are present
        text.append(make_hour_text(h))
    text.append(make_time_number(m, 'хвилину', 'хвилини', 'хвилин'))
    return ', '.join(text)
