import random
import csv
import os
import pandas as pd
import matplotlib.pyplot as plt

# Constants
INITIAL_BALANCE = 1000
INITIAL_BET = 10
DECK_SIZE = 52
DECKS = 6
BLACKJACK = 21
NUM_SIMULATIONS = 1000  # Total number of games per run
NUM_RUNS = 10  # Number of runs
CSV_FILE = 'blackjack_results.csv'

# Define card values
card_values = {str(i): i for i in range(2, 11)}
card_values.update({'J': 10, 'Q': 10, 'K': 10, 'A': 11})

def create_deck():
    """Create a deck of cards."""
    deck = list(card_values.keys()) * 4 * DECKS
    random.shuffle(deck)
    return deck

def deal_card(deck):
    """Deal a single card from the deck."""
    return deck.pop()

def hand_value(hand):
    """Calculate the value of a hand."""
    value, aces = 0, hand.count('A')
    for card in hand:
        value += card_values[card]
    while value > BLACKJACK and aces:
        value -= 10
        aces -= 1
    return value

def basic_strategy(player_hand, dealer_card):
    """Determine the action based on basic strategy."""
    player_value = hand_value(player_hand)
    dealer_value = card_values[dealer_card]
    
    if player_value >= 17:
        return 'stand'
    if player_value >= 13 and dealer_value <= 6:
        return 'stand'
    if player_value == 12 and dealer_value in [4, 5, 6]:
        return 'stand'
    if player_value == 11:
        return 'double'
    if player_value == 10 and dealer_value <= 9:
        return 'double'
    if player_value <= 8:
        return 'hit'
    return 'hit'

def print_hand(player_hand, dealer_hand, reveal_dealer_card=False):
    """Print the hands of the player and dealer."""
    print(f"Player's hand: {player_hand} (Value: {hand_value(player_hand)})")
    if reveal_dealer_card:
        print(f"Dealer's hand: {dealer_hand} (Value: {hand_value(dealer_hand)})")
    else:
        print(f"Dealer's hand: [{dealer_hand[0]}, ?]")

def play_blackjack(balance, bet):
    """Play a game of blackjack and return the outcome and the updated balance."""
    deck = create_deck()
    player_hand = [deal_card(deck), deal_card(deck)]
    dealer_hand = [deal_card(deck), deal_card(deck)]

    # Player's turn
    while True:
        action = basic_strategy(player_hand, dealer_hand[0])
        if action == 'hit':
            player_hand.append(deal_card(deck))
            if hand_value(player_hand) > BLACKJACK:
                return -bet, balance - bet, player_hand, dealer_hand
        elif action == 'stand':
            break
        elif action == 'double':
            bet *= 2
            player_hand.append(deal_card(deck))
            if hand_value(player_hand) > BLACKJACK:
                return -bet, balance - bet, player_hand, dealer_hand
            break

    # Dealer's turn
    while hand_value(dealer_hand) < 17:
        dealer_hand.append(deal_card(deck))
    
    print_hand(player_hand, dealer_hand, reveal_dealer_card=True)

    # Determine winner
    player_value = hand_value(player_hand)
    dealer_value = hand_value(dealer_hand)

    if player_value > BLACKJACK:
        return -bet, balance - bet, player_hand, dealer_hand
    elif dealer_value > BLACKJACK or player_value > dealer_value:
        return bet, balance + bet, player_hand, dealer_hand
    elif player_value < dealer_value:
        return -bet, balance - bet, player_hand, dealer_hand
    else:
        return 0, balance, player_hand, dealer_hand

def write_to_csv(data):
    """Write game results to a CSV file."""
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Run #', 'Game #', 'Bet Amount', 'Player Hand Total', 'Dealer Hand Total', 'Win/Loss', 'Balance'])
        writer.writerows(data)

def analyze_data():
    """Analyze and plot the data from the CSV file."""
    df = pd.read_csv(CSV_FILE)

    # Plotting the balance over games for each run
    plt.figure(figsize=(12, 6))
    for run in df['Run #'].unique():
        run_data = df[df['Run #'] == run]
        plt.plot(run_data.index, run_data['Balance'], label=f'Run {run}')
    
    plt.xlabel('Game #')
    plt.ylabel('Balance')
    plt.title('Balance Over Time for Each Run')
    plt.legend()
    plt.grid(True)
    plt.show()

def main():
    all_results = []

    # Clear the CSV file at the start
    if os.path.exists(CSV_FILE):
        os.remove(CSV_FILE)

    for run in range(NUM_RUNS):
        print(f"Starting run {run + 1}")
        total_balance = INITIAL_BALANCE
        initial_bet = INITIAL_BET
        current_bet = INITIAL_BET
        num_wins = 0
        num_losses = 0
        num_pushes = 0

        for i in range(NUM_SIMULATIONS):
            if total_balance < current_bet:
                print("Insufficient balance for the next bet.")
                break
            
            balance = total_balance
            outcome, balance, player_hand, dealer_hand = play_blackjack(balance, current_bet)
            total_balance = balance
            
            # Determine the result string
            if outcome > 0:
                result = 'Win'
                num_wins += 1
                current_bet = INITIAL_BET  # Reset bet after a win
            elif outcome < 0:
                result = 'Loss'
                num_losses += 1
                current_bet *= 2  # Double the bet after a loss
            else:
                result = 'Push'
                num_pushes += 1
                # Bet amount remains the same after a push

            # Append results to the list
            all_results.append([
                run + 1,  # Run number
                i + 1,  # Game number
                current_bet,  # Current bet amount
                hand_value(player_hand),  # Player hand total
                hand_value(dealer_hand),  # Dealer hand total
                result,  # Win/Loss/Push
                total_balance  # Balance after the game
            ])

    # Write results to CSV
    write_to_csv(all_results)

    print(f"\nSimulation complete. Results written to {CSV_FILE}")

    # Analyze and plot data
    analyze_data()

if __name__ == "__main__":
    main()
