#!/usr/bin/env python
import unittest
import schedule
from datetime import datetime


class TestSchedule(unittest.TestCase):
    def test_get_rounded_time(self):
        self.assertEqual(schedule._get_rounded_time(datetime(2023, 1, 25, 2, 30, 22, 11)),
                         None)
        self.assertEqual(schedule._get_rounded_time(datetime(2023, 1, 25, 2, 40, 22, 11)),
                         datetime(2023, 1, 25, 3, 0, 0, 0))
        self.assertEqual(schedule._get_rounded_time(datetime(2023, 1, 25, 23, 43, 22, 11)),
                         datetime(2023, 1, 26, 0, 0, 0, 0))
        self.assertEqual(schedule._get_rounded_time(datetime(2023, 1, 25, 23, 19, 22, 11)),
                         datetime(2023, 1, 25, 23, 0, 0, 0))
        self.assertEqual(schedule._get_rounded_time(datetime(2023, 1, 31, 23, 55, 22, 11)),
                         datetime(2023, 2, 1, 0, 0, 0, 0))
        self.assertEqual(schedule._get_rounded_time(datetime(2023, 1, 31, 23, 00, 22, 11)),
                         datetime(2023, 1, 31, 23, 0, 0, 0))
        self.assertEqual(schedule._get_rounded_time(datetime(2023, 1, 31, 23, 26, 22, 11)),
                         None)
        self.assertEqual(schedule._get_rounded_time(datetime(2023, 1, 31, 23, 34, 22, 11)),
                         None)

    def test_get_next_switch(self):
        r = schedule._get_next_switch(True, 0, 0)
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0], 6)

        r = schedule._get_next_switch(False, 0, 0)
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0], 3)

        r = schedule._get_next_switch(True, 0, 3)
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0], 3)

        r = schedule._get_next_switch(False, 0, 6)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0], 3)
        self.assertEqual(r[1], 6)

        r = schedule._get_next_switch(True, 0, 18)
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0], 6)

        r = schedule._get_next_switch(True, 3, 18)
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0], 6)

        r = schedule._get_next_switch(False, 5, 12)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0], 3)
        self.assertEqual(r[1], 6)

        r = schedule._get_next_switch(False, 6, 6)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0], 3)
        self.assertEqual(r[1], 6)

        r = schedule._get_next_switch(True, 6, 12)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0], 3)
        self.assertEqual(r[1], 9)

        r = schedule._get_next_switch(True, 6, 9)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0], 6)
        self.assertEqual(r[1], 12)

        r = schedule._get_next_switch(False, 6, 21)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0], 3)
        self.assertEqual(r[1], 6)

        r = schedule._get_next_switch(False, 2, 12)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0], 3)
        self.assertEqual(r[1], 6)

    def test_get_schedule_info(self):
        print(schedule.get_schedule_info(datetime(2023, 1, 25, 12, 11, 22, 11), False))
        print(schedule.get_schedule_info(datetime(2023, 1, 25, 5, 45, 22, 11), True))
        print(schedule.get_schedule_info(datetime(2023, 1, 22, 8, 45, 22, 11), True))
        print(schedule.get_schedule_info(datetime(2023, 1, 21, 20, 45, 22, 11), False))
        print(schedule.get_schedule_info(datetime(2023, 1, 25, 17, 45, 22, 11), True))
        print(schedule.get_schedule_info(datetime(2023, 1, 25, 20, 55, 22, 11), False))

    def test_get_scheduled_switches(self):
        time, switch = schedule._get_scheduled_switches(datetime(2023, 1, 25, 12, 35, 22, 11), False)
        self.assertEqual(time, None)
        self.assertEqual(switch, None)

        time, switch = schedule._get_scheduled_switches(datetime(2023, 1, 25, 11, 11, 22, 11), False)
        self.assertEqual(time, None)
        self.assertEqual(switch, None)

        time, switch = schedule._get_scheduled_switches(datetime(2023, 1, 25, 3, 11, 22, 11), True)
        self.assertEqual(time, None)
        self.assertEqual(switch, None)

        time, switch = schedule._get_scheduled_switches(datetime(2023, 1, 25, 5, 11, 22, 11), False)
        self.assertEqual(time, None)
        self.assertEqual(switch, None)

        time, switch = schedule._get_scheduled_switches(datetime(2023, 1, 22, 0, 11, 22, 11), True)
        self.assertNotEqual(time, None)
        self.assertEqual(switch[0], 6)

        time, switch = schedule._get_scheduled_switches(datetime(2023, 1, 22, 8, 45, 22, 11), True)
        self.assertNotEqual(time, None)
        self.assertEqual(switch[0], 6)
        self.assertEqual(switch[1], 12)

    def test_get_timetable_switch_state(self):
        self.assertEqual(schedule._get_timetable_switch_state(datetime(2023, 1, 23, 0, 0, 0, 0)), '_')
        self.assertEqual(schedule._get_timetable_switch_state(datetime(2023, 1, 23, 1, 0, 0, 0)), None)
        self.assertEqual(schedule._get_timetable_switch_state(datetime(2023, 1, 23, 2, 0, 0, 0)), None)
        self.assertEqual(schedule._get_timetable_switch_state(datetime(2023, 1, 23, 3, 0, 0, 0)), ' ')
        self.assertEqual(schedule._get_timetable_switch_state(datetime(2023, 1, 23, 3, 0, 0, 0)), ' ')
        self.assertEqual(schedule._get_timetable_switch_state(datetime(2023, 1, 23, 6, 0, 0, 0)), 'x')
        self.assertEqual(schedule._get_timetable_switch_state(datetime(2023, 1, 23, 7, 0, 0, 0)), None)
        self.assertEqual(schedule._get_timetable_switch_state(datetime(2023, 1, 22, 0, 0, 0, 0)), '_')
        self.assertEqual(schedule._get_timetable_switch_state(datetime(2023, 1, 22, 15, 0, 0, 0)), '_')
