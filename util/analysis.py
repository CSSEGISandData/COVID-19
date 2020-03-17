from typing import List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import t


class BasicStats:
    def __init__(self, vals: Union[List[float], np.ndarray], ddof: int = 0):
        self.vals = vals
        self.mean = np.mean(self.vals)
        self.min = np.min(self.vals)
        self.max = np.max(self.vals)
        self.std = np.std(self.vals, ddof=ddof)
        self.ci = self.calculate_confidence()

    def print_percent_spec(self, spec: float) -> None:
        print(f'Mean %: {100 * self.mean / spec:.0f}%')
        print(f'Min %: {100 * self.min / spec:.0f}%')
        print(f'Max %: {100 *self.max / spec:.0f}%')
        print(f'Stdv %: {100 * self.std / spec:.0f}%')

    def __repr__(self):
        return f'Mean: {self.mean:.2f}\nMin: {self.min:.2f}\nMax: {self.max:.2f}\nStdv: {self.std:.3f}'

    def __str__(self):
        return self.__repr__()

    def calculate_confidence(self, conf_level: float = 0.95) -> Tuple[float, float]:
        # t = scipy.stats.t
        crit_value = t.ppf(conf_level, df=len(self.vals) - 1)
        term2 = crit_value * (self.std / np.sqrt(len(self.vals)))
        ci1 = self.mean - term2
        ci2 = self.mean + term2
        return (ci1, ci2)

    def print_confidence_interval(self, conf_level: float = 0.95) -> None:
        ci = self.calculate_confidence(conf_level=conf_level)
        print(f'{int(conf_level * 100)}% Confidence interval = {ci[0]:.2f} - {ci[1]:.2f}')
        print(f'Range = {abs(ci[1] - ci[0]):.2f} Mean = {np.mean(ci):.2f}')


def fill_region(x: List[float],
                lower: float,
                upper: float,
                kwargs: Optional[dict] = None,
                ax: plt.Axes = None) -> None:
    """ Fills a region of a matplotlib plot. Frequently used to overlay things like specifcation
    regions or windows on top of data. 'kwargs' gets passed directly into a call to
    'plt.fill_between()', so refer to that documentation on available keywords.

    Arguments:
        x {List[float]} -- start and end X position to draw the region
        lower {float} -- lower limit of the region to draw
        upper {float} -- upper limit of the region to draw

    Keyword Arguments:
        kwargs {Optional[dict]} -- optional keywords to pass on, a common 'kwargs' looks like:
            {
                'color': green,
                'alpha': 0.2,
                'label': 'In-Spec'
            }
            (default: {None})
        ax {plt.Axes} -- Axes object to draw the region onto (default: {None})

    Returns:
        plt.Axes -- Axes object with the drawn region
    """
    ax = ax if ax is not None else plt.gca()
    kwargs = kwargs if kwargs is not None else {}
    ax.fill_between(x, [lower]*2, [upper]*2, **kwargs)


def create_gridlines(ax: plt.Axes = None) -> None:
    """ Places gridlines on a 2D Axes object.

    Keyword Arguments:
        ax {plt.Axes} -- which Axes object to use, defaults to the current active Axes if one isn't
            passed in (default: {None})

    Returns:
        None
    """
    ax = ax if ax is not None else plt.gca()
    ax.grid(b=True, which='major', color='k', alpha=0.3)
    ax.grid(b=True, which='minor', color='k', alpha=0.1, linestyle='--')
    ax.minorticks_on()
