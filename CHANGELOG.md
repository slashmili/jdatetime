# Changelog

## [6.1.0] 2026-08-10

### Fixed

* `%I` and `%-I` now render the 12-hour clock instead of duplicating `%H`
* Pass a Gregorian datetime to `tzinfo.dst()` #188
* Use `int` for the `fold` type, matching the standard library #186

### Added

* Add `date.strptime()` and make `date.strptime()`, `datetime.strptime()`, and
  `date.fromisoformat()` preserve subclasses, matching standard library behavior


## [6.0.2] 2026-08-06

### Fixed

* `astimezone()` no longer resets the instance locale to the global default #190

## [6.0.1] - 2026-07-15

### Fixed

* Update type hint #187


## [6.0.0] - 2026-07-13

### Fixed

* Update type hints to match with typeshed #184
* Drop legacy Python 2 bytes support #183

### Add

* Add persian short month for %b #180


## [5.3.0] - 2026-05-19

### Add

* Add type hints


## [5.2.0] - 2025-01-26

### Add

* Support for validating %A %a in strptime  #161

# Changelog

## [5.1.1] - 2025-01-26

### Fixed

* Fix __ne__ for different datetime types #164

## [5.1.0] - 2025-01-13

### Fixed

* Fix compare datetime with diffrent timezones #159

### Add
* Drop Python 3.8 support
* Add support for Python 3.13


## [5.0.0] - 2024-03-26

### Add
* Add support for Python 3.12

### Changed
* BREAKING CHANGE: Arithmetic operations on `date`/`datetime` against an unknown type will now return `NotImplemented` instead of raising `TypeError`
* Drop Python 3.7 support
* Move jalali.py to jalali_core dependency due to licensing issues #148

### Fixed
* treat %% as an escape sequence in strftime

## [4.1.1] - 2023-03-28

### Add
* Add `fromisoformat` method to `jdatetime.date`
* Add support for Python 3.11

### Fixed
* Fix two chars month handling in ``jdatetime.datetime.strptime``

## [4.1.0] - 2022-03-22
### Add
* Add support for ``%z`` directive in ``jdatetime.datetime.strptime`
* Add support for ``%b`` and ``%B`` directive directive in ``jdatetime.datetime.strptime`
### Changed 
* Potential breaking change: Replace spaces with ZWNJ (نیم‌فاصله) in output of ``jdatetime.datetime.strftime`

## [4.0.0] - 2022-02-14
### Add
* Add ``fold`` attribute to ``jdatetime.datetime``

### Change
* Drop Python < 3.7 support

## [3.8.2] - 2022-01-24
### Fixed
* Fix older version objects unpickling problem

## [3.8.1] - 2022-01-17
### Fixed
* Fixed pickle problem of jdate and jdatetime objects(#108)

## [3.8.0] - 2022-01-07
### Fixed
* Fixed unicode literal problem in isoformat

## [3.7.0] - 2021-12-20
### Add
* Add ZoneInfo support

## [3.6.4] - 2021-09-15
### Add
* Add date.min based on cpython implementation
* Add date.max based on cpython implementation

## [3.6.3] - 2020-12-11
### Change
* Run test and publish package from github action

## [3.6.2] - 2019-10-24
### Add
* Support for python 3.7 and 3.8


## [3.6.1] - 2019-09-19
### Fixed
* Fixed %Y length in strptime


## [3.6.0] - 2019-09-10
### Fixed
* improve fromgregorian to handle date and datetime input in Pythonic way


## [3.5.0] - 2019-08-04
## Add
* Adds support for '%-I' format token
### Fixed
* Fixes '12:mm:ss am' display problem in strftime
* Fixes '%X' token in strftime:
* Fixes Week of year, currently it starts with zero and increases every 7 days, ignoring weekdays

## [3.4.0] - 2019-07-16
### Add
* support subtraction with python datetime

## [3.3.0] - 2019-07-13
### Add
* add isoformat for jdatetime.datetime

## [3.2.0] - 2019-02-02
### Add
* add timetuple and timestamp function

## [3.1.0] - 2018-12-25
### Fixed
* Handle naive datatime in replace function

## [3.0.2] - 2018-09-2
### Fixed
* Handle joint alphabetic characters in strptime format

## [3.0.0] - 2018-07-22
### Add
* Added instance "locale" attribute #37
### Change
* date/datetime instances with different locale attrs are not equal anymore #37
###  Fixed
* fixed a bug in %p placeholder #40

## [2.2.0] - 2018-07-07
### Add
* Added padding-less variations of strftime format symbols #36

## [2.1.0] - 2018-06-20
### Add
* Set default date/datetime locales per thread #35

## [2.0.0] - 2018-02-25
### Add
* Support for pytz


The CHANGELOG for [1.X](https://github.com/slashmili/python-jalali/tree/v1.9.1) releases
