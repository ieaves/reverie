import nflgame
import reverie as rev
import os
import pandas as pd
import tqdm

dir_path = os.path.dirname(os.path.realpath(__file__))
output_directory = os.path.abspath(os.path.join(dir_path, '..', 'data', 'game_data'))

os.makedirs(output_directory, exist_ok=True)
years = list(range(2009, 2020))
for year in tqdm.tqdm(years):
    csv_filename = os.path.join(output_directory, f'season{year}.csv')
    parquet_filename = os.path.join(output_directory, f'{year}.parquet')
    nflgame.combine(nflgame.games(year)).csv(csv_filename)

    df = pd.read_csv(csv_filename)
    df.to_parquet(parquet_filename)
    os.remove(csv_filename)

