import featuretools as ft
import pandas as pd


def tdfs(entityset,
         target_entity,
         cutoffs=None,
         features_only=False,
         window_size=None,
         training_window=None,
         num_windows=None,
         start=None,
         **kwargs):
    '''
    Must specify 2 of the optional args:
    - window_size and num_windows
    - window_size and start
    - num_windows and start

    If features_only is False, cutoffs must be provided
    '''
    temporal_cutoffs = None
    if not features_only:
        index = entityset[target_entity].index
        instance_id_column = 'instance_id'
        if 'instance_id' in cutoffs.columns:
            instance_ids = cutoffs['instance_id']
        elif index in cutoffs:
            instance_ids = cutoffs[index]
            instance_id_column = index
        else:
            instance_ids = cutoffs.iloc[:, 0]
            instance_id_column = cutoffs.columns[0]
        time_column = 'time'
        if time_column not in cutoffs:
            not_instance_id = [c for c in cutoffs.columns if c != instance_id_column]
            time_column = not_instance_id[0]
        times = cutoffs[time_column]
        temporal_cutoffs = make_temporal_cutoffs(instance_ids, times, window_size,
                                                 num_windows, start)
    result = ft.dfs(entityset=entityset,
                    features_only=features_only,
                    cutoff_time=temporal_cutoffs,
                    target_entity=target_entity,
                    cutoff_time_in_index=True,
                    training_window=training_window,
                    **kwargs)
    if not features_only:
        fm, fl = result
        return fm.sort_index(level=[entityset[target_entity].index,
                                    'time']), fl
    return result


def make_temporal_cutoffs(instance_ids,
                          cutoffs,
                          window_size=None,
                          num_windows=None,
                          start=None):
    '''
    Must specify 2 of the optional args:
    - window_size and num_windows
    - window_size and start
    '''
    out = []
    for _id, time in zip(instance_ids, cutoffs):
        to_add = pd.DataFrame()
        to_add["time"] = pd.date_range(end=time,
                                       periods=num_windows,
                                       freq=window_size,
                                       start=start)
        to_add['instance_id'] = [_id] * len(to_add['time'])
        out.append(to_add)
    return pd.concat(out).reset_index(drop=True)