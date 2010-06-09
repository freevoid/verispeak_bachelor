import itertools
import numpy as np
from pylab import plot
cycle_colors = itertools.cycle(['red','green','blue','yellow','magenta','k','orange','lightgreen','cyan'])

def plot_features(features, **kwargs):
    plot(range(len(features)), features, **kwargs)

def plot_features_list(features_list, **kwargs):
    map(plot_features, features_list)

def plot_simple(array, color=None):
    if color is None:
        color = cycle_colors.next()
    plot(np.arange(len(array)), array, color=color)

def plot_amp(source, sample_frequency, color=None, **matplotlib_kwargs):
    if color is None:
        color = cycle_colors.next() 
    time_array = np.arange(len(source)) * 1000.0 / sample_frequency
    plot(time_array, source, color=color, **matplotlib_kwargs)

