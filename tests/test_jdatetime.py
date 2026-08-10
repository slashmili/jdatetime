import datetime
import locale
import pickle
import platform
import time
from typing import Any
from zoneinfo import ZoneInfo

import pytest

import jdatetime

try:
    import greenlet  # type: ignore
except ImportError:
    greenlet: Any = None

from tests import TehranTime, load_pickle


def test_datetime_date_method_keeps_datetime_locale_on_date_instance():
    datetime_obj = jdatetime.datetime(1397, 4, 22, locale='nl_NL')
    date = datetime_obj.date()
    assert date.locale == 'nl_NL'


def test_init_locale_is_effective_only_if_not_none():
    orig_locale = jdatetime.get_locale()
    jdatetime.set_locale('en_US')
    try:
        datetime_obj = jdatetime.datetime(1397, 4, 22, locale=None)
        assert datetime_obj.locale == 'en_US'
    finally:
        jdatetime.set_locale(orig_locale)


def test_init_locale_is_effective_only_if_not_empty():
    orig_locale = jdatetime.get_locale()
    jdatetime.set_locale('nl_NL')
    try:
        datetime_obj = jdatetime.datetime(1397, 4, 22, locale='')
        assert datetime_obj.locale == 'nl_NL'
    finally:
        jdatetime.set_locale(orig_locale)


def test_locale_property_is_read_only():
    datetime_obj = jdatetime.datetime(1397, 4, 22)
    with pytest.raises(AttributeError):
        datetime_obj.locale = jdatetime.FA_LOCALE  # type: ignore


def test_fold():
    # Test default value
    dt = jdatetime.datetime(1400, 11, 22)
    assert dt.fold == 0
    assert dt.time().fold == 0

    # Test custome value for fold
    dt = jdatetime.datetime(1400, 11, 22, fold=1)
    assert dt.fold == 1
    assert dt.time().fold == 1

    # Test invalid value for fold
    with pytest.raises(ValueError, match='fold must be either 0 or 1'):
        jdatetime.datetime(1400, 11, 22, fold=2)

    # Test combine
    t = jdatetime.time(12, 13, 14, fold=1)
    d = jdatetime.date(1400, 11, 22)
    assert jdatetime.datetime.combine(d, t) == jdatetime.datetime(1400, 11, 22, 12, 13, 14, fold=1)

    # Test replace
    dt = jdatetime.datetime(1400, 11, 22, fold=0)
    new_dt = dt.replace(fold=1)
    assert new_dt.fold == 1


def test_locale_property_returns_locale():
    datetime_obj = jdatetime.datetime(1397, 4, 22, locale='nl_NL')
    assert datetime_obj.locale == 'nl_NL'


def test_init_locale_is_named_argument_only():
    with pytest.raises(TypeError):
        datetime.datetime(1397, 4, 22, 'nl_NL')  # type: ignore


def test_init_accepts_instance_locale():
    datetime_obj = jdatetime.datetime(1397, 4, 23, locale=jdatetime.FA_LOCALE)
    assert datetime_obj.strftime('%A') == 'شنبه'


def test_today():
    today = datetime.date.today()
    converted_today = jdatetime.date.today().togregorian()
    assert today.year == converted_today.year


def test_fromtimestamp():
    d = jdatetime.date.fromtimestamp(1783232224)
    assert d.year == 1405
    assert d.month == 4
    assert d.day == 14


def test_fromordinal():
    d = jdatetime.date.fromordinal(1)
    assert d.year == 1


def test_comparison():
    today = jdatetime.date.today()
    assert not (today < today - jdatetime.timedelta(days=76))
    assert not (today <= today - jdatetime.timedelta(days=1))
    assert today + jdatetime.timedelta(days=1) > today
    assert today + jdatetime.timedelta(days=30) >= today
    assert today == today  # noqa: PLR0124
    assert not (today > today)  # noqa: PLR0124
    assert not (today < today)  # noqa: PLR0124
    assert today >= today  # noqa: PLR0124
    assert today <= today  # noqa: PLR0124
    not_today = jdatetime.date(today.year, today.month, today.day) + jdatetime.timedelta(days=1)
    assert today != not_today

    dtg = jdatetime.datetime(1380, 12, 1, 1, 2, 4)
    assert dtg < dtg + jdatetime.timedelta(seconds=1)
    assert dtg - jdatetime.timedelta(seconds=1) < dtg
    assert dtg is not None


