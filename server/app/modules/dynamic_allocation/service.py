from flask import current_app
from .optimizer import trigger_cbc_solver
from app.utils.helper import get_file
import logging

logger = logging.getLogger('waitress')


def trigger_optimization_service(sku_source_ids, margin=None):
    solver_type = current_app.config['SOLVER_TYPE']
    objective_metric = current_app.config['OBJECTIVE_METRIC']
    objective_threshold_flag = current_app.config['OBJECTIVE_THRESHOLD_FLAG']
    sku_num = current_app.config['SKU_NUM']

    df_availability = get_file(current_app.config['SKU_SOURCE_CAPACITY_FILE_PATH'])

    if all(item in df_availability['id'].tolist() for item in sku_source_ids):
        df_availability_filtered = df_availability.loc[df_availability['id'].isin(sku_source_ids)]
    else:
        logger.error(f"An id you have supplied in the 'sku_source_ids' list could not be found in "
                     f"the source data file. 'sku_source_ids': {sku_source_ids}")
        return f"An id you have supplied in the 'sku_source_ids' list could not be found in " \
               f"the source data file. 'sku_source_ids': {sku_source_ids} ", 500

    df_requirement = get_file(current_app.config['SKU_TARGET_DEMAND_FILE_PATH'])

    df_objective = get_file(current_app.config['SOURCE_TARGETS_LINKS'])
    df_objective_filtered = df_objective.loc[df_objective['sku'].isin(df_availability_filtered['sku'].unique())]
    df_objective_filtered = df_objective_filtered.loc[
        df_objective_filtered['source'].isin(df_availability_filtered['source'].unique())]

    if objective_metric not in ['margin', 'cost']:
        logger.error(f"Objective metric not recognised: {objective_metric}")
        return f"Objective metric not recognised: {objective_metric}", 500

    if solver_type == 'CBC':
        logger.info("Solver type: CBC")
        return trigger_cbc_solver(sku_num,
                                  objective_metric,
                                  objective_threshold_flag,
                                  margin,
                                  df_availability_filtered,
                                  df_requirement,
                                  df_objective_filtered), 200
    else:
        logger.error("Solver selected in settings is not supported.")
        return "Solver selected in settings is not supported.", 500
