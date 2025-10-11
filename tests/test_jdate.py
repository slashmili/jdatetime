import datetime
import pickle
import time
from unittest import TestCase

import jdatetime
from tests import load_pickle


class TestJDate(TestCase):
    def test_as_locale_returns_same_date_with_specified_locale(self):
        jdate_en = jdatetime.date(1397, 4, 23, locale='en_US')
        jdate_fa = jdate_en.aslocale('fa_IR')
        self.assertEqual(jdate_fa.year, 1397)
        self.assertEqual(jdate_fa.month, 4)
        self.assertEqual(jdate_fa.day, 23)
        self.assertEqual(jdate_fa.locale, 'fa_IR')

    def test_init_locale_is_effective_only_if_not_none(self):
        orig_locale = jdatetime.get_locale()
        jdatetime.set_locale('en_US')
        self.addCleanup(jdatetime.set_locale, orig_locale)
        date = jdatetime.date(1397, 4, 22, locale=None)
        self.assertEqual(date.locale, 'en_US')

    def test_init_locale_is_effective_only_if_not_empty(self):
        orig_locale = jdatetime.get_locale()
        jdatetime.set_locale('nl_NL')
        self.addCleanup(jdatetime.set_locale, orig_locale)
        date = jdatetime.date(1397, 4, 22, locale='')
        self.assertEqual(date.locale, 'nl_NL')

    def test_locale_property_is_read_only(self):
        date = jdatetime.date(1397, 4, 22)
        with self.assertRaises(AttributeError):
            date.locale = jdatetime.FA_LOCALE

    def test_locale_property_returns_locale(self):
        date = jdatetime.date(1397, 4, 22, locale='nl_NL')
        self.assertEqual(date.locale, 'nl_NL')

    def test_init_locale_is_named_argument_only(self):
        with self.assertRaises(TypeError):
            datetime.date(1397, 4, 22, 'nl_NL')

    def test_init_accepts_instance_locale(self):
        date = jdatetime.date(1397, 4, 23, locale=jdatetime.FA_LOCALE)
        self.assertEqual(date.strftime('%A'), 'شنبه')

    def test_dates_are_not_equal_if_locales_are_different(self):
        date_fa = jdatetime.date(1397, 4, 22, locale='fa_IR')
        date_nl = jdatetime.date(1397, 4, 22, locale='nl_NL')
        self.assertNotEqual(date_fa, date_nl)

    def test_fromgregorian_accepts_locale_keyword_arg_when_datetime_passed(
        self,
    ):
        today = datetime.datetime.today().date()
        j_today = jdatetime.date.fromgregorian(date=today, locale='nl_NL')
        self.assertEqual(j_today.locale, 'nl_NL')

    def test_fromgregorian_accepts_locale_keyword_arg_when_int_passed(self):
        j_today = jdatetime.date.fromgregorian(day=15, month=7, year=2018, locale='nl_NL')
        self.assertEqual(j_today.locale, 'nl_NL')

    def test_togregorian_leap(self):
        self.assertEqual(
            jdatetime.date(1402, 12, 9).togregorian(),
            datetime.date(2024, 2, 28),
        )
        self.assertEqual(
            jdatetime.date(1402, 12, 10).togregorian(),
            datetime.date(2024, 2, 29),
        )
        self.assertEqual(
            jdatetime.date(1402, 12, 11).togregorian(),
            datetime.date(2024, 3, 1),
        )

    def test_replace_keeps_the_locale_of_source_date(self):
        date = jdatetime.date(1397, 4, 22, locale='nl_NL')
        other_date = date.replace(day=20)
        self.assertEqual(other_date.day, 20)
        self.assertEqual(other_date.locale, 'nl_NL')

    def test_add_time_delta(self):
        date = jdatetime.date(1397, 4, 22, locale='nl_NL')
        new_date = date + datetime.timedelta(days=1)
        self.assertEqual(new_date.year, 1397)
        self.assertEqual(new_date.month, 4)
        self.assertEqual(new_date.day, 23)
        self.assertEqual(new_date.locale, 'nl_NL')

    def test_unknown_type_operations(self):
        date = jdatetime.date(1402, 1, 9)
        unknown_type = object()
        assert (
            date.__sub__(unknown_type)
            is date.__rsub__(unknown_type)
            is date.__add__(unknown_type)
            is date.__radd__(unknown_type)
            is date.__eq__(unknown_type)
            is date.__ne__(unknown_type)
            is date.__lt__(unknown_type)
            is date.__le__(unknown_type)
            is date.__gt__(unknown_type)
            is date.__ge__(unknown_type)
            is NotImplemented
        )
        with self.assertRaisesRegex(
            TypeError,
            r"unsupported operand type\(s\) for \+=: 'date' and 'object'",
        ):
            date += unknown_type

    def test_reverse_add_time_delta(self):
        date = jdatetime.date(1397, 4, 22, locale='nl_NL')
        new_date = datetime.timedelta(days=2) + date
        self.assertEqual(new_date.year, 1397)
        self.assertEqual(new_date.month, 4)
        self.assertEqual(new_date.day, 24)
        self.assertEqual(new_date.locale, 'nl_NL')

    def test_subtract_time_delta(self):
        date = jdatetime.date(1397, 4, 22, locale='nl_NL')
        new_date = date - datetime.timedelta(days=1)
        self.assertEqual(new_date.year, 1397)
        self.assertEqual(new_date.month, 4)
        self.assertEqual(new_date.day, 21)
        self.assertEqual(new_date.locale, 'nl_NL')

    def test_subtract_datetime_date(self):
        date = jdatetime.date(1397, 4, 22, locale='nl_NL')
        delta = date - datetime.date(2018, 7, 12)
        self.assertEqual(delta.days, 1)

    def test_timetuple(self):
        date = jdatetime.date(
            1397,
            4,
            22,
        )
        self.assertEqual(
            date.timetuple(),
            time.struct_time((2018, 7, 13, 0, 0, 0, 4, 194, -1)),
        )

    def test_all_weekdays(self):
        date = jdatetime.date(1394, 1, 1)  # it is saturday
        for i in range(7):  # test th whole week
            self.assertEqual((date + datetime.timedelta(days=i)).weekday(), i)

    def test_max_year(self):
        dmax = jdatetime.date.max
        self.assertTrue(isinstance(dmax, jdatetime.date))
        self.assertEqual(dmax.year, jdatetime.MAXYEAR)
        self.assertRaises(ValueError, jdatetime.date, jdatetime.MAXYEAR + 1, 1, 1)
        with self.assertRaises(
            ValueError,
            msg='Should raise an exception when we go over date.max',
        ):
            _ = dmax + jdatetime.date.resolution

    def test_min_year(self):
        dmin = jdatetime.date.min
        self.assertTrue(isinstance(dmin, jdatetime.date))
        self.assertEqual(dmin.year, jdatetime.MINYEAR)
        self.assertRaises(ValueError, jdatetime.date, jdatetime.MINYEAR - 1, 1, 1)
        with self.assertRaises(
            ValueError,
            msg='Should raise an exception when we ge below date.min',
        ):
            _ = dmin - jdatetime.date.resolution

    def test_pickle(self):
        d = jdatetime.date.today()
        self.assertEqual(pickle.loads(pickle.dumps(d)), d)

    def test_unpickle_older_date_object(self):
        d = load_pickle('jdate_py3_jdatetime3.7.pickle')
        self.assertEqual(d, jdatetime.date(1400, 10, 11))

    def test_fromisoformat(self):
        self.assertEqual(
            jdatetime.date.fromisoformat('1378-02-22'),
            jdatetime.date(day=22, month=2, year=1378),
        )

        self.assertEqual(  # new Python 3.11 format
            jdatetime.date.fromisoformat('14020231'),
            jdatetime.date(1402, 2, 31),
        )

        with self.assertRaises(ValueError, msg="Invalid isoformat string: 'some-invalid-format'"):
            jdatetime.date.fromisoformat('some-invalid-format')

        with self.assertRaises(TypeError, msg='fromisoformat: argument must be str'):
            jdatetime.date.fromisoformat(1)
