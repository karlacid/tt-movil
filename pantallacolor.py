from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.uix.widget import Widget
from logintel import PantallaLogin
from controles import PantallaControles
from pantallacolor import PantallaColor

# REMOVIDO: Window.size = (760, 540)
# Dejar que la ventana use el tamaño de la pantalla del dispositivo


class BotonPrincipal(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_color = (0.05, 0.1, 0.2, 1)
        self.color = (1, 1, 1, 1)
        self.size_hint = (None, None)
        self.size = (dp(250), dp(55))
        self.font_size = sp(18)
        self.bold = True

        with self.canvas.before:
            Color(*self.background_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class PantallaBienvenida(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "pantalla_bienvenida"
        self.build_ui()

    def build_ui(self):
        main_layout = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(15))

        with main_layout.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.bg_rect = Rectangle(size=Window.size, pos=self.pos)
        self.bind(size=self.update_bg, pos=self.update_bg)

        # Espaciador superior
        main_layout.add_widget(Widget(size_hint_y=0.15))

        logo = Image(
            source="Imagen5-Photoroom.png",
            size_hint=(None, None),
            size=(dp(120), dp(120)),
            pos_hint={"center_x": 0.5},
        )

        main_layout.add_widget(logo)

        titulo = Label(
            text="[b]PETOTECH[/b]",
            markup=True,
            font_size=sp(32),
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=dp(50),
        )
        main_layout.add_widget(titulo)

        subtitulo = Label(
            text="Tu solución tecnológica para el futuro",
            font_size=sp(16),
            color=(0.1, 0.3, 0.7, 1),
            size_hint_y=None,
            height=dp(35),
        )
        main_layout.add_widget(subtitulo)

        main_layout.add_widget(Widget(size_hint_y=0.15))

        boton = BotonPrincipal(text="TENGO UNA CONTRASEÑA")
        boton.pos_hint = {"center_x": 0.5}
        boton.on_press = self.go_to_login

        main_layout.add_widget(boton)

        copyright_label = Label(
            text="Copyright © 2025 - PetoTech System",
            font_size=sp(12),
            color=(0.3, 0.3, 0.3, 1),
            size_hint_y=None,
            height=dp(25),
        )
        main_layout.add_widget(Widget(size_hint_y=0.1))
        main_layout.add_widget(copyright_label)

        self.add_widget(main_layout)

    def update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def go_to_login(self):
        self.manager.current = "pantalla_login"


class PetoTechApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(PantallaBienvenida(name="pantalla_bienvenida"))
        sm.add_widget(PantallaLogin(name="pantalla_login"))
        sm.add_widget(PantallaControles(name="controles"))
        sm.add_widget(PantallaColor(
            name="pantalla_azul",
            start_color=(0.5, 0.8, 1, 1),   # Azul claro
            end_color=(0.1, 0.4, 0.7, 1)    # Azul oscuro
        ))
        sm.add_widget(PantallaColor(
            name="pantalla_roja",
            start_color=(1, 0.5, 0.5, 1),   # Rojo claro
            end_color=(0.8, 0.1, 0.1, 1)    # Rojo oscuro
        ))

        return sm


if __name__ == "__main__":
    PetoTechApp().run()