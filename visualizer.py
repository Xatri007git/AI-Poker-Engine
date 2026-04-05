import pygame
import sys
from game import GamePhase
from player import PlayerStatus

# --- Configuration & Colors ---
WIDTH, HEIGHT = 1000, 700
TABLE_COLOR = (35, 100, 50)     # Dark Green Felt
BORDER_COLOR = (139, 69, 19)    # Brown Wood
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 30)
GOLD = (255, 215, 0)
GRAY = (150, 150, 150)

class PokerGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("AI Poker Engine Live View")
        
        # Initialize fonts (using system default fonts)
        self.card_font_large = pygame.font.SysFont('arial', 28, bold=True)
        self.card_font_small = pygame.font.SysFont('arial', 18)
        self.text_font = pygame.font.SysFont('segoeui', 20)
        self.title_font = pygame.font.SysFont('segoeui', 24, bold=True)

    def draw_card(self, card, x, y, hidden=False):
        """Draws a playing card at the specified coordinates."""
        card_w, card_h = 60, 90
        
        # Draw card shadow & base
        pygame.draw.rect(self.screen, (20, 20, 20), (x+2, y+2, card_w, card_h), border_radius=5)
        
        if hidden:
            # Draw card back
            pygame.draw.rect(self.screen, (40, 60, 120), (x, y, card_w, card_h), border_radius=5)
            pygame.draw.rect(self.screen, WHITE, (x, y, card_w, card_h), 2, border_radius=5)
            return

        # Draw card front
        pygame.draw.rect(self.screen, WHITE, (x, y, card_w, card_h), border_radius=5)
        pygame.draw.rect(self.screen, BLACK, (x, y, card_w, card_h), 1, border_radius=5)

        if card is None:
            return

        card_str = str(card)
        rank, suit = card_str[:-1], card_str[-1]
        color = RED if suit in ['♥', '♦'] else BLACK

        # Top-left rank and suit
        rank_text = self.card_font_small.render(rank, True, color)
        suit_text = self.card_font_small.render(suit, True, color)
        self.screen.blit(rank_text, (x + 5, y + 5))
        self.screen.blit(suit_text, (x + 5, y + 25))

        # Center large rank
        center_text = self.card_font_large.render(rank, True, color)
        text_rect = center_text.get_rect(center=(x + card_w//2, y + card_h//2))
        self.screen.blit(center_text, text_rect)

    def draw_table(self):
        """Draws the wooden border and green felt."""
        self.screen.fill((20, 20, 20)) # Background
        # Table outline (Wood)
        pygame.draw.ellipse(self.screen, BORDER_COLOR, (50, 100, 900, 500))
        # Table inner (Felt)
        pygame.draw.ellipse(self.screen, TABLE_COLOR, (70, 120, 860, 460))

    def render_game_state(self, game, show_all_cards=True):
        """Main render loop to be called at every game step."""
        # Process Pygame events to keep the OS from marking the window as "Not Responding"
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        self.draw_table()

        # 1. Draw Community Cards & Pot (Center of table)
        center_x, center_y = WIDTH // 2, HEIGHT // 2 - 20
        
        # Pot information
        pot_text = self.title_font.render(f"Pot: ${game.pot}   Call: ${game.current_bet}", True, GOLD)
        phase_text = self.text_font.render(f"Phase: {game.phase.value.upper()}", True, WHITE)
        self.screen.blit(pot_text, pot_text.get_rect(center=(center_x, center_y - 70)))
        self.screen.blit(phase_text, phase_text.get_rect(center=(center_x, center_y - 100)))

        # Community Cards
        card_spacing = 70
        start_x = center_x - (5 * card_spacing) // 2 + 5
        
        for i in range(5):
            x = start_x + (i * card_spacing)
            if i < len(game.community_cards):
                self.draw_card(game.community_cards[i], x, center_y - 30)
            else:
                # Empty card slot outline
                pygame.draw.rect(self.screen, (50, 120, 70), (x, center_y - 30, 60, 90), 2, border_radius=5)

        # 2. Draw Players
        # Positions: Bottom, Left, Top, Right
        positions = [
            (WIDTH // 2, HEIGHT - 100),       # Bottom (Player 0)
            (150, HEIGHT // 2),               # Left (Player 1)
            (WIDTH // 2, 80),                 # Top (Player 2)
            (WIDTH - 150, HEIGHT // 2)        # Right (Player 3)
        ]

        for i, player in enumerate(game.players):
            # Only support up to 4 graphical positions in this specific layout
            if i >= len(positions): 
                break
                
            pos_x, pos_y = positions[i]
            is_active = (i == game.active_player_index and game.phase != GamePhase.SHOWDOWN)
            
            # Highlight active player's area
            if is_active:
                pygame.draw.rect(self.screen, GOLD, (pos_x - 100, pos_y - 60, 200, 140), 3, border_radius=10)

            # Draw Hole Cards
            cards_x = pos_x - 65
            cards_y = pos_y - 45
            
            if player.status == PlayerStatus.OUT:
                pass # Draw nothing
            elif player.status == PlayerStatus.FOLDED:
                self.draw_card(None, cards_x, cards_y, hidden=True)
                self.draw_card(None, cards_x + 70, cards_y, hidden=True)
            elif show_all_cards or game.phase == GamePhase.SHOWDOWN:
                if len(player.hole_cards) == 2:
                    self.draw_card(player.hole_cards[0], cards_x, cards_y)
                    self.draw_card(player.hole_cards[1], cards_x + 70, cards_y)
            else:
                self.draw_card(None, cards_x, cards_y, hidden=True)
                self.draw_card(None, cards_x + 70, cards_y, hidden=True)

            # Draw Player Info Label
            btn_str = " Ⓑ" if i == game.button_position else ""
            status_color = GRAY if player.status in [PlayerStatus.FOLDED, PlayerStatus.OUT] else WHITE
            
            info_bg = pygame.Surface((180, 60))
            info_bg.set_alpha(200)
            info_bg.fill(BLACK)
            self.screen.blit(info_bg, (pos_x - 90, pos_y + 50))

            name_text = self.title_font.render(f"{player.name}{btn_str}", True, status_color)
            stack_text = self.text_font.render(f"${player.stack} | Bet: ${player.bet_amount}", True, GOLD)
            
            self.screen.blit(name_text, (pos_x - 80, pos_y + 55))
            self.screen.blit(stack_text, (pos_x - 80, pos_y + 80))

        # Update the actual window
        pygame.display.flip()

# Create a global instance so the window doesn't destroy and recreate itself every frame
_gui_instance = None

def update_gui(game):
    global _gui_instance
    if _gui_instance is None:
        _gui_instance = PokerGUI()
    _gui_instance.render_game_state(game, show_all_cards=True)