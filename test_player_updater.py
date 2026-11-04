from player_class import Player
from common_classes import PlayerUpdater, Item, Knowledge, Display


def test_player_updater():
    player = Player("Test", "white")

    # Set a variable
    PlayerUpdater("name", "Alice").do(player, None)
    assert player.name == "Alice"

    # Add and subtract numeric values
    PlayerUpdater("atk", 3, "add").do(player, None)
    assert player.atk == 5

    PlayerUpdater("atk", 2, "subtract").do(player, None)
    assert player.atk == 3

    # Test HP bounds
    PlayerUpdater("hp", 5, "add").do(player, None)
    assert player.hp == 10

    PlayerUpdater("hp", 20, "subtract").do(player, None)
    assert player.hp == 0

    # Test dictionary updates
    PlayerUpdater("secrets", "Found a secret", "add", "secret1").do(player, None)
    assert player.secrets["secret1"] == "Found a secret"

    PlayerUpdater("secrets", None, "remove", "secret1").do(player, None)
    assert "secret1" not in player.secrets

def test_knowledge_update(monkeypatch):
    player = Player("Test", "white")
    knowledge = Knowledge("secret1", "happiness", "A hidden passage exists.")

    monkeypatch.setattr(Display, "do", lambda self, player, place: 1)

    knowledge.do(player, None)

    assert player.secrets["secret1"] is knowledge


def test_gain_knowledge():
    player = Player("Test", "white")
    knowledge = Knowledge("secret1", "happiness", "A hidden passage exists.")

    player.gain_knowledge(knowledge)

    assert player.secrets["secret1"] == knowledge.knowledge


def test_gain_item():
    player = Player("Test", "white")

    item = Item(
        name="Key",
        add_health=0,
        add_damage=0,
        add_defense=0,
        knowledge=None,
        discover_message="You found a key!",
        keepable=True,
        aspect="happiness"
    )

    player.gain_item(item)

    assert player.inventory["Key"] is item