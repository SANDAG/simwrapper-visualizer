import pandas as pd
import numpy as np
import os
import yaml

base_path = os.path.dirname(os.path.realpath(__file__))
config_file = base_path + r'\combine.yaml'
with open(config_file, 'r') as f:
    config = yaml.safe_load(f)
f.close()

for table in config['tables']:
    merge_cols = config['tables'][table]['merge']

    for run in config['runs']:
        in_df = pd.read_csv(config['runs'][run] + '\\' + table + '.csv')

        if 'transpose' in config['tables'][table]:
            in_df = in_df.T
            in_df.index.name = config['tables'][table]['transpose']
            in_df = in_df.reset_index()

        name_map = {}
        names = []
        counter = 0 #For separating columns into different tables

        try:
            for col in config['tables'][table]['dtype']:
                in_df[col] = in_df[col].astype(config['tables'][table]['dtype'][col])
        except KeyError:
            pass

        for col in in_df.columns:
            #Remove columns to be skipped
            if 'skip' in config['tables'][table] and col in config['tables'][table]['skip']:
                del in_df[col]
                continue
            elif col in merge_cols:
                in_df[col] = in_df[col].apply(lambda x: str(x).replace('.0', '')) #Convert to string in case different data types
            elif 'separate' in config['tables'][table] and col in config['tables'][table]['separate']:
                name_map[col] = '{0}_{1}'.format(run, counter)
                names.append(col)
                counter += 1
            else:
                name_map[col] = run# + '_' + col

        #Add marginal totals if needed
        if 'total' in config['tables'][table]:
            for col in config['tables'][table]['total']:
                assert col in merge_cols, 'Column `{}` must be in merge columns'.format(col)
                if 'Total' in in_df[col].values or 'All' in in_df[col].values or 'All Households' in in_df[col].values:
                    continue
                else:
                    in_df = in_df.set_index(merge_cols)
                    level = list(range(len(merge_cols)))
                    level.remove(merge_cols.index(col))
                    totals = in_df.sum(level = level).reset_index()
                    totals[col] = config['tables'][table]['total'][col]
                    in_df = pd.concat((in_df.reset_index(), totals))

        #Merge tables from different runs together. If no table exists yet copy `in_df`
        try:
            out_df = out_df.merge(in_df.rename(columns = name_map), how = 'outer', on = merge_cols)
        except NameError:
            out_df = in_df.rename(columns = name_map)
            

    if 'pct_diff' in config['tables'][table]:
        for col in config['tables'][table]['pct_diff']:
            out_df['%Diff_' + col] = out_df[config['tables'][table]['pct_diff'][col][0] + '_' + col] / out_df[config['tables'][table]['pct_diff'][col][1] + '_' + col] - 1

    if 'separate' in config['tables'][table]:
        out_dfs = {}
        for i in range(counter):
            out_dfs[names[i]] = pd.DataFrame()
            for col in out_df.columns:
                if col in merge_cols:
                    out_dfs[names[i]][col] = out_df[col]
                elif '_{}'.format(i) in col:
                    out_dfs[names[i]][col.split('_')[0]] = out_df[col]

            outfile = config['outpath'] + '\\' + names[i].replace(' ', '') + '.csv'
            if 'suffix' in config['tables'][table]:
                outfile = outfile.replace('.csv', '_{}.csv'.format(config['tables'][table]['suffix']))

            out_dfs[names[i]].to_csv(outfile, index = False)

        del in_df, out_df, out_dfs

    elif 'subsets' in config['tables'][table]:
        for subset in config['tables'][table]['subsets']:
            subset_df = out_df.query(config['tables'][table]['subsets'][subset]['query'])
            if 'rename' in config['tables'][table]['subsets'][subset]:
                for col in config['tables'][table]['subsets'][subset]['rename']:
                    subset_df[col] = subset_df[col].replace(config['tables'][table]['subsets'][subset]['rename'][col])
            subset_df.to_csv(config['outpath'] + '\\' + subset + '.csv', index = False)

    else:
        out_df.index.name = 'index'
        out_df.fillna(0).to_csv(config['outpath'] + '\\' + table + '.csv', index = False)
        del in_df, out_df

print('Done')