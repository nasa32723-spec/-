"""
Модуль игровой логики для игры про шарики.
Отвечает за управление шариками, их движением, взаимодействиями и инвентарём.
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional
import math


@dataclass
class Vector2:
    """Двумерный вектор для позиции и скорости."""
    x: float
    y: float

    def __add__(self, other: 'Vector2') -> 'Vector2':
        return Vector2(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar: float) -> 'Vector2':
        return Vector2(self.x * scalar, self.y * scalar)

    def distance_to(self, other: 'Vector2') -> float:
        """Вычисляет расстояние до другой точки."""
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx * dx + dy * dy)


class Ball:
    """Класс, представляющий один шарик в игре."""

    def __init__(self, x: float, y: float, radius: float, color: Tuple[int, int, int]):
        """
        Инициализирует шарик.

        Args:
            x, y: Начальная позиция
            radius: Радиус шарика
            color: RGB цвет в формате (R, G, B) от 0 до 255
        """
        self.position = Vector2(x, y)
        self.velocity = Vector2(0, 0)
        self.radius = radius
        self.color = color
        self.is_alive = True

    def update(self, dt: float, gravity: float = 9.81, friction: float = 0.98):
        """
        Обновляет позицию и скорость шарика за время dt.

        Args:
            dt: Время, прошедшее с последнего update
            gravity: Ускорение свободного падения
            friction: Коэффициент трения воздуха
        """
        # Применяем гравитацию
        self.velocity.y += gravity * dt

        # Применяем трение
        self.velocity.x *= friction
        self.velocity.y *= friction

        # Обновляем позицию
        self.position = self.position + self.velocity * dt

    def apply_force(self, force: Vector2):
        """Применяет силу к шарику (изменяет его скорость)."""
        self.velocity = self.velocity + force

    def distance_to(self, other: 'Ball') -> float:
        """Вычисляет расстояние до другого шарика."""
        return self.position.distance_to(other.position)

    def is_colliding_with(self, other: 'Ball') -> bool:
        """Проверяет, касается ли этот шарик другого шарика."""
        distance = self.distance_to(other)
        return distance <= self.radius + other.radius

    def remove(self):
        """Помечает шарик как удалённый."""
        self.is_alive = False


def rgb_to_hsl(color: Tuple[int, int, int]) -> Tuple[float, float, float]:
    """
    Преобразует RGB в HSL (Hue, Saturation, Lightness).
    
    Args:
        color: RGB цвет (0-255)
        
    Returns:
        HSL кортеж (0-360, 0-100, 0-100)
    """
    r, g, b = color[0] / 255.0, color[1] / 255.0, color[2] / 255.0
    
    max_val = max(r, g, b)
    min_val = min(r, g, b)
    delta = max_val - min_val
    
    # Lightness
    l = (max_val + min_val) / 2.0
    
    if delta == 0:
        h = s = 0.0
    else:
        # Saturation
        s = delta / (1 - abs(2 * l - 1))
        
        # Hue
        if max_val == r:
            h = 60 * (((g - b) / delta) % 6)
        elif max_val == g:
            h = 60 * ((b - r) / delta + 2)
        else:
            h = 60 * ((r - g) / delta + 4)
        
        if h < 0:
            h += 360
    
    return (h, s * 100, l * 100)


def hsl_to_rgb(hsl: Tuple[float, float, float]) -> Tuple[int, int, int]:
    """
    Преобразует HSL в RGB.
    
    Args:
        hsl: HSL кортеж (0-360, 0-100, 0-100)
        
    Returns:
        RGB цвет (0-255)
    """
    h, s, l = hsl[0], hsl[1] / 100.0, hsl[2] / 100.0
    
    c = (1 - abs(2 * l - 1)) * s
    h_prime = h / 60.0
    x = c * (1 - abs((h_prime % 2) - 1))
    
    if 0 <= h_prime < 1:
        r1, g1, b1 = c, x, 0
    elif 1 <= h_prime < 2:
        r1, g1, b1 = x, c, 0
    elif 2 <= h_prime < 3:
        r1, g1, b1 = 0, c, x
    elif 3 <= h_prime < 4:
        r1, g1, b1 = 0, x, c
    elif 4 <= h_prime < 5:
        r1, g1, b1 = x, 0, c
    else:
        r1, g1, b1 = c, 0, x
    
    m = l - c / 2
    r = int(round((r1 + m) * 255))
    g = int(round((g1 + m) * 255))
    b = int(round((b1 + m) * 255))
    
    return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))


def mix_colors(color1: Tuple[int, int, int], color2: Tuple[int, int, int], use_hsl: bool = True) -> Tuple[int, int, int]:
    """
    Смешивает два цвета математически.
    
    Поддерживает два режима:
    1. RGB-смешивание (use_hsl=False): берёт среднее значение каждого канала
    2. HSL-смешивание (use_hsl=True): преобразует в HSL, смешивает компоненты, преобразует обратно
       Это даёт более плавные натуральные переходы цветов (как при смешивании краски)
    
    Args:
        color1, color2: RGB цвета в формате (R, G, B) от 0 до 255
        use_hsl: Если True, использует HSL модель для более интересного результата
        
    Returns:
        Новый RGB цвет
    """
    if use_hsl:
        # Преобразуем оба цвета в HSL
        hsl1 = rgb_to_hsl(color1)
        hsl2 = rgb_to_hsl(color2)
        
        # Смешиваем компоненты
        # Для Hue используем специальную логику, т.к. это циклическое значение (0-360)
        h_diff = (hsl2[0] - hsl1[0]) % 360
        if h_diff > 180:
            h_diff -= 360
        h_mix = (hsl1[0] + h_diff / 2.0) % 360
        
        # Saturation и Lightness просто усредняются
        s_mix = (hsl1[1] + hsl2[1]) / 2.0
        l_mix = (hsl1[2] + hsl2[2]) / 2.0
        
        # Преобразуем обратно в RGB
        return hsl_to_rgb((h_mix, s_mix, l_mix))
    else:
        # Простое RGB-усреднение
        r = (color1[0] + color2[0]) // 2
        g = (color1[1] + color2[1]) // 2
        b = (color1[2] + color2[2]) // 2
        return (r, g, b)


class GameLogic:
    """Основной класс логики игры."""

    def __init__(self, screen_width: float, screen_height: float):
        """
        Инициализирует игровую логику.

        Args:
            screen_width: Ширина экрана
            screen_height: Высота экрана
        """
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.balls: List[Ball] = []
        self.inventory: List[Ball] = []

        # Зона удаления шариков (нижний правый угол, например)
        # Формат: (x_min, y_min, x_max, y_max)
        self.deletion_zone = (screen_width * 0.85, screen_height * 0.85, screen_width, screen_height)

        # Параметры физики
        self.gravity = 500  # пиксели/сек²
        self.friction = 0.98
        self.mouse_pull_force = 300  # Сила всасывания

        # Расстояние, на котором шарик "всасывается" в мышку
        self.pull_range = 100

    def add_ball(self, x: float, y: float, radius: float, color: Tuple[int, int, int]) -> Ball:
        """Добавляет новый шарик на экран."""
        ball = Ball(x, y, radius, color)
        self.balls.append(ball)
        return ball

    def update(self, dt: float, mouse_pos: Optional[Tuple[float, float]] = None, mouse_pull: bool = False):
        """
        Обновляет состояние всех шариков.

        Args:
            dt: Время, прошедшее с последнего update (в секундах)
            mouse_pos: Позиция мышки (x, y) или None
            mouse_pull: True если нажата кнопка «всасывания»
        """
        # Обновляем позиции всех живых шариков
        for ball in self.balls:
            if ball.is_alive:
                ball.update(dt, self.gravity, self.friction)

        # Обрабатываем границы экрана (отскок)
        self._handle_screen_boundaries()

        # Обрабатываем всасывание в мышку
        if mouse_pos and mouse_pull:
            self._handle_mouse_pull(mouse_pos)

        # Проверяем столкновения и смешивание цветов
        self._handle_collisions()

        # Удаляем шарики в зоне удаления
        self._handle_deletion_zone()

        # Очищаем мёртвые шарики
        self.balls = [b for b in self.balls if b.is_alive]

    def _handle_screen_boundaries(self):
        """Обрабатывает отскок шариков от границ экрана."""
        for ball in self.balls:
            if ball.is_alive:
                # Левая и правая границы
                if ball.position.x - ball.radius < 0:
                    ball.position.x = ball.radius
                    ball.velocity.x = abs(ball.velocity.x) * 0.8  # Отскок с потерей энергии
                elif ball.position.x + ball.radius > self.screen_width:
                    ball.position.x = self.screen_width - ball.radius
                    ball.velocity.x = -abs(ball.velocity.x) * 0.8

                # Верхняя и нижняя границы
                if ball.position.y - ball.radius < 0:
                    ball.position.y = ball.radius
                    ball.velocity.y = abs(ball.velocity.y) * 0.8
                elif ball.position.y + ball.radius > self.screen_height:
                    ball.position.y = self.screen_height - ball.radius
                    ball.velocity.y = -abs(ball.velocity.y) * 0.8

    def _handle_mouse_pull(self, mouse_pos: Tuple[float, float]):
        """
        Обрабатывает всасывание шариков в мышку.

        Args:
            mouse_pos: Позиция мышки (x, y)
        """
        mouse_vec = Vector2(mouse_pos[0], mouse_pos[1])

        for ball in self.balls:
            if not ball.is_alive:
                continue

            distance = ball.position.distance_to(mouse_vec)

            if distance < self.pull_range:
                # Вычисляем направление к мышке
                direction_x = (mouse_pos[0] - ball.position.x) / (distance + 0.001)
                direction_y = (mouse_pos[1] - ball.position.y) / (distance + 0.001)

                # Применяем силу притяжения
                pull_force = Vector2(direction_x * self.mouse_pull_force, direction_y * self.mouse_pull_force)
                ball.apply_force(pull_force)

                # Если шарик очень близко к мышке, всасываем его
                if distance < ball.radius * 2:
                    self._absorb_ball(ball)

    def _absorb_ball(self, ball: Ball):
        """Всасывает шарик в инвентарь."""
        ball.is_alive = False
        self.inventory.append(ball)

    def spit_ball(self, mouse_pos: Tuple[float, float], direction: Tuple[float, float], force: float = 500):
        """
        Выплёвывает шарик из инвентаря.

        Args:
            mouse_pos: Позиция мышки, откуда выплёвывается шарик
            direction: Направление выплевывания (normalized вектор)
            force: Сила выплевывания
        """
        if not self.inventory:
            return

        # Берём последний всасанный шарик
        ball = self.inventory.pop()

        # Устанавливаем позицию и скорость
        ball.position = Vector2(mouse_pos[0], mouse_pos[1])
        ball.velocity = Vector2(direction[0] * force, direction[1] * force)
        ball.is_alive = True

        # Возвращаем на экран
        self.balls.append(ball)

    def _handle_collisions(self):
        """Обрабатывает столкновения шариков и смешивание цветов."""
        for i in range(len(self.balls) - 1):
            for j in range(i + 1, len(self.balls)):
                ball1 = self.balls[i]
                ball2 = self.balls[j]

                if not ball1.is_alive or not ball2.is_alive:
                    continue

                if ball1.is_colliding_with(ball2):
                    # Смешиваем цвета (используем HSL для более естественного результата)
                    new_color = mix_colors(ball1.color, ball2.color, use_hsl=True)

                    # Выбираем какой шарик "выживает" (например, больший)
                    if ball1.radius >= ball2.radius:
                        ball1.color = new_color
                        # Небольшое увеличение размера
                        ball1.radius += ball2.radius * 0.1
                        ball2.is_alive = False
                    else:
                        ball2.color = new_color
                        ball2.radius += ball1.radius * 0.1
                        ball1.is_alive = False

    def _handle_deletion_zone(self):
        """Удаляет шарики, которые попали в зону удаления."""
        x_min, y_min, x_max, y_max = self.deletion_zone

        for ball in self.balls:
            if ball.is_alive:
                if x_min <= ball.position.x <= x_max and y_min <= ball.position.y <= y_max:
                    ball.remove()

    def get_balls_data(self) -> List[dict]:
        """Возвращает данные всех живых шариков для визуализации."""
        return [
            {
                'x': ball.position.x,
                'y': ball.position.y,
                'radius': ball.radius,
                'color': ball.color,
            }
            for ball in self.balls
            if ball.is_alive
        ]

    def get_inventory_count(self) -> int:
        """Возвращает количество шариков в инвентаре."""
        return len(self.inventory)

    def get_deletion_zone(self) -> Tuple[float, float, float, float]:
        """Возвращает координаты зоны удаления."""
        return self.deletion_zone

    def set_deletion_zone(self, x_min: float, y_min: float, x_max: float, y_max: float):
        """Устанавливает новую зону удаления."""
        self.deletion_zone = (x_min, y_min, x_max, y_max)

    def clear_all(self):
        """Очищает все шарики и инвентарь."""
        self.balls.clear()
        self.inventory.clear()
