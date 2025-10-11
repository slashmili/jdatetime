import datetime
import locale
import pickle
import platform
import sys
import threading
import time
from unittest import TestCase, skipIf, skipUnless
from zoneinfo import ZoneInfo

import jdatetime

try:
    import greenlet

    greenlet_installed = True
except ImportError:
    greenlet_installed = False

from tests import load_pickle


class GMTTime(jdatetime.tzinfo):
    def utcoffset(self, dt):
        return jdatetime.timedelta(hours=0)

    def tzname(self, dt):
        return 'GMT'

    def dst(self, dt):
        return jdatetime.timedelta(0)


class TehranTime(jdatetime.tzinfo):
    def utcoffset(self, dt):
        return jdatetime.timedelta(hours=3, minutes=30)

    def tzname(self, dt):
        return 'IRDT'

    def dst(self, dt):
        return jdatetime.timedelta(0)


class TestJDateTime(TestCase):
    def test_datetime_date_method_keeps_datetime_locale_on_date_instance(self):
        datetime = jdatetime.datetime(1397, 4, 22, locale='nl_NL')
        date = datetime.date()
        self.assertEqual(date.locale, 'nl_NL')

    def test_init_locale_is_effective_only_if_not_none(self):
        orig_locale = jdatetime.get_locale()
        jdatetime.set_locale('en_US')
        self.addCleanup(jdatetime.set_locale, orig_locale)
        datetime = jdatetime.datetime(1397, 4, 22, locale=None)
        self.assertEqual(datetime.locale, 'en_US')

    def test_init_locale_is_effective_only_if_not_empty(self):
        orig_locale = jdatetime.get_locale()
        jdatetime.set_locale('nl_NL')
        self.addCleanup(jdatetime.set_locale, orig_locale)
        datetime = jdatetime.datetime(1397, 4, 22, locale='')
        self.assertEqual(datetime.locale, 'nl_NL')

    def test_locale_property_is_read_only(self):
        datetime = jdatetime.datetime(1397, 4, 22)
        with self.assertRaises(AttributeError):
            datetime.locale = jdatetime.FA_LOCALE

    def test_fold(self):
        # Test default value
        dt = jdatetime.datetime(1400, 11, 22)
        self.assertEqual(dt.fold, 0)
        self.assertEqual(dt.time().fold, 0)

        # Test custome value for fold
        dt = jdatetime.datetime(1400, 11, 22, fold=1)
        self.assertEqual(dt.fold, 1)
        self.assertEqual(dt.time().fold, 1)

        # Test invalid value for fold
        with self.assertRaises(ValueError, msg='fold must be either 0 or 1'):
            jdatetime.datetime(1400, 11, 22, fold=2)

        # Test combine
        t = jdatetime.time(12, 13, 14, fold=1)
        d = jdatetime.date(1400, 11, 22)
        self.assertEqual(
            jdatetime.datetime.combine(d, t),
            jdatetime.datetime(1400, 11, 22, 12, 13, 14, fold=1),
        )

        # Test replace
        dt = jdatetime.datetime(1400, 11, 22, fold=0)
        new_dt = dt.replace(fold=1)
        self.assertEqual(new_dt.fold, 1)

    def test_locale_property_returns_locale(self):
        datetime = jdatetime.datetime(1397, 4, 22, locale='nl_NL')
        self.assertEqual(datetime.locale, 'nl_NL')

    def test_init_locale_is_named_argument_only(self):
        with self.assertRaises(TypeError):
            datetime.datetime(1397, 4, 22, 'nl_NL')

    def test_init_accepts_instance_locale(self):
        datetime = jdatetime.datetime(1397, 4, 23, locale=jdatetime.FA_LOCALE)
        self.assertEqual(datetime.strftime('%A'), 'شنبه')

    def test_today(self):
        today = datetime.date.today()
        converted_today = jdatetime.date.today().togregorian()
        self.assertEqual(today.year, converted_today.year)

    def test_fromtimestamp(self):
        d = jdatetime.date.fromtimestamp(1783232224)
        self.assertEqual(1405, d.year)
        self.assertEqual(4, d.month)
        self.assertEqual(14, d.day)

    def test_fromordinal(self):
        d = jdatetime.date.fromordinal(1)
        self.assertEqual(1, d.year)

    def test_comparison(self):
        today = jdatetime.date.today()
        self.assertFalse(today < today - jdatetime.timedelta(days=76))
        self.assertFalse(today <= today - jdatetime.timedelta(days=1))
        self.assertTrue(today + jdatetime.timedelta(days=1) > today)
        self.assertTrue(today + jdatetime.timedelta(days=30) >= today)
        self.assertTrue(today == today)
        self.assertFalse(today > today)
        self.assertFalse(today < today)
        self.assertTrue(today >= today)
        self.assertTrue(today <= today)
        not_today = jdatetime.date(today.year, today.month, today.day) + jdatetime.timedelta(days=1)
        self.assertTrue(today != not_today)

        dtg = jdatetime.datetime(1380, 12, 1, 1, 2, 4)
        self.assertTrue(dtg < dtg + jdatetime.timedelta(seconds=1))
        self.assertTrue(dtg - jdatetime.timedelta(seconds=1) < dtg)
        self.assertFalse(dtg is None)

    def test_date_conversion_date_input(self):
        # todo: add some corner cases
        d1 = datetime.date(2010, 11, 23)
        jd1 = jdatetime.date(1389, 9, 2)
        d2 = datetime.date(2011, 5, 13)
        jd2 = jdatetime.date(1390, 2, 23)

        self.assertEqual(d1, jd1.togregorian())
        self.assertEqual(d2, jd2.togregorian())
        self.assertEqual(jd1, jdatetime.date.fromgregorian(date=d1))
        self.assertEqual(jd2, jdatetime.date.fromgregorian(date=d2))

    def test_date_conversion_integer_input(self):
        d_check_with = jdatetime.date(1390, 2, 23)
        jd_datetime = jdatetime.datetime.fromgregorian(
            year=2011,
            month=5,
            day=13,
            hour=14,
            minute=15,
            second=16,
        )
        self.assertEqual(
            True,
            jd_datetime == jdatetime.datetime.combine(d_check_with, jdatetime.time(14, 15, 16)),
        )

        gdatetime = datetime.datetime(2011, 5, 13, 14, 15, 16)
        self.assertEqual(jd_datetime.togregorian(), gdatetime)

    def test_strftime(self):
        s = jdatetime.date(1390, 2, 23)
        string_format = '%a %A %b %B %c %d %H %I %j %m %M %p %S %w %W %x %X %y %Y %f %z %Z'
        output = (
            'Fri Friday Ord Ordibehesht Fri Ord 23 00:00:00 '
            '1390 23 00 12 054 02 00 AM 00 6 8 02/23/90 00:00:00 90 1390 000000  '
        )
        self.assertEqual(s.strftime(string_format), output)

        dt = jdatetime.datetime(1390, 2, 23, 12, 13, 14, 1)
        unicode_format = '%a %A %b %B %c %d %H %I %j %m %M %p %S %w %W %x %X %y %Y %f'
        output = (
            'Fri Friday Ord Ordibehesht Fri Ord 23 12:13:14 '
            '1390 23 12 12 054 02 13 PM 14 6 8 02/23/90 12:13:14 90 1390 000001'
        )
        self.assertEqual(dt.strftime(unicode_format), output)

        dt = jdatetime.datetime(1390, 2, 23, 12, 13, 14, 1)
        string_format = 'ﺱﺎﻟ = %y، ﻡﺎﻫ = %m، ﺭﻭﺯ = %d'
        output = 'ﺱﺎﻟ = 90، ﻡﺎﻫ = 02، ﺭﻭﺯ = 23'
        self.assertEqual(dt.strftime(string_format), output)

        class NYCTime(jdatetime.tzinfo):
            def utcoffset(self, dt):
                return jdatetime.timedelta(hours=-4)

            def tzname(self, dt):
                return 'EDT'

            def dst(self, dt):
                return jdatetime.timedelta(0)

        nyc = NYCTime()
        dt = jdatetime.datetime(1389, 2, 17, 19, 10, 2, tzinfo=nyc)
        self.assertEqual(dt.strftime('%Z %z'), 'EDT -0400')

        teh = TehranTime()
        dt = jdatetime.datetime(1389, 2, 17, 19, 10, 2, tzinfo=teh)
        self.assertEqual(dt.strftime('%Z %z'), 'IRDT +0330')

    def test_strftime_unicode(self):
        s = jdatetime.date(1390, 2, 23)
        self.assertEqual(s.strftime(b'%a %A'), 'Fri Friday')

    def test_strftime_single_digit(self):
        dt = jdatetime.datetime(1390, 2, 3, 4, 5, 6)
        self.assertEqual(
            dt.strftime('%-m %m %-d %d %-H %H %-M %M %-S %S'),
            '2 02 3 03 4 04 5 05 6 06',
        )

    def test_strftime_escape_percent(self):
        dt = jdatetime.datetime(1402, 1, 7)
        self.assertEqual(dt.strftime('%%x=%x'), '%x=01/07/02')
        self.assertEqual(dt.strftime('%%d=%d'), '%d=07')
        self.assertEqual(dt.strftime('%%%d'), '%07')

    def test_strftime_unknown_directive(self):
        self.assertEqual(jdatetime.date.today().strftime('%Q'), '%Q')

    def test_kabiseh(self):
        kabiseh_year = jdatetime.date.fromgregorian(date=datetime.date(2013, 3, 20))
        self.assertTrue(kabiseh_year.isleap())

        normal_year = jdatetime.date.fromgregorian(date=datetime.date(2014, 3, 20))
        self.assertFalse(normal_year.isleap())

        kabiseh_year = jdatetime.date(1391, 12, 30)
        self.assertTrue(kabiseh_year.isleap())

        with self.assertRaises(ValueError):
            jdatetime.date(1392, 12, 30)

    def test_datetime(self):
        d = jdatetime.datetime(1390, 1, 2, 12, 13, 14)

        self.assertEqual(d.time(), jdatetime.time(12, 13, 14))
        self.assertEqual(d.date(), jdatetime.date(1390, 1, 2))

    def test_datetimetoday(self):
        jnow = jdatetime.datetime.today()
        today = datetime.datetime.today().date()
        gnow = jdatetime.date.fromgregorian(date=today)

        self.assertEqual(jnow.date(), gnow)

    def test_datetimefromtimestamp(self):
        t = time.time()
        jnow = jdatetime.datetime.fromtimestamp(t).date()
        gnow = datetime.datetime.fromtimestamp(t).date()

        self.assertEqual(jdatetime.date.fromgregorian(date=gnow), jnow)

    def test_combine(self):
        t = jdatetime.time(12, 13, 14)
        d = jdatetime.date(1390, 4, 5)
        dt = jdatetime.datetime(1390, 4, 5, 12, 13, 14)

        self.assertEqual(jdatetime.datetime.combine(d, t), dt)

    def test_combine_keeps_date_locale(self):
        t = jdatetime.time(11, 20, 30)
        d = jdatetime.date(1397, 4, 24, locale='nl_NL')
        self.assertEqual(jdatetime.datetime.combine(d, t).locale, 'nl_NL')

    def test_replace(self):
        dt = jdatetime.datetime.today()
        args = {
            'year': 1390,
            'month': 12,
            'day': 1,
            'hour': 13,
            'minute': 14,
            'second': 15,
            'microsecond': 1233,
        }
        dtr = dt.replace(**args)
        dtn = jdatetime.datetime(1390, 12, 1, 13, 14, 15, 1233)

        self.assertEqual(dtr, dtn)

    def test_replace_keeps_date_locale(self):
        dt = jdatetime.datetime(1397, 4, 24, locale='nl_NL')
        args = {'year': 1390, 'month': 12, 'hour': 13}
        self.assertEqual(dt.replace(**args).locale, 'nl_NL')

    def test_replace_remove_tzinfo(self):
        teh = TehranTime()
        dt = jdatetime.datetime(1397, 8, 17, 7, 54, 28, tzinfo=teh)
        dt_naive = dt.replace(tzinfo=None)
        self.assertEqual(dt_naive.tzinfo, None)

    def test_strptime(self):
        date_string = '1363-6-6 12:13:14'
        date_format = '%Y-%m-%d %H:%M:%S'
        dt1 = jdatetime.datetime.strptime(date_string, date_format)
        dt2 = jdatetime.datetime(1363, 6, 6, 12, 13, 14)

        self.assertEqual(dt1, dt2)

    def test_strptime_bare(self):
        date_string = '13630606121314'
        date_format = '%Y%m%d%H%M%S'
        dt1 = jdatetime.datetime.strptime(date_string, date_format)
        dt2 = jdatetime.datetime(1363, 6, 6, 12, 13, 14)

        self.assertTrue(dt1 == dt2)

    def test_strptime_handles_alphabets_in_format(self):
        date_string = '1363-6-6T12:13:14'
        date_format = '%Y-%m-%dT%H:%M:%S'
        dt1 = jdatetime.datetime.strptime(date_string, date_format)
        dt2 = jdatetime.datetime(1363, 6, 6, 12, 13, 14)

        self.assertEqual(dt1, dt2)

    def test_strptime_special_chars(self):
        date_string = '[1363*6*6] ? (12+13+14)'
        date_format = '[%Y*%m*%d] ? (%H+%M+%S)'
        dt1 = jdatetime.datetime.strptime(date_string, date_format)
        dt2 = jdatetime.datetime(1363, 6, 6, 12, 13, 14)

        self.assertEqual(dt1, dt2)

    def test_strptime_small_y(self):
        self.assertEqual(
            jdatetime.datetime(1468, 1, 1),
            jdatetime.datetime.strptime('68/1/1', '%y/%m/%d'),
        )
        self.assertEqual(
            jdatetime.datetime(1369, 1, 1),
            jdatetime.datetime.strptime('69/1/1', '%y/%m/%d'),
        )

    def test_strptime_do_not_match_excessive_characters(self):
        with self.assertRaises(ValueError, msg='%y should not match the trailing space character'):
            jdatetime.datetime.strptime('21 ', '%y')

    def test_strptime_nanoseconds(self):
        self.assertEqual(
            jdatetime.datetime(1279, 1, 1, 0, 0, 0, 700000),
            jdatetime.datetime.strptime('7', '%f'),
        )
        self.assertEqual(
            jdatetime.datetime(1279, 1, 1, 0, 0, 0, 12300),
            jdatetime.datetime.strptime('0123', '%f'),
        )

    def test_strptime_handle_b_B_directive(self):
        tests = [
            ('14 Ordibehesht 1400', '%d %B %Y', (1400, 2, 14)),
            ('14 ordibehesht 1400', '%d %B %Y', (1400, 2, 14)),
            ('14 ordiBehesHt 1400', '%d %B %Y', (1400, 2, 14)),
            ('۱۴ Ordibehesht ۱۴۰۰', '%d %B %Y', (1400, 2, 14)),
            ('۱۴ ordibehesht ۱۴۰۰', '%d %B %Y', (1400, 2, 14)),
            ('۱۴ orDibeHesht ۱۴۰۰', '%d %B %Y', (1400, 2, 14)),
            ('1۴ Ordibehesht 14۰۰', '%d %B %Y', (1400, 2, 14)),
            ('۱4 ordibehesht 14۰0', '%d %B %Y', (1400, 2, 14)),
            ('۱4 OrdiBeheshT 14۰0', '%d %B %Y', (1400, 2, 14)),
            ('۱۴ اردیبهشت ۱۴۰۰', '%d %B %Y', (1400, 2, 14)),
            ('14 اردیبهشت 1400', '%d %B %Y', (1400, 2, 14)),
            ('1۴ اردیبهشت ۱4۰0', '%d %B %Y', (1400, 2, 14)),
            ('14 Ord 1400', '%d %b %Y', (1400, 2, 14)),
            ('14 ord 1400', '%d %b %Y', (1400, 2, 14)),
            ('14 oRD 1400', '%d %b %Y', (1400, 2, 14)),
            ('۱۴ Ord ۱۴۰۰', '%d %b %Y', (1400, 2, 14)),
            ('۱۴ ord ۱۴۰۰', '%d %b %Y', (1400, 2, 14)),
            ('۱۴ OrD ۱۴۰۰', '%d %b %Y', (1400, 2, 14)),
            ('۱4 Ord 14۰0', '%d %b %Y', (1400, 2, 14)),
            ('۱4 ord 14۰0', '%d %b %Y', (1400, 2, 14)),
            ('۱4 ORD 14۰0', '%d %b %Y', (1400, 2, 14)),
            ('۱۴ دی ۱۴۰۰', '%d %B %Y', (1400, 10, 14)),
            ('۱۴ dey ۱۴۰۰', '%d %b %Y', (1400, 10, 14)),
        ]
        for date_string, date_format, expected_date in tests:
            with self.subTest(date_string=date_string, date_format=date_format):
                date = jdatetime.datetime.strptime(date_string, date_format)
                self.assertEqual(jdatetime.datetime(*expected_date), date)

    def test_strptime_invalid_date_string_b_directive(self):
        with self.assertRaises(ValueError, msg="time data '14 DRO 1400' does not match format '%d %b %Y'"):
            jdatetime.datetime.strptime('14 DRO 1400', '%d %b %Y')

    def test_strptime_invalid_date_string_B_directive(self):
        with self.assertRaises(ValueError, msg="time data '14 ordi 1400' does not match format '%d %B %Y'"):
            jdatetime.datetime.strptime('14 ordi 1400', '%d %B %Y')

    def test_strptime_handle_z_directive(self):
        tests = [
            ('+0123', '%z', datetime.timedelta(seconds=4980)),
            ('-0123', '%z', datetime.timedelta(seconds=-4980)),
            ('+۰۱۲۳', '%z', datetime.timedelta(seconds=4980)),
            ('-۰۱۲3', '%z', datetime.timedelta(seconds=-4980)),
            ('+012345', '%z', datetime.timedelta(seconds=5025)),
            ('+012345.012345', '%z', datetime.timedelta(seconds=5025, microseconds=12345)),
            ('-012345.012345', '%z', datetime.timedelta(seconds=-5025, microseconds=-12345)),
            ('+01:23', '%z', datetime.timedelta(seconds=4980)),
            ('+01:23:45', '%z', datetime.timedelta(seconds=5025)),
            ('+01:23:45.123', '%z', datetime.timedelta(seconds=5025, microseconds=123000)),
        ]
        for date_string, date_format, time_delta in tests:
            with self.subTest(date_string=date_string, date_format=date_format):
                date = jdatetime.datetime.strptime(date_string, date_format)
                self.assertEqual(datetime.timezone(time_delta), date.tzinfo)

    def test_strptime_invalid_date_string_z_directive(self):
        tests = [
            ('0123', '%z', "time data '0123' does not match format '%z'"),
            ('-01', '%z', "time data '-01' does not match format '%z'"),
            ('+012', '%z', "time data '+012' does not match format '%z'"),
            ('+01:2356', '%z', 'Inconsistent use of : in -01:2356'),
            ('+0123:56', '%z', "invalid literal for int() with base 10: ':5'"),
            ('+012345123456', '%z', "time data '+012345123456' does not match format '%z'"),
        ]
        for date_string, date_format, msg in tests:
            with self.subTest(date_string=date_string, date_format=date_format, msg=msg):
                with self.assertRaises(ValueError, msg=msg):
                    jdatetime.datetime.strptime(date_string, date_format)

    def test_strptime_A_p_j_directives(self):
        dt = jdatetime.datetime(1401, 2, 3, 4)
        fmt = '%Y %m %d %H %j %p %A %a'
        self.assertEqual(
            jdatetime.datetime.strptime(dt.strftime(fmt), fmt),
            dt,
        )

    def test_timetz(self):
        teh = TehranTime()

        dt_gmt = datetime.datetime(2015, 6, 27, 1, 2, 3, tzinfo=teh)
        self.assertEqual('01:02:03+03:30', dt_gmt.timetz().__str__())

    def test_fromgregorian_accepts_named_argument_of_date_and_locale(self):
        gd = datetime.date(2018, 7, 14)
        jdt = jdatetime.datetime.fromgregorian(date=gd, locale='nl_NL')
        self.assertEqual(jdt.year, 1397)
        self.assertEqual(jdt.month, 4)
        self.assertEqual(jdt.day, 23)
        self.assertEqual(jdt.locale, 'nl_NL')

    def test_fromgregorian_accepts_named_argument_of_datetime_and_locale(self):
        gdt = datetime.datetime(2018, 7, 15, 11, 7, 0)
        jdt = jdatetime.datetime.fromgregorian(datetime=gdt, locale='nl_NL')
        self.assertEqual(jdt.year, 1397)
        self.assertEqual(jdt.month, 4)
        self.assertEqual(jdt.day, 24)
        self.assertEqual(jdt.hour, 11)
        self.assertEqual(jdt.minute, 7)
        self.assertEqual(jdt.locale, 'nl_NL')

    def test_fromgregorian_accepts_named_argument_of_date_with_date_input(
        self,
    ):
        gdt = datetime.date(2018, 7, 15)
        jdt = jdatetime.datetime.fromgregorian(date=gdt, locale='nl_NL')
        self.assertEqual(jdt.year, 1397)
        self.assertEqual(jdt.month, 4)
        self.assertEqual(jdt.day, 24)
        self.assertEqual(jdt.hour, 0)
        self.assertEqual(jdt.minute, 0)
        self.assertEqual(jdt.locale, 'nl_NL')

    def test_fromgregorian_accepts_named_argument_of_date_with_datetime_input(
        self,
    ):
        gdt = datetime.datetime(2018, 7, 15, 11, 7, 0)
        jdt = jdatetime.datetime.fromgregorian(date=gdt, locale='nl_NL')
        self.assertEqual(jdt.year, 1397)
        self.assertEqual(jdt.month, 4)
        self.assertEqual(jdt.day, 24)
        self.assertEqual(jdt.hour, 11)
        self.assertEqual(jdt.minute, 7)
        self.assertEqual(jdt.locale, 'nl_NL')

    def test_fromgregorian_accepts_year_month_day_and_locale(self):
        jdt = jdatetime.datetime.fromgregorian(year=2018, month=7, day=15, locale='nl_NL')
        self.assertEqual(jdt.year, 1397)
        self.assertEqual(jdt.month, 4)
        self.assertEqual(jdt.day, 24)
        self.assertEqual(jdt.locale, 'nl_NL')

    def test_datetime_raise_exception_on_invalid_calculation(self):
        date_1395 = jdatetime.datetime(1395, 1, 1)

        with self.assertRaises(TypeError):
            date_1395 - 1

        with self.assertRaises(TypeError):
            date_1395 + 1

        with self.assertRaises(TypeError):
            jdatetime.timedelta(days=1) - date_1395

        with self.assertRaises(TypeError):
            date_1395 + date_1395

    def test_datetime_calculation_on_timedelta(self):
        date_1395 = jdatetime.datetime(1395, 1, 1)
        day_before = date_1395 - jdatetime.timedelta(days=1)
        day_after = date_1395 + jdatetime.timedelta(days=1)

        self.assertEqual(day_before, jdatetime.datetime(1394, 12, 29, 0, 0))
        self.assertEqual(day_after, jdatetime.datetime(1395, 1, 2, 0, 0))

        day_after = jdatetime.timedelta(days=1) + date_1395

        self.assertEqual(day_before, jdatetime.datetime(1394, 12, 29, 0, 0))
        self.assertEqual(day_after, jdatetime.datetime(1395, 1, 2, 0, 0))

    def test_datetime_calculation_on_two_dates(self):
        date_1394 = jdatetime.datetime(1394, 1, 1)
        date_1395 = jdatetime.datetime(1395, 1, 1)

        day_diff = date_1395 - date_1394

        self.assertEqual(day_diff, datetime.timedelta(365))

        day_diff = date_1394 - date_1395

        self.assertEqual(day_diff, datetime.timedelta(-365))

    def test_date_raise_exception_on_invalid_calculation(self):
        date_1395 = jdatetime.date(1395, 1, 1)

        with self.assertRaises(TypeError):
            date_1395 - 1

        with self.assertRaises(TypeError):
            date_1395 + 1

        with self.assertRaises(TypeError):
            jdatetime.timedelta(days=1) - date_1395

        with self.assertRaises(TypeError):
            date_1395 + date_1395

    def test_date_calculation_on_timedelta(self):
        date_1395 = jdatetime.date(1395, 1, 1)
        day_before = date_1395 - jdatetime.timedelta(days=1)
        day_after = date_1395 + jdatetime.timedelta(days=1)

        self.assertEqual(day_before, jdatetime.date(1394, 12, 29))
        self.assertEqual(day_after, jdatetime.date(1395, 1, 2))

        day_after = jdatetime.timedelta(days=1) + date_1395

        self.assertEqual(day_before, jdatetime.date(1394, 12, 29))
        self.assertEqual(day_after, jdatetime.date(1395, 1, 2))

    def test_date_calculation_on_two_dates(self):
        date_1394 = jdatetime.date(1394, 1, 1)
        date_1395 = jdatetime.date(1395, 1, 1)

        day_diff = date_1395 - date_1394

        self.assertEqual(day_diff, datetime.timedelta(365))

        day_diff = date_1394 - date_1395

        self.assertEqual(day_diff, datetime.timedelta(-365))

    def test_add_timedelta_keeps_source_datetime_locale(self):
        jdate = jdatetime.datetime(1397, 4, 23, locale='nl_NL')
        new_jdate = jdate + datetime.timedelta(days=1)
        self.assertEqual(new_jdate.year, 1397)
        self.assertEqual(new_jdate.month, 4)
        self.assertEqual(new_jdate.day, 24)
        self.assertEqual(new_jdate.locale, 'nl_NL')

    def test_subtract_timedelta_keeps_source_datetime_locale(self):
        jdate = jdatetime.datetime(1397, 4, 23, locale='nl_NL')
        new_jdate = jdate - datetime.timedelta(days=1)
        self.assertEqual(new_jdate.year, 1397)
        self.assertEqual(new_jdate.month, 4)
        self.assertEqual(new_jdate.day, 22)
        self.assertEqual(new_jdate.locale, 'nl_NL')

    def test_with_none_locale_set(self):
        self.reset_locale()
        day_of_week = jdatetime.date(1395, 1, 2).strftime('%a')

        self.assertEqual(day_of_week, 'Mon')

    def reset_locale(self):
        if platform.system() == 'Windows':
            locale.setlocale(locale.LC_ALL, 'English_United States')
        else:
            locale.setlocale(locale.LC_ALL, '')

    def test_with_fa_locale(self):
        self.set_fa_locale()
        day_of_week = jdatetime.date(1395, 1, 2).strftime('%a')

        self.assertEqual(day_of_week, 'دوشنبه')

    def set_fa_locale(self):
        if platform.system() == 'Windows':
            locale.setlocale(locale.LC_ALL, 'Persian')
        else:
            locale.setlocale(locale.LC_ALL, 'fa_IR')

    def test_datetime_to_str(self):
        date = jdatetime.datetime(1394, 1, 1, 0, 0, 0)
        self.assertEqual(str(date), '1394-01-01 00:00:00')

    def test_with_pytz(self):
        try:
            import pytz
            from pytz import timezone
        except Exception:
            pytz = None
        if pytz:
            tehran = timezone('Asia/Tehran')
            date = jdatetime.datetime(1394, 1, 1, 0, 0, 0, tzinfo=tehran)
            self.assertEqual(str(date), '1394-01-01 00:00:00+0326')

    def test_as_locale_returns_same_datetime_with_specified_locale(self):
        jdt_en = jdatetime.datetime(1397, 4, 23, 11, 47, 30, 40, locale='en_US')
        jdt_fa = jdt_en.aslocale('fa_IR')
        self.assertEqual(jdt_fa.year, 1397)
        self.assertEqual(jdt_fa.month, 4)
        self.assertEqual(jdt_fa.day, 23)
        self.assertEqual(jdt_fa.hour, 11)
        self.assertEqual(jdt_fa.minute, 47)
        self.assertEqual(jdt_fa.second, 30)
        self.assertEqual(jdt_fa.microsecond, 40)
        self.assertEqual(jdt_fa.locale, 'fa_IR')

    def test_timetuple(self):
        jdt = jdatetime.datetime(1397, 4, 23, 11, 47, 30, 40)
        self.assertEqual(
            jdt.timetuple(),
            time.struct_time((2018, 7, 14, 11, 47, 30, 5, 195, -1)),
        )

    @skipUnless(
        hasattr(datetime.datetime, 'timestamp'),
        '`datetime.datetime.timestamp` is not implemented in older pythons',
    )
    def test_timestamp_implemented(self):
        teh = TehranTime()
        jdt = jdatetime.datetime(1397, 4, 23, 11, 47, 30, 40, tzinfo=teh)
        self.assertEqual(jdt.timestamp(), 1531556250.00004)

    @skipIf(
        hasattr(datetime.datetime, 'timestamp'),
        '`datetime.datetime.timestamp` is not implemented in older pythons',
    )
    def test_timestamp_not_implemented(self):
        teh = TehranTime()
        jdt = jdatetime.datetime(1397, 4, 23, 11, 47, 30, 40, tzinfo=teh)
        with self.assertRaises(NotImplementedError):
            jdt.timestamp()

    def test_isoformat_default_args(self):
        jdt = jdatetime.datetime(1398, 4, 11)
        jiso = jdt.isoformat()

        self.assertAlmostEqual(jiso, '1398-04-11T00:00:00')

    def test_isoformat_custom_sep(self):
        jdt = jdatetime.datetime(1398, 4, 11)
        jiso = jdt.isoformat('M')

        self.assertAlmostEqual(jiso, '1398-04-11M00:00:00')

    def test_isoformat_unicode_arg_python2(self):
        jdt = jdatetime.datetime(1398, 4, 11)
        jiso = jdt.isoformat('M')
        # Used to raise:
        # AssertionError: argument 1 must be a single character: M
        ujiso = jdt.isoformat('M')
        self.assertEqual(jiso, ujiso)

    def test_isoformat_bad_sep(self):
        jdt = jdatetime.datetime(1398, 4, 11)

        for t in ['dummy', 123, 123.123, (1, 2, 3), [1, 2, 3]]:
            with self.assertRaises(AssertionError):
                jdt.isoformat(t)

    def test_isoformat_custom_timespec(self):
        jdt = jdatetime.datetime(1398, 4, 11, 11, 6, 5, 123456)

        hours = jdt.isoformat(timespec='hours')
        minutes = jdt.isoformat(timespec='minutes')
        seconds = jdt.isoformat(timespec='seconds')
        milliseconds = jdt.isoformat(timespec='milliseconds')
        microseconds = jdt.isoformat(timespec='microseconds')

        self.assertEqual(hours, '1398-04-11T11')
        self.assertEqual(minutes, '1398-04-11T11:06')
        self.assertEqual(seconds, '1398-04-11T11:06:05')
        self.assertEqual(milliseconds, '1398-04-11T11:06:05.123')
        self.assertEqual(microseconds, '1398-04-11T11:06:05.123456')

    def test_zoneinfo_as_timezone(self):
        tzinfo = ZoneInfo('Asia/Tehran')
        jdt = jdatetime.datetime(1398, 4, 11, 11, 6, 5, 123456, tzinfo=tzinfo)
        self.assertEqual(str(jdt), '1398-04-11 11:06:05.123456+0430')

    def test_pickle(self):
        dt = jdatetime.datetime.now()
        self.assertEqual(pickle.loads(pickle.dumps(dt)), dt)

    def test_unpickle_older_datetime_object(self):
        dt = load_pickle('jdatetime_py3_jdatetime3.7.pickle')
        self.assertEqual(dt, jdatetime.datetime(1400, 10, 11, 1, 2, 3, 30))


