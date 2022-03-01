import json
from tests.integration_tests import client


def test_trigger_optimization_no_body(client):
    result = client.post('/api/trigger_optimization')
    assert result.status_code == 422


def test_trigger_optimization_no_margin(client):
    result = client.post('/api/trigger_optimization', json={"sku_source_ids": [3]})
    assert result.status_code == 200
    r_json = json.loads(result.data)
    assert r_json['dynamic_allocation']  # 'dynamic_allocation' list should be empty if the problem is infeasible


def test_trigger_optimization_no_sku_source_id(client):
    result = client.post('/api/trigger_optimization', json={"margin": 0.2})
    assert result.status_code == 422


def test_margin_exceeds_one(client):
    result = client.post('/api/trigger_optimization', json={"sku_source_ids": [1, 2], "margin": 1.1})
    assert result.status_code == 422


def test_margin_less_than_zero(client):
    result = client.post('/api/trigger_optimization', json={"sku_source_ids": [1, 2], "margin": -0.1})
    assert result.status_code == 422


def test_margin_not_a_number(client):
    result = client.post('/api/trigger_optimization', json={"sku_source_ids": [1, 2], "margin": 'test'})
    assert result.status_code == 422


def test_sku_source_id_empty(client):
    result = client.post('/api/trigger_optimization', json={"sku_source_ids": [], "margin": 0.2})
    assert result.status_code == 422


def test_sku_source_id_not_in_data(client):
    result = client.post('/api/trigger_optimization', json={"sku_source_ids": [1, 2, 7], "margin": 0.2})
    assert result.status_code == 500


def test_invalid_metric_objective(client):
    client.application.config['OBJECTIVE_METRIC'] = 'test'
    result = client.post('/api/trigger_optimization', json={"sku_source_ids": [1, 2], "margin": 0.2})
    assert result.status_code == 500


def test_invalid_solver_type(client):
    client.application.config['SOLVER_TYPE'] = 'test'
    result = client.post('/api/trigger_optimization', json={"sku_source_ids": [1, 2], "margin": 0.2})
    assert result.status_code == 500


def test_cbc_solver_perfectly_balanced(client):
    result = client.post('/api/trigger_optimization', json={"sku_source_ids": [0, 1, 2, 3], "margin": 0.2})
    r_json = json.loads(result.data)

    check_for_sxtx = [each for each in r_json['dynamic_allocation'] if each['is_sxtx']]
    assert not check_for_sxtx
    assert r_json['dynamic_allocation']
    assert result.status_code == 200


def test_cbc_solver_complex(client):
    client.application.config['SKU_SOURCE_CAPACITY_FILE_PATH'] = 'test_data/sku_test_2/' \
                                                                 'sku_variation_2_df_sku_source_capacity.csv'
    client.application.config['SKU_TARGET_DEMAND_FILE_PATH'] = 'test_data/sku_test_2/' \
                                                               'sku_variation_2_df_sku_target_demand.csv'
    client.application.config['SOURCE_TARGETS_LINKS'] = 'test_data/sku_test_2/' \
                                                        'sku_variation_2_df_sources_targets_links.csv'
    result = client.post('/api/trigger_optimization', json={"sku_source_ids": [0, 1, 2, 3, 4], "margin": 0.2})
    assert result.status_code == 200


# Test to ensure we are filtering out SKU and Source if not present in requested ids
def test_cbc_solver_unbalanced_too_much_capacity(client):
    client.application.config['SKU_SOURCE_CAPACITY_FILE_PATH'] = 'test_data/sku_test_too_much_capacity/' \
                                                                 'sku_variation_test_df_sku_source_capacity.csv'
    client.application.config['SKU_TARGET_DEMAND_FILE_PATH'] = 'test_data/sku_test_too_much_capacity/' \
                                                               'sku_variation_test_df_sku_target_demand.csv'
    client.application.config['SOURCE_TARGETS_LINKS'] = 'test_data/sku_test_too_much_capacity/' \
                                                        'sku_variation_test_df_sources_targets_links.csv'
    result = client.post('/api/trigger_optimization', json={"sku_source_ids": [0, 1, 2, 3], "margin": 0.2})
    r_json = json.loads(result.data)
    assert r_json['dynamic_allocation']
    assert result.status_code == 200


