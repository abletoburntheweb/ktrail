from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import QRect
from random import randint, choices


class TileType:
    def __init__(self, name, texture_paths, weights=None):
        self.name = name
        self.textures = [QPixmap(path) for path in texture_paths]
        self.weights = weights or [1] * len(self.textures)

    def get_random_texture(self):
        return choices(self.textures, weights=self.weights, k=1)[0]


class Tree:
    def __init__(self, x, y, texture):
        self.x = x
        self.y = y
        self.width = 384
        self.height = 384
        self.texture = texture.scaled(self.width, self.height)

    def move(self, speed):
        self.y += speed

    def is_visible(self, screen_rect):
        tree_rect = QRect(self.x, self.y, self.width, self.height)
        return screen_rect.intersects(tree_rect)


class TileManagerDuo:
    def __init__(self, tile_size, rows, cols, screen_width, screen_height):
        self.tile_size = tile_size
        self.rows = rows
        self.cols = cols
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.left_zone_width = screen_width // 2
        self.right_zone_width = screen_width - self.left_zone_width

        self.tiles = []
        self.trees = []

        self.tile_types = {}
        self.tree_type = None

    def add_tile_type(self, name, texture_paths, weights=None):
        self.tile_types[name] = TileType(name, texture_paths, weights)

    def load_default_tile_types(self):
        self.add_tile_type(
            "asphalt",
            [
                "assets/textures/asf.png",
                "assets/textures/asf1.png",
                "assets/textures/asf2.png",
                "assets/textures/asf3.png"
            ],
            weights=[4, 3, 2, 1]
        )
        self.add_tile_type("grass", ["assets/textures/grass.png"])
        self.add_tile_type("grass_side", ["assets/textures/grass_side.png"])
        self.add_tile_type("grass_side_l", ["assets/textures/grass_side_l.png"])
        self.add_tile_type("decoration", ["assets/textures/j_bush.png"])

        self.add_tile_type(
            "tree",
            [
                "assets/textures/tree.png",
                "assets/textures/tree2.png",
                "assets/textures/el.png"
            ],
            weights=[3, 3, 4])

        self.tree_type = self.tile_types["tree"]

    def get_tile_texture(self, name):
        if name not in self.tile_types:
            return QPixmap()
        return self.tile_types[name].get_random_texture()

    def create_tile(self, col, row, y_pos):
        x = col * self.tile_size
        zone = "left" if x < self.left_zone_width else "right"

        half_cols = self.cols // 2
        col_in_half = col % half_cols

        if zone == "right":
            col_in_half = half_cols - 1 - col_in_half

        if col_in_half < 3:
            tile_type = "grass"
        else:
            tile_type = "asphalt"

        texture = self.get_tile_texture(tile_type).scaled(self.tile_size, self.tile_size)

        grass_side_texture = None
        if zone == "left" and col_in_half ==3:
            grass_side_texture = self.get_tile_texture("grass_side_l").scaled(self.tile_size, self.tile_size)
        elif zone == "right" and col_in_half == 3:
            grass_side_texture = self.get_tile_texture("grass_side").scaled(self.tile_size, self.tile_size)

        decorations = []
        if tile_type == "grass" and randint(1, 100) <= 10:
            decoration = self.get_tile_texture("decoration")
            decorations.append(decoration)

        return {
            "x": x,
            "y": y_pos,
            "type": tile_type,
            "texture": texture,
            "decorations": decorations,
            "grass_side_texture": grass_side_texture,
            "zone": zone
        }

    def init_tiles(self):
        self.tiles.clear()
        for row in range(self.rows):
            for col in range(self.cols):
                y = row * self.tile_size - 1
                self.tiles.append(self.create_tile(col, row, y))

        self.init_trees_on_grass()

    def init_trees_on_grass(self):
        self.trees.clear()
        for tile in self.tiles:
            if tile["type"] == "grass" and randint(1, 100) <= 5:
                self.spawn_tree(tile["x"], tile["y"])

    def spawn_tree(self, x, y):
        offset = 64
        tree_x = x - (384 - self.tile_size) // 2
        tree_y = y - (384 - self.tile_size) // 2 - offset
        texture = self.tree_type.get_random_texture()
        self.trees.append(Tree(tree_x, tree_y, texture))

    def update_tiles(self,speed_right, speed_left):
        new_tiles = []

        for tile in self.tiles:
            speed = speed_left if tile["x"] < self.left_zone_width else speed_right
            new_y = tile["y"] + speed
            if new_y <= self.screen_height:
                tile["y"] = new_y
                new_tiles.append(tile)

        for col in range(self.cols):
            x = col * self.tile_size
            top_y = -self.tile_size + max(speed_left, speed_right) - 1

            has_top = any(t["x"] == x and t["y"] <= 0 < t["y"] + self.tile_size for t in new_tiles)
            if not has_top:
                new_tile = self.create_tile(col, 0, top_y)
                new_tiles.insert(0, new_tile)

                if new_tile["type"] == "grass" and randint(1, 100) <= 25:
                    self.spawn_tree(new_tile["x"], new_tile["y"])

        self.tiles = [t for t in new_tiles if t["y"] + self.tile_size > 0]

        screen_rect = QRect(0, 0, self.screen_width, self.screen_height)
        for tree in self.trees:
            speed = speed_left if tree.x < self.left_zone_width else speed_right
            tree.move(speed)
        self.trees = [t for t in self.trees if t.is_visible(screen_rect)]

    def draw_tiles(self, painter):
        screen_rect = QRect(0, 0, self.screen_width, self.screen_height)

        for tile in self.tiles:
            painter.drawPixmap(int(tile["x"]), int(tile["y"]), tile["texture"])
            if tile["grass_side_texture"]:
                painter.drawPixmap(int(tile["x"]), int(tile["y"]), tile["grass_side_texture"])
            for decoration in tile["decorations"]:
                painter.drawPixmap(
                    int(tile["x"] + (self.tile_size - decoration.width()) // 2),
                    int(tile["y"] + (self.tile_size - decoration.height()) // 2),
                    decoration
                )

        for tree in self.trees:
            if tree.is_visible(screen_rect):
                painter.drawPixmap(tree.x, tree.y, tree.texture)