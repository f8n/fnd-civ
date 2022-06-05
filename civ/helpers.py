import math

PLAYER_STATE_KEYS = [
    'player', 'current_turn',
    'land', 'farms', 'science', 'culture', 'soldiers',
    'population', 'resources',
]
INITIAL_LAND = 5
INITIAL_RESOURCES = 50
INITIAL_POP = 10
INITIAL_LOOT = INITIAL_RESOURCES / INITIAL_LAND # attack loot for first battle

# Resign messages
RESIGN_MESSAGE_POP = "Population has gone to 0"
RESIGN_MESSAGE_LAND = "Land has gone to 0"

# Helpers

def parse_player_state(player_state):
    return dict(zip(PLAYER_STATE_KEYS, player_state))

def assert_player_state(world, player, key, val):
    state = parse_player_state(world.getState(player))
    print(state)
    assert state[key] == val

def assert_turn_action(tx, key, val):
    turn_action = tx.events['TurnAction'][0]
    print(turn_action)
    assert turn_action[key] == val

def assert_turn_summary(tx, key, val):
    turn_summary = tx.events['TurnSummary'][0]
    print(turn_summary)
    assert turn_summary[key] == val

def assert_resign_event(tx, key, val):
    event = tx.events['Resign'][0]
    print(event)
    assert event[key] == val

def compute_loot(turn=0, diff=0):
    return math.floor((INITIAL_RESOURCES + (INITIAL_LAND * turn) + diff) / INITIAL_LAND)
