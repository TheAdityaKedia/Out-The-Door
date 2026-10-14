# Oblique Strategies card of the day, from cards.txt (one card per line).

_cards = None


def load(path="cards.txt"):
    global _cards
    if _cards is None:
        with open(path) as f:
            _cards = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return _cards


def card_for(days, path="cards.txt"):
    # Same card all day; steps through the deck in a shuffled-looking order.
    cards = load(path)
    return cards[(days * 37) % len(cards)]
