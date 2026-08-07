import pathlib
import pickle

import jdatetime


def load_pickle(filename):
    pickle_path = pathlib.Path(__file__).parent / 'pickled_objects' / filename
    with pickle_path.open('rb') as f:
        return pickle.load(f)


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
