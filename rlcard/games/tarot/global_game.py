import random

from rlcard.games.tarot.bid.bid import TarotBid
from rlcard.games.tarot.alpha_and_omega.player import TarotPlayer as Player
from rlcard.games.tarot.dog.dog import TarotDog

from rlcard.games.tarot.bid.bid_game import BidGame
from rlcard.games.tarot.dog.dog_game import DogGame
from rlcard.games.tarot.main_game.main_game import MainGame

random.seed(42)  # TODO REMOVE


class GlobalGame(object):

    def __init__(self):
        self.current_game_part = 'BID'
        self.num_players = 4
        self.num_cards_per_player = 18
        self.num_cards_dog = 6
        self.starting_player = 0  # random.randint(0, self.num_players - 1) TODO - Understand issue when starting_player different from current_player in env ?
        self.payoffs = [0 for _ in range(self.num_players)]
        # Initialize a dealer that can deal cards
        self.dealer = None
        # Initialize four players to play the game
        self.players = None
        self.taking_player_id = None
        self.taking_bid = None
        # Initialize a Bid instance
        self.bid_game = None
        self.bid_round = None
        self.bid_over = False
        # Initialize the dog
        self.dog_game = None
        self.dog = TarotDog()
        self.dog_over = False
        # Depending on the bid and dog, the known cards differ:
        self.known_cards = []
        # Initialize a Round instance
        self.main_game = None
        self.main_round = None
        self.main_over = False
        self.is_game_over = False

    def init_game(self):
        """ Initialize players and state for bid game

        Returns:
            (tuple): Tuple containing:

                (dict): The first state in one game
                (int): Current bidder's id
        """
        self.current_game_part = 'BID'
        self.bid_over = False
        self.dog_over = False
        self.main_over = False
        self.is_game_over = False
        self.players = [Player(i) for i in range(self.num_players)]
        # Initialize bid Round
        self.bid_game = BidGame(self.players, self.num_players, self.starting_player, self.num_cards_per_player,
                                self.num_cards_dog, self.dog)

        self.bid_game.init_game()

        player_id = self.bid_game.bid_round.current_player_id
        state = self.bid_game.get_state(player_id)

        return state, player_id

    def step(self, played_action):
        """ Get the next state

        Args:
            played_action (TarotCard or TarotBid): A specific TarotCard or TarotBid

        Returns:
            (tuple): Tuple containing:

                (dict): next player's state
                (int): next plater's id
        """
        if self.current_game_part == 'BID':
            state, player_id = self.bid_game.step(played_action)
            state = self.bid_game.get_state(player_id)
            self.bid_game.bid_round.current_player_id = player_id
            if self.bid_game.bid_over:
                self.bid_over = True
                self.taking_player_id = self.bid_game.taking_player_id
                self.taking_bid = self.bid_game.taking_bid
                if self.taking_bid < 4:
                    self.current_game_part = 'DOG'
                    player_id = self.taking_player_id
                    self.dog_game = DogGame(self.players, self.taking_player_id, self.num_cards_per_player,
                                            self.num_cards_dog, self.dog, self.taking_bid)
                    self.dog_game.init_game()
                    state = self.dog_game.get_state(player_id)
                else:
                    self.dog_over = True
                    self.current_game_part = 'MAIN'
                    player_id = self.starting_player
                    self.dog_game = DogGame(self.players, self.taking_player_id, self.num_cards_per_player,
                                            self.num_cards_dog, self.dog, self.taking_bid)
                    self.main_game = MainGame(self.num_players, self.num_cards_per_player, self.starting_player,
                                              self.players, self.bid_game.taking_player_id,
                                              self.dog_game.dog_round.new_dog)
                    self.main_game.init_game()
                    state = self.main_game.get_state(player_id)
        elif self.current_game_part == 'DOG':
            state, player_id = self.dog_game.step(played_action)
            state = self.dog_game.get_state(player_id)
            if self.dog_game.is_over:
                self.dog_over = True
                self.current_game_part = 'MAIN'
                player_id = self.starting_player
                self.main_game = MainGame(self.num_players, self.num_cards_per_player, self.starting_player,
                                          self.players, self.bid_game.taking_player_id,
                                          self.dog_game.dog_round.new_dog)
                self.main_game.init_game()
                state = self.main_game.get_state(player_id)
        elif self.current_game_part == 'MAIN':
            state, player_id = self.main_game.step(played_action)
            if self.main_game.is_over:
                self.main_over = True
                self.is_game_over = True
        else:
            raise AttributeError
        return state, player_id

    def get_state(self, player_id):
        """ Return player's state

        Args:
            player_id (int): player id

        Returns:
            (dict): The state of the player
        """
        if self.current_game_part == 'BID':
            state = self.bid_game.get_state(player_id)
        elif self.current_game_part == 'DOG':
            state = self.dog_game.get_state(player_id)
        else:
            state = self.main_game.get_state(player_id)
        return state

    def get_payoffs(self):
        """ Return the payoffs of the game

        Returns:
            (list): Each entry corresponds to the payoff of one player
        """

        return self.main_game.get_payoffs()

    def get_legal_actions(self):
        """ Return the legal actions for current player

        Returns:
            (list): A list of legal actions
        """
        if self.current_game_part == 'BID':
            return self.bid_game.get_legal_actions()
        elif self.current_game_part == 'DOG':
            return self.dog_game.get_legal_actions()
        else:
            return self.main_game.get_legal_actions()

    def get_player_num(self):
        """ Return the number of players in Tarot

        Returns:
            (int): The number of players in the game
        """
        return self.num_players

    def get_action_num(self):
        """ Return the number of applicable actions

        Returns:
            (int): The number of actions. There are 78 actions
        """
        if self.current_game_part == 'BID':
            return BidGame.get_action_num()
        elif self.current_game_part == 'DOG':
            return DogGame.get_action_num()
        else:
            return MainGame.get_action_num()

    def get_player_id(self):
        """ Return the current player's id

        Returns:
            (int): current player's id
        """
        if self.current_game_part == 'BID':
            return self.bid_game.get_player_id()
        elif self.current_game_part == 'DOG':
            return self.dog_game.get_player_id()
        else:
            return self.main_game.get_player_id()

    def is_over(self):
        """

        :return:
        """
        return self.is_game_over
