from rutas import config


def test_config_loads():
    assert config.SEED == 42
    assert config.DATA_PROCESSED.name == "processed"
