"""solitaire.py
A solitaire game
Author: Daniel Harris
Created: 17.07.18
"""
from tkinter import *
from random import shuffle

WINDOW = Tk()

BUTTON_HEIGHT = 200
BUTTON_WIDTH = 131
BUTTON_SMALL_HEIGHT = int(BUTTON_HEIGHT / 4)
BUTTON_RELIEF = "flat"

CARD_SUITS = {
    "0": "Spades",
    "1": "Hearts",
    "2": "Diamonds",
    "3": "Clubs"
}
RED_SUITS = (1, 2)
NUM_SUITS = len(CARD_SUITS)
BOARD_SIZE = NUM_SUITS + 3

# Card States
STR_DECK = "Deck" # In the hidden part of the deck
STR_TOP_DECK = "Top Deck" # Just drawn from the deck
STR_USED_DECK = "Used Deck" # Was drawn from the deck but was not used and
# another card was drawn
STR_BOARD = "Board" # Hidden card on the board
STR_TOP_BOARD = "Top Board" # At the very bottom of its section of the board
STR_VIS_BOARD = "Vis Board" # On the board and visible, but there are cards
# underneath it
STR_PILE = "Pile" # On the pile with one or more cards on top
STR_TOP_PILE = "Top Pile" # On the top of the pile

CARD_NAMES = {
    "1": "A",
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6",
    "7": "7",
    "8": "8",
    "9": "9",
    "10": "10",
    "11": "J",
    "12": "Q",
    "13": "K"
}

DECK_SIZE = NUM_SUITS * len(CARD_NAMES)

EMPTY_IMAGE = PhotoImage(file="card_folder\\empty.gif")
BACK_IMAGE = PhotoImage(file="card_folder\\red_back.gif")

class Empty:
    """An empty class for storing dummy cards"""
    
    def __init__(self, state=STR_DECK, pos=0, height=0):
        """Initializer"""
        self.state = state
        self.state_position = pos
        self.state_height = height

class DualButton:
    """Creates a pseudo-button that can be disabled"""
    
    STR_COMMAND = "command"
    
    def __init__(self, parent, disable_button=False, **kwargs):
        """Initialises both a button and a label"""
        self.button_off = disable_button
        self.button = Button(parent, **kwargs)
        if DualButton.STR_COMMAND in kwargs.keys():
            del kwargs[DualButton.STR_COMMAND]
        self.label = Label(parent, **kwargs)
    
    def disable_button(self):
        """Disables the button"""
        self.button_off = True
        if len(self.button.grid_info()) != 0:
            self.button.grid_forget()
            self.label.grid(**self.grid_options)
    
    def enable_button(self):
        """Enables the button"""
        self.button_off = False
        if len(self.label.grid_info()) != 0:
            self.label.grid_forget()
            self.button.grid(**self.grid_options)
    
    def grid(self, **options):
        """Adds the widget to a grid"""
        if self.button_off is True:
            self.label.grid(**options)
        else:
            self.button.grid(**options)
        self.grid_options = options
    
    def grid_forget(self):
        """Removes the widget from the grid"""
        self.button.grid_forget()
        self.label.grid_forget()
    
    def grid_configure(self, **options):
        """Configures the positioning of the widget"""
        if self.button_off is True:
            self.label.grid_forget()
            self.label.grid(**options)
            self.grid_options = self.label.grid_info()
        else:
            self.button.grid_forget()
            self.button.grid(**options)
            self.grid_options = self.button.grid_info()            
        
    def config(self, **kwargs):
        """Configures the options of the label and button. Same as configure"""
        self.configure(**kwargs)
        
    def configure(self, **kwargs):
        """Configures the options of the label and button"""
        self.button.configure(**kwargs)
        if DualButton.STR_COMMAND in kwargs.keys():
            del kwargs[DualButton.STR_COMMAND]
        self.label.configure(**kwargs)

