import os
import json
import pytest
from src.world.city_data import get_city_list_from_dem_xls
from src.simulation.params import Params


@pytest.fixture
def config_path():
    return os.path.join(os.path.dirname(__file__), "..", "src", "config.json")

@pytest.fixture
def cities_path(config_path):
    with open(config_path) as json_data_file:
        ConfigData = json.load(json_data_file)
        citiesDataPath = ConfigData['CitiesFilePath']
    return citiesDataPath

@pytest.fixture
def cities(cities_path):
    cities = get_city_list_from_dem_xls(cities_path)
    return cities


@pytest.fixture
def params_path(config_path):
    with open(config_path) as json_data_file:
        ConfigData = json.load(json_data_file)
        ParamsDataPath = ConfigData['ParamsFilePath']
    return os.path.join(os.path.dirname(__file__), ParamsDataPath)


@pytest.fixture
def params(params_path):
    Params.load_from(params_path)
    return Params.loader()


@pytest.fixture
def R0_percent(params):
    return float(params["population"]["R0_percent"])


def pytest_addoption(parser):
    parser.addoption(
        "--runslow", action="store_true", default=False, help="run slow tests"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow to run")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runslow"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)
