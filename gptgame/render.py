import pygame
from game import Game
from statechange import StateChange
from unit import Spawner, Soldier


class Renderer:
    def __init__(self, game) -> None:
        dims = game.game_dimensions()
        self.cell_size = 50
        self.width = dims[0] * self.cell_size
        self.height = dims[1] * self.cell_size
        self.game = game
        pygame.init()
        pygame.display.set_caption("GPT Game")
        self.screen = pygame.display.set_mode((self.width, self.height))
        # self.font = pygame.font.SysFont("Arial", 20)
        # self.font_small = pygame.font.SysFont("Arial", 10)
        self.debug = False

    def render(self, state_changes: StateChange):
        board = self.game.board
        self.screen.fill((0, 0, 0))
        for i in range(board.height()):
            for j in range(board.width()):
                tile = board.get_tile(j, i)
                self.render_tile(tile)

        for state_change in state_changes.state_changes:
            self.render_state_change(state_change)
        
        pygame.display.flip()

    def render_state_change(self, state_change: StateChange):
        for action in state_change:
            # act_action = action[1]
            # move_action = action[0]
            if action.__class__.__name__ == "AttackAction":
                self.render_attack_action(action)
            # TODO: Add other actions

    def render_attack_action(self, action):
        color = action.attacker.player.color
        attacker_pos = self.get_center(action.attacker.x, action.attacker.y)
        target_pos = self.get_center(action.target.x, action.target.y)
        pygame.draw.line(self.screen, color, attacker_pos, target_pos, 2)

    def render_tile(self, tile):
        self.render_rubble(tile)
        self.render_resource(tile)
        self.render_occupant(tile)
        if self.debug:
            self.render_health(tile)
            self.render_cooldown(tile)
            self.render_attack_range(tile)
            self.render_unit_vision_range(tile)

    def render_rubble(self, tile):
        rubble = tile.rubble
        if rubble == 0:
            return
        color = (rubble * 50, rubble * 50, rubble * 50)
        pygame.draw.rect(self.screen, color, self.get_rect(tile.x, tile.y))

    def render_resource(self, tile):
        resource = tile.resource
        if resource == 0:
            return
        color = (0, 255, 0)
        circle_radius = 5
        pygame.draw.circle(
            self.screen, color, self.get_center(tile.x, tile.y), circle_radius
        )

    def render_occupant(self, tile):
        if not tile.is_occupied():
            return
        occupant = tile.occupant
        color = occupant.player.color
        if isinstance(occupant, Spawner):
            pygame.draw.rect(self.screen, color, self.get_rect(tile.x, tile.y))
        elif isinstance(occupant, Soldier):
            pygame.draw.circle(self.screen, color, self.get_center(tile.x, tile.y), 10)
            # pygame.draw.rect(self.screen, color, self.get_rect(tile.x, tile.y))

    def render_health(self, tile):
        raise NotImplementedError

    def render_cooldown(self, tile):
        raise NotImplementedError

    def render_attack_range(self, tile):
        raise NotImplementedError

    def render_unit_vision_range(self, tile):
        raise NotImplementedError

    def get_rect(self, x, y):
        return pygame.Rect(
            x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size
        )

    def get_center(self, x, y):
        return (
            x * self.cell_size + self.cell_size // 2,
            y * self.cell_size + self.cell_size // 2,
        )
