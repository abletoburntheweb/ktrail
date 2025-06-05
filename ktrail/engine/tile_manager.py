from PyQt5.QtGui import QPixmap
from random import choices

class TileType:
    def __init__(self, name, texture_paths, weights=None):
        self.name = name
        self.textures = [QPixmap(path) for path in texture_paths]
        self.weights = weights or [1] * len(self.textures)

    def get_random_texture(self):
        return choices(self.textures, weights=self.weights, k=1)[0]

class TileManager:
    def __init__(self, tile_size, rows, cols, screen_width, screen_height):
        self.tile_size = tile_size
        self.rows = rows
        self.cols = cols
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.tile_types = {}
        self.tiles = []

    def add_tile_type(self, name, texture_paths, weights=None):
        self.tile_types[name] = TileType(name, texture_paths, weights)

    def get_tile_texture(self, name):
        if name not in self.tile_types:
            return QPixmap()
        return self.tile_types[name].get_random_texture()

    def init_tiles(self):
        self.tiles.clear()
        for row in range(self.rows):
            for col in range(self.cols):
                x = col * self.tile_size
                y = row * self.tile_size - 1
                tile_type = "asphalt" if col < 4 else "grass"
                texture = self.get_tile_texture(tile_type).scaled(self.tile_size, self.tile_size)
                self.tiles.append({
                    "x": x,
                    "y": y,
                    "type": tile_type,
                    "texture": texture
                })

    def update_tiles(self, speed):
        new_tiles = []
        for tile in self.tiles:
            new_y = tile["y"] + speed
            if new_y <= self.screen_height:
                tile["y"] = new_y
                new_tiles.append(tile)

        # Добавляем новые тайлы сверху
        for col in range(self.cols):
            x = col * self.tile_size
            top_y = -self.tile_size + (speed - 1)

            # Проверяем, есть ли уже тайл в этом столбце
            has_top = any(t["x"] == x and t["y"] <= 0 < t["y"] + self.tile_size for t in new_tiles)
            if not has_top:
                tile_type = "asphalt" if col < 4 else "grass"
                texture = self.get_tile_texture(tile_type).scaled(self.tile_size, self.tile_size)
                new_tiles.insert(0, {
                    "x": x,
                    "y": top_y,
                    "type": tile_type,
                    "texture": texture
                })

        # Удаляем тайлы, которые полностью вышли за экран
        self.tiles = [t for t in new_tiles if t["y"] + self.tile_size > 0]

        return self.tiles

    def draw_tiles(self, painter):
        """Рисует все тайлы на экране"""
        for tile in self.tiles:
            painter.drawPixmap(tile["x"], tile["y"], tile["texture"])