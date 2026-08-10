import datetime
import sys
import threading
from typing import Any
from zoneinfo import ZoneInfo

import pytest

import jdatetime

try:
    import greenlet  # type: ignore
except ImportError:
    greenlet: Any = None


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


def test_get_locale_returns_none_if_no_locale_set_yet():
    assert jdatetime.get_locale() is None


@pytest.mark.skipif(greenlet is not None, reason='thread ident is used when greenlet is not installed')
def test_set_locale_is_per_thread_with_no_effect_on_other_threads():
    event = threading.Event()
    fa_record = []
    fa_thread = threading.Thread(target=record_thread_locale, args=(fa_record, event, 'fa_IR'))
    nl_record = []
    nl_thread = threading.Thread(target=record_thread_locale, args=(nl_record, event, 'nl_NL'))

    fa_thread.start()
    nl_thread.start()
    event.set()  # ensure both threads run concurrently
    fa_thread.join()
    nl_thread.join()

    assert len(fa_record) == 1
    assert fa_record[0] == 'fa_IR'
    assert len(nl_record) == 1
    assert nl_record[0] == 'nl_NL'
    assert jdatetime.get_locale() is None  # MainThread is not affected neither


@pytest.mark.skipif(greenlet is None, reason='greenlets ident is used when greenlet module is installed')
def test_set_locale_is_per_greenlet_with_no_effect_on_other_greenlets():
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

    assert len(fa_record) == 1
    assert fa_record[0] == 'fa_IR'
    assert len(nl_record) == 1
    assert nl_record[0] == 'nl_NL'


@pytest.mark.skipif(greenlet is not None, reason='thread ident is used when greenlet is not installed')
def test_set_locale_sets_default_locale_for_date_objects():
    def record_locale_formatted_date(record, locale):
        jdatetime.set_locale(locale)
        dt = jdatetime.date(1397, 3, 27)
        record.append(dt.strftime('%A'))
        record.append(dt.strftime('%B'))

    fa_record = []
    fa_th = threading.Thread(target=record_locale_formatted_date, args=(fa_record, jdatetime.FA_LOCALE))
    fa_th.start()
    fa_th.join()

    assert fa_record == ['یک‌شنبه', 'خرداد']


@pytest.mark.skipif(greenlet is None, reason='greenlets ident is used when greenlet module is installed')
def test_set_locale_sets_default_locale_for_date_objects_with_greenlets():
    def record_locale_formatted_date(record, locale):
        jdatetime.set_locale(locale)
        dt = jdatetime.date(1397, 3, 27)
        record.append(dt.strftime('%A'))
        record.append(dt.strftime('%B'))

    fa_record = []
    fa_greenlet = greenlet.greenlet(record_locale_formatted_date)
    fa_greenlet.switch(fa_record, jdatetime.FA_LOCALE)

    assert fa_record == ['یک‌شنبه', 'خرداد']


def test_fromisoformat():
    UTC = datetime.timezone.utc

    assert jdatetime.datetime.fromisoformat('1402-01-03T15:35:59.898169') == jdatetime.datetime(
        1402, 1, 3, 15, 35, 59, 898169
    )

    assert jdatetime.datetime.fromisoformat('1401-11-04 00:05:23.283') == jdatetime.datetime(
        1401, 11, 4, 0, 5, 23, 283000
    )

    assert jdatetime.datetime.fromisoformat('1403-11-04 00:05:23.283+00:00') == jdatetime.datetime(
        1403, 11, 4, 0, 5, 23, 283000, tzinfo=UTC
    )

    assert jdatetime.datetime.fromisoformat('1400-11-04T00:05:23+04:00') == jdatetime.datetime(
        1400, 11, 4, 0, 5, 23, 0, tzinfo=datetime.timezone(datetime.timedelta(seconds=14400))
    )

    assert jdatetime.datetime.fromisoformat('14020101') == jdatetime.datetime(1402, 1, 1)

    if sys.version_info[:2] >= (3, 11):  # new Python 3.11 time formats
        assert jdatetime.datetime.fromisoformat('1402-02-31T00:05:23Z') == jdatetime.datetime(
            1402, 2, 31, 0, 5, 23, 0, tzinfo=UTC
        )

        assert jdatetime.datetime.fromisoformat('14031230T010203') == jdatetime.datetime(
            1403, 12, 30, 1, 2, 3
        )


def test_unknown_type_operations():
    dt = jdatetime.datetime(1402, 1, 9)
    unknown_type = object()

    assert dt.__sub__(unknown_type) is NotImplemented  # type: ignore
    assert dt.__rsub__(unknown_type) is NotImplemented  # type: ignore
    assert dt.__add__(unknown_type) is NotImplemented  # type: ignore
    assert dt.__radd__(unknown_type) is NotImplemented  # type: ignore
    assert dt.__eq__(unknown_type) is NotImplemented
    assert dt.__ne__(unknown_type) is NotImplemented
    assert dt.__lt__(unknown_type) is NotImplemented  # type: ignore
    assert dt.__le__(unknown_type) is NotImplemented  # type: ignore
    assert dt.__gt__(unknown_type) is NotImplemented  # type: ignore
    assert dt.__ge__(unknown_type) is NotImplemented  # type: ignore

    with pytest.raises(TypeError, match=r"unsupported operand type\(s\) for \-=: 'datetime' and 'object'"):
        dt -= unknown_type  # type: ignore


def test_resolution():
    assert jdatetime.datetime.resolution == jdatetime.timedelta(microseconds=1)


def test_min_max():
    assert jdatetime.datetime.max == jdatetime.datetime(9377, 12, 12, 23, 59, 59, 999999)
    assert jdatetime.datetime.min == jdatetime.datetime(1, 1, 1, 0, 0)


def test_dst_calculation_with_timezone():
    # Let's use America/New_York timezone
    # In 2026:
    # July 17 (Jalali: 1405-04-26) is in DST (+1 hour offset)
    # Dec 17 (Jalali: 1405-09-26) is NOT in DST (0 offset)
    tz = ZoneInfo('America/New_York')

    # 1. Test during Daylight Saving Time (Summer)
    summer_jdt = jdatetime.datetime(1405, 4, 26, 12, 0, tzinfo=tz)
    assert summer_jdt.dst() == jdatetime.timedelta(hours=1)

    # 2. Test during Standard Time (Winter)
    winter_jdt = jdatetime.datetime(1405, 9, 26, 12, 0, tzinfo=tz)
    assert winter_jdt.dst() == jdatetime.timedelta(0)


def test_dst_returns_none_without_tz():
    # Naive datetime should return None
    naive_jdt = jdatetime.datetime(1405, 4, 26, 12, 0)
    assert naive_jdt.dst() is None
