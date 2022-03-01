# File for default configurations


class DevConfig():
    DEBUG = False
    DEFAULT_HOST = '0.0.0.0'
    DEFAULT_PORT = 5000
    SKU_SOURCE_CAPACITY_FILE_PATH = 'data/sku_3/sku_variation_3_df_sku_source_capacity.csv'
    SKU_TARGET_DEMAND_FILE_PATH = 'data/sku_3/sku_variation_3_df_sku_target_demand.csv'
    SOURCE_TARGETS_LINKS = 'data/sku_3/sku_variation_3_df_sources_targets_links.csv'
    SOLVER_TYPE = 'CBC'
    OBJECTIVE_METRIC = 'margin'
    OBJECTIVE_THRESHOLD_FLAG = 1
    SKU_NUM = 2


class TestConfig():
    DEBUG = True
    DEFAULT_HOST = '0.0.0.0'
    DEFAULT_PORT = 5000
    SKU_SOURCE_CAPACITY_FILE_PATH = 'test_data/sku_test_1/sku_variation_test_df_sku_source_capacity.csv'
    SKU_TARGET_DEMAND_FILE_PATH = 'test_data/sku_test_1/sku_variation_test_df_sku_target_demand.csv'
    SOURCE_TARGETS_LINKS = 'test_data/sku_test_1/sku_variation_test_df_sources_targets_links.csv'
    SOLVER_TYPE = 'CBC'
    OBJECTIVE_METRIC = 'margin'
    OBJECTIVE_THRESHOLD_FLAG = 1
    SKU_NUM = 2


class ProdConfig(DevConfig):
    pass
