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


class TileManager:
    def __init__(self, tile_size, rows, cols, screen_width, screen_height):
        self.tile_size = tile_size
        self.rows = rows
        self.cols = cols
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.tiles = []
        self.trees = []
        self.tile_types = {}

        self.tree_type = None  # Для случайного выбора дерева

    def load_default_tile_types(self):
        """Загружает типы тайлов с текстурами и весами"""
        self.add_tile_type("asphalt", [
            "assets/textures/asf.png",
            "assets/textures/asf1.png",
            "assets/textures/asf2.png",
            "assets/textures/asf3.png"
        ], weights=[4, 3, 2, 1])

        self.add_tile_type("grass", ["assets/textures/grass.png"])
        self.add_tile_type("grass_side", ["assets/textures/grass_side.png"])
        self.add_tile_type("decoration", ["assets/textures/j_bush.png"])

        self.add_tile_type("tree", [
            "assets/textures/tree.png",
            "assets/textures/tree2.png",
            "assets/textures/el.png"
        ], weights=[3, 3, 4])

        self.tree_type = self.tile_types["tree"]

    def add_tile_type(self, name, texture_paths, weights=None):
        self.tile_types[name] = TileType(name, texture_paths, weights)

    def get_tile_texture(self, name):
        if name not in self.tile_types:
            return QPixmap()
        return self.tile_types[name].get_random_texture()

    def create_tile(self, col, row, tile_type, y_pos):
        """Создаёт один тайл с декорациями"""
        x = col * self.tile_size
        texture = self.get_tile_texture(tile_type).scaled(self.tile_size, self.tile_size)

        grass_side_texture = self.get_tile_texture("grass_side").scaled(self.tile_size, self.tile_size) if col == 3 else None

        decorations = []
        if tile_type == "grass" and randint(1, 100) <= 10:
            decorations.append(self.get_tile_texture("decoration"))

        return {
            "x": x,
            "y": y_pos,
            "type": tile_type,
            "texture": texture,
            "decorations": decorations,
            "grass_side_texture": grass_side_texture
        }

    def init_tiles(self):
        """Инициализирует начальные тайлы"""
        self.tiles.clear()
        for row in range(self.rows):
            for col in range(self.cols):
                y = row * self.tile_size - 1
                tile_type = "asphalt" if col < 4 else "grass"
                self.tiles.append(self.create_tile(col, row, tile_type, y))

        self.init_trees_on_grass()

    def init_trees_on_grass(self):
        """Добавляет деревья только на траве"""
        self.trees.clear()
        for tile in self.tiles:
            if tile["type"] == "grass" and randint(1, 100) <= 5:
                self.spawn_tree(tile["x"], tile["y"])

    def spawn_tree(self, x, y):
        """Создаёт дерево со случайной текстурой и смещением"""
        texture = self.tree_type.get_random_texture()
        offset = 64
        tree_x = x - (384 - self.tile_size) // 2
        tree_y = y - (384 - self.tile_size) // 2 - 90
        self.trees.append(Tree(tree_x, tree_y, texture))

    def update_tiles(self, speed):
        """Обновляет тайлы и добавляет новые сверху"""
        new_tiles = []

        # Обновляем существующие тайлы
        for tile in self.tiles:
            new_y = tile["y"] + speed
            if new_y <= self.screen_height:
                tile["y"] = new_y
                new_tiles.append(tile)

        # Добавляем новые тайлы сверху
        for col in range(self.cols):
            top_y = -self.tile_size + (speed - 1)
            has_top = any(t["x"] == col * self.tile_size and t["y"] <= 0 < t["y"] + self.tile_size for t in new_tiles)
            if not has_top:
                tile_type = "asphalt" if col < 4 else "grass"
                new_tile = self.create_tile(col, 0, tile_type, top_y)
                new_tiles.insert(0, new_tile)

                # Добавляем дерево на траву
                if tile_type == "grass" and randint(1, 100) <= 25:
                    self.spawn_tree(new_tile["x"], new_tile["y"])

        self.tiles = [t for t in new_tiles if t["y"] + self.tile_size > 0]

        # Обновляем позиции деревьев
        screen_rect = QRect(0, 0, self.screen_width, self.screen_height)
        for tree in self.trees:
            tree.move(speed)
        self.trees = [t for t in self.trees if t.is_visible(screen_rect)]

        return self.tiles

    def draw_tiles(self, painter):
        """Рисует все тайлы и деревья"""
        screen_rect = QRect(0, 0, self.screen_width, self.screen_height)

        for tile in self.tiles:
            painter.drawPixmap(tile["x"], tile["y"], tile["texture"])
            if tile["grass_side_texture"]:
                painter.drawPixmap(tile["x"], tile["y"], tile["grass_side_texture"])
            for decoration in tile["decorations"]:
                painter.drawPixmap(tile["x"], tile["y"], decoration)

        for tree in self.trees:
            if tree.is_visible(screen_rect):
                painter.drawPixmap(tree.x, tree.y, tree.texture)