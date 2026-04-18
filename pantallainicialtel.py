from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Ellipse, Line
from kivy.metrics import dp
from estilos import (
    C_FONDO, C_AZUL, C_BLANCO,
    TopBar, SeparadorBicolor, BotonPrincipal,
    TituloLabel, SubtituloLabel, CopyrightLabel,
    separador_decorativo,
    H_LOGO_LG, PAD_H, PAD_SEP_CENTRO,
)
from logintel import PantallaLogin
from controles import PantallaControles
from selecjuez import SeleccJuez
from websocket_manager import WebSocketManager


class FiguraTKD(Widget):
    def __init__(self, color, **kwargs):
        super().__init__(**kwargs)
        self._color = color
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *a):
        self.canvas.clear()
        cx = self.center_x
        cy = self.center_y
        s  = min(self.width, self.height) * 0.022
        with self.canvas:
            Color(*self._color)
            r = s * 5
            Ellipse(pos=(cx - s*4 - r, cy + s*9 - r), size=(r*2, r*2))
            Line(points=[cx-s*4, cy+s*9, cx+s*1, cy-s*2],  width=s*1.7, cap='round')
            Line(points=[cx+s*1, cy-s*2, cx-s*4, cy-s*14], width=s*1.7, cap='round')
            Line(points=[cx+s*1, cy-s*2, cx+s*6, cy-s*14], width=s*1.7, cap='round')
            Line(points=[cx-s*4, cy+s*5, cx-s*10, cy+s*1], width=s*1.5, cap='round')
            Line(points=[cx+s*1, cy-s*2, cx+s*14, cy+s*10], width=s*2.0, cap='round')
            Color(*self._color[:3], 0.15)
            rh = s * 6.5
            Ellipse(pos=(cx+s*14-rh, cy+s*10-rh), size=(rh*2, rh*2))
            Color(*self._color[:3], 0.28)
            rh2 = s * 4.5
            Ellipse(pos=(cx+s*14-rh2, cy+s*10-rh2), size=(rh2*2, rh2*2))
            Color(*self._color[:3], 0.55)
            rh3 = s * 2.8
            Ellipse(pos=(cx+s*14-rh3, cy+s*10-rh3), size=(rh3*2, rh3*2))
            Color(*self._color[:3], 1.0)
            rh4 = s * 1.3
            Ellipse(pos=(cx+s*14-rh4, cy+s*10-rh4), size=(rh4*2, rh4*2))


class PantallaBienvenida(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'pantalla_bienvenida'
        self.build_ui()

    def build_ui(self):
        with self.canvas.before:
            Color(*C_FONDO)
            self._bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._upd_bg, pos=self._upd_bg)

        root = BoxLayout(orientation='vertical', spacing=0)
        root.add_widget(TopBar(subtitulo='Sistema de Jueces'))
        root.add_widget(SeparadorBicolor())

        centro = BoxLayout(orientation='vertical', padding=[PAD_H, 0, PAD_H, 0], spacing=0)

        centro.add_widget(Widget(size_hint_y=0.30))
        centro.add_widget(Image(
            source='Imagen5-Photoroom.png',
            size_hint=(None, None),
            size=(H_LOGO_LG, H_LOGO_LG),
            pos_hint={'center_x': 0.5},
        ))
        centro.add_widget(Widget(size_hint_y=None, height=dp(18)))
        centro.add_widget(TituloLabel(text='PETOTECH', font_size=dp(34), height=dp(48)))
        centro.add_widget(Widget(size_hint_y=None, height=dp(6)))
        centro.add_widget(separador_decorativo(PAD_SEP_CENTRO))
        centro.add_widget(Widget(size_hint_y=None, height=dp(10)))
        centro.add_widget(SubtituloLabel(text='Sistema de Jueces'))
        centro.add_widget(Widget(size_hint_y=0.30))

        self._boton = BotonPrincipal(text='TENGO UNA CONTRASEÑA', size_hint=(1, None), height=dp(54))
        self._boton.bind(on_press=self.go_to_login)
        centro.add_widget(self._boton)
        centro.add_widget(Widget(size_hint_y=None, height=dp(16)))
        centro.add_widget(CopyrightLabel())
        centro.add_widget(Widget(size_hint_y=None, height=dp(20)))

        root.add_widget(centro)
        self.add_widget(root)

    def _upd_bg(self, *a):
        self._bg.pos  = self.pos
        self._bg.size = self.size

    def go_to_login(self, *a):
        self.manager.current = 'pantalla_login'


class PetoTechApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(PantallaBienvenida(name='pantalla_bienvenida'))
        sm.add_widget(PantallaLogin(name='pantalla_login'))
        sm.add_widget(SeleccJuez(name='selecjuez'))
        sm.add_widget(PantallaControles(name='controles'))
        return sm

    def on_stop(self):
        WebSocketManager().disconnect()


if __name__ == '__main__':
    PetoTechApp().run()