from PyQt5.QtGui import QPixmap
from random import choices, randint


class TileType:
    def __init__(self, name, texture_paths, weights=None):
        self.name = name
        self.textures = [QPixmap(path) for path in texture_paths]
        self.weights = weights or [1] * len(self.textures)

    def get_random_texture(self):
        return choices(self.textures, weights=self.weights, k=1)[0]


class TileManagerDuo:
    def __init__(self, tile_size, rows, cols, screen_width, screen_height):
        self.tile_size = tile_size
        self.rows = rows
        self.cols = cols
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Разделение экрана на левую и правую части
        self.left_zone_width = screen_width // 2
        self.right_zone_width = screen_width - self.left_zone_width

        self.tile_types = {}
        self.tiles = []

    def add_tile_type(self, name, texture_paths, weights=None):
        self.tile_types[name] = TileType(name, texture_paths, weights)

    def get_tile_texture(self, name):
        if name not in self.tile_types:
            return QPixmap()
        return self.tile_types[name].get_random_texture()

    def init_tiles(self):
        """Инициализация начальных тайлов."""
        self.tiles.clear()
        for row in range(self.rows):
            for col in range(self.cols):
                x = col * self.tile_size
                y = row * self.tile_size - 1
                tile_type = "asphalt" if col < 4 else "grass"
                texture = self.get_tile_texture(tile_type).scaled(self.tile_size, self.tile_size)
                decorations = []
                grass_side_texture = None

                # Добавляем текстуру границы для 4-го столба
                if col == 3:
                    grass_side_texture = self.get_tile_texture("grass_side").scaled(self.tile_size, self.tile_size)

                # Добавляем декорации только на траве
                if tile_type == "grass":
                    # С вероятностью 10% добавляем декорацию
                    if choices([True, False], weights=[10, 90], k=1)[0]:
                        decoration = self.get_tile_texture("decoration")
                        decorations.append(decoration)

                # Определяем зону тайла (левая или правая)
                zone = "left" if x < self.left_zone_width else "right"

                self.tiles.append({
                    "x": x,
                    "y": y,
                    "type": tile_type,
                    "texture": texture,
                    "decorations": decorations,
                    "grass_side_texture": grass_side_texture,
                    "zone": zone  # Новая переменная для определения зоны
                })

    def update_tiles(self, speed_left, speed_right):
        """
        Обновляет позиции тайлов с учетом двух скоростей.
        :param speed_left: Скорость для левой части экрана (игрок 1).
        :param speed_right: Скорость для правой части экрана (игрок 2).
        """
        new_tiles = []
        for tile in self.tiles:
            # Выбираем скорость в зависимости от зоны
            speed = speed_left if tile["x"] < self.left_zone_width else speed_right
            new_y = tile["y"] + speed

            if new_y <= self.screen_height:
                tile["y"] = new_y
                new_tiles.append(tile)

        # Добавляем новые тайлы сверху
        for col in range(self.cols):
            x = col * self.tile_size
            top_y = -self.tile_size + max(speed_left, speed_right) - 1

            has_top = any(t["x"] == x and t["y"] <= 0 < t["y"] + self.tile_size for t in new_tiles)
            if not has_top:
                tile_type = "asphalt" if col < 4 else "grass"
                texture = self.get_tile_texture(tile_type).scaled(self.tile_size, self.tile_size)
                decorations = []
                grass_side_texture = None

                # Добавляем текстуру границы для 4-го столба
                if col == 3:
                    grass_side_texture = self.get_tile_texture("grass_side").scaled(self.tile_size, self.tile_size)

                # Добавляем декорации только на траве
                if tile_type == "grass":
                    # Проверяем, есть ли уже декорация в этом столбе
                    has_decoration_in_col = any(
                        t["x"] == x and t["decorations"] for t in new_tiles
                    )
                    if not has_decoration_in_col and randint(1, 100) <= 10:
                        decoration = self.get_tile_texture("decoration")
                        decorations.append(decoration)

                # Определяем зону тайла
                zone = "left" if x < self.left_zone_width else "right"

                new_tiles.insert(0, {
                    "x": x,
                    "y": top_y,
                    "type": tile_type,
                    "texture": texture,
                    "decorations": decorations,
                    "grass_side_texture": grass_side_texture,
                    "zone": zone
                })

        # Удаляем тайлы, которые полностью вышли за экран
        self.tiles = [t for t in new_tiles if t["y"] + self.tile_size > 0]

        return self.tiles

    def draw_tiles(self, painter):
        """Рисует все тайлы на экране."""
        for tile in self.tiles:
            # Отрисовываем основную текстуру тайла
            painter.drawPixmap(int(tile["x"]), int(tile["y"]), tile["texture"])

            # Отрисовываем текстуру границы (если есть)
            if tile["grass_side_texture"]:
                painter.drawPixmap(int(tile["x"]), int(tile["y"]), tile["grass_side_texture"])

            # Отрисовываем декорации
            for decoration in tile["decorations"]:
                # Отрисовываем декорацию в центре тайла
                painter.drawPixmap(
                    int(tile["x"] + (self.tile_size - decoration.width()) // 2),
                    int(tile["y"] + (self.tile_size - decoration.height()) // 2),
                    decoration
                )