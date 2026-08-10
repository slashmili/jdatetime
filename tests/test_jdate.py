import datetime
import pickle
import time

import pytest

import jdatetime
from tests import load_pickle


def test_as_locale_returns_same_date_with_specified_locale():
    jdate_en = jdatetime.date(1397, 4, 23, locale='en_US')
    jdate_fa = jdate_en.aslocale('fa_IR')
    assert jdate_fa.year == 1397
    assert jdate_fa.month == 4
    assert jdate_fa.day == 23
    assert jdate_fa.locale == 'fa_IR'


def test_init_locale_is_effective_only_if_not_none():
    orig_locale = jdatetime.get_locale()
    jdatetime.set_locale('en_US')
    try:
        date = jdatetime.date(1397, 4, 22, locale=None)
        assert date.locale == 'en_US'
    finally:
        jdatetime.set_locale(orig_locale)


def test_init_locale_is_effective_only_if_not_empty():
    orig_locale = jdatetime.get_locale()
    jdatetime.set_locale('nl_NL')
    try:
        date = jdatetime.date(1397, 4, 22, locale='')
        assert date.locale == 'nl_NL'
    finally:
        jdatetime.set_locale(orig_locale)


def test_locale_property_is_read_only():
    date = jdatetime.date(1397, 4, 22)
    with pytest.raises(AttributeError):
        date.locale = jdatetime.FA_LOCALE  # type: ignore


def test_locale_property_returns_locale():
    date = jdatetime.date(1397, 4, 22, locale='nl_NL')
    assert date.locale == 'nl_NL'


def test_init_locale_is_named_argument_only():
    with pytest.raises(TypeError):
        datetime.date(1397, 4, 22, 'nl_NL')  # type: ignore


def test_init_accepts_instance_locale():
    date = jdatetime.date(1397, 4, 23, locale=jdatetime.FA_LOCALE)
    assert date.strftime('%A') == 'شنبه'


def test_dates_are_not_equal_if_locales_are_different():
    date_fa = jdatetime.date(1397, 4, 22, locale='fa_IR')
    date_nl = jdatetime.date(1397, 4, 22, locale='nl_NL')
    assert date_fa != date_nl


def test_fromgregorian_accepts_locale_keyword_arg_when_datetime_passed():
    today = datetime.datetime.today().date()
    j_today = jdatetime.date.fromgregorian(date=today, locale='nl_NL')
    assert j_today.locale == 'nl_NL'


def test_fromgregorian_accepts_locale_keyword_arg_when_int_passed():
    j_today = jdatetime.date.fromgregorian(day=15, month=7, year=2018, locale='nl_NL')
    assert j_today.locale == 'nl_NL'


def test_togregorian_leap():
    assert jdatetime.date(1402, 12, 9).togregorian() == datetime.date(2024, 2, 28)
    assert jdatetime.date(1402, 12, 10).togregorian() == datetime.date(2024, 2, 29)
    assert jdatetime.date(1402, 12, 11).togregorian() == datetime.date(2024, 3, 1)


def test_replace_keeps_the_locale_of_source_date():
    date = jdatetime.date(1397, 4, 22, locale='nl_NL')
    other_date = date.replace(day=20)
    assert other_date.day == 20
    assert other_date.locale == 'nl_NL'


def test_add_time_delta():
    date = jdatetime.date(1397, 4, 22, locale='nl_NL')
    new_date = date + datetime.timedelta(days=1)
    assert new_date.year == 1397
    assert new_date.month == 4
    assert new_date.day == 23
    assert new_date.locale == 'nl_NL'


def test_unknown_type_operations():
    date = jdatetime.date(1402, 1, 9)
    unknown_type = object()
    assert date.__sub__(unknown_type) is NotImplemented  # type: ignore
    assert date.__rsub__(unknown_type) is NotImplemented  # type: ignore
    assert date.__add__(unknown_type) is NotImplemented  # type: ignore
    assert date.__radd__(unknown_type) is NotImplemented  # type: ignore
    assert date.__eq__(unknown_type) is NotImplemented
    assert date.__ne__(unknown_type) is NotImplemented
    assert date.__lt__(unknown_type) is NotImplemented  # type: ignore
    assert date.__le__(unknown_type) is NotImplemented  # type: ignore
    assert date.__gt__(unknown_type) is NotImplemented  # type: ignore
    assert date.__ge__(unknown_type) is NotImplemented  # type: ignore

    with pytest.raises(TypeError, match=r"unsupported operand type\(s\) for \+=: 'date' and 'object'"):
        date += unknown_type  # type: ignore