# Test to ensure we are filtering out SKU and Source if not present in requested ids
def test_cbc_solver_unbalanced_too_much_demand(client):
    client.application.config['SKU_SOURCE_CAPACITY_FILE_PATH'] = 'test_data/sku_test_too_much_demand/' \
                                                                 'sku_variation_test_df_sku_source_capacity.csv'
    client.application.config['SKU_TARGET_DEMAND_FILE_PATH'] = 'test_data/sku_test_too_much_demand/' \
                                                               'sku_variation_test_df_sku_target_demand.csv'
    client.application.config['SOURCE_TARGETS_LINKS'] = 'test_data/sku_test_too_much_demand/' \
                                                        'sku_variation_test_df_sources_targets_links.csv'
    result = client.post('/api/trigger_optimization', json={"sku_source_ids": [0, 1, 2, 3], "margin": 0.2})
    r_json = json.loads(result.data)
    assert r_json['dynamic_allocation']
    assert result.status_code == 200


# Test to ensure we are filtering out any rows in the link_capacity dataframe that are for SKUs not present
# in the submitted sku_source_id list. This filtering out is required as the optimizer loops through all breaking arcs
# (links) and uses these to invalidate those routes in the flow. If we do not filter these out before the breaking arcs
# list is created, we will get a KeyError when it is not found in the flow dict.
# This is because flow has the following structure: [sku][source][target].
# Link is considered breaking if it's does not meet our set
# objective value: 'df_objective['margin'] < objective_threshold_value'
# The test below only refers to SKU '2', and will fail unless the filtering has successfully been completed.
def test_cbc_solver_filtering_out_based_on_sku(client):
    client.application.config['SKU_SOURCE_CAPACITY_FILE_PATH'] = 'test_data/sku_test_2/' \
                                                                 'sku_variation_2_df_sku_source_capacity.csv'
    client.application.config['SKU_TARGET_DEMAND_FILE_PATH'] = 'test_data/sku_test_2/' \
                                                               'sku_variation_2_df_sku_target_demand.csv'
    client.application.config['SOURCE_TARGETS_LINKS'] = 'test_data/sku_test_2/' \
                                                        'sku_variation_2_df_sources_targets_links.csv'
    result = client.post('/api/trigger_optimization', json={"sku_source_ids": [0, 1, 2], "margin": 0.2})
    r_json = json.loads(result.data)
    assert r_json['dynamic_allocation']
    assert result.status_code == 200


# Test to ensure we are filtering out any rows in the link_capacity dataframe that are for sources not present
# in the submitted sku_source_id list. This filtering out is required as the optimizer loops through all breaking arcs
# (links) and uses these to invalidate those routes in the flow. If we do not filter these out before the breaking arcs
# list is created, we will get a KeyError when it is not found in the flow dict.
# This is because flow has the following structure: [sku][source][target].
# Link is considered breaking if it's does not meet our set
# objective value: 'df_objective['margin'] < objective_threshold_value'
# The test below only refers to SKU '2', and will fail unless the filtering has successfully been completed.
def test_cbc_solver_filtering_out_based_on_source(client):
    client.application.config['SKU_SOURCE_CAPACITY_FILE_PATH'] = 'test_data/sku_test_2/' \
                                                                 'sku_variation_2_df_sku_source_capacity.csv'
    client.application.config['SKU_TARGET_DEMAND_FILE_PATH'] = 'test_data/sku_test_2/' \
                                                               'sku_variation_2_df_sku_target_demand.csv'
    client.application.config['SOURCE_TARGETS_LINKS'] = 'test_data/sku_test_2/' \
                                                        'sku_variation_2_df_sources_targets_links.csv'
    result = client.post('/api/trigger_optimization', json={"sku_source_ids": [1, 2], "margin": 0.2})
    r_json = json.loads(result.data)
    assert r_json['dynamic_allocation']
    assert result.status_code == 200


def test_cbc_solver_infeasible(client):
    result = client.post('/api/trigger_optimization', json={"sku_source_ids": [3], "margin": 0.4})
    assert result.status_code == 200
    r_json = json.loads(result.data)
    assert not r_json['dynamic_allocation']  # 'dynamic_allocation' list should be empty if the problem is infeasible
    assert r_json['solver_metadata']['solution'] == 'Problem Infeasible'


def test_cbc_solver_costs(client):
    result = client.post('/api/trigger_optimization', json={"sku_source_ids": [3]})
    assert result.status_code == 200
    r_json = json.loads(result.data)
    print(r_json)
    assert r_json['dynamic_allocation']
    assert r_json['dynamic_allocation'][0]
