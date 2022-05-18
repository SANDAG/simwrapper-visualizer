import pandas as pd
import numpy as np
import yaml
import os

base_path = os.path.dirname(os.path.realpath(__file__))
config_file = base_path + r'\extract_metrics.yaml'
with open(config_file, 'r') as f:
    config = yaml.safe_load(f)
f.close()

for table in config['tables']:
    measure_table = pd.read_excel(os.path.join(base_path, config['tables'][table]['infile']), **config['tables'][table]['input_args'])

    #scenario_tables = {}
    #for scenario in config['tables'][table]['scenarios']:
    #    scenario_tables[scenario] = pd.DataFrame(df.loc[config['tables'][table]['measures'].values(), config['tables'][table]['scenarios'][scenario].values()].values,
    #                                             config['tables'][table]['measures'].keys(),
    #                                             config['tables'][table]['scenarios'][scenario].keys())
    
    #output_tables = {}
    for measure in config['tables'][table]['measures'].keys():
        scenario_table = {}
        for scenario in config['tables'][table]['scenarios']:
            scenario_table[scenario] = pd.Series(measure_table.loc[config['tables'][table]['measures'][measure], config['tables'][table]['scenarios'][scenario].values()].values,
                                                 config['tables'][table]['scenarios'][scenario].keys())
        #output_tables[measure] = pd.DataFrame(scenario_table)

        pd.DataFrame(scenario_table).to_csv(os.path.join(base_path, config['outpath'], '{}.csv'.format(measure)))

print('Go')