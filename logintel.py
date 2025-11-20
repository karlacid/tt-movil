from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.metrics import dp, sp
from kivy.uix.widget import Widget
import requests

# Dirección de tu servidor Flask (ajústala si cambia la IP)
SERVER_URL = "http://192.168.100.8:5000"


class RoundedTextInput(TextInput):
    """Campo de texto con esquinas redondeadas y diseño moderno."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_active = ""
        self.background_color = (0, 0, 0, 0)
        self.multiline = False
        self.size_hint_y = None
        self.height = dp(48)
        self.padding = [dp(12), dp(10), dp(12), dp(10)]
        self.font_size = sp(16)
        self.color = (1, 1, 1, 1)
        self.hint_text_color = (1, 1, 1, 0.7)
        self.cursor_color = (1, 1, 1, 1)
        self.selection_color = (0.2, 0.6, 1, 0.5)
        self.bold = True

        with self.canvas.before:
            Color(0.2, 0.6, 1, 0.5)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
        self.bind(pos=self._update_rects, size=self._update_rects)

    def _update_rects(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size


class HoverButton(Button):
    """Botón con color personalizado y bordes redondeados."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_down = ""
        self.default_color = (0.2, 0.6, 1, 1)
        self.background_color = self.default_color
        self.color = (1, 1, 1, 1)
        self.size_hint_y = None
        self.height = dp(45)
        self.font_size = sp(15)
        self.bold = True
        self.border_radius = dp(10)

        with self.canvas.before:
            Color(*self.background_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.border_radius])
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class PantallaLogin(Screen):
    """Pantalla de inicio de sesión conectada al servidor Flask."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "pantalla_login"
        self.build_ui()

    def build_ui(self):
        main_layout = BoxLayout(orientation="vertical", padding=dp(15))

        # Fondo claro
        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.background_rect = Rectangle(size=Window.size, pos=self.pos)
        self.bind(size=self.update_background, pos=self.update_background)

        # Espaciador superior flexible
        main_layout.add_widget(Widget(size_hint_y=0.1))

        # Contenedor central con tamaño adaptativo
        center_layout = BoxLayout(
            orientation="vertical",
            size_hint=(0.9, None),
            height=dp(350),
            pos_hint={"center_x": 0.5},
            spacing=dp(12),
            padding=[dp(15), dp(15), dp(15), dp(15)]
        )

        # Logo
        logo_placeholder = Image(
            source="Imagen5-Photoroom.png",
            size_hint=(None, None),
            size=(dp(70), dp(70)),
            pos_hint={"center_x": 0.5}
        )
        center_layout.add_widget(logo_placeholder)

        # Título
        titulo = Label(
            text="[b]INICIO DE SESIÓN[/b]",
            markup=True,
            font_size=sp(22),
            color=(0.1, 0.4, 0.7, 1),
            size_hint_y=None,
            height=dp(32)
        )
        center_layout.add_widget(titulo)
        center_layout.add_widget(Widget(size_hint_y=None, height=dp(10)))

        # Etiqueta y campo de contraseña
        contrasena_label = Label(
            text="Contraseña",
            font_size=sp(16),
            color=(0.1, 0.4, 0.7, 1),
            size_hint_y=None,
            height=dp(25)
        )
        center_layout.add_widget(contrasena_label)

        self.contrasena_input = RoundedTextInput(
            hint_text="********",
            password=True
        )
        center_layout.add_widget(self.contrasena_input)
        center_layout.add_widget(Widget(size_hint_y=None, height=dp(8)))

        # Botones
        botones_layout = BoxLayout(orientation="horizontal", spacing=dp(12),
                                   size_hint_y=None, height=dp(45))

        btn_aceptar = HoverButton(text="ACEPTAR", size_hint=(0.5, 1))
        btn_aceptar.bind(on_press=self.iniciar_sesion)
        botones_layout.add_widget(btn_aceptar)

        btn_volver = HoverButton(text="VOLVER", background_color=(0.2, 0.6, 1, 1),
                                 size_hint=(0.5, 1))
        btn_volver.bind(on_press=self.volver)
        botones_layout.add_widget(btn_volver)

        center_layout.add_widget(botones_layout)

        main_layout.add_widget(center_layout)

        # Espaciador flexible
        main_layout.add_widget(Widget(size_hint_y=0.05))

        # Copyright
        copyright_label = Label(
            text="Copyright © 2025 - PetoTech System",
            font_size=sp(11),
            color=(0.3, 0.3, 0.3, 1),
            size_hint_y=None,
            height=dp(22),
            halign="center"
        )
        main_layout.add_widget(copyright_label)
        main_layout.add_widget(Widget(size_hint_y=None, height=dp(10)))
        
        self.add_widget(main_layout)

    def update_background(self, *args):
        self.background_rect.size = self.size
        self.background_rect.pos = self.pos

    def on_enter(self, *args):
        Clock.schedule_once(self.establecer_foco, 0.1)

    def establecer_foco(self, dt):
        self.contrasena_input.focus = True

    # 🟢 CONEXIÓN AL SERVIDOR FLASK
    def iniciar_sesion(self, instance):
        contrasena = self.contrasena_input.text.strip()
        if not contrasena:
            self.mostrar_mensaje("Error", "Por favor ingresa una contraseña.")
            return

        try:
            url = f"{SERVER_URL}/login"
            response = requests.post(url, json={"password": contrasena})
            data = response.json()

            if response.status_code == 200 and data.get("status") == "ok":
                self.manager.current = "controles"
                self.mostrar_mensaje("Éxito", "Sesión iniciada correctamente")
            else:
                self.mostrar_mensaje("Error", "Contraseña incorrecta.")
        except Exception as e:
            self.mostrar_mensaje("Error", f"No se pudo conectar al servidor.\n{e}")

    def mostrar_mensaje(self, titulo, mensaje):
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(12))

        lbl_mensaje = Label(
            text=mensaje,
            color=(0.2, 0.6, 1, 1),
            font_size=sp(14),
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(55)
        )
        lbl_mensaje.bind(size=lbl_mensaje.setter('text_size'))
        content.add_widget(lbl_mensaje)

        btn_aceptar = Button(
            text="ACEPTAR",
            size_hint_y=None,
            height=dp(42),
            background_normal="",
            background_color=(0.2, 0.6, 1, 1),
            color=(1, 1, 1, 1),
            bold=True,
            font_size=sp(14)
        )

        popup = Popup(
            title=titulo,
            title_color=(0.2, 0.6, 1, 1),
            title_size=sp(16),
            title_align="center",
            content=content,
            size_hint=(0.8, None),
            height=dp(180),
            separator_height=0,
            background=""
        )

        with popup.canvas.before:
            Color(1, 1, 1, 1)
            popup.rect = RoundedRectangle(pos=popup.pos, size=popup.size, radius=[dp(8)])
        popup.bind(pos=self._update_popup_rect, size=self._update_popup_rect)

        btn_aceptar.bind(on_press=popup.dismiss)
        content.add_widget(btn_aceptar)
        popup.open()

    def _update_popup_rect(self, instance, value):
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size

    def volver(self, instance):
        self.manager.current = "pantalla_bienvenida"