class TestJdatetimeComparison(TestCase):
    # __eq__
    def test_eq_datetime(self):
        date_string = '1363-6-6 12:13:14'
        date_format = '%Y-%m-%d %H:%M:%S'

        dt1 = jdatetime.datetime.strptime(date_string, date_format)

        date_string = '1364-6-6 12:13:14'
        dt2 = jdatetime.datetime.strptime(date_string, date_format)

        self.assertNotEqual(dt2, dt1)

    def test_eq_datetime_now(self):
        import time

        dt1 = jdatetime.datetime.now()
        time.sleep(0.1)
        dt2 = jdatetime.datetime.now()
        self.assertNotEqual(dt2, dt1)

    def test_eq_datetime_diff_tz(self):
        gmt = GMTTime()
        teh = TehranTime()

        dt_gmt = datetime.datetime(2015, 6, 27, 0, 0, 0, tzinfo=gmt)
        dt_teh = datetime.datetime(2015, 6, 27, 3, 30, 0, tzinfo=teh)
        self.assertEqual(dt_teh, dt_gmt, 'In standrd python datetime, __eq__ considers timezone')

        jdt_gmt = jdatetime.datetime(1389, 2, 17, 0, 0, 0, tzinfo=gmt)
        jdt_teh = jdatetime.datetime(1389, 2, 17, 3, 30, 0, tzinfo=teh)
        self.assertEqual(jdt_teh, jdt_gmt)

    def test_eq_datetimes_with_different_locales_are_not_equal(self):
        dt_en = jdatetime.datetime(2018, 4, 15, 0, 0, 0, locale='en_US')
        dt_fa = jdatetime.datetime(2018, 4, 15, 0, 0, 0, locale='fa_IR')
        self.assertNotEqual(dt_en, dt_fa)
        self.assertNotEqual(dt_fa, dt_en)

    def test_eq_with_none(self):
        dt1 = jdatetime.datetime(2023, 9, 30, 12, 0, 0, locale='fa_IR')
        self.assertFalse(dt1.__eq__(None))

    def test_eq_with_not_implemented(self):
        dt1 = jdatetime.datetime(2023, 9, 30, 12, 0, 0, locale='fa_IR')
        dt2 = 'not a datetime object'
        self.assertFalse(dt1 == dt2)

    # __ne__
    def test_ne_different_dates(self):
        dt1 = jdatetime.datetime(1403, 1, 1, 0, 0, 0)
        dt2 = jdatetime.datetime(1403, 1, 2, 0, 0, 0)
        self.assertTrue(dt1 != dt2)

    def test_neq_different_times(self):
        dt1 = jdatetime.datetime(1403, 1, 1, 12, 0, 0)
        dt2 = jdatetime.datetime(1403, 1, 1, 13, 0, 0)
        self.assertTrue(dt1 != dt2)

    def test_neq_different_timezones(self):
        gmt = GMTTime()
        teh = TehranTime()

        dt1 = jdatetime.datetime(1403, 1, 1, 12, 0, 0, tzinfo=teh)
        dt2 = jdatetime.datetime(1403, 1, 1, 12, 0, 0, tzinfo=gmt)
        self.assertTrue(dt1 != dt2)

    def test_neq_same_datetime(self):
        dt1 = jdatetime.datetime(1403, 1, 1, 12, 0, 0)
        dt2 = jdatetime.datetime(1403, 1, 1, 12, 0, 0)
        self.assertFalse(dt1 != dt2)

    def test_neq_different_types(self):
        dt1 = jdatetime.datetime(1403, 1, 1, 12, 0, 0)
        self.assertTrue(dt1 != '1403-01-01 12:00:00')

    def test_neq_with_none(self):
        dt1 = jdatetime.datetime(1403, 1, 1, 12, 0, 0)
        self.assertTrue(dt1.__ne__(None))

    def test_neq_different_datetime_types(self):
        dt1 = jdatetime.datetime(1403, 1, 1, 12, 0, 0)
        dt2 = dt1.togregorian()
        self.assertFalse(dt1 != dt2)

        # different hour
        dt2 = dt1.togregorian() + datetime.timedelta(hours=1)
        self.assertTrue(dt1 != dt2)
        dt2 = dt1.togregorian() - datetime.timedelta(hours=1)
        self.assertTrue(dt1 != dt2)

        # different day
        dt2 = dt1.togregorian() + datetime.timedelta(days=1)
        self.assertTrue(dt1 != dt2)
        dt2 = dt1.togregorian() - datetime.timedelta(days=1)
        self.assertTrue(dt1 != dt2)

        # different month
        dt2 = dt1.togregorian() + datetime.timedelta(days=31)
        self.assertTrue(dt1 != dt2)
        dt2 = dt1.togregorian() - datetime.timedelta(days=31)
        self.assertTrue(dt1 != dt2)

        # different year
        dt2 = dt1.togregorian() + datetime.timedelta(days=370)
        self.assertTrue(dt1 != dt2)
        dt2 = dt1.togregorian() - datetime.timedelta(days=370)
        self.assertTrue(dt1 != dt2)

    def test_neq_not_implemented(self):
        dt1 = jdatetime.datetime(1403, 1, 1, 12, 0, 0)
        self.assertEqual(dt1.__ne__('not datetime object'), NotImplemented)

    # __ge__
    def test_ge_with_same_datetime(self):
        dt1 = jdatetime.datetime(1402, 7, 8, 12, 0, 0)
        dt2 = jdatetime.datetime(1402, 7, 8, 12, 0, 0)

        self.assertTrue(dt1 >= dt2)

    def test_ge_with_greater_datetime(self):
        dt1 = jdatetime.datetime(1402, 7, 8, 12, 0, 0)
        dt2 = jdatetime.datetime(1402, 7, 7, 12, 0, 0)

        self.assertTrue(dt1 >= dt2)

    def test_ge_with_lesser_datetime(self):
        dt1 = jdatetime.datetime(1402, 7, 8, 12, 0, 0)
        dt2 = jdatetime.datetime(1402, 7, 9, 12, 0, 0)

        self.assertFalse(dt1 >= dt2)

    # __gt__
    def test_gt_with_same_datetime(self):
        dt1 = jdatetime.datetime(2023, 9, 30, 12, 0, 0)
        dt2 = jdatetime.datetime(2023, 9, 30, 12, 0, 0)

        self.assertFalse(dt1 > dt2)

    def test_gt_with_greater_datetime(self):
        dt1 = jdatetime.datetime(2023, 10, 1, 12, 0, 0)
        dt2 = jdatetime.datetime(2023, 9, 30, 12, 0, 0)

        self.assertTrue(dt1 > dt2)

    def test_gt_with_lesser_datetime(self):
        dt1 = jdatetime.datetime(2023, 9, 29, 12, 0, 0)
        dt2 = jdatetime.datetime(2023, 9, 30, 12, 0, 0)

        self.assertFalse(dt1 > dt2)

    # __le__
    def test_le_with_same_datetime(self):
        dt1 = jdatetime.datetime(1402, 7, 1, 12, 0, 0)
        dt2 = jdatetime.datetime(1402, 7, 1, 12, 0, 0)

        self.assertTrue(dt1 <= dt2)

    def test_le_with_greater_datetime(self):
        dt1 = jdatetime.datetime(1402, 7, 2, 12, 0, 0)
        dt2 = jdatetime.datetime(1402, 7, 1, 12, 0, 0)

        self.assertFalse(dt1 <= dt2)

    def test_le_with_lesser_datetime(self):
        dt1 = jdatetime.datetime(1402, 6, 30, 12, 0, 0)
        dt2 = jdatetime.datetime(1402, 7, 1, 12, 0, 0)

        self.assertTrue(dt1 <= dt2)

    # __lt__
    def test_lt_with_same_datetime(self):
        dt1 = jdatetime.datetime(1402, 7, 1, 12, 0, 0)
        dt2 = jdatetime.datetime(1402, 7, 1, 12, 0, 0)

        self.assertFalse(dt1 < dt2)

    def test_lt_with_greater_datetime(self):
        dt1 = jdatetime.datetime(1402, 7, 2, 12, 0, 0)
        dt2 = jdatetime.datetime(1402, 7, 1, 12, 0, 0)

        self.assertFalse(dt1 < dt2)

    def test_lt_with_lesser_datetime(self):
        dt1 = jdatetime.datetime(1402, 6, 30, 12, 0, 0)
        dt2 = jdatetime.datetime(1402, 7, 1, 12, 0, 0)

        self.assertTrue(dt1 < dt2)


class TestJdatetimeGetSetLocale(TestCase):
    @staticmethod
    def record_thread_locale(record, event, locale):
        """Set and capture locale in current thread.
        Use an event to coordinate execution for multithreaded
        tests. Because thread idents maybe recycled and reused
        and jdatetime uses threads idents to identify unique
        threads.
        """
        event.wait(timeout=10)
        jdatetime.set_locale(locale)
        record.append(jdatetime.get_locale())

    def test_get_locale_returns_none_if_no_locale_set_yet(self):
        self.assertIsNone(jdatetime.get_locale())

    @skipIf(greenlet_installed, 'thread ident is used when greenlet is not installed')
    def test_set_locale_is_per_thread_with_no_effect_on_other_threads(self):
        event = threading.Event()
        fa_record = []
        fa_thread = threading.Thread(target=self.record_thread_locale, args=(fa_record, event, 'fa_IR'))
        nl_record = []
        nl_thread = threading.Thread(target=self.record_thread_locale, args=(nl_record, event, 'nl_NL'))

        fa_thread.start()
        nl_thread.start()
        event.set()  # ensure both threads run concurrently
        fa_thread.join()
        nl_thread.join()

        self.assertEqual(1, len(fa_record))
        self.assertEqual('fa_IR', fa_record[0])
        self.assertEqual(1, len(nl_record))
        self.assertEqual('nl_NL', nl_record[0])
        self.assertIsNone(jdatetime.get_locale())  # MainThread is not affected neither

    @skipUnless(greenlet_installed, 'greenelts ident is used when greenlet module is installed')
    def test_set_locale_is_per_greenlet_with_no_effect_on_other_greenlets(self):
        fa_record = []

        def record_greenlet_locale_fa():
            jdatetime.set_locale('fa_IR')
            nl_greenlet.switch()
            fa_record.append(jdatetime.get_locale())
            nl_greenlet.switch()

        nl_record = []

        def record_greenlet_locale_nl():
            jdatetime.set_locale('nl_NL')
            fa_greenlet.switch()
            nl_record.append(jdatetime.get_locale())
            fa_greenlet.switch()

        fa_greenlet = greenlet.greenlet(record_greenlet_locale_fa)
        nl_greenlet = greenlet.greenlet(record_greenlet_locale_nl)
        fa_greenlet.switch()

        self.assertEqual(1, len(fa_record))
        self.assertEqual('fa_IR', fa_record[0])
        self.assertEqual(1, len(nl_record))
        self.assertEqual('nl_NL', nl_record[0])

    @skipIf(greenlet_installed, 'thread ident is used when greenlet is not installed')
    def test_set_locale_sets_default_locale_for_date_objects(self):
        def record_locale_formatted_date(record, locale):
            jdatetime.set_locale(locale)
            dt = jdatetime.date(1397, 3, 27)
            record.append(dt.strftime('%A'))
            record.append(dt.strftime('%B'))

        fa_record = []
        fa_th = threading.Thread(target=record_locale_formatted_date, args=(fa_record, jdatetime.FA_LOCALE))
        fa_th.start()
        fa_th.join()

        self.assertEqual(['یک‌شنبه', 'خرداد'], fa_record)

    @skipUnless(greenlet_installed, 'greenlets ident is used when greenlet module is installed')
    def test_set_locale_sets_default_locale_for_date_objects_with_greenlets(self):
        def record_locale_formatted_date(record, locale):
            jdatetime.set_locale(locale)
            dt = jdatetime.date(1397, 3, 27)
            record.append(dt.strftime('%A'))
            record.append(dt.strftime('%B'))

        fa_record = []
        fa_greenlet = greenlet.greenlet(record_locale_formatted_date)
        fa_greenlet.switch(fa_record, jdatetime.FA_LOCALE)

        self.assertEqual(['یک‌شنبه', 'خرداد'], fa_record)

    def test_fromisoformat(self):
        UTC = datetime.timezone.utc

        self.assertEqual(
            jdatetime.datetime.fromisoformat('1402-01-03T15:35:59.898169'),
            jdatetime.datetime(1402, 1, 3, 15, 35, 59, 898169),
        )

        self.assertEqual(
            jdatetime.datetime.fromisoformat('1401-11-04 00:05:23.283'),
            jdatetime.datetime(1401, 11, 4, 0, 5, 23, 283000),
        )

        self.assertEqual(
            jdatetime.datetime.fromisoformat('1403-11-04 00:05:23.283+00:00'),
            jdatetime.datetime(1403, 11, 4, 0, 5, 23, 283000, tzinfo=UTC),
        )

        self.assertEqual(
            jdatetime.datetime.fromisoformat('1400-11-04T00:05:23+04:00'),
            jdatetime.datetime(
                1400, 11, 4, 0, 5, 23, 0, tzinfo=datetime.timezone(datetime.timedelta(seconds=14400))
            ),
        )

        self.assertEqual(
            jdatetime.datetime.fromisoformat('14020101'),
            jdatetime.datetime(1402, 1, 1),
        )

        if sys.version_info[:2] >= (3, 11):  # new Python 3.11 time formats
            self.assertEqual(
                jdatetime.datetime.fromisoformat('1402-02-31T00:05:23Z'),
                jdatetime.datetime(1402, 2, 31, 0, 5, 23, 0, tzinfo=UTC),
            )

            self.assertEqual(
                jdatetime.datetime.fromisoformat('14031230T010203'),
                jdatetime.datetime(1403, 12, 30, 1, 2, 3),
            )

    def test_unknown_type_operations(self):
        dt = jdatetime.datetime(1402, 1, 9)
        unknown_type = object()
        self.assertTrue(
            dt.__sub__(unknown_type)
            is dt.__rsub__(unknown_type)
            is dt.__add__(unknown_type)
            is dt.__radd__(unknown_type)
            is dt.__eq__(unknown_type)
            is dt.__ne__(unknown_type)
            is dt.__lt__(unknown_type)
            is dt.__le__(unknown_type)
            is dt.__gt__(unknown_type)
            is dt.__ge__(unknown_type)
            is NotImplemented
        )
        with self.assertRaisesRegex(
            TypeError,
            r"unsupported operand type\(s\) for \-=: 'datetime' and 'object'",
        ):
            dt -= unknown_type
