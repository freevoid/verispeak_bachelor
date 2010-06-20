import bisect
from functools import partial

from base import Object
import wave

class FileToFeaturesStack(Object):

    READER, RAW_NORM, FRAMER, FRAME_NORM, EXTRACTOR, POST_NORM = range(0, 600, 100)
    NORM_TYPES = (RAW_NORM, FRAME_NORM, POST_NORM)

    def _insert_filter(self, order, func):
        bisect.insort(self.stack, (order, func))

    def _get(self, order):
        idx = bisect.bisect(self.stack, (order, None))
        if idx < len(self.stack):
            if self.stack[idx][0] == order:
                return self.stack[idx]
        return None

    def _pop(self, order):
        idx = bisect.bisect(self.stack, (order, None))
        if idx < len(self.stack):
            if self.stack[idx][0] == order:
                return self.stack.pop(idx)
        return None

    def _replace_filter(self, order, func, **kwargs):
        if kwargs:
            func = partial(func, **kwargs)
        self._pop(order)
        self._insert_filter(order, func)

    def setReader(self, reader, **kwargs):
        self._replace_filter(self.READER, reader, **kwargs)

    def setFramer(self, framer, **kwargs):
        self._replace_filter(self.FRAMER, framer, **kwargs)

    def setExtractor(self, extractor, **kwargs):
        self._replace_filter(self.EXTRACTOR, extractor, **kwargs)

    def addNormalizer(self, type_, func, **kwargs):
        if kwargs:
            func = partial(func, **kwargs)
        self.normalizers.get(type_).append(func)
        if  self._get(type_) is None:
            self._insert_filter(type_, partial(self.normalize, type_=type_))

    def normalize(self, pcm_array, type_):
        for fun in self.normalizers[type_]:
            pcm_array = fun(pcm_array)
        return pcm_array

    def __init__(self, reader=None, extractor=None, framer=None,
            raw_norm=(), frame_norm=(), post_norm=()):
        super(FileToFeaturesStack, self).__init__()
        self.normalizers = {
            self.RAW_NORM: raw_norm,
            self.FRAME_NORM: frame_norm,
            self.POST_NORM: post_norm
        }
        self.stack = []
        if reader:
            self.setReader(reader)
        if framer:
            self.setFramer(framer)
        if extractor:
            self.setExtractor(extractor)

        for type_, norm_stack in self.normalizers.iteritems():
            if norm_stack:
                self._insert_filter(type_, partial(self.normalize, type_=type_))
        
    def process(self, filename):
        """
        Function represents all actions neccessary to obrain
        feature vectors from a filename of an audio file
        """
        import logging
        arg = filename
        for type_, fun in self.stack:
            #print fun.fun.__name__, arg.__class__
            logging.debug("Performing speech transformation of type %s.", type_)
            arg = fun(arg)
            logging.debug("Type after transformation: %s, length: %s", type(arg), len(arg))
        return arg

    __call__ = process

class TemplatedFileToFeaturesStack(FileToFeaturesStack):
    reader = wave.Wave
    framer = None
    extractor = None
    raw_norm = ()
    frame_norm = ()
    post_norm = ()
    def __init__(self):
        super(TemplatedFileToFeaturesStack, self).__init__(
                reader=self.reader,
                framer=self.framer,
                extractor=self.extractor,
                raw_norm=self.raw_norm,
                frame_norm=self.frame_norm,
                post_norm=self.post_norm
                )

