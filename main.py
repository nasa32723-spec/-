from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController


class AbandonedAsylumScene:
    """Create a basic abandoned asylum scene with fog, lights, and a few props."""

    def __init__(self):
        self._setup_window()
        self._setup_lighting()
        self._setup_environment()
        self._setup_props()
        self._setup_player()

    def _setup_window(self):
        window.title = "Abandoned Asylum"
        window.borderless = False
        window.fullscreen = False
        window.exit_button.visible = False
        window.fps_counter.enabled = True

        # Fog / atmosphere
        window.fog_color = color.rgb(60, 60, 70)
        window.fog_density = 0.02

        # Slight bluish tint to everything
        window.color = color.rgb(15, 15, 30)

    def _setup_lighting(self):
        # Ambient / fill lighting
        AmbientLight(color=color.rgb(45, 60, 80))

        # A weak bluish directional light (moonlight / old fluorescent)
        directional = DirectionalLight()
        directional.rotation_x = 60
        directional.rotation_y = -30
        directional.color = color.rgba(160, 180, 255, 150)

        # Subtle point light for flickering effect (optional)
        self.flicker_light = PointLight(parent=scene, y=3, z=2, color=color.rgba(150, 180, 255, 120), brightness=1)

    def _setup_environment(self):
        # Ground (dirty tiled floor)
        floor_texture = self._try_load_texture("textures/dirty_tile.png") or load_texture("white_cube")
        self.floor = Entity(
            model="plane",
            scale=(28, 1, 10),
            texture=floor_texture,
            texture_scale=(8, 8),
            collider="box",
            color=color.rgb(120, 120, 120),
        )

        # Walls (grey bricks)
        brick_texture = self._try_load_texture("textures/brick_wall.png") or load_texture("brick")

        wall_height = 4
        wall_thickness = 0.4
        wall_length = 28

        # Left wall
        Entity(
            model="cube",
            scale=(wall_thickness, wall_height, wall_length),
            position=(-5, wall_height / 2, 0),
            texture=brick_texture,
            texture_scale=(1, 3),
            collider="box",
            color=color.rgb(90, 90, 100),
        )

        # Right wall
        Entity(
            model="cube",
            scale=(wall_thickness, wall_height, wall_length),
            position=(5, wall_height / 2, 0),
            texture=brick_texture,
            texture_scale=(1, 3),
            collider="box",
            color=color.rgb(90, 90, 100),
        )

        # Back wall (at far end)
        Entity(
            model="cube",
            scale=(10 + wall_thickness * 2, wall_height, wall_thickness),
            position=(0, wall_height / 2, wall_length / 2),
            texture=brick_texture,
            texture_scale=(3, 3),
            collider="box",
            color=color.rgb(90, 90, 100),
        )

        # Front wall with door opening
        Entity(
            model="cube",
            scale=(10 + wall_thickness * 2, wall_height, wall_thickness),
            position=(0, wall_height / 2, -wall_length / 2),
            texture=brick_texture,
            texture_scale=(3, 3),
            collider="box",
            color=color.rgb(90, 90, 100),
        )

    def _setup_props(self):
        # Simple gurney/каталка made of scaled cubes
        gurney_base = Entity(
            model="cube",
            scale=(1.8, 0.2, 0.6),
            position=(0, 0.4, -4),
            color=color.rgb(80, 80, 90),
            collider="box",
        )
        gurney_frame = Entity(
            parent=gurney_base,
            model="cube",
            scale=(1.8, 0.1, 0.2),
            position=(0, 0.15, -0.2),
            color=color.rgb(120, 120, 120),
        )
        for dx in (-0.75, 0.75):
            for dz in (-0.25, 0.25):
                Entity(
                    parent=gurney_base,
                    model="cube",
                    scale=(0.1, 0.4, 0.1),
                    position=(dx, -0.3, dz),
                    color=color.rgb(70, 70, 80),
                )

        # Window with bars
        window_frame = Entity(
            model="cube",
            scale=(2.2, 2.2, 0.2),
            position=(4.95, 2.2, -1.5),
            color=color.rgb(40, 40, 50),
            collider="box",
        )

        # Bars
        for i in range(-1, 2):
            Entity(
                parent=window_frame,
                model="cube",
                scale=(0.12, 1.8, 0.12),
                position=(0.6 * i, 0, -0.15),
                color=color.rgb(70, 70, 80),
            )
        for i in range(-1, 2):
            Entity(
                parent=window_frame,
                model="cube",
                scale=(1.6, 0.12, 0.12),
                position=(0, 0.6 * i, -0.15),
                color=color.rgb(70, 70, 80),
            )

        # Door (static) in front wall
        self.door = Entity(
            model="cube",
            scale=(2, 3.5, 0.2),
            position=(0, 1.75, -14),
            color=color.rgb(35, 35, 40),
            texture=self._try_load_texture("textures/old_wood.png"),
            collider="box",
        )

    def _setup_player(self):
        self.player = FirstPersonController(
            position=(0, 1, 6),
            speed=4,
            gravity=1,
            cursor=True,
        )
        mouse.locked = True

    def _try_load_texture(self, path: str):
        """Attempt to load a texture; fall back to None if missing."""
        try:
            return load_texture(path)
        except Exception:
            return None


if __name__ == "__main__":
    app = Ursina()
    scene = AbandonedAsylumScene()
    app.run()
