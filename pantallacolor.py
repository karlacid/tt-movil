from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.uix.widget import Widget

from websocket_manager import WebSocketManager


AZULES = [
    (0.55, 0.75, 0.95, 1),  # 1
    (0.35, 0.60, 0.85, 1),  # 2
    (0.20, 0.45, 0.75, 1),  # 3
    (0.10, 0.30, 0.60, 1),  # 4
    (0.05, 0.15, 0.35, 1),  # 5
]

ROJOS = [
    (1.00, 0.70, 0.70, 1),  # 1
    (0.95, 0.45, 0.45, 1),  # 2
    (0.85, 0.25, 0.25, 1),  # 3
    (0.70, 0.12, 0.12, 1),  # 4
    (0.45, 0.05, 0.05, 1),  # 5
]


class BotonPuntaje(Button):
    def __init__(self, color_combate, puntos, color_fondo, pantalla, **kwargs):
        super().__init__(**kwargs)

        self.color_combate = color_combate
        self.puntos = puntos
        self.pantalla = pantalla

        self.text = "NULL" if puntos is None else str(puntos)
        self.font_size = sp(28)
        self.bold = True
        self.size_hint = (None, None)
        self.size = (dp(90), dp(90))
        self.background_normal = ""
        self.background_color = color_fondo
        self.color = (1, 1, 1, 1)

        with self.canvas.before:
            Color(*self.background_color)
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(12)]
            )

        self.bind(pos=self.update_rect, size=self.update_rect)
        self.bind(on_press=self.enviar_puntaje)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def enviar_puntaje(self, instance):
        WebSocketManager().enviar_punto(self.color_combate, self.puntos)
        self.pantalla.manager.current = "controles"


class PantallaColor(Screen):
    def __init__(self, start_color, end_color, **kwargs):
        super().__init__(**kwargs)
        self.color_asignado = "AZUL" if "azul" in self.name.lower() else "ROJO"
        self.build_ui()

    def build_ui(self):
        main_layout = BoxLayout(
            orientation="vertical",
            spacing=dp(15),
            padding=dp(15),
            size_hint=(1, 1)
        )

        with main_layout.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.bg_rect = Rectangle(size=Window.size, pos=self.pos)

        self.bind(size=self.update_bg, pos=self.update_bg)
        main_layout.add_widget(Widget(size_hint_y=0.25))

       
        layout_botones = BoxLayout(
            orientation="horizontal",
            spacing=dp(20),
            size_hint=(None, None),
            height=dp(100),
            pos_hint={"center_x": 0.5},
        )

        colores = AZULES if self.color_asignado == "AZUL" else ROJOS

        for i in range(1, 6):
            btn = BotonPuntaje(
                color_combate=self.color_asignado,
                puntos=i,
                color_fondo=colores[i - 1],
                pantalla=self
            )
            layout_botones.add_widget(btn)

        layout_botones.width = (dp(90) * 5) + (dp(20) * 4)
        main_layout.add_widget(layout_botones)

        
        color_null = (0, 0.4, 0.8, 1) if self.color_asignado == "AZUL" else (0.7, 0, 0, 1)

        btn_null = BotonPuntaje(
            color_combate=self.color_asignado,
            puntos=None,
            color_fondo=color_null,
            pantalla=self
        )

       
        btn_null.size = (
            (dp(90) * 3) + (dp(20) * 2),
            dp(90)
        )

        layout_null = BoxLayout(
            orientation="horizontal",
            size_hint=(None, None),
            height=dp(110),
            spacing=dp(20),
            pos_hint={"center_x": 0.5}
        )

        layout_null.width = btn_null.width
        layout_null.add_widget(btn_null)

        main_layout.add_widget(layout_null)
        main_layout.add_widget(Widget(size_hint_y=0.25))

        self.add_widget(main_layout)

    def update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos
