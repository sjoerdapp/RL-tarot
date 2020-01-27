from collections import OrderedDict

import numpy as np

from rlcard.games.tarot.alpha_and_omega.card import TarotCard as Card
from rlcard.games.tarot.bid.bid import TarotBid

# a map of color to its index

COLOR_MAP = {'SPADE': 0, 'CLOVER': 1, 'HEART': 2, 'DIAMOND': 3, 'TRUMP': 4}

VALUE_MAP = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
             '8': 8, '9': 9, '10': 10, '11': 11, '12': 12, '13': 13, '14': 14,
             '15': 15, '16': 16, '17': 17, '18': 18, '19': 19, '20': 20, '21': 21}

BID_SPACE = OrderedDict({'PASSE': 0, 'PETITE': 1, 'POUSSE': 2, 'GARDE': 3, 'GARDE_SANS': 4, 'GARDE_CONTRE': 5})
BID_LIST = list(BID_SPACE.keys())
all_bids = [TarotBid('PASSE'),
            TarotBid('PETITE'),
            TarotBid('POUSSE'),
            TarotBid('GARDE'),
            TarotBid('GARDE_SANS'),
            TarotBid('GARDE_CONTRE')]


def init_deck():
    """ Generate tarot deck of 78 cards
    """
    card_deck = []
    card_info = Card.info
    for color in card_info['color']:

        # init number cards
        for num in card_info['color_value']:
            card_deck.append(Card(False, color=color, color_value=num))

    # init trump cards
    for num in card_info['trump_value']:
        card_deck.append(Card(True, trump_value=num))

    return card_deck


deck = init_deck()
ACTION_DICT = dict()
for index, a_card in enumerate(deck):
    ACTION_DICT[a_card.str] = index
ACTION_SPACE = OrderedDict(ACTION_DICT)
ACTION_LIST = list(ACTION_SPACE.keys())


def cards2list(cards):
    """ Get the corresponding string representation of cards

    Args:
        cards (list): list of TarotCards objects

    Returns:
        (string): string representation of cards
    """
    cards_list = []
    for card in cards:
        cards_list.append(card.get_str())
    return cards_list


def hand2dict(hand):
    """ Get the corresponding dict representation of hand

    Args:
        hand (list): list of string of hand's card

    Returns:
        (dict): dict of hand
    """
    hand_dict = {}
    for card in hand:
        hand_dict[card] = 1
    return hand_dict


def encode_hand(plane: np.ndarray, hand, index_to_encode=0):
    """ Encode hand and represerve it into plane
    Args:
        plane (array): n*5*22 numpy array
        hand (list): list of string of hand's card
        index_to_encode (int): see tarot extract state function
    Returns:
        (array): n*5*22 numpy array
    """
    # plane = np.zeros((n, 5, 22), dtype=int)
    plane[index_to_encode] = np.zeros((5, 22), dtype=int)
    for card in hand:
        card_info = card.split('-')
        color = COLOR_MAP[card_info[0]]
        value = VALUE_MAP[card_info[1]]
        plane[index_to_encode][color][value] = 1
    return plane


def encode_target(plane, target, index_to_encode=2):
    """ Encode target and represerve it into plane
    Args:
        plane (array): n*5*22 numpy array - we give only one composant to this function
        target(str): string of target card
        :param plane:
        :param target:
        :param index_to_encode:
    Returns:
        (array): n*5*22 numpy array
    """
    plane[index_to_encode] = np.zeros((5, 22), dtype=int)
    if target is None:
        return plane
    target_info = target.split('-')
    color = COLOR_MAP[target_info[0]]
    value = VALUE_MAP[target_info[1]]
    plane[index_to_encode][color][value] = 1
    return plane


def encode_bid(plane, bid, index_to_encode='2-0'):
    """
    index_to_encode gives the path inside plane to encode the given bids
    :param index_to_encode: Index 2-0 when encoding own personnal max bid, and '2-1' when encoding other bids
    :param plane:
    :param bid: List of bids to be encoded
    :return:
    """
    if bid is None:
        return plane
    if isinstance(bid, TarotBid):
        bid = [bid]
    bid_values = [BID_SPACE[bid[i].get_str()] for i in range(len(bid)) if bid[i] is not None]
    indexs = [int(index_to_encode.split('-')[i]) for i in [0, 1]]
    plane[indexs[0]][indexs[1]] = np.zeros(22, dtype=int)
    for bid_value in bid_values:
        plane[indexs[0]][indexs[1]][bid_value] += 1
    return plane


def get_TarotCard_from_str(card):
    """

    :param card:
    :return: TarotCard object
    """
    if card is None:
        return None
    else:
        color, value = card.split('-')
        if color == 'TRUMP':
            is_trump = True
            return Card(is_trump, trump_value=int(value))
        else:
            is_trump = False
            return Card(is_trump, color=color, color_value=int(value))


def get_TarotBid_from_str(bid):
    """

    :param bid:
    :return:
    """
    if bid is None:
        return None
    else:
        return TarotBid(bid)


def get_end_pot_information(pot_cards):
    """

    :param pot_cards: dictionnary with target_card, and the num_players cards of all players
    :return: winner_id, pot_value, nb_bouts
    """
    target_card = pot_cards['target']
    trump_values = dict()
    values = dict()
    color_values = dict()
    colors = dict()
    for player_id in range(len(pot_cards) - 1):
        if pot_cards[player_id].is_trump:
            trump_values[player_id] = pot_cards[player_id].trump_value
            values[player_id] = -1
            colors[player_id] = 'TRUMP'
        else:
            trump_values[player_id] = -1
            values[player_id] = pot_cards[player_id].color_value
            colors[player_id] = pot_cards[player_id].color
    # If target is trump :
    if target_card.is_trump:
        winner_id = max(trump_values, key=trump_values.get)
    # If color is given in target card
    else:
        trump_used = False
        for player_id in range(len(pot_cards) - 1):
            if colors[player_id] == 'TRUMP':
                trump_used = True
        if trump_used:
            winner_id = max(trump_values, key=trump_values.get)
        else:
            target_color = target_card.color
            for player_id in range(len(pot_cards) - 1):
                color_values[player_id] = (target_color == colors[player_id]) * values[player_id]
            winner_id = max(color_values, key=color_values.get)

    return winner_id, get_pot_value(pot_cards), get_nb_bouts(pot_cards)


def get_pot_value(pot_cards):
    """

    :param pot_cards: dict cards of all players + THE TARGET CARD NOT TO BE COUNTED
    :return: point value of this pot (float)
    """
    total_points = 0
    for player_id in range(len(pot_cards) - 1):
        total_points += pot_cards[player_id].get_value()

    return total_points


def get_nb_bouts(pot_cards):
    """

    :param pot_cards:
    :return:
    """
    total_bouts = 0
    for player_id in range(len(pot_cards) - 1):
        total_bouts += pot_cards[player_id].is_bout()

    return total_bouts
