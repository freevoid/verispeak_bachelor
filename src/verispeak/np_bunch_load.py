import sys
import numpy as np

YSHAPE = 24
DEFAULT_INITIAL_SIZE = 1024*1024 // YSHAPE
MIN_CUTOFF_LENGTH = 0

def bunch_load(filenames, initial_size=DEFAULT_INITIAL_SIZE,
        verbose=True, filter_func=lambda x: True):
    result_array = np.ndarray((initial_size, YSHAPE), 'float64')
    effective_size = 0
    allocated_size = initial_size

    for filename in filenames:
        f = open(filename)
        new_array = np.load(f)
        if len(new_array) <= MIN_CUTOFF_LENGTH or not isinstance(new_array, np.ndarray): continue

        assert effective_size <= allocated_size
        print "New array from `%s`, shape:" % filename, new_array.shape
        chunk_size, yshape = new_array.shape
        assert YSHAPE == yshape
        effective_size += chunk_size
        if verbose:
            print "Chunk, size %s. updating effective to %s" % (chunk_size, effective_size)
        if effective_size > allocated_size:
            to_allocate = effective_size - allocated_size
            allocated_size += to_allocate
            result_array.resize(allocated_size, YSHAPE)
            assert effective_size == allocated_size
        assert result_array[effective_size-chunk_size:effective_size].size == new_array.size
        result_array[effective_size-chunk_size:effective_size,:] = new_array
        assert len(result_array) == allocated_size
        if verbose:
            print result_array.size

    return result_array, effective_size

if __name__=='__main__':
    files = sys.argv[1:]
    g = bunch_load(files)