def test_reverse_add_time_delta():
    date = jdatetime.date(1397, 4, 22, locale='nl_NL')
    new_date = datetime.timedelta(days=2) + date
    assert new_date.year == 1397
    assert new_date.month == 4
    assert new_date.day == 24
    assert new_date.locale == 'nl_NL'


def test_subtract_time_delta():
    date = jdatetime.date(1397, 4, 22, locale='nl_NL')
    new_date = date - datetime.timedelta(days=1)
    assert new_date.year == 1397
    assert new_date.month == 4
    assert new_date.day == 21
    assert new_date.locale == 'nl_NL'


def test_subtract_datetime_date():
    date = jdatetime.date(1397, 4, 22, locale='nl_NL')
    delta = date - datetime.date(2018, 7, 12)
    assert delta.days == 1


def test_timetuple():
    date = jdatetime.date(1397, 4, 22)
    assert date.timetuple() == time.struct_time((2018, 7, 13, 0, 0, 0, 4, 194, -1))


def test_all_weekdays():
    date = jdatetime.date(1394, 1, 1)  # it is saturday
    for i in range(7):  # test the whole week
        assert (date + datetime.timedelta(days=i)).weekday() == i


def test_max_year():
    dmax = jdatetime.date.max
    assert isinstance(dmax, jdatetime.date)
    assert dmax.year == jdatetime.MAXYEAR

    with pytest.raises(ValueError):
        jdatetime.date(jdatetime.MAXYEAR + 1, 1, 1)

    # Should raise an exception when we go over date.max
    with pytest.raises(ValueError):
        _ = dmax + jdatetime.date.resolution


def test_min_year():
    dmin = jdatetime.date.min
    assert isinstance(dmin, jdatetime.date)
    assert dmin.year == jdatetime.MINYEAR

    with pytest.raises(ValueError):
        jdatetime.date(jdatetime.MINYEAR - 1, 1, 1)

    # Should raise an exception when we ge below date.min
    with pytest.raises(ValueError):
        _ = dmin - jdatetime.date.resolution


def test_pickle():
    d = jdatetime.date.today()
    assert pickle.loads(pickle.dumps(d)) == d


def test_unpickle_older_date_object():
    d = load_pickle('jdate_py3_jdatetime3.7.pickle')
    assert d == jdatetime.date(1400, 10, 11)


def test_fromisoformat():
    assert jdatetime.date.fromisoformat('1378-02-22') == jdatetime.date(day=22, month=2, year=1378)

    # new Python 3.11 format
    assert jdatetime.date.fromisoformat('14020231') == jdatetime.date(1402, 2, 31)

    with pytest.raises(ValueError, match="Invalid isoformat string: 'some-invalid-format'"):
        jdatetime.date.fromisoformat('some-invalid-format')

    with pytest.raises(TypeError, match='fromisoformat: argument must be str'):
        jdatetime.date.fromisoformat(1)  # type: ignore


def test_resolution():
    assert jdatetime.date.resolution == jdatetime.timedelta(days=1)


@pytest.mark.parametrize(
    ('date_string', 'format'),
    [
        ('1405-05-19', '%Y-%m-%d'),
        ('1405-05-19 13', '%Y-%m-%d %H'),
        ('1405-05-19 13:45', '%Y-%m-%d %H:%M'),
        ('1405-05-19 13:45:59', '%Y-%m-%d %H:%M:%S'),
        ('1405-05-19 13:45:59.123456', '%Y-%m-%d %H:%M:%S.%f'),
        ('1405-05-19 13:45:59 +0330', '%Y-%m-%d %H:%M:%S %z'),
    ],
)
def test_strptime_discards_time(date_string, format):
    result = jdatetime.date.strptime(date_string, format)

    assert result == jdatetime.date(1405, 5, 19)


def test_strptime_returns_subclass():
    class MyDate(jdatetime.date):
        pass

    result = MyDate.strptime('1405-05-19', '%Y-%m-%d')

    assert type(result) is MyDate
    assert result == MyDate(1405, 5, 19)