def test_date_conversion_date_input():
    # todo: add some corner cases
    d1 = datetime.date(2010, 11, 23)
    jd1 = jdatetime.date(1389, 9, 2)
    d2 = datetime.date(2011, 5, 13)
    jd2 = jdatetime.date(1390, 2, 23)

    assert d1 == jd1.togregorian()
    assert d2 == jd2.togregorian()
    assert jd1 == jdatetime.date.fromgregorian(date=d1)
    assert jd2 == jdatetime.date.fromgregorian(date=d2)


def test_date_conversion_integer_input():
    d_check_with = jdatetime.date(1390, 2, 23)
    jd_datetime = jdatetime.datetime.fromgregorian(
        year=2011,
        month=5,
        day=13,
        hour=14,
        minute=15,
        second=16,
    )
    assert jd_datetime == jdatetime.datetime.combine(d_check_with, jdatetime.time(14, 15, 16))

    gdatetime = datetime.datetime(2011, 5, 13, 14, 15, 16)
    assert jd_datetime.togregorian() == gdatetime


def test_strftime():
    s = jdatetime.date(1390, 2, 23)
    string_format = '%a %A %b %B %c %d %H %I %j %m %M %p %S %w %W %x %X %y %Y %f %z %Z'
    output = (
        'Fri Friday Ord Ordibehesht Fri Ord 23 00:00:00 '
        '1390 23 00 12 054 02 00 AM 00 6 8 02/23/90 00:00:00 90 1390 000000  '
    )
    assert s.strftime(string_format) == output

    dt = jdatetime.datetime(1390, 2, 23, 12, 13, 14, 1)
    unicode_format = '%a %A %b %B %c %d %H %I %j %m %M %p %S %w %W %x %X %y %Y %f'
    output = (
        'Fri Friday Ord Ordibehesht Fri Ord 23 12:13:14 '
        '1390 23 12 12 054 02 13 PM 14 6 8 02/23/90 12:13:14 90 1390 000001'
    )
    assert dt.strftime(unicode_format) == output

    dt = jdatetime.datetime(1390, 2, 23, 12, 13, 14, 1)
    string_format = 'ﺱﺎﻟ = %y، ﻡﺎﻫ = %m، ﺭﻭﺯ = %d'
    output = 'ﺱﺎﻟ = 90، ﻡﺎﻫ = 02، ﺭﻭﺯ = 23'
    assert dt.strftime(string_format) == output

    class NYCTime(jdatetime.tzinfo):
        def utcoffset(self, dt):
            return jdatetime.timedelta(hours=-4)

        def tzname(self, dt):
            return 'EDT'

        def dst(self, dt):
            return jdatetime.timedelta(0)

    nyc = NYCTime()
    dt = jdatetime.datetime(1389, 2, 17, 19, 10, 2, tzinfo=nyc)
    assert dt.strftime('%Z %z') == 'EDT -0400'

    teh = TehranTime()
    dt = jdatetime.datetime(1389, 2, 17, 19, 10, 2, tzinfo=teh)
    assert dt.strftime('%Z %z') == 'IRDT +0330'


def test_strftime_I_directive_uses_twelve_hour_clock():
    import datetime as _std

    # %I and %-I must render the 12-hour clock (1..12), matching stdlib.
    for hour in range(24):
        jd = jdatetime.datetime(1400, 1, 1, hour, 5, 0)
        std = _std.datetime(2020, 1, 1, hour, 5, 0)
        assert jd.strftime('%I') == std.strftime('%I')
        assert jd.strftime('%-I') == std.strftime('%I').lstrip('0')
        assert jd._hour12 == int(std.strftime('%I'))
        # %I must be consistent with the (correct) %p directive:
        # reconstructing the 24-hour value from (%p, %I) round-trips.
        twelve = int(jd.strftime('%I'))
        base = 0 if twelve == 12 else twelve
        reconstructed = base + (12 if jd.strftime('%p') == 'PM' else 0)
        assert reconstructed == hour

    # Spot-check the values that the previous 24-hour behaviour got wrong.
    assert jdatetime.datetime(1400, 1, 1, 0, 0).strftime('%I') == '12'
    assert jdatetime.datetime(1400, 1, 1, 13, 0).strftime('%I') == '01'
    assert jdatetime.datetime(1400, 1, 1, 23, 0).strftime('%I') == '11'
    assert jdatetime.datetime(1400, 1, 1, 13, 0).strftime('%-I') == '1'
    # A plain date (no time component) is midnight -> 12.
    assert jdatetime.date(1400, 1, 1).strftime('%I') == '12'


