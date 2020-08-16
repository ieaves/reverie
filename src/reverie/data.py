from typing import List

from bs4 import BeautifulSoup as BS
import pandas as pd
import requests
import attr
import functools
import os
import tqdm

def split_pos_pos_rank(value):
    index = next(i for i, v in enumerate(value) if v.isnumeric())
    return value[0:index], value[index:]


def _process_play_team_bye(df):
    ts = df['Player Team (Bye)'].str.split()
    df['bye'] = ts.apply(lambda x: x[-1].strip('()'))
    df['team'] = ts.apply(lambda x: x[-2])
    df['player_name'] = ts.apply(lambda x: ' '.join(x[0:-2]))
    df.drop(columns=['Player Team (Bye)'], inplace=True)
    return df


@attr.s
class FantasyPros:
    ADP_URL = attr.ib(default="https://www.fantasypros.com/nfl/adp/ppr-overall.php")
    PROJ_URL = attr.ib(default="https://www.fantasypros.com/nfl/projections/{position}.php?week=draft")

    def position_projection_url(self, position):
        return self.PROJ_URL.format(position=position)

    @staticmethod
    def request(url: str) -> BS:
        res = requests.get(url)
        if not res.ok:
            raise Exception(f"Request to {url} failed with {res.status_code}")
        return BS(res.content, 'html.parser')

    @functools.cached_property
    def adp_df(self) -> pd.DataFrame:
        soup = self.request(self.ADP_URL)
        table = soup.find('table', {'id': 'data'})
        df = pd.read_html(str(table))[0]

        df = _process_play_team_bye(df)

        ts = df['POS'].apply(split_pos_pos_rank)
        df['position'] = ts.str.get(0)
        df['position_rank'] = ts.str.get(1)
        df.drop(columns=['POS'], inplace=True)

        return df

    @functools.cached_property
    def projections_df(self) -> pd.DataFrame:
        def get_position_df(position: str) -> pd.DataFrame:
            soup = self.request(self.position_projection_url(position))
            table = soup.find('table', {'id': 'data'})
            df = pd.read_html(str(table))[0]
            if isinstance(df.columns, pd.core.indexes.multi.MultiIndex):
                df.columns = ["_".join(('' if 'Unnamed' in l0 else l0, l1)).lstrip("_") for l0, l1 in df.columns]
            df['position'] = position.upper()
            return df

        # url has positions in lower case
        positions = ['rb', 'qb', 'te', 'wr', 'k', 'dst']
        df = pd.concat(get_position_df(position) for position in positions)
        df['player_name'] = df['Player'].apply(lambda x: ' '.join(x.split()[:-1]))
        df.drop(columns=['Player'], inplace=True)
        df = df.drop_duplicates()
        return df

@attr.s
class HistoricalADP:
    BASE_URL = attr.ib("https://fantasyfootballcalculator.com/adp/standard/12-team/all/{year}")
    earliest_supported_year = attr.ib(default=2007)

    def get_url_for_year(self, year):
        return self.BASE_URL.format(year=year)

    @staticmethod
    def request(url: str) -> BS:
        res = requests.get(url)
        if not res.ok:
            raise Exception(f"Request to {url} failed with {res.status_code}")
        return BS(res.content, 'html.parser')

    def get_adp_for_year(self, year):
        soup = self.request(self.get_url_for_year(year))
        table = soup.find("table", {"class": "table adp"})
        df = pd.read_html(str(table))[0]
        nulls = df.isna().all()
        df.drop(columns=nulls[nulls].index.values, inplace=True)
        return df


def populate_historical_adp(write_directory: str, years: List[int]) -> None:
    ffc_adp = HistoricalADP()
    os.makedirs(write_directory, exist_ok=True)
    for year in tqdm.tqdm(years):
        filename = os.path.join(write_directory, f'{year}.parquet')
        df = ffc_adp.get_adp_for_year(year)
        df.to_parquet(filename, engine='pyarrow')

