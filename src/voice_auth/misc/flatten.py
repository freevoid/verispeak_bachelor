from collections import Iterable
def flatiter(iterable):
    '''
    >>> x = [1, (2, ['three', 4], 'five'), 6, 7]
    >>> list(flatiter(x))
    [1, 2, 'three', 4, 'five', 6, 7]
    '''
    stack = [iter(iterable)]
    while stack:
        current = stack.pop()
        for i in current:
            if isinstance(i, Iterable) and not isinstance(i, basestring):
                stack.append(current)
                stack.append(iter(i))
                break
            else:
                yield i

if __name__=='__main__':
    import doctest
    doctest.testmod()

