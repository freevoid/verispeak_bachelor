class Delegate:
    def __init__(self, fun, kwargs={}, **rest):
        self.fun = fun
        kwargs.update(rest)
        self.kwargs = kwargs

    def __call__(self, *args):
        print "CALL", args, self.kwargs
        return self.fun(*args, **self.kwargs)

