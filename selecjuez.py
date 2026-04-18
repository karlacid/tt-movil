from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line
from kivy.metrics import dp, sp
from kivy.clock import Clock
from estilos import (
    C_FONDO, C_AZUL, C_AZUL_OSC, C_AZUL_HDR, C_ROJO,
    C_GRIS, C_GRIS_BRD, C_BLANCO, C_SUBTITULO, C_COPYRIGHT, C_ERROR,
    C_POPUP_BORDE,
    R_POPUP, H_LOGO_SM, PAD_H, PAD_SEP_ANGOSTO,
    TopBar, SeparadorBicolor, BotonPrincipal,
    TituloLabel, CopyrightLabel,
    separador_decorativo,
)
from websocket_manager import WebSocketManager


class BotonJuez(Button):
    def __init__(self, numero, **kwargs):
        super().__init__(**kwargs)
        self.numero            = numero
        self.background_normal = ''
        self.background_color  = (0, 0, 0, 0)
        self.text              = ''
        self.size_hint_y       = None
        self.height            = dp(72)

        with self.canvas.before:
            Color(*C_AZUL)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])
            Color(*C_AZUL_HDR)
            self._brd = Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, dp(14)),
                width=1.2,
            )

        self._lbl = Label(
            text=f'JUEZ  {numero}',
            font_size=sp(20), bold=True,
            color=C_BLANCO, halign='center', valign='middle',
        )
        self.add_widget(self._lbl)

        self._lbl_estado = Label(
            text='Disponible',
            font_size=sp(10),
            color=(1, 1, 1, 0.55),
            halign='center', valign='middle',
        )
        self.add_widget(self._lbl_estado)
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *a):
        self._bg.pos  = self.pos
        self._bg.size = self.size
        self._brd.rounded_rectangle = (self.x, self.y, self.width, self.height, dp(14))
        self._lbl.pos        = (self.x, self.y + dp(18))
        self._lbl.size       = (self.width, dp(30))
        self._lbl.text_size  = self._lbl.size
        self._lbl_estado.pos       = (self.x, self.y + dp(6))
        self._lbl_estado.size      = (self.width, dp(16))
        self._lbl_estado.text_size = self._lbl_estado.size

    def set_ocupado(self, ocupado):
        self.disabled = ocupado
        self.opacity  = 0.45 if ocupado else 1.0
        with self.canvas.before:
            Color(*(C_GRIS if ocupado else C_AZUL))
            self._bg.pos  = self.pos
            self._bg.size = self.size
            Color(*(C_GRIS_BRD if ocupado else C_AZUL_HDR))
            self._brd.rounded_rectangle = (self.x, self.y, self.width, self.height, dp(14))
        self._lbl_estado.text = 'Ocupado' if ocupado else 'Disponible'


class SeleccJuez(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name          = 'selecjuez'
        self.mensaje_error = None
        self.botones       = {}
        self.build_ui()

    def build_ui(self):
        with self.canvas.before:
            Color(*C_FONDO)
            self._bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._upd_bg, pos=self._upd_bg)

        root = BoxLayout(orientation='vertical', spacing=0)
        root.add_widget(TopBar(subtitulo='Selección de juez'))
        root.add_widget(SeparadorBicolor())

        main = BoxLayout(orientation='vertical', padding=[PAD_H, 0, PAD_H, 0], spacing=0)

        main.add_widget(Widget(size_hint_y=0.20))
        main.add_widget(Image(
            source='Imagen5-Photoroom.png',
            size_hint=(None, None),
            size=(H_LOGO_SM, H_LOGO_SM),
            pos_hint={'center_x': 0.5},
        ))
        main.add_widget(Widget(size_hint_y=None, height=dp(14)))
        main.add_widget(TituloLabel(text='SELECCIONA TU JUEZ'))
        main.add_widget(Widget(size_hint_y=None, height=dp(6)))
        main.add_widget(separador_decorativo(PAD_SEP_ANGOSTO))
        main.add_widget(Widget(size_hint_y=None, height=dp(6)))

        self.mensaje_error = Label(
            text='', markup=True,
            font_size=sp(12), color=C_ERROR,
            size_hint_y=None, height=dp(20),
            halign='center', valign='middle',
        )
        main.add_widget(self.mensaje_error)
        main.add_widget(Widget(size_hint_y=0.10))

        for i in range(1, 4):
            btn = BotonJuez(numero=i)
            btn.bind(on_press=lambda x, n=i: self.seleccionar_juez(n))
            self.botones[i] = btn
            main.add_widget(btn)
            if i < 3:
                main.add_widget(Widget(size_hint_y=None, height=dp(10)))

        main.add_widget(Widget(size_hint_y=0.15))
        main.add_widget(CopyrightLabel())
        main.add_widget(Widget(size_hint_y=None, height=dp(20)))

        root.add_widget(main)
        self.add_widget(root)
        Clock.schedule_interval(self.actualizar_estado, 0.3)

    def _upd_bg(self, *a):
        self._bg.pos  = self.pos
        self._bg.size = self.size

    def actualizar_estado(self, *args):
        ws = WebSocketManager()
        for i, btn in self.botones.items():
            btn.set_ocupado(i in ws.jueces_ocupados)

    def seleccionar_juez(self, numero):
        ws = WebSocketManager()
        if numero in ws.jueces_ocupados:
            self._mostrar_error('[b]Este juez ya está ocupado[/b]')
            return
        ws.enviar_juez_seleccionado(numero)
        ws.juez_id = numero
        ws.jueces_ocupados.add(numero)
        self.actualizar_estado()
        Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'controles'), 0.2)

    def mostrar_error_ocupado(self):
        ws = WebSocketManager()
        if ws.juez_id in ws.jueces_ocupados:
            ws.jueces_ocupados.discard(ws.juez_id)
        ws.juez_id = None
        self._mostrar_error('[b]Este juez fue seleccionado por otro dispositivo[/b]')
        self.actualizar_estado()
        if self.manager.current == 'controles':
            self.manager.current = 'selecjuez'

    def mostrar_error_posicion_invalida(self):
        ws = WebSocketManager()
        if ws.juez_id in ws.jueces_ocupados:
            ws.jueces_ocupados.discard(ws.juez_id)
        ws.juez_id = None
        self._mostrar_error('[b]Posición inválida[/b]')
        self.actualizar_estado()

    def _mostrar_error(self, texto):
        self.mensaje_error.text = texto
        Clock.schedule_once(lambda dt: setattr(self.mensaje_error, 'text', ''), 3)

    def on_enter(self):
        if self.mensaje_error:
            self.mensaje_error.text = ''
        self.actualizar_estado()