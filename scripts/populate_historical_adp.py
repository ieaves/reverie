import reverie as rev
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
output_directory = os.path.abspath(os.path.join(dir_path, '..', 'data', 'ADP'))
print(f'Writing to {output_directory}')
years = range(2007, 2021)
rev.data.populate_historical_adp(output_directory, years)