class CardContainer:
    """A class that holds Cards"""
    
    def __init__(self):
        """Creates a card containter"""
        self.cards = []
    
    def __str__(self):
        """Returns a string representation of the container"""
        return_string = ""
        for card in self.cards:
            return_string += str(card) + ", "
        return return_string
    
    def pop(self, pos=-1):
        """Removes and returns a card, defaulting to the last one"""
        return self.cards.pop(pos)
    
    def peek(self, pos=-1, remove=False):
        """Returns a card, defaulting to the last one"""
        return self.cards[pos]
    
    def __len__(self):
        """Returns the number of cards in the container"""
        return len(self.cards)
    
    def append(self, other):
        """A method to add a card to the container"""
        self.cards.append(other)

class Card:
    """A Card class"""
    
    def __init__(self, card_id, board):
        """Creates a card"""
        self.card_id = card_id
        self.suit = CARD_SUITS[str(card_id % NUM_SUITS)]
        self.value = (card_id // NUM_SUITS) + 1
        self.is_red = True if card_id % NUM_SUITS in RED_SUITS else False
        self.state = STR_DECK # The area the card is placed on the board
        self.state_position = 0 # The horizontal position of the card
        self.state_height = 0 # The number of cards below this one
        self.board = board
        self.image = PhotoImage(file="card_folder\\" + CARD_NAMES[str(self.value)] + self.suit[0] + ".gif")
        self.button = DualButton(board.window, 
                                 height=BUTTON_HEIGHT, 
                                 width=BUTTON_WIDTH, 
                                 image=self.image, 
                                 relief="flat", anchor=N, 
                                 command=self.send_move, 
                                 highlightthickness=0, 
                                 borderwidth=0)
    
    def send_move(self):
        """Tells the board to start moving this card"""
        self.board.prepare_move(self)
    
    def __str__(self):
        """Returns a string representation of the card"""
        return CARD_NAMES[str(self.value)] + self.suit[0]
    
    def get_position(self):
        """Returns a tuple containing the state, position and height of the card"""
        return (self.state, self.state_position, self.state_height)
    
    def move(self, state=None, position=None, height=None):
        """Moves this card to the specified position"""
        state = self.state = self.state if state is None else state
        position = self.state_position = self.state_position if position is None else position
        height = self.state_height = self.state_height if height is None else height
        
        self.button.grid_forget()
        
        # If the card is visible
        if state not in [STR_PILE, STR_USED_DECK, STR_DECK]:
            host_frame = self.board.get_card_place(state, position)
            self.button.enable_button()
            self.button.config(image=self.image)
            if state == STR_BOARD:
                self.button.disable_button()
                self.button.config(image=BACK_IMAGE, height=BUTTON_SMALL_HEIGHT)
            elif state == STR_TOP_PILE:
                self.button.disable_button()
                self.button.config(height=BUTTON_HEIGHT)
            elif state == STR_VIS_BOARD:
                self.button.config(height=BUTTON_SMALL_HEIGHT)
            else:
                self.button.config(height=BUTTON_HEIGHT)
                
            row = height if state in [STR_BOARD, STR_VIS_BOARD, STR_TOP_BOARD] else 0
            self.button.grid(in_=host_frame, row=row, column=0)
    
    def move_here(self):
        """Tells the board to move a moving card here"""
        self.board.move_card(self)



class Board:
    """A Board class"""
    
    SYSTEM_BG = "SystemButtonFace"
    CANCEL_BG = "red"
    VALID_BG = "green"
    
    def __init__(self, window):
        """Creates a Board"""
        self.window = window
        window.columnconfigure(NUM_SUITS, weight=1)
        
        self.card_dict = {}
        self.moving_card = None
        
        # Creates each pile
        self.piles_frame = Frame(window)
        self.piles_frame.grid(row=0, column=0, columnspan=NUM_SUITS)
        self.pile_list = [] # There is a pile for each suit stored here
        for i in range(0, NUM_SUITS):
            self.pile_list.append(Pile(self, i))
            self.pile_list[-1].pile_frame.grid(row=0, column=i)
        
        # Creates each stack
        self.stacks_frame = Frame(window)
        self.stacks_frame.grid(row=1, column=0, columnspan=BOARD_SIZE)
        self.stack_list = [] # There are (usually) 7 stacks stored here
        for i in range(0, BOARD_SIZE):
            self.stack_list.append(Stack(self, i))
            self.stack_list[-1].stack_frame.grid(row=0, column=i, sticky=N)
            max_height = BOARD_SIZE + len(CARD_NAMES) # Max number of hidden 
            # cards plus the biggest possible stack of cards
        
        # Deals the cards
        self.deck = Deck(self)
        self.deal()
    
    def deal(self):
        """Deals the cards"""
        card_list = []
        for card_id in range(DECK_SIZE):
            new_card = Card(card_id, self)
            card_list.append(new_card)
            self.card_dict[CARD_NAMES[str(new_card.value)] + new_card.suit[0]] = new_card
        
        # Shuffles the cards and moves them to the deck
        shuffle(card_list)
        for i, card in enumerate(card_list):
            self.deck.closed_deck_cards.append(card)
            card.state_height=i
        
        for stack in self.stack_list:
            stack.empty_button.grid_forget()
        
        # Removes cards from the deck and places them on the board
        for i in range(BOARD_SIZE):
            card = self.deck.closed_deck_cards.pop()
            card.move(STR_TOP_BOARD, i, i)
            self.get_card_list(STR_TOP_BOARD, i).append(card)
            for j in range(i+1, BOARD_SIZE):
                card = self.deck.closed_deck_cards.pop()
                card.move(STR_BOARD, j, i)
                self.get_card_list(STR_BOARD, j).append(card)                
                
    def get_card_place(self, state, position):
        """Returns the frame for the card to place its button"""
        if state == STR_TOP_PILE:
            return self.pile_list[position].pile_frame
        elif state == STR_TOP_DECK:
            return self.deck.open_frame     
        else:
            return self.stack_list[position].stack_frame
    
    def get_card_list(self, state, position):
        """Returns the list for the card to place its reference"""
        if state == STR_TOP_PILE or state == STR_PILE:
            return self.pile_list[position].pile_cards
        elif state == STR_TOP_DECK or state == STR_USED_DECK:
            return self.deck.open_deck_cards
        elif state == STR_DECK:
            return self.deck.closed_deck_cards        
        else:
            return self.stack_list[position].stack_cards
    
    def restore_commands(self):
        """Restores the normal commands of the cards after a card is moved"""
        self.deck.closed_deck_button.enable_button()
        
        for pile in self.pile_list:
            pile.empty_button.config(bg=Board.SYSTEM_BG)
            pile.empty_button.disable_button()
            
        for stack in self.stack_list:
            stack.empty_button.config(bg=Board.SYSTEM_BG)
            stack.empty_button.disable_button()
            
        for card in self.card_dict.values():
            if card.state in [STR_TOP_DECK, STR_TOP_BOARD, STR_VIS_BOARD]:
                card.button.enable_button()
                card.button.config(command=card.send_move, bg=Board.SYSTEM_BG)
            else:
                card.button.disable_button()
                card.button.config(command=card.send_move, bg=Board.SYSTEM_BG)
    
    def prepare_move(self, moving_card):
        """Prepares a card to be moved, changing the command of all possible
        targets"""
        self.moving_card = moving_card
        moving_card.button.config(command=moving_card.move_here, bg=Board.CANCEL_BG)
        for card in self.card_dict.values():
            # Allows some cards in the top of the pile to have cards moved to it
            if card.state == STR_TOP_PILE and card.value + 1 == \
               moving_card.value and card.suit == moving_card.suit and \
               moving_card.state != STR_VIS_BOARD:
                card.button.enable_button()
                card.button.config(command=card.move_here, bg=Board.VALID_BG)
            # Allows some cards on the board to have cards moved to it
            elif card.state == STR_TOP_BOARD and card.value == \
                 moving_card.value + 1 and card.is_red != moving_card.is_red \
                 and card.get_position()[:2] != moving_card.get_position()[:2]:
                card.button.enable_button()
                card.button.config(command=card.move_here, bg=Board.VALID_BG)
            # Allows the user to cancel the move by selecting the same button
            elif card == moving_card:
                card.button.enable_button()
            else:
                card.button.disable_button()
        
        self.deck.closed_deck_button.disable_button()
        
        # Allows Aces to be moved to empty piles
        for pile in self.pile_list:
            if len(pile.pile_cards) == 0 and moving_card.state != STR_VIS_BOARD\
               and moving_card.value == 1:
                pile.empty_button.enable_button()
                pile.empty_button.config(bg=Board.VALID_BG)
        
        # Allows Kings to be moved to empty stacks
        for stack in self.stack_list:
            if len(stack.stack_cards) == 0 and \
               moving_card.value == len(CARD_NAMES):
                stack.empty_button.enable_button()
                stack.empty_button.config(bg=Board.VALID_BG)
    
    def move_card(self, target):
        """Moves a moving card to a target card"""
        
        # If the target card is not the same as the moving card
        if target != self.moving_card:
            
            # This sets the desired new state of the moving card
            if self.moving_card.state != STR_VIS_BOARD:
                state = target.state
            else:
                state = STR_VIS_BOARD
            position = target.state_position
            height = target.state_height + 1
            
            # If the target is not on the pile
            if type(target) == Card:
                if target.state == STR_TOP_BOARD:
                    target.state = STR_VIS_BOARD
                    target.button.config(height=BUTTON_SMALL_HEIGHT)
                elif target.state == STR_TOP_PILE:
                    target.state = STR_PILE
                    target.button.grid_forget()
    
            prev_pos = self.moving_card.get_position()
            # If the desired state implies that only one card will move
            if state in [STR_TOP_PILE, STR_TOP_BOARD]:
                self.get_card_list(state, position).append(self.moving_card)
                self.moving_card.move(state, position, height)
                self.get_card_list(*prev_pos[:2]).pop()
                
                # Shows the next card of the deck if the moving card was there
                if prev_pos[0] == STR_TOP_DECK:
                    if prev_pos[2] > 0:
                        self.deck.open_deck_cards.peek().move(state=STR_TOP_DECK)
                    else:
                        self.deck.open_deck_label.grid()
                # Otherwise the card must be on the board, so show the next
                # card in that position
                else:
                    prev_stack = self.stack_list[prev_pos[1]]
                    if len(prev_stack.stack_cards) == 0:
                        prev_stack.empty_button.disable_button()
                        prev_stack.empty_button.grid()
                    else:
                        self.get_card_list(*prev_pos[:2]).peek().move(
                            STR_TOP_BOARD)
            # Otherwise, there must be multiple cards moving, so move all cards
            # in the pile
            elif state == STR_VIS_BOARD:
                vis_target = Empty(state, position, height)
                self.move_recursive(self.get_card_list(*prev_pos[:2]), 
                                    prev_pos[2], vis_target)
                prev_stack = self.stack_list[prev_pos[1]]
                if len(prev_stack.stack_cards) == 0:
                    prev_stack.empty_button.disable_button()
                    prev_stack.empty_button.grid()
                else:
                    self.get_card_list(*prev_pos[:2]).peek().move(STR_TOP_BOARD)                
                
        self.restore_commands()
        
    def move_recursive(self, home_list, index, target):
        """Recursively moves a stack of cards from a home list to a target"""
        if len(home_list) > index:
            if len(home_list) == index + 1:
                target.state = STR_TOP_BOARD            
            self.get_card_list(target.state, target.state_position).append(home_list.peek(index))
            home_list.peek(index).move(target.state, target.state_position, target.state_height)
            target.state_height += 1
            self.move_recursive(home_list, index+1, target)
            home_list.pop()
            
            

class Pile:
    """A class that operates an ordered pile of cards"""
    
    def __init__(self, board, pileid):
        """Creates the pile operator"""
        self.board = board
        self.pileid = pileid
        self.pile_frame = Frame(self.board.piles_frame)
        self.pile_cards = CardContainer()
        self.empty_button = DualButton(self.pile_frame,
                                       True,
                                       image=EMPTY_IMAGE,
                                       relief=BUTTON_RELIEF,
                                       command=self.move_here,
                                       highlightthickness=0,
                                       borderwidth=0)
        self.empty_button.grid()
    
    def move_here(self):
        """Moves a card to this empty pile"""
        self.empty_button.grid_forget()
        target = Empty(STR_TOP_PILE, self.pileid, -1)
        self.board.move_card(target)

class Stack:
    """A class that operates a stack of cards on the board"""
    
    def __init__(self, board, stackid):
        """Creates the pile operator"""
        self.board = board
        self.stackid = stackid
        self.stack_frame = Frame(self.board.stacks_frame)
        self.stack_cards = CardContainer()
        self.empty_button = DualButton(self.stack_frame,
                                       True,
                                       image=EMPTY_IMAGE,
                                       relief=BUTTON_RELIEF,
                                       command=self.move_here,
                                       highlightthickness=0,
                                       borderwidth=0)
        self.empty_button.grid(row=0, column=0)
    
    def move_here(self):
        """Moves a card to this empty stack"""
        self.empty_button.grid_forget()
        target = Empty(STR_TOP_BOARD, self.stackid, -1)
        self.board.move_card(target)
    
class Deck:
    """A class that operates the deck"""
    
    def __init__(self, board):
        """Creates the deck operator"""
        self.closed_frame = Frame(board.window)
        self.closed_frame.grid(row=0, column=BOARD_SIZE - 2)
        self.closed_deck_cards = CardContainer()
        self.closed_deck_button = DualButton(self.closed_frame, 
                                         image=BACK_IMAGE,
                                         relief=BUTTON_RELIEF,
                                         command=self.flip, 
                                         highlightthickness=0, 
                                         borderwidth=0)
        self.closed_deck_button.grid()
        
        self.open_frame = Frame(board.window)
        self.open_frame.grid(row=0, column=BOARD_SIZE - 1)
        self.open_deck_cards = CardContainer()
        self.open_deck_label = Label(self.open_frame, 
                                     image=EMPTY_IMAGE, 
                                     highlightthickness=0, 
                                     borderwidth=0)  
        self.open_deck_label.grid()
    
    def flip(self):
        """Moves a card from the deck to the top of the deck if possible.
        Otherwise this refreshes the deck"""
        # Flips a card if there are cards in the deck
        if len(self.closed_deck_cards) != 0:
            card = self.closed_deck_cards.pop()
            if len(self.open_deck_cards) != 0: 
                # Hides the last visible card of the deck
                self.open_deck_cards.peek().move(state=STR_USED_DECK)
            else:
                # Hides the empty card marker
                self.open_deck_label.grid_forget()
                
            card.move(state=STR_TOP_DECK, height=len(self.open_deck_cards))
            self.open_deck_cards.append(card)
            if len(self.closed_deck_cards) == 0:
                self.closed_deck_button.config(image=EMPTY_IMAGE)
        # Otherwise resets the deck
        else:
            card = self.open_deck_cards.pop()
            card.button.grid_forget()
            self.closed_deck_cards.append(card)
            card.move(state=STR_DECK, height=0)
            for i in range(len(self.open_deck_cards)):
                card = self.open_deck_cards.pop()
                self.closed_deck_cards.append(card)
                card.move(state=STR_DECK, height=i)
            self.closed_deck_button.config(image=BACK_IMAGE)
            self.open_deck_label.grid()     

board = Board(WINDOW)
if __name__ == "__main__":
    WINDOW.mainloop()