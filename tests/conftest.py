import pytest
from brownie import (
    BasicStrategy,
    TestAttackStrategy,
    TestCreateStrategy,
    TestExploreStrategy,
    TestFarmStrategy,
    TestMultiActionStrategy,
    TestProduceStrategy,
    TestResearchStrategy,
    TestTradeStrategy,
    World,
    accounts
)


@pytest.fixture
def world():
    return accounts[0].deploy(World);

@pytest.fixture
def basic_strategy():
    return accounts[0].deploy(BasicStrategy)

@pytest.fixture
def create_strategy():
    return accounts[0].deploy(TestCreateStrategy)

@pytest.fixture
def explore_strategy():
    return accounts[0].deploy(TestExploreStrategy)

@pytest.fixture
def produce_strategy():
    return accounts[0].deploy(TestProduceStrategy)

@pytest.fixture
def research_strategy():
    return accounts[0].deploy(TestResearchStrategy)

@pytest.fixture
def farm_strategy():
    return accounts[0].deploy(TestFarmStrategy)

@pytest.fixture
def trade_strategy():
    return accounts[0].deploy(TestTradeStrategy)

@pytest.fixture
def attack_strategy():
    return accounts[0].deploy(TestAttackStrategy)

@pytest.fixture
def multi_action_strategy():
    return accounts[0].deploy(TestMultiActionStrategy)
