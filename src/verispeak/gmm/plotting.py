# -*- coding: utf-8 -*-
from verispeak.ruplot import pyplot
from verispeak.base import Object

class GMMPlotter(Object):
    def __init__(self, gmm):
        assert hasattr(gmm, 'get_params')
        self.gmm = gmm
        self.refresh_params()

        maxvar = 3*self.sigmas.max()
        self.set_lim(self.mus.min() - maxvar, self.mus.max() + maxvar)
        self._pdfs = {}

        self._cache_dirty = False

    def refresh_params(self):
        self.weights, self.mus, self.sigmas = self.gmm.get_params()

    @staticmethod
    def plot_mfcc_pdf(samples, idx, bins=30, align_lim=True, **plotargs):
        pyplot.title(u"Гистограмма распределения")
        pyplot.xlabel(u"Значение кепстрального коэффициента")
        pyplot.ylabel(u"Вероятность")
        return pyplot.hist(samples[:, idx], bins=bins, normed=True,
                **plotargs)

    def plot_mfcc_and_align(self, samples, idx, bins=30, **plotargs):
        vals, bins, patches = self.plot_mfcc_pdf(samples, idx, bins=bins, **plotargs)
        self.set_lim(bins[0], bins[-1])
        self._cache_dirty = True
        return vals, bins, patches

    def set_lim(self, min, max):
        self._min, self._max = min, max
        self._interval = max - min

    def _prepare_pdfs(self, idx, divs):
        pyplot.title(u"Плотность распределения смеси")
        pyplot.xlabel(u"Значение кепстрального коэффициента")
        pyplot.ylabel(u"Вероятность")
        if self._pdfs.has_key((idx, divs)) and not self._cache_dirty: return self._pdfs[(idx, divs)]
        gmm = self.gmm

        mus = self.mus[:, idx]
        sigmas = self.sigmas[:, idx]

        bins = np.arange(self._min, self._max, self._interval / divs)
        from scipy import stats
        norms = (stats.norm(mu, sigma) for (mu, sigma) in zip(mus, sigmas))
        pdfs = [self.weights[i]*norm.pdf(bins) for i, norm in enumerate(norms)]
        self._pdfs[(idx, divs)] = (bins, pdfs)
        self._cache_dirty = False
        return bins, pdfs

    def plot_component_pdfs(self, idx, divs=100, **plotargs):
        bins, pdfs = self._prepare_pdfs(idx, divs)
        for pdf in pdfs:
            pyplot.plot(bins, pdf, **plotargs)

    def plot_overall_pdf(self, idx, divs=100, **plotargs):
        bins, pdfs = self._prepare_pdfs(idx, divs)
        return pyplot.plot(bins, sum(pdfs), **plotargs)

