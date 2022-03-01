
from app.utils.helper import get_file
from flask import current_app


def get_available_stock():
    data_frame_source_capacity = get_file(current_app.config['SKU_SOURCE_CAPACITY_FILE_PATH'])
    return data_frame_source_capacity.to_dict('records')


def get_current_demand():
    data_frame_target_demand = get_file(current_app.config['SKU_TARGET_DEMAND_FILE_PATH'])
    return data_frame_target_demand.to_dict('records')


def get_link_costs():
    data_frame_link_costs = get_file(current_app.config['SOURCE_TARGETS_LINKS'])
    return data_frame_link_costs.to_dict('records')



