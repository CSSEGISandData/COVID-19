from datetime import datetime
from pathlib import Path
from typing import Any, List, Tuple, Union

import numpy as np


_DATA_DIR = Path('csse_covid_19_data/csse_covid_19_time_series')
CONFIRMED_CSV = _DATA_DIR / 'time_series_19-covid-Confirmed.csv'
DEATHS_CSV = _DATA_DIR / 'time_series_19-covid-Deaths.csv'
RECOVERED_CSV = _DATA_DIR / 'time_series_19-covid-Recovered.csv'


def attempt_datetime_cast(v: str) -> Union[str, datetime]:
    try:
        return datetime.strptime(v, '%m/%d/%y')
    except ValueError:
        return v


class CovidData:
    def __init__(self, unstructdata: List[List[Union[str, int]]]):
        self.headers: Tuple[Union[str, datetime]] = tuple([attempt_datetime_cast(h)
                                                           for h in unstructdata[0]])
        self.data = np.array(unstructdata[1:]).astype(object)  # exclude the heeaders
        self._nm = 4
        _data = (self.data[:, self._nm:]).astype(int)
        self.data[:, self._nm:] = _data
        self.dates = np.array(self.headers[self._nm:], dtype=datetime)
        self._country_idx = self.cidx('Country/Region')
        self.countries = set(self.data[:, self._country_idx])

    def cidx(self, header: Union[str, datetime]) -> int:
        return self.headers.index(header)

    def get_country(self, loc: str) -> np.ndarray:
        assert loc in self.countries, f'Could not find data for country {loc}'
        rows = self.data[:, self._country_idx] == loc
        return np.sum(self.data[rows, self._nm:], axis=0)

    def get_date(self, date: datetime) -> np.ndarray:
        assert date in self.dates, f'Cound not find entries for date {date}'
        cidx = self.cidx(date)
        return self.data[:, cidx]


def cast(val: str, return_type: Any) -> Any:
    try:
        return return_type(val)
    except (ValueError, TypeError) as err:
        raise err


def parse_time_series(fpath: Path) -> CovidData:
    with open(fpath, 'r') as f:
        lines = [line.strip('\n').replace('\t', '').split(',') for line in f]
    skiplines = 1
    cnt = 0
    for l in lines:
        if cnt <= skiplines:
            cnt += 1
        else:
            if '"Korea' == l[1]:
                l[1] = 'South Korea'
                l.pop(2)
            if len(l) > len(lines[0]):  # should be safe as long as headers don't change
                l[0] = f'{l[0]}, {l[1]}'
                l.pop(1)
            for cidx, val in enumerate(l):
                try:
                    if cidx > 3:
                        l[cidx] = cast(val, int)
                except ValueError as err:
                    print(len(l), l)
                    print(f'Could not cast {val} to int. \nrow={lines.index(l)}\tcol={cidx}')
                    raise err
    return lines


if __name__ == '__main__':
    conf = CovidData(parse_time_series(CONFIRMED_CSV))
    dead = CovidData(parse_time_series(DEATHS_CSV))
    rcvd = CovidData(parse_time_series(RECOVERED_CSV))

    import matplotlib.pyplot as plt
    from util.analysis import create_gridlines
    data = conf

    _, (ax, ax2) = plt.subplots(nrows=2, sharex=True)
    for country in ('US', 'Italy', 'Spain', 'South Korea', 'Iran'):
        try:
            start_mask = data.get_country(country) > 100
            days_elapsed = [dt.days for dt in data.dates[start_mask] - data.dates[start_mask][0]]
            y = data.get_country(country)[start_mask]
            ax.plot(days_elapsed, y, '.-', alpha=0.75, label=country)
            ax2.plot(days_elapsed, np.gradient(y), '.-', alpha=0.75, label=country)
        except IndexError:
            continue
    ax.legend(loc=0, ncol=2 if len(ax.get_legend_handles_labels()[0]) > 4 else 1)
    ax.set_ylabel('Confirmed Cases')
    ax2.set_xlabel('Days Passed Since 100th Confirmed Case')
    ax2.set_ylabel('Rate of New Confirmed Cases')
    create_gridlines(ax=ax)
    create_gridlines(ax=ax2)
    ax.set_title(f'COVID-19 Update: {datetime.today().strftime("%Y-%m-%d")}')
    plt.show()