def test_strftime_fa_locale_uses_short_month_names_for_b_directive():
    tests = [
        (1, 'فرو', 'فروردین'),
        (2, 'ارد', 'اردیبهشت'),
        (3, 'خرد', 'خرداد'),
        (4, 'تیر', 'تیر'),
        (5, 'مرد', 'مرداد'),
        (6, 'شهر', 'شهریور'),
        (7, 'مهر', 'مهر'),
        (8, 'آبا', 'آبان'),
        (9, 'آذر', 'آذر'),
        (10, 'دی', 'دی'),
        (11, 'بهم', 'بهمن'),
        (12, 'اسف', 'اسفند'),
    ]
    for month, expected_short_month, expected_full_month in tests:
        dt = jdatetime.datetime(1400, month, 1, locale=jdatetime.FA_LOCALE)
        assert dt.strftime('%b') == expected_short_month
        assert dt.strftime('%B') == expected_full_month


def test_strftime_single_digit():
    dt = jdatetime.datetime(1390, 2, 3, 4, 5, 6)
    assert dt.strftime('%-m %m %-d %d %-H %H %-M %M %-S %S') == '2 02 3 03 4 04 5 05 6 06'


def test_strftime_escape_percent():
    dt = jdatetime.datetime(1402, 1, 7)
    assert dt.strftime('%%x=%x') == '%x=01/07/02'
    assert dt.strftime('%%d=%d') == '%d=07'
    assert dt.strftime('%%%d') == '%07'


def test_strftime_unknown_directive():
    assert jdatetime.date.today().strftime('%Q') == '%Q'


def test_kabiseh():
    kabiseh_year = jdatetime.date.fromgregorian(date=datetime.date(2013, 3, 20))
    assert kabiseh_year.isleap() is True

    normal_year = jdatetime.date.fromgregorian(date=datetime.date(2014, 3, 20))
    assert normal_year.isleap() is False

    kabiseh_year = jdatetime.date(1391, 12, 30)
    assert kabiseh_year.isleap() is True

    with pytest.raises(ValueError):
        jdatetime.date(1392, 12, 30)


def test_datetime():
    d = jdatetime.datetime(1390, 1, 2, 12, 13, 14)

    assert d.time() == jdatetime.time(12, 13, 14)
    assert d.date() == jdatetime.date(1390, 1, 2)


def test_datetimetoday():
    jnow = jdatetime.datetime.today()
    today = datetime.datetime.today().date()
    gnow = jdatetime.date.fromgregorian(date=today)

    assert jnow.date() == gnow


def test_datetimefromtimestamp():
    t = time.time()
    jnow = jdatetime.datetime.fromtimestamp(t).date()
    gnow = datetime.datetime.fromtimestamp(t).date()

    assert jdatetime.date.fromgregorian(date=gnow) == jnow


def test_combine():
    t = jdatetime.time(12, 13, 14)
    d = jdatetime.date(1390, 4, 5)
    dt = jdatetime.datetime(1390, 4, 5, 12, 13, 14)

    assert jdatetime.datetime.combine(d, t) == dt


def test_combine_keeps_date_locale():
    t = jdatetime.time(11, 20, 30)
    d = jdatetime.date(1397, 4, 24, locale='nl_NL')
    assert jdatetime.datetime.combine(d, t).locale == 'nl_NL'


