import pathlib
import pickle


def load_pickle(filename):
    pickle_path = pathlib.Path(__file__).parent / 'pickled_objects' / filename
    with pickle_path.open('rb') as f:
        return pickle.load(f)
