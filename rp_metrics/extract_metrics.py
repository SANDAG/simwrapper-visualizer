import pandas as pd
import numpy as np
import yaml
import os

base_path = os.path.dirname(os.path.realpath(__file__))
config_file = base_path + r'\extract_metrics.yaml'
with open(config_file, 'r') as f:
    config = yaml.safe_load(f)
f.close()

out_tables = {}
for table in config['tables']:
    measure_table = pd.read_excel(os.path.join(base_path, config['tables'][table]['infile']),
                                  table,
                                  **config['tables'][table]['input_args'])
   
    for measure in config['tables'][table]['measures'].keys():
        scenario_table = {}
        for scenario in config['tables'][table]['scenarios']:
            scenario_table[scenario] = pd.Series(measure_table.loc[config['tables'][table]['measures'][measure], config['tables'][table]['scenarios'][scenario].values()].values,
                                                 config['tables'][table]['scenarios'][scenario].keys())

        out_tables[measure] = pd.DataFrame(scenario_table)
        out_tables[measure].index.name = config['tables'][table]['index_name']

if 'merge' in config:
    for table in config['merge']:
        out_tables[table] = pd.merge(out_tables[config['merge'][table]['left']],
                                     out_tables[config['merge'][table]['right']],
                                     **config['merge'][table]['args'])
        del out_tables[config['merge'][table]['left']], out_tables[config['merge'][table]['right']]

for table in out_tables:
    out_tables[table].to_csv(os.path.join(base_path, config['outpath'], '{}.csv'.format(table)))

print('Go')