def test_replace():
    dt = jdatetime.datetime.today()
    args: dict = {
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

    assert dtr == dtn


def test_replace_keeps_date_locale():
    dt = jdatetime.datetime(1397, 4, 24, locale='nl_NL')
    args: dict = {'year': 1390, 'month': 12, 'hour': 13}
    assert dt.replace(**args).locale == 'nl_NL'


def test_astimezone_keeps_locale():
    orig_locale = jdatetime.get_locale()
    jdatetime.set_locale('en_US')
    try:
        teh = TehranTime()
        dt = jdatetime.datetime(1397, 8, 17, 7, 54, 28, tzinfo=teh, locale='fa_IR')
        converted = dt.astimezone(datetime.timezone.utc)
        assert converted.locale == 'fa_IR'
    finally:
        jdatetime.set_locale(orig_locale)


def test_replace_remove_tzinfo():
    teh = TehranTime()
    dt = jdatetime.datetime(1397, 8, 17, 7, 54, 28, tzinfo=teh)
    dt_naive = dt.replace(tzinfo=None)
    assert dt_naive.tzinfo is None


def test_strptime():
    date_string = '1363-6-6 12:13:14'
    date_format = '%Y-%m-%d %H:%M:%S'
    dt1 = jdatetime.datetime.strptime(date_string, date_format)
    dt2 = jdatetime.datetime(1363, 6, 6, 12, 13, 14)

    assert dt1 == dt2


def test_strptime_bare():
    date_string = '13630606121314'
    date_format = '%Y%m%d%H%M%S'
    dt1 = jdatetime.datetime.strptime(date_string, date_format)
    dt2 = jdatetime.datetime(1363, 6, 6, 12, 13, 14)

    assert dt1 == dt2


def test_strptime_handles_alphabets_in_format():
    date_string = '1363-6-6T12:13:14'
    date_format = '%Y-%m-%dT%H:%M:%S'
    dt1 = jdatetime.datetime.strptime(date_string, date_format)
    dt2 = jdatetime.datetime(1363, 6, 6, 12, 13, 14)

    assert dt1 == dt2


def test_strptime_special_chars():
    date_string = '[1363*6*6] ? (12+13+14)'
    date_format = '[%Y*%m*%d] ? (%H+%M+%S)'
    dt1 = jdatetime.datetime.strptime(date_string, date_format)
    dt2 = jdatetime.datetime(1363, 6, 6, 12, 13, 14)

    assert dt1 == dt2


def test_strptime_small_y():
    assert jdatetime.datetime(1468, 1, 1) == jdatetime.datetime.strptime('68/1/1', '%y/%m/%d')
    assert jdatetime.datetime(1369, 1, 1) == jdatetime.datetime.strptime('69/1/1', '%y/%m/%d')


def test_strptime_do_not_match_excessive_characters():
    with pytest.raises(ValueError) as exc_info:
        jdatetime.datetime.strptime('21 ', '%y')
    assert str(exc_info.value) == "time data '21 ' does not match format '%y'"


def test_strptime_nanoseconds():
    assert jdatetime.datetime(1279, 1, 1, 0, 0, 0, 700000) == jdatetime.datetime.strptime('7', '%f')
    assert jdatetime.datetime(1279, 1, 1, 0, 0, 0, 12300) == jdatetime.datetime.strptime('0123', '%f')


def test_strptime_handle_b_B_directive():
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
        ('۱۴ ارد ۱۴۰۰', '%d %b %Y', (1400, 2, 14)),
    ]
    for date_string, date_format, expected_date in tests:
        date = jdatetime.datetime.strptime(date_string, date_format)
        assert date == jdatetime.datetime(*expected_date)


def test_strptime_invalid_date_string_b_directive():
    with pytest.raises(ValueError, match="time data '14 DRO 1400' does not match format '%d %b %Y'"):
        jdatetime.datetime.strptime('14 DRO 1400', '%d %b %Y')


def test_strptime_invalid_date_string_B_directive():
    with pytest.raises(ValueError, match="time data '14 ordi 1400' does not match format '%d %B %Y'"):
        jdatetime.datetime.strptime('14 ordi 1400', '%d %B %Y')


def test_strptime_handle_z_directive():
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
        date = jdatetime.datetime.strptime(date_string, date_format)
        assert date.tzinfo == datetime.timezone(time_delta)


