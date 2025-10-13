jdatetime
=========

jdatetime is Jalali_ implementation of Python's datetime module

Status
------

.. image:: https://github.com/slashmili/python-jalali/workflows/Tests/badge.svg?branch=main
   :target: https://github.com/slashmili/python-jalali/actions


.. image:: https://ci.appveyor.com/api/projects/status/ge5rk703ydx649a6?svg=true
   :target: https://ci.appveyor.com/project/slashmili/python-jalali

.. image:: https://img.shields.io/pypi/v/jdatetime.svg
   :target: https://pypi.python.org/pypi/jdatetime

.. image:: https://img.shields.io/pypi/pyversions/jdatetime.svg
   :target: https://pypi.python.org/pypi/jdatetime

Install
-------
``pip install jdatetime``

Documents
---------
This module exactly follows Python Standard datetime module's methods http://docs.python.org/release/3.7.1/library/datetime.html

Also these methods are added to jdatetime.date and jdatetime.datetime :


.. code-block:: python

    fromgregorian(**kw)
        Convert gregorian to jalali and return jdatetime.date
        jdatetime.date.fromgregorian(day=X,month=X,year=X)
        jdatetime.date.fromgregorian(date=datetime.date)
        jdatetime.datetime.fromgregorian(datetime=datetime.datetime)
    togregorian(self)
        Convert current jalali date to gregorian and return datetime.date
    isleap(self)
        check if year is leap year
        algortim is based on http://en.wikipedia.org/wiki/Leap_year


Example
-------

.. code-block:: shell

    >>> import jdatetime
    >>> jdatetime.datetime.now()
    jdatetime.datetime(1394, 12, 4, 8, 37, 31, 855729)
    >>> jdatetime.date.today()
    jdatetime.date(1394, 12, 4)


Locale
------
In order to get the date string in farsi you need to set the locale to `jdatetime.FA_LOCALE`. The locale
could be specified explicitly upon instantiation of `date`/`datetime` instances, or by
setting a default locale.

Instance locales is *named argument only*:

.. code-block:: python

    import jdatetime
    fa_date = jdatetime.date(1397, 4, 23, locale=jdatetime.FA_LOCALE)
    fa_datetime = jdatetime.datetime(1397, 4, 23, 11, 40, 30, locale=jdatetime.FA_LOCALE)


`date` and `datetime` instances provide the method `aslocale()` to return a clone of the instance
with the same timestamp, in a different locale.


Default Locale
~~~~~~~~~~~~~~
It's possible to set the default locale, so all new instances created afterwards would use
the desired locale, unless explicitly specified otherwise.

.. code-block:: shell

    >>> import locale
    >>> import jdatetime
    >> jdatetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S")
    u'Wed, 08 Ord 1395 20:47:32'
    >>> locale.setlocale(locale.LC_ALL, jdatetime.FA_LOCALE)
    'fa_IR'
    >>> jdatetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S")
    u'\u0686\u0647\u0627\u0631\u0634\u0646\u0628\u0647, 08 \u0627\u0631\u062f\u06cc\u0628\u0647\u0634\u062a 1395 20:47:56'


If your requirements demand to support different locales withing the same process,
you could set the default locale per thread. New `date` and `datetime` instances
created in each thread, will use the specified locale by default.
This supports both Python threads, and greenlets.


.. code-block:: python

    import jdatetime
    jdatetime.set_locale(jdatetime.FA_LOCALE)
    jdatetime.datetime.now().strftime('%A %B')
    # u'\u062f\u0648\u0634\u0646\u0628\u0647 \u062e\u0631\u062f\u0627\u062f'

Development
-----------

You can contribute to this project forking it from GitHub and sending pull requests.

First fork_ the repository_ and then clone it:

.. code:: shell

    $ git clone git@github.com:<you>/python-jalali.git

Before committing, you can run all the above tests against all supported Python versions with tox.
You need to install tox first:

.. code:: shell

    $ pip install tox

And then you can run all tests:

.. code:: shell

    $ tox

If you wish to limit the testing to specific Python version, you can parametrize the tox run:

.. code:: shell

    $ tox -e py39

Release Steps
~~~~~~~~~~~~~~
* Bump the ``__VERSION__`` in ``jdatetime/__init__.py``. We are using Semantic Versioning.
* Add release notes in CHANGELOG.md
* Commit and push the changes. Create a PR
* After the PR is merged, create a release with a tag name like `v<version>`
* Github Action creates the package and deploys it to pypi.

.. _Jalali: http://en.wikipedia.org/wiki/Iranian_calendar
.. _fork: https://help.github.com/en/articles/fork-a-repo
.. _repository: https://github.com/slashmili/python-jalali
