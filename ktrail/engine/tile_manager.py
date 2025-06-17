# tile_manager.py

from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QRect
from random import choices, randint


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

    def load_default_tile_types(self):
        """Загружает стандартные типы тайлов."""
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
        self.add_tile_type("bush", ["assets/textures/j_bush.png"])
        self.add_tile_type("tree", ["assets/textures/tree.png"])

    def add_tile_type(self, name, texture_paths, weights=None):
        """Добавляет новый тип тайла."""
        self.tile_types[name] = TileType(name, texture_paths, weights)

    def get_tile_texture(self, name):
        """Возвращает случайную текстуру для заданного типа тайла."""
        if name not in self.tile_types:
            print(f"[TileManager] Тип тайла '{name}' не найден!")
            return QPixmap()
        return self.tile_types[name].get_random_texture()

    def init_tiles(self):
        """Инициализирует начальную сетку тайлов."""
        self.tiles.clear()
        for row in range(self.rows):
            for col in range(self.cols):
                x = col * self.tile_size
                y = row * self.tile_size - 1
                tile_type = "asphalt" if col < 4 else "grass"
                texture = self.get_tile_texture(tile_type).scaled(self.tile_size, self.tile_size)
                decorations = []
                grass_side_texture = None

                # Граница между дорогой и травой
                if col == 3:
                    grass_side_texture = self.get_tile_texture("grass_side").scaled(self.tile_size, self.tile_size)

                # Добавляем кусты и деревья на траву
                if tile_type == "grass":
                    # Кусты (15% шанс)
                    if randint(1, 100) <= 15:
                        decoration = {
                            "type": "bush",
                            "pixmap": self.get_tile_texture("bush").scaled(192, 192)
                        }
                        decorations.append(decoration)

                    # Деревья (5% шанс)
                    if randint(1, 100) <= 5:
                        decoration = {
                            "type": "tree",
                            "pixmap": self.get_tile_texture("tree").scaled(384, 384)
                        }
                        decorations.append(decoration)

                # Сохраняем тайл
                self.tiles.append({
                    "x": x,
                    "y": y,
                    "type": tile_type,
                    "texture": texture,
                    "decorations": decorations,
                    "grass_side_texture": grass_side_texture
                })

    def update_tiles(self, speed):
        """Обновляет позиции тайлов при прокрутке."""
        new_tiles = []

        # Перемещаем старые тайлы
        for tile in self.tiles:
            new_y = tile["y"] + speed
            if new_y <= self.screen_height:
                tile["y"] = new_y
                new_tiles.append(tile)

        # Добавляем новые тайлы сверху
        for col in range(self.cols):
            x = col * self.tile_size
            top_y = -self.tile_size + (speed - 1)

            has_top = any(t["x"] == x and t["y"] <= 0 < t["y"] + self.tile_size for t in new_tiles)
            if not has_top:
                tile_type = "asphalt" if col < 4 else "grass"
                texture = self.get_tile_texture(tile_type).scaled(self.tile_size, self.tile_size)
                decorations = []
                grass_side_texture = None

                if col == 3:
                    grass_side_texture = self.get_tile_texture("grass_side").scaled(self.tile_size, self.tile_size)

                if tile_type == "grass":
                    has_decoration_in_col = any(t["x"] == x and t["decorations"] for t in new_tiles)

                    if not has_decoration_in_col:
                        # Кусты (15% шанс)
                        if randint(1, 100) <= 15:
                            decoration = {
                                "type": "bush",
                                "pixmap": self.get_tile_texture("bush").scaled(192, 192)
                            }
                            decorations.append(decoration)

                        # Деревья (5% шанс)
                        if randint(1, 100) <= 5:
                            decoration = {
                                "type": "tree",
                                "pixmap": self.get_tile_texture("tree").scaled(384, 384)
                            }
                            decorations.append(decoration)

                new_tiles.insert(0, {
                    "x": x,
                    "y": top_y,
                    "type": tile_type,
                    "texture": texture,
                    "decorations": decorations,
                    "grass_side_texture": grass_side_texture
                })

        # Удаляем ушедшие за экран
        self.tiles = [t for t in new_tiles if t["y"] + self.tile_size > 0]

        return self.tiles

    def draw_tiles(self, painter):
        """Рисует все тайлы и их декорации."""
        for tile in self.tiles:
            # Основная текстура тайла
            painter.drawPixmap(tile["x"], tile["y"], tile["texture"])

            # Граница между дорогой и травой
            if tile["grass_side_texture"]:
                painter.drawPixmap(tile["x"], tile["y"], tile["grass_side_texture"])

            # Декорации
            for decoration in tile["decorations"]:
                texture = decoration["pixmap"]
                if decoration["type"] == "tree":
                    # Центрируем дерево относительно тайла
                    painter.drawPixmap(
                        tile["x"],  # Сдвигаем влево
                        tile["y"],  # Поднимаем выше
                        texture
                    )
                else:
                    # Куст по центру тайла
                    painter.drawPixmap(
                        tile["x"],
                        tile["y"],
                        texture
                    )