def test_strptime_invalid_date_string_z_directive():
    tests = [
        ('0123', '%z', "time data '0123' does not match format '%z'"),
        ('-01', '%z', "time data '-01' does not match format '%z'"),
        ('+012', '%z', "time data '+012' does not match format '%z'"),
        ('+01:2356', '%z', 'Inconsistent use of : in +01:2356'),  # Fixed: + not -
        ('+0123:56', '%z', "invalid literal for int() with base 10: ':5'"),
        ('+012345123456', '%z', "time data '+012345123456' does not match format '%z'"),
    ]
    for date_string, date_format, expected_msg in tests:
        with pytest.raises(ValueError) as exc_info:
            jdatetime.datetime.strptime(date_string, date_format)
        assert str(exc_info.value) == expected_msg


def test_strptime_A_p_j_directives():
    dt = jdatetime.datetime(1401, 2, 3, 4)
    fmt = '%Y %m %d %H %j %p %A %a'
    assert jdatetime.datetime.strptime(dt.strftime(fmt), fmt) == dt


def test_timetz():
    teh = TehranTime()
    dt_gmt = datetime.datetime(2015, 6, 27, 1, 2, 3, tzinfo=teh)
    assert str(dt_gmt.timetz()) == '01:02:03+03:30'


def test_fromgregorian_accepts_named_argument_of_date_and_locale():
    gd = datetime.date(2018, 7, 14)
    jdt = jdatetime.datetime.fromgregorian(date=gd, locale='nl_NL')
    assert jdt.year == 1397
    assert jdt.month == 4
    assert jdt.day == 23
    assert jdt.locale == 'nl_NL'


def test_fromgregorian_accepts_named_argument_of_datetime_and_locale():
    gdt = datetime.datetime(2018, 7, 15, 11, 7, 0)
    jdt = jdatetime.datetime.fromgregorian(datetime=gdt, locale='nl_NL')
    assert jdt.year == 1397
    assert jdt.month == 4
    assert jdt.day == 24
    assert jdt.hour == 11
    assert jdt.minute == 7
    assert jdt.locale == 'nl_NL'


def test_fromgregorian_accepts_named_argument_of_date_with_date_input():
    gdt = datetime.date(2018, 7, 15)
    jdt = jdatetime.datetime.fromgregorian(date=gdt, locale='nl_NL')
    assert jdt.year == 1397
    assert jdt.month == 4
    assert jdt.day == 24
    assert jdt.hour == 0
    assert jdt.minute == 0
    assert jdt.locale == 'nl_NL'


def test_fromgregorian_accepts_named_argument_of_date_with_datetime_input():
    gdt = datetime.datetime(2018, 7, 15, 11, 7, 0)
    jdt = jdatetime.datetime.fromgregorian(date=gdt, locale='nl_NL')
    assert jdt.year == 1397
    assert jdt.month == 4
    assert jdt.day == 24
    assert jdt.hour == 11
    assert jdt.minute == 7
    assert jdt.locale == 'nl_NL'


def test_fromgregorian_accepts_year_month_day_and_locale():
    jdt = jdatetime.datetime.fromgregorian(year=2018, month=7, day=15, locale='nl_NL')
    assert jdt.year == 1397
    assert jdt.month == 4
    assert jdt.day == 24
    assert jdt.locale == 'nl_NL'


def test_datetime_raise_exception_on_invalid_calculation():
    date_1395 = jdatetime.datetime(1395, 1, 1)

    with pytest.raises(TypeError):
        date_1395 - 1  # type: ignore

    with pytest.raises(TypeError):
        date_1395 + 1  # type: ignore

    with pytest.raises(TypeError):
        jdatetime.timedelta(days=1) - date_1395  # type: ignore

    with pytest.raises(TypeError):
        date_1395 + date_1395  # type: ignore


def test_datetime_calculation_on_timedelta():
    date_1395 = jdatetime.datetime(1395, 1, 1)
    day_before = date_1395 - jdatetime.timedelta(days=1)
    day_after = date_1395 + jdatetime.timedelta(days=1)

    assert day_before == jdatetime.datetime(1394, 12, 29, 0, 0)
    assert day_after == jdatetime.datetime(1395, 1, 2, 0, 0)

    day_after = jdatetime.timedelta(days=1) + date_1395

    assert day_before == jdatetime.datetime(1394, 12, 29, 0, 0)
    assert day_after == jdatetime.datetime(1395, 1, 2, 0, 0)


