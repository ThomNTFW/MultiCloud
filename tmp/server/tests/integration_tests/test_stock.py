import json
from tests.integration_tests import client


def test_available_stock(client):
    result = client.get('/api/available_stock')
    r_json = json.loads(result.data)
    assert len(r_json) == 3
    assert len((r_json['demand'])) == 4
    assert len((r_json['stock'])) == 4


def test_missing_data_path_key_in_settings(client):
    del client.application.config['SKU_SOURCE_CAPACITY_FILE_PATH']
    result = client.get('/api/available_stock')
    assert result.status_code == 500


def test_incorrect_data_path_in_settings(client):
    client.application.config['SKU_SOURCE_CAPACITY_FILE_PATH'] = 'test'
    result = client.get('/api/available_stock')
    assert result.status_code == 500
