import os
import sys
import time
from player import PlayerStatus,Player,PlayerAction
from game import PokerGame, GamePhase
from baseplayers import InputPlayer, RaisePlayer, FoldPlayer, cheating_player


def run_game(num_hands):
    disqualified_players = [] # list of disqualified players
    attempt_limit = 3 # number of tries a player is provided before making a valid move(inclusive)
    players = [
        InputPlayer("Alice", 1000),
        InputPlayer("Bob", 1000),
        cheating_player("Charlie", 1000),
        InputPlayer("David", 1000)
    ]
    
    # Create game
    game = PokerGame(players, big_blind=20)

    # Run several hands
    for _ in range(num_hands):
        print(f"\nHand number {game.hand_number + 1}")
        game_status = game.start_new_hand()
        if not game_status:
            print(f"Not enough players left in the game... game over.") 
            break
        
        # Main game loop
        num_tries = 0
        while game.phase != GamePhase.SHOWDOWN:
            if num_tries == attempt_limit:
                #game.player_action(PlayerAction.FOLD, 0) # instead of folding we must kick this player out
                game.players[game.active_player_index].status = PlayerStatus.OUT
                disqualified_players.append(game.players[game.active_player_index])
                # Move to next player_hand
                game.has_played[game.active_player_index] = True
                game.active_player_index = (game.active_player_index + 1) % len(game.players)

                # Check if betting round is complete
                if game.is_betting_round_complete():
                    game.advance_game_phase()
                else:
                    game._adjust_active_player_index()

                # Show updated game state
                game.display_game_state()
                num_tries = 0
                continue

            player = game.players[game.active_player_index]

            if game.num_active_players() == 1 and player.bet_amount == game.current_bet:
                game.advance_game_phase()
                game.display_game_state()
                continue

            print(f"\n{player.name}'s turn")
            print(f"Your cards: {[str(c) for c in player.hole_cards]}")

            try:
                is_successful = game.get_player_input()
            except Exception as e:
                print(f"Player {player.name}'s turn failed: {e}")
                is_successful = False

            if not is_successful:
                print("Invalid command received.")
                num_tries += 1
            else:
                num_tries = 0
            time.sleep(.5)

        print("\nHand complete. Starting new hand...")
        # time.sleep(5)

    print("Winners are:")
    for g, winner, winning in game.hand_winners:
        print(f"Game {g}: {winner} ({winning})")
    print("\nFinal stack sizes are:")
    for player in game.players:
        if(player not in disqualified_players):
         print(f"{player.name}: ${player.stack}")
    
    print("The following players were disqualified for invalid inputs or cheating: ")
    for player in disqualified_players:
        print(player.name)


if __name__ == "__main__":
    # start_time = time.time()
    # with open("logs.txt", "w", encoding="utf-8") as f:
    #     sys.stdout = f
    #     run_game(40)
    #
    # sys.stdout = sys.__stdout__
    # end_time = time.time()
    # print("Game over. Total time taken:", end_time - start_time)
    run_game(5)