def test_datetime_calculation_on_two_dates():
    date_1394 = jdatetime.datetime(1394, 1, 1)
    date_1395 = jdatetime.datetime(1395, 1, 1)

    day_diff = date_1395 - date_1394
    assert day_diff == datetime.timedelta(365)

    day_diff = date_1394 - date_1395
    assert day_diff == datetime.timedelta(-365)


def test_date_raise_exception_on_invalid_calculation():
    date_1395 = jdatetime.date(1395, 1, 1)

    with pytest.raises(TypeError):
        date_1395 - 1  # type: ignore

    with pytest.raises(TypeError):
        date_1395 + 1  # type: ignore

    with pytest.raises(TypeError):
        jdatetime.timedelta(days=1) - date_1395  # type: ignore

    with pytest.raises(TypeError):
        date_1395 + date_1395  # type: ignore


def test_date_calculation_on_timedelta():
    date_1395 = jdatetime.date(1395, 1, 1)
    day_before = date_1395 - jdatetime.timedelta(days=1)
    day_after = date_1395 + jdatetime.timedelta(days=1)

    assert day_before == jdatetime.date(1394, 12, 29)
    assert day_after == jdatetime.date(1395, 1, 2)

    day_after = jdatetime.timedelta(days=1) + date_1395

    assert day_before == jdatetime.date(1394, 12, 29)
    assert day_after == jdatetime.date(1395, 1, 2)


def test_date_calculation_on_two_dates():
    date_1394 = jdatetime.date(1394, 1, 1)
    date_1395 = jdatetime.date(1395, 1, 1)

    day_diff = date_1395 - date_1394
    assert day_diff == datetime.timedelta(365)

    day_diff = date_1394 - date_1395
    assert day_diff == datetime.timedelta(-365)


def test_add_timedelta_keeps_source_datetime_locale():
    jdate = jdatetime.datetime(1397, 4, 23, locale='nl_NL')
    new_jdate = jdate + datetime.timedelta(days=1)
    assert new_jdate.year == 1397
    assert new_jdate.month == 4
    assert new_jdate.day == 24
    assert new_jdate.locale == 'nl_NL'


def test_subtract_timedelta_keeps_source_datetime_locale():
    jdate = jdatetime.datetime(1397, 4, 23, locale='nl_NL')
    new_jdate = jdate - datetime.timedelta(days=1)
    assert new_jdate.year == 1397
    assert new_jdate.month == 4
    assert new_jdate.day == 22
    assert new_jdate.locale == 'nl_NL'


def reset_locale():
    if platform.system() == 'Windows':
        locale.setlocale(locale.LC_ALL, 'English_United States')
    else:
        locale.setlocale(locale.LC_ALL, '')


def test_with_none_locale_set():
    reset_locale()
    day_of_week = jdatetime.date(1395, 1, 2).strftime('%a')
    assert day_of_week == 'Mon'


def set_fa_locale():
    if platform.system() == 'Windows':
        locale.setlocale(locale.LC_ALL, jdatetime.FA_LOCALE)
    else:
        locale.setlocale(locale.LC_ALL, 'fa_IR')


def test_with_fa_locale():
    set_fa_locale()
    day_of_week = jdatetime.date(1395, 1, 2).strftime('%a')
    assert day_of_week == 'دوشنبه'


def test_datetime_to_str():
    date = jdatetime.datetime(1394, 1, 1, 0, 0, 0)
    assert str(date) == '1394-01-01 00:00:00'


def test_with_pytz():
    pytest.importorskip('pytz')
    from pytz import timezone  # type: ignore

    tehran = timezone('Asia/Tehran')
    date = jdatetime.datetime(1394, 1, 1, 0, 0, 0, tzinfo=tehran)
    assert str(date) == '1394-01-01 00:00:00+0326'


