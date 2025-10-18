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
from kivy.app import App
from kivy.metrics import dp, sp
from kivy.uix.widget import Widget

# Importa la pantalla de controles para poder hacer la transición.
from controles import PantallaControles

class RoundedTextInput(TextInput):
    """
    Clase personalizada para un TextInput con esquinas redondeadas.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_active = ""
        self.background_color = (0, 0, 0, 0)
        self.multiline = False
        self.size_hint_y = None
        self.height = dp(55)
        self.padding = [dp(15), dp(15), dp(15), dp(15)]
        self.font_size = sp(24)
        self.color = (1, 1, 1, 1)
        self.hint_text_color = (1, 1, 1, 0.7)
        self.cursor_color = (1, 1, 1, 1)
        self.selection_color = (0.2, 0.6, 1, 0.5)
        self.bold = True

        with self.canvas.before:
            Color(0.2, 0.6, 1, 0.5)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(12)]
            )
            
        self.bind(pos=self._update_rects, size=self._update_rects)

    def _update_rects(self, *args):
        """Actualiza la posición y el tamaño del rectángulo de fondo."""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

class HoverButton(Button):
    """
    Clase personalizada para botones con un estilo específico.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.default_color = (0.2, 0.6, 1, 1)
        self.background_color = self.default_color
        self.color = (1, 1, 1, 1)
        self.size_hint_y = None
        self.height = dp(50)
        self.font_size = sp(22)
        self.bold = True
        self.border_radius = dp(12)

        with self.canvas.before:
            Color(*self.background_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.border_radius])
        
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        """Actualiza la posición y el tamaño del rectángulo de fondo."""
        self.rect.pos = self.pos
        self.rect.size = self.size
        
class PantallaLogin(Screen):
    """
    Pantalla de inicio de sesión que coincide con el diseño de la imagen.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'pantalla_login'
        self.build_ui()

    def build_ui(self):
        """Construye la interfaz de usuario de la pantalla de inicio de sesión."""
        main_layout = BoxLayout(orientation='vertical')

        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.background_rect = Rectangle(size=Window.size, pos=self.pos)
        self.bind(size=self.update_background, pos=self.update_background)

        center_layout = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            size=(dp(450), dp(450)),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            spacing=dp(20),
            padding=[dp(20), dp(20), dp(20), dp(40)]
        )
        
        # Reemplaza el Label con un widget de imagen.
        logo_placeholder = Image(
            source="Imagen5-Photoroom.png",
            size_hint=(None, None),
            size=(dp(100), dp(100)),
            pos_hint={'center_x': 0.5}
        )
        center_layout.add_widget(logo_placeholder)

        titulo = Label(
            text='[b]INICIO DE SESIÓN[/b]',
            markup=True,
            font_size=sp(32),
            color=(0.1, 0.4, 0.7, 1),
            size_hint_y=None,
            height=dp(40))
        center_layout.add_widget(titulo)

        center_layout.add_widget(Widget(size_hint_y=None, height=dp(20)))

        contrasena_label = Label(
            text='Contraseña',
            font_size=sp(24),
            color=(0.1, 0.4, 0.7, 1),
            size_hint_y=None,
            height=dp(30))
        center_layout.add_widget(contrasena_label)

        self.contrasena_input = RoundedTextInput(
            hint_text='********',
            password=True
        )
        center_layout.add_widget(self.contrasena_input)

        center_layout.add_widget(Widget(size_hint_y=None, height=dp(10)))

        botones_layout = BoxLayout(
            orientation='horizontal',
            spacing=dp(20),
            size_hint_y=None,
            height=dp(50))

        btn_aceptar = HoverButton(text='ACEPTAR', size_hint=(0.5, 1))
        btn_aceptar.bind(on_press=self.iniciar_sesion)
        botones_layout.add_widget(btn_aceptar)

        btn_volver = HoverButton(
            text='VOLVER',
            background_color=(0.2, 0.6, 1, 1),
            size_hint=(0.5, 1))
        btn_volver.bind(on_press=self.volver)
        botones_layout.add_widget(btn_volver)

        center_layout.add_widget(botones_layout)
        
        center_layout.add_widget(Widget())
        
        copyright_label = Label(
            text="Copyright © 2025 - PetoTech System",
            font_size=sp(14),
            color=(0.3, 0.3, 0.3, 1),
            size_hint_y=None,
            height=dp(30),
            pos_hint={'center_x': 0.5},
            halign='center'
        )
        main_layout.add_widget(Widget())
        main_layout.add_widget(center_layout)
        main_layout.add_widget(copyright_label)
        
        self.add_widget(main_layout)

    def update_background(self, *args):
        """Actualiza el fondo de la pantalla al redimensionar."""
        self.background_rect.size = self.size
        self.background_rect.pos = self.pos

    def on_enter(self, *args):
        """Se ejecuta cuando se entra a esta pantalla, estableciendo el foco en el campo de contraseña."""
        Clock.schedule_once(self.establecer_foco, 0.1)

    def establecer_foco(self, dt):
        """Establece el foco en el campo de entrada de la contraseña."""
        self.contrasena_input.focus = True

    def iniciar_sesion(self, instance):
        """Verifica la contraseña y cambia a la pantalla de controles si es correcta."""
        contrasena_VALIDA = "123"
        contrasena = self.contrasena_input.text.strip()
        
        if contrasena == contrasena_VALIDA:
            self.manager.current = 'controles'
            self.mostrar_mensaje("Éxito", "Sesión iniciada correctamente")
        else:
            self.mostrar_mensaje("Error", "Contraseña incorrecta")

    def mostrar_mensaje(self, titulo, mensaje):
        """Muestra una ventana emergente personalizada."""
        content = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20))
        
        lbl_mensaje = Label(
            text=mensaje,
            color=(0.2, 0.6, 1, 1),
            font_size=sp(20),
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=dp(80))
        content.add_widget(lbl_mensaje)
        
        btn_aceptar = Button(
            text='ACEPTAR',
            size_hint_y=None,
            height=dp(50),
            background_normal='',
            background_color=(0.2, 0.6, 1, 1),
            color=(1, 1, 1, 1),
            bold=True,
            font_size=sp(18))
        
        popup = Popup(
            title=titulo,
            title_color=(0.2, 0.6, 1, 1),
            title_size=sp(22),
            title_align='center',
            content=content,
            size_hint=(None, None),
            size=(dp(450), dp(250)),
            separator_height=0,
            background=''
        )
        
        with popup.canvas.before:
            Color(1, 1, 1, 1)
            popup.rect = RoundedRectangle(
                pos=popup.pos,
                size=popup.size,
                radius=[dp(10)]
            )
        
        def update_popup_rect(instance, value):
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size
        
        popup.bind(pos=update_popup_rect, size=update_popup_rect)
        
        btn_aceptar.bind(on_press=popup.dismiss)
        content.add_widget(btn_aceptar)
        
        popup.open()
        
    def volver(self, instance):
        """Regresa a la pantalla de bienvenida."""
        self.manager.current = 'pantalla_bienvenida'