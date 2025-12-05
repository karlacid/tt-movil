from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp, sp
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.widget import Widget
from websocket_manager import WebSocketManager

class HoverButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0.2, 0.6, 1, 1)
        self.color = (1, 1, 1, 1)
        self.size_hint_y = None
        self.height = dp(50)
        self.font_size = sp(16)
        self.bold = True

        with self.canvas.before:
            Color(*self.background_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])

        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class SeleccJuez(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "selecjuez"
        self.mensaje_error = None
        self.build_ui()

    def build_ui(self):

        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.bg = Rectangle(size=Window.size, pos=self.pos)

        self.bind(size=self.update_bg, pos=self.update_bg)

        main_layout = BoxLayout(orientation="vertical", padding=dp(20))

        main_layout.add_widget(Widget(size_hint_y=0.08))

        logo = Image(
            source="Imagen5-Photoroom.png",
            size_hint=(None, None),
            size=(dp(70), dp(70)),
            pos_hint={"center_x": 0.5}
        )
        main_layout.add_widget(logo)

        main_layout.add_widget(Widget(size_hint_y=0.05))

        content = BoxLayout(
            orientation="vertical",
            size_hint=(0.9, None),
            height=dp(320),
            pos_hint={"center_x": 0.5},
            spacing=dp(18)
        )

        titulo = Label(
            text="[b]SELECCIONA TU JUEZ[/b]",
            markup=True,
            font_size=sp(22),
            color=(0.1, 0.4, 0.7, 1),
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(titulo)

        self.mensaje_error = Label(
            text="",
            markup=True,
            font_size=sp(14),
            color=(1, 0.2, 0.2, 1),
            size_hint_y=None,
            height=dp(30)
        )
        content.add_widget(self.mensaje_error)

        self.botones = {}

        for i in range(1, 4):
            btn = HoverButton(text=f"JUEZ {i}")
            btn.bind(on_press=lambda x, n=i: self.seleccionar_juez(n))
            self.botones[i] = btn
            content.add_widget(btn)

        main_layout.add_widget(content)
        main_layout.add_widget(Widget(size_hint_y=0.1))
        self.add_widget(main_layout)

        Clock.schedule_interval(self.actualizar_estado, 0.3)

    def update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos

    def actualizar_estado(self, *args):
        ws = WebSocketManager()

        for i, btn in self.botones.items():
            if i in ws.jueces_ocupados:
                btn.disabled = True
                btn.text = f"JUEZ {i} (OCUPADO)"
                btn.opacity = 0.35
                with btn.canvas.before:
                    Color(0.5, 0.5, 0.5, 1)
                    btn.rect.size = btn.size
            else:
                btn.disabled = False
                btn.text = f"JUEZ {i}"
                btn.opacity = 1
                with btn.canvas.before:
                    Color(0.2, 0.6, 1, 1)
                    btn.rect.size = btn.size

    def seleccionar_juez(self, numero):
        ws = WebSocketManager()

        if numero in ws.jueces_ocupados:
            self.mensaje_error.text = "[b]Este juez ya está ocupado[/b]"
            Clock.schedule_once(lambda dt: setattr(self.mensaje_error, 'text', ''), 3)
            return

        # Enviar selección al servidor
        ws.enviar_juez_seleccionado(numero)
        
        # Actualizar estado local temporalmente
        ws.juez_id = numero
        ws.jueces_ocupados.add(numero)
        self.actualizar_estado()
        
        # Cambiar de pantalla
        Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'controles'), 0.2)

    def mostrar_error_ocupado(self):
        """Se llama cuando el servidor responde JUEZ_OCUPADO"""
        ws = WebSocketManager()
        
        # Revertir la selección local
        if ws.juez_id in ws.jueces_ocupados:
            ws.jueces_ocupados.discard(ws.juez_id)
        ws.juez_id = None
        
        self.mensaje_error.text = "[b]Este juez fue seleccionado por otro dispositivo[/b]"
        Clock.schedule_once(lambda dt: setattr(self.mensaje_error, 'text', ''), 3)
        self.actualizar_estado()
        
        # Si estaba en la pantalla de controles, regresar
        if self.manager.current == "controles":
            self.manager.current = "selecjuez"
    
    def mostrar_error_posicion_invalida(self):
        """Se llama cuando el servidor responde POSICION_INVALIDA"""
        ws = WebSocketManager()
        
        if ws.juez_id in ws.jueces_ocupados:
            ws.jueces_ocupados.discard(ws.juez_id)
        ws.juez_id = None
        
        self.mensaje_error.text = "[b]Posición inválida[/b]"
        Clock.schedule_once(lambda dt: setattr(self.mensaje_error, 'text', ''), 3)
        self.actualizar_estado()

    def on_enter(self):
        if self.mensaje_error:
            self.mensaje_error.text = ""
        
        self.actualizar_estado()