def test_as_locale_returns_same_datetime_with_specified_locale():
    jdt_en = jdatetime.datetime(1397, 4, 23, 11, 47, 30, 40, locale='en_US')
    jdt_fa = jdt_en.aslocale('fa_IR')
    assert jdt_fa.year == 1397
    assert jdt_fa.month == 4
    assert jdt_fa.day == 23
    assert jdt_fa.hour == 11
    assert jdt_fa.minute == 47
    assert jdt_fa.second == 30
    assert jdt_fa.microsecond == 40
    assert jdt_fa.locale == 'fa_IR'


def test_timetuple():
    jdt = jdatetime.datetime(1397, 4, 23, 11, 47, 30, 40)
    assert jdt.timetuple() == time.struct_time((2018, 7, 14, 11, 47, 30, 5, 195, -1))


def test_timestamp_implemented():
    if not hasattr(datetime.datetime, 'timestamp'):
        pytest.skip('`datetime.datetime.timestamp` is not implemented in older pythons')

    teh = TehranTime()
    jdt = jdatetime.datetime(1397, 4, 23, 11, 47, 30, 40, tzinfo=teh)
    assert jdt.timestamp() == 1531556250.00004


def test_timestamp_not_implemented():
    if hasattr(datetime.datetime, 'timestamp'):
        pytest.skip('`datetime.datetime.timestamp` is implemented in this python version')

    teh = TehranTime()
    jdt = jdatetime.datetime(1397, 4, 23, 11, 47, 30, 40, tzinfo=teh)
    with pytest.raises(NotImplementedError):
        jdt.timestamp()


def test_isoformat_default_args():
    jdt = jdatetime.datetime(1398, 4, 11)
    jiso = jdt.isoformat()
    assert jiso == '1398-04-11T00:00:00'


def test_isoformat_custom_sep():
    jdt = jdatetime.datetime(1398, 4, 11)
    jiso = jdt.isoformat('M')
    assert jiso == '1398-04-11M00:00:00'


def test_isoformat_unicode_arg_python2():
    jdt = jdatetime.datetime(1398, 4, 11)
    jiso = jdt.isoformat('M')
    # Used to raise:
    # AssertionError: argument 1 must be a single character: M
    ujiso = jdt.isoformat('M')
    assert jiso == ujiso


def test_isoformat_bad_sep():
    jdt = jdatetime.datetime(1398, 4, 11)

    for t in ['dummy', 123, 123.123, (1, 2, 3), [1, 2, 3]]:
        with pytest.raises(AssertionError):
            jdt.isoformat(t)


def test_isoformat_custom_timespec():
    jdt = jdatetime.datetime(1398, 4, 11, 11, 6, 5, 123456)

    hours = jdt.isoformat(timespec='hours')
    minutes = jdt.isoformat(timespec='minutes')
    seconds = jdt.isoformat(timespec='seconds')
    milliseconds = jdt.isoformat(timespec='milliseconds')
    microseconds = jdt.isoformat(timespec='microseconds')

    assert hours == '1398-04-11T11'
    assert minutes == '1398-04-11T11:06'
    assert seconds == '1398-04-11T11:06:05'
    assert milliseconds == '1398-04-11T11:06:05.123'
    assert microseconds == '1398-04-11T11:06:05.123456'


def test_zoneinfo_as_timezone():
    tzinfo = ZoneInfo('Asia/Tehran')
    jdt = jdatetime.datetime(1398, 4, 11, 11, 6, 5, 123456, tzinfo=tzinfo)
    assert str(jdt) == '1398-04-11 11:06:05.123456+0430'


def test_pickle():
    dt = jdatetime.datetime.now()
    assert pickle.loads(pickle.dumps(dt)) == dt


def test_unpickle_older_datetime_object():
    dt = load_pickle('jdatetime_py3_jdatetime3.7.pickle')
    assert dt == jdatetime.datetime(1400, 10, 11, 1, 2, 3, 30)


def test_strptime_returns_subclass():
    class MyDateTime(jdatetime.datetime):
        pass

    result = MyDateTime.strptime('1405-05-19 12:34:56', '%Y-%m-%d %H:%M:%S')

    assert type(result) is MyDateTime
    assert result == MyDateTime(1405, 5, 19, 12, 34, 56)
