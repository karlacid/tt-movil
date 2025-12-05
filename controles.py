from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle, Rectangle, Triangle
from kivy.metrics import dp, sp
from websocket_manager import WebSocketManager


class FullScreenButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        border_radius = kwargs.get("border_radius", [dp(25)])

        with self.canvas.before:
            Color(*kwargs.get("background_color", (0.5, 0.5, 0.5, 1)))
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=border_radius)

        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class TriangleAlertButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.text = ""

        with self.canvas.before:
            Color(1, 0.8, 0, 1)
            self.triangle = Triangle(points=[0, 0, 0, 0, 0, 0])

            Color(0.9, 0.7, 0, 1)
            self.triangle_border = Triangle(points=[0, 0, 0, 0, 0, 0])

        with self.canvas.after:
            Color(0, 0, 0, 1)
            self.exclamation_rect = Rectangle(pos=(0, 0), size=(0, 0))
            self.exclamation_dot = Rectangle(pos=(0, 0), size=(0, 0))

        self.bind(pos=self.update_triangle, size=self.update_triangle)

    def update_triangle(self, *args):
        center_x = self.center_x
        center_y = self.center_y
        width = min(self.width, self.height) * 0.7
        height = width * 0.866

        border_offset = dp(3)
        self.triangle_border.points = [
            center_x, center_y + height/2 + border_offset,
            center_x - width/2 - border_offset, center_y - height/2 - border_offset,
            center_x + width/2 + border_offset, center_y - height/2 - border_offset
        ]

        self.triangle.points = [
            center_x, center_y + height/2,
            center_x - width/2, center_y - height/2,
            center_x + width/2, center_y - height/2
        ]

        base_size = min(self.width, self.height)
        exclamation_width = max(dp(6), base_size * 0.08)
        exclamation_height = height * 0.45
        dot_size = max(dp(8), base_size * 0.1)
        spacing = max(dp(8), base_size * 0.08)

        self.exclamation_rect.pos = (
            center_x - exclamation_width/2,
            center_y - exclamation_height/2 + spacing
        )
        self.exclamation_rect.size = (exclamation_width, exclamation_height)

        self.exclamation_dot.pos = (
            center_x - dot_size/2,
            center_y - height/2 + spacing * 0.8
        )
        self.exclamation_dot.size = (dot_size, dot_size)


