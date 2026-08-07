import datetime

import jdatetime
from tests import GMTTime, TehranTime


def test_eq_datetime():
    date_string = '1363-6-6 12:13:14'
    date_format = '%Y-%m-%d %H:%M:%S'

    dt1 = jdatetime.datetime.strptime(date_string, date_format)

    date_string = '1364-6-6 12:13:14'
    dt2 = jdatetime.datetime.strptime(date_string, date_format)

    assert dt2 != dt1


def test_eq_datetime_now():
    import time

    dt1 = jdatetime.datetime.now()
    time.sleep(0.1)
    dt2 = jdatetime.datetime.now()
    assert dt2 != dt1


def test_eq_datetime_diff_tz():
    gmt = GMTTime()
    teh = TehranTime()

    dt_gmt = datetime.datetime(2015, 6, 27, 0, 0, 0, tzinfo=gmt)
    dt_teh = datetime.datetime(2015, 6, 27, 3, 30, 0, tzinfo=teh)
    assert dt_teh == dt_gmt, 'In standard python datetime, __eq__ considers timezone'

    jdt_gmt = jdatetime.datetime(1389, 2, 17, 0, 0, 0, tzinfo=gmt)
    jdt_teh = jdatetime.datetime(1389, 2, 17, 3, 30, 0, tzinfo=teh)
    assert jdt_teh == jdt_gmt


def test_eq_datetimes_with_different_locales_are_not_equal():
    dt_en = jdatetime.datetime(2018, 4, 15, 0, 0, 0, locale='en_US')
    dt_fa = jdatetime.datetime(2018, 4, 15, 0, 0, 0, locale='fa_IR')
    assert dt_en != dt_fa
    assert dt_fa != dt_en


def test_eq_with_none():
    dt1 = jdatetime.datetime(2023, 9, 30, 12, 0, 0, locale='fa_IR')
    assert dt1.__eq__(None) is False


def test_eq_with_not_implemented():
    dt1 = jdatetime.datetime(2023, 9, 30, 12, 0, 0, locale='fa_IR')
    dt2 = 'not a datetime object'
    assert (dt1 == dt2) is False


# __ne__
def test_ne_different_dates():
    dt1 = jdatetime.datetime(1403, 1, 1, 0, 0, 0)
    dt2 = jdatetime.datetime(1403, 1, 2, 0, 0, 0)
    assert dt1 != dt2


def test_neq_different_times():
    dt1 = jdatetime.datetime(1403, 1, 1, 12, 0, 0)
    dt2 = jdatetime.datetime(1403, 1, 1, 13, 0, 0)
    assert dt1 != dt2


def test_neq_different_timezones():
    gmt = GMTTime()
    teh = TehranTime()

    dt1 = jdatetime.datetime(1403, 1, 1, 12, 0, 0, tzinfo=teh)
    dt2 = jdatetime.datetime(1403, 1, 1, 12, 0, 0, tzinfo=gmt)
    assert dt1 != dt2


def test_neq_same_datetime():
    dt1 = jdatetime.datetime(1403, 1, 1, 12, 0, 0)
    dt2 = jdatetime.datetime(1403, 1, 1, 12, 0, 0)
    assert not (dt1 != dt2)  # noqa: SIM202


def test_neq_different_types():
    dt1 = jdatetime.datetime(1403, 1, 1, 12, 0, 0)
    assert dt1 != '1403-01-01 12:00:00'


def test_neq_with_none():
    dt1 = jdatetime.datetime(1403, 1, 1, 12, 0, 0)
    assert dt1.__ne__(None) is True


def test_neq_different_datetime_types():
    dt1 = jdatetime.datetime(1403, 1, 1, 12, 0, 0)
    dt2 = dt1.togregorian()
    assert not (dt1 != dt2)  # noqa: SIM202

    # different hour
    dt2 = dt1.togregorian() + datetime.timedelta(hours=1)
    assert dt1 != dt2
    dt2 = dt1.togregorian() - datetime.timedelta(hours=1)
    assert dt1 != dt2

    # different day
    dt2 = dt1.togregorian() + datetime.timedelta(days=1)
    assert dt1 != dt2
    dt2 = dt1.togregorian() - datetime.timedelta(days=1)
    assert dt1 != dt2

    # different month
    dt2 = dt1.togregorian() + datetime.timedelta(days=31)
    assert dt1 != dt2
    dt2 = dt1.togregorian() - datetime.timedelta(days=31)
    assert dt1 != dt2

    # different year
    dt2 = dt1.togregorian() + datetime.timedelta(days=370)
    assert dt1 != dt2
    dt2 = dt1.togregorian() - datetime.timedelta(days=370)
    assert dt1 != dt2


def test_neq_not_implemented():
    dt1 = jdatetime.datetime(1403, 1, 1, 12, 0, 0)
    assert dt1.__ne__('not datetime object') is NotImplemented


# __ge__
def test_ge_with_same_datetime():
    dt1 = jdatetime.datetime(1402, 7, 8, 12, 0, 0)
    dt2 = jdatetime.datetime(1402, 7, 8, 12, 0, 0)
    assert dt1 >= dt2


def test_ge_with_greater_datetime():
    dt1 = jdatetime.datetime(1402, 7, 8, 12, 0, 0)
    dt2 = jdatetime.datetime(1402, 7, 7, 12, 0, 0)
    assert dt1 >= dt2


def test_ge_with_lesser_datetime():
    dt1 = jdatetime.datetime(1402, 7, 8, 12, 0, 0)
    dt2 = jdatetime.datetime(1402, 7, 9, 12, 0, 0)
    assert not (dt1 >= dt2)


# __gt__
def test_gt_with_same_datetime():
    dt1 = jdatetime.datetime(2023, 9, 30, 12, 0, 0)
    dt2 = jdatetime.datetime(2023, 9, 30, 12, 0, 0)
    assert not (dt1 > dt2)


def test_gt_with_greater_datetime():
    dt1 = jdatetime.datetime(2023, 10, 1, 12, 0, 0)
    dt2 = jdatetime.datetime(2023, 9, 30, 12, 0, 0)
    assert dt1 > dt2


def test_gt_with_lesser_datetime():
    dt1 = jdatetime.datetime(2023, 9, 29, 12, 0, 0)
    dt2 = jdatetime.datetime(2023, 9, 30, 12, 0, 0)
    assert not (dt1 > dt2)


# __le__
def test_le_with_same_datetime():
    dt1 = jdatetime.datetime(1402, 7, 1, 12, 0, 0)
    dt2 = jdatetime.datetime(1402, 7, 1, 12, 0, 0)
    assert dt1 <= dt2


def test_le_with_greater_datetime():
    dt1 = jdatetime.datetime(1402, 7, 2, 12, 0, 0)
    dt2 = jdatetime.datetime(1402, 7, 1, 12, 0, 0)
    assert not (dt1 <= dt2)


def test_le_with_lesser_datetime():
    dt1 = jdatetime.datetime(1402, 6, 30, 12, 0, 0)
    dt2 = jdatetime.datetime(1402, 7, 1, 12, 0, 0)
    assert dt1 <= dt2


# __lt__
def test_lt_with_same_datetime():
    dt1 = jdatetime.datetime(1402, 7, 1, 12, 0, 0)
    dt2 = jdatetime.datetime(1402, 7, 1, 12, 0, 0)
    assert not (dt1 < dt2)


def test_lt_with_greater_datetime():
    dt1 = jdatetime.datetime(1402, 7, 2, 12, 0, 0)
    dt2 = jdatetime.datetime(1402, 7, 1, 12, 0, 0)
    assert not (dt1 < dt2)


def test_lt_with_lesser_datetime():
    dt1 = jdatetime.datetime(1402, 6, 30, 12, 0, 0)
    dt2 = jdatetime.datetime(1402, 7, 1, 12, 0, 0)
    assert dt1 < dt2
