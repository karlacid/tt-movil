import requests
from kivy.uix.screenmanager import Screen
from kivy.logger import Logger
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line
from kivy.clock import Clock
from kivy.metrics import dp, sp
from estilos import (
    C_FONDO, C_AZUL, C_AZUL_MED, C_ROJO, C_BLANCO,
    C_BOTON, C_BOTON_BRD, C_SUBTITULO, C_COPYRIGHT, C_EXITO,
    C_POPUP_BORDE,
    F_BOTON, R_BOTON, R_INPUT, R_POPUP,
    H_BOTON, H_INPUT, H_LOGO_MD, PAD_H, PAD_SEP_ANGOSTO,
    TopBar, SeparadorBicolor, BotonPrincipal,
    TituloLabel, SubtituloLabel, CopyrightLabel,
    separador_decorativo, separador_popup,
)
from websocket_manager import WebSocketManager, SERVER_IP, SERVER_PORT, LOGIN_API_ENDPOINT

BASE_SERVER_URL = f"http://{SERVER_IP}:{SERVER_PORT}"


class RoundedTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_active = ''
        self.background_color  = (0, 0, 0, 0)
        self.multiline         = False
        self.size_hint_y       = None
        self.height            = H_INPUT
        self.padding           = [dp(16), dp(14), dp(16), dp(14)]
        self.font_size         = sp(17)
        self.color             = (0.10, 0.18, 0.32, 1)
        self.hint_text_color   = (0.60, 0.65, 0.72, 1)
        self.cursor_color      = C_AZUL
        self.selection_color   = (*C_AZUL_MED[:3], 0.35)
        self.bold              = False

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[R_INPUT])
            Color(*C_AZUL_MED[:3], 0.4)
            self._brd = Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, R_INPUT),
                width=1.2,
            )
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *a):
        self._bg.pos  = self.pos
        self._bg.size = self.size
        self._brd.rounded_rectangle = (self.x, self.y, self.width, self.height, R_INPUT)


class PantallaLogin(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'pantalla_login'
        self.build_ui()

    def build_ui(self):
        with self.canvas.before:
            Color(*C_FONDO)
            self._bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._upd_bg, pos=self._upd_bg)

        root = BoxLayout(orientation='vertical', spacing=0)
        root.add_widget(TopBar(subtitulo='Inicio de sesión'))
        root.add_widget(SeparadorBicolor())

        main = BoxLayout(orientation='vertical', padding=[PAD_H, 0, PAD_H, 0], spacing=0)

        main.add_widget(Widget(size_hint_y=0.25))
        main.add_widget(Image(
            source='Imagen5-Photoroom.png',
            size_hint=(None, None),
            size=(H_LOGO_MD, H_LOGO_MD),
            pos_hint={'center_x': 0.5},
        ))
        main.add_widget(Widget(size_hint_y=None, height=dp(14)))
        main.add_widget(TituloLabel(text='INICIO DE SESIÓN'))
        main.add_widget(Widget(size_hint_y=None, height=dp(6)))
        main.add_widget(separador_decorativo(PAD_SEP_ANGOSTO))
        main.add_widget(Widget(size_hint_y=0.20))

        lbl_pass = Label(
            text='Contraseña del combate',
            font_size=sp(13),
            color=C_SUBTITULO,
            size_hint_y=None,
            height=dp(22),
            halign='left',
            valign='middle',
        )
        lbl_pass.bind(size=lbl_pass.setter('text_size'))
        main.add_widget(lbl_pass)
        main.add_widget(Widget(size_hint_y=None, height=dp(6)))

        self.contrasena_input = RoundedTextInput(hint_text='Ingresa tu contraseña', password=True)
        main.add_widget(self.contrasena_input)
        main.add_widget(Widget(size_hint_y=None, height=dp(10)))

        self.status_label = Label(
            text='',
            font_size=sp(12),
            color=C_SUBTITULO,
            size_hint_y=None,
            height=dp(20),
            halign='center',
            valign='middle',
        )
        main.add_widget(self.status_label)
        main.add_widget(Widget(size_hint_y=None, height=dp(14)))

        botones = BoxLayout(orientation='horizontal', spacing=dp(12), size_hint_y=None, height=H_BOTON)
        self.btn_aceptar = BotonPrincipal(text='ACEPTAR', size_hint_x=0.6)
        self.btn_aceptar.bind(on_press=self.iniciar_sesion)
        botones.add_widget(self.btn_aceptar)

        self.btn_volver = BotonPrincipal(
            text='VOLVER',
            bg=(0.30, 0.30, 0.30, 1),
            brd=(0.45, 0.45, 0.45, 1),
            size_hint_x=0.4,
        )
        self.btn_volver.bind(on_press=self.volver)
        botones.add_widget(self.btn_volver)
        main.add_widget(botones)

        main.add_widget(Widget(size_hint_y=0.15))
        main.add_widget(CopyrightLabel())
        main.add_widget(Widget(size_hint_y=None, height=dp(20)))

        root.add_widget(main)
        self.add_widget(root)

    def _upd_bg(self, *a):
        self._bg.pos  = self.pos
        self._bg.size = self.size

    def on_enter(self, *args):
        self.contrasena_input.text  = ''
        self.status_label.text      = ''
        self.status_label.color     = C_SUBTITULO
        self.btn_aceptar.disabled   = False
        Clock.schedule_once(self._foco, 0.1)

    def _foco(self, dt):
        self.contrasena_input.focus = True

    def iniciar_sesion(self, instance):
        contrasena = self.contrasena_input.text.strip()
        if not contrasena:
            self.mostrar_mensaje('Error', 'Por favor ingresa una contraseña.')
            return
        self.btn_aceptar.disabled = True
        self.status_label.text    = 'Conectando...'
        self.status_label.color   = C_SUBTITULO
        Logger.info(f'Kivy: Intentando login: {contrasena}')
        WebSocketManager().login_and_connect(
            contrasena,
            on_success=self.on_login_success,
            on_error=self.on_login_error,
        )

    def on_login_success(self):
        Logger.info('Kivy: Login exitoso')
        ws = WebSocketManager()
        self.status_label.text  = f'Conectado al combate {ws.combate_id}'
        self.status_label.color = C_EXITO
        Clock.schedule_once(lambda dt: self._navigate_to_selecjuez(), 0.5)

    def on_login_error(self, error_msg):
        Logger.error(f'Kivy: Error en login: {error_msg}')
        self.status_label.text    = ''
        self.btn_aceptar.disabled = False
        if 'Contraseña incorrecta' in error_msg or 'Contraseña de Juez incorrecta' in error_msg:
            self.mostrar_mensaje('Contraseña incorrecta',
                'La contraseña ingresada no corresponde\na ningún combate activo.')
        elif 'Timeout' in error_msg or 'no respondió' in error_msg:
            self.mostrar_mensaje('Error de conexión',
                'El servidor no respondió a tiempo.\nVerifique su conexión.')
        elif 'No se pudo conectar' in error_msg:
            self.mostrar_mensaje('Error de conexión',
                f'No se pudo conectar al servidor.\nIP: {SERVER_IP}  Puerto: {SERVER_PORT}')
        else:
            self.mostrar_mensaje('Error', error_msg)

    def _navigate_to_selecjuez(self):
        self.manager.current = 'selecjuez'

    def mostrar_mensaje(self, titulo, mensaje):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=[dp(20), dp(16), dp(20), dp(16)])
        content.add_widget(separador_popup())
        content.add_widget(Widget(size_hint_y=None, height=dp(8)))

        lbl_titulo = Label(
            text=f'[b]{titulo}[/b]', markup=True,
            color=(0.10, 0.18, 0.32, 1), font_size=sp(16),
            halign='center', valign='middle',
            size_hint_y=None, height=dp(26),
        )
        lbl_titulo.bind(size=lbl_titulo.setter('text_size'))
        content.add_widget(lbl_titulo)

        lbl = Label(
            text=mensaje, color=C_SUBTITULO, font_size=sp(13),
            halign='center', valign='middle',
            size_hint_y=None, height=dp(50),
        )
        lbl.bind(size=lbl.setter('text_size'))
        content.add_widget(lbl)
        content.add_widget(Widget(size_hint_y=None, height=dp(6)))

        btn_ok = BotonPrincipal(text='ACEPTAR')
        content.add_widget(btn_ok)

        popup = Popup(
            title='', title_size=sp(1),
            content=content,
            size_hint=(0.85, None), height=dp(240),
            separator_height=0, background='',
            auto_dismiss=False,
        )
        with popup.canvas.before:
            Color(*C_FONDO)
            popup._bg = RoundedRectangle(pos=popup.pos, size=popup.size, radius=[R_POPUP])
            Color(*C_POPUP_BORDE)
            popup._brd = Line(
                rounded_rectangle=(popup.x, popup.y, popup.width, popup.height, R_POPUP),
                width=1,
            )
        def _upd(inst, _):
            inst._bg.pos  = inst.pos
            inst._bg.size = inst.size
            inst._brd.rounded_rectangle = (inst.x, inst.y, inst.width, inst.height, R_POPUP)
        popup.bind(pos=_upd, size=_upd)
        btn_ok.bind(on_press=popup.dismiss)
        popup.open()

    def volver(self, instance):
        self.manager.current = 'pantalla_bienvenida'