class PantallaControles(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "controles"
        self.botones_habilitados = False  # Nuevo: rastrea el estado de habilitación
        self.build_ui()

    def build_ui(self):

        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.bg = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self.update_bg, pos=self.update_bg)

        main_layout = BoxLayout(
            orientation="horizontal",
            padding=dp(20),
            spacing=dp(15)
        )

        self.plus_btn_azul = FullScreenButton(
            text="+",
            font_size=sp(120),
            background_color=(0.1, 0.4, 0.7, 1),
            bold=True
        )
        self.plus_btn_azul.bind(on_press=self.go_to_azul)

        self.plus_btn_rojo = FullScreenButton(
            text="+",
            font_size=sp(120),
            background_color=(0.8, 0.1, 0.1, 1),
            bold=True
        )
        self.plus_btn_rojo.bind(on_press=self.go_to_rojo)

        center = BoxLayout(
            orientation="vertical",
            size_hint=(0.35, 1),
            spacing=dp(15)
        )

        self.btn_alerta = TriangleAlertButton()
        self.btn_alerta.bind(on_press=self.alerta_accion)

        self.btn_finalizar = FullScreenButton(
            text="FINALIZAR",
            font_size=sp(15),
            background_color=(0.05, 0.2, 0.4, 1),
            bold=True,
            size_hint=(1, 0.3)
        )
        self.btn_finalizar.bind(on_press=self.mostrar_confirmacion)

        center.add_widget(self.btn_alerta)
        center.add_widget(self.btn_finalizar)

        main_layout.add_widget(self.plus_btn_azul)
        main_layout.add_widget(center)
        main_layout.add_widget(self.plus_btn_rojo)

        self.add_widget(main_layout)
        self.bloquear_botones()


    def update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos

    def bloquear_botones(self):
        """Bloquea los botones de suma y actualiza el estado"""
        self.plus_btn_azul.disabled = True
        self.plus_btn_rojo.disabled = True
        self.plus_btn_azul.opacity = 0.35
        self.plus_btn_rojo.opacity = 0.35
        self.botones_habilitados = False
        print("Botones de suma BLOQUEADOS")

    def habilitar_botones(self):
        """Habilita los botones de suma cuando hay 2+ incidencias"""
        self.plus_btn_azul.disabled = False
        self.plus_btn_rojo.disabled = False
        self.plus_btn_azul.opacity = 1
        self.plus_btn_rojo.opacity = 1
        self.botones_habilitados = True
        print("Botones de suma HABILITADOS")

    def reset_puntos_visuales(self):
        """
        Se llama cuando hay colores diferentes (RESET_PUNTOS).
        Solo limpia visuales pero mantiene botones habilitados si ya lo estaban.
        """
        print("Reset visual de puntos (mantiene habilitación si ya había 2+ incidencias)")
        # Aquí podrías limpiar indicadores visuales si los tienes
        # Por ejemplo, si tienes labels que muestran los puntos seleccionados
        
        # NO llamamos a bloquear_botones() aquí
        # Los botones se mantienen en su estado actual

    def reset_ui(self):
        """
        Reset completo cuando se calcula el promedio o se reinicia todo.
        Bloquea botones y limpia todo el estado.
        """
        print("Reset completo de UI")
        self.bloquear_botones()
        # Aquí reseteas cualquier otro estado visual

    def alerta_accion(self, instance):
        print("Marcando incidencia...")
        WebSocketManager().enviar_incidencia()
        
        original_color = self.btn_alerta.canvas.before.children[0].rgba
        with self.btn_alerta.canvas.before:
            self.btn_alerta.canvas.before.children[0].rgba = (1, 0.5, 0, 1)
        
        from kivy.clock import Clock
        Clock.schedule_once(
            lambda dt: setattr(self.btn_alerta.canvas.before.children[0], 'rgba', original_color),
            0.5
        )

    def mostrar_confirmacion(self, instance):
        content = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20))

        lbl_mensaje = Label(
            text="¿Seguro que deseas finalizar el combate?",
            color=(0.2, 0.6, 1, 1),
            font_size=sp(20),
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=dp(80)
        )
        content.add_widget(lbl_mensaje)

        botones = BoxLayout(spacing=dp(20), size_hint_y=None, height=dp(50))

        btn_si = Button(
            text='SÍ',
            background_normal='',
            background_color=(0.2, 0.6, 1, 1),
            color=(1, 1, 1, 1),
            bold=True,
            font_size=sp(18)
        )

        btn_no = Button(
            text='NO',
            background_normal='',
            background_color=(0.7, 0.1, 0.1, 1),
            color=(1, 1, 1, 1),
            bold=True,
            font_size=sp(18)
        )

        botones.add_widget(btn_si)
        botones.add_widget(btn_no)

        content.add_widget(botones)

        popup = Popup(
            title="Confirmación",
            title_color=(0.2, 0.6, 1, 1),
            title_size=sp(22),
            title_align='center',
            content=content,
            size_hint=(None, None),
            size=(dp(500), dp(260)),
            separator_height=0,
            background='',
            auto_dismiss=False
        )

        with popup.canvas.before:
            Color(0.52, 0.76, 0.75, 0.8)
            popup.rect = RoundedRectangle(
                pos=popup.pos,
                size=popup.size,
                radius=[dp(10)]
            )

        def update_popup_rect(instance, value):
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size

        popup.bind(pos=update_popup_rect, size=update_popup_rect)

        btn_no.bind(on_press=popup.dismiss)
        btn_si.bind(on_press=lambda x: self.confirmar_finalizar(popup))

        popup.open()

    def confirmar_finalizar(self, popup):
        popup.dismiss()
        
        ws = WebSocketManager()
        if ws.juez_id:
            ws.jueces_ocupados.discard(ws.juez_id)
            ws.juez_id = None
        
        ws.disconnect()
        self.manager.current = "pantalla_login"

    def go_to_azul(self, instance):
        if not self.plus_btn_azul.disabled:
            self.manager.current = "pantalla_azul"

    def go_to_rojo(self, instance):
        if not self.plus_btn_rojo.disabled:
            self.manager.current = "pantalla_roja"

    def on_enter(self):
        """Se llama cada vez que se entra a esta pantalla"""
        # SIEMPRE bloquear botones al regresar a controles
        # Solo se habilitan cuando llega HABILITAR_PUNTOS del servidor
        self.bloquear_botones()
        print(">>> on_enter: Controles bloqueados, esperando 2+ incidencias")