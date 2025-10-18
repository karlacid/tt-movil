from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.graphics import Color, RoundedRectangle, Rectangle, Triangle, Line
from kivy.metrics import dp, sp
from kivy.core.window import Window
from kivy.uix.widget import Widget

class TrianguloButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        
        with self.canvas.before:
            Color(0.1, 0.4, 0.7, 1)  # Color del triángulo
            self.triangle = Triangle(points=[])
            
            Color(1, 1, 1, 1)  # Color de la exclamación
            self.line = Line(points=[], width=dp(2))
        
        self.bind(pos=self.update_shape, size=self.update_shape)

    def update_shape(self, *args):
        x, y = self.pos
        w, h = self.size
        
        tamano_triangulo = min(w, h) * 0.95
        
        centro_x = x + w / 2
        centro_y = y + h / 2

        p1 = (centro_x - tamano_triangulo / 2, centro_y - tamano_triangulo / 2)
        p2 = (centro_x + tamano_triangulo / 2, centro_y - tamano_triangulo / 2)
        p3 = (centro_x, centro_y + tamano_triangulo / 2)
        
        self.triangle.points = [p1[0], p1[1], p2[0], p2[1], p3[0], p3[1]]
        self.line.points = [p1[0], p1[1], p2[0], p2[1], p3[0], p3[1], p1[0], p1[1]]

class FullScreenButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_down = ""
        self.color = (1, 1, 1, 1)
        self.bold = True
        self.border_radius = dp(12)
        self.background_color = kwargs.get("background_color", (0.2, 0.6, 1, 1))
        
        with self.canvas.before:
            Color(*self.background_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.border_radius])
        
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class PantallaControles(Screen):
    
    primary_color = (0.1, 0.4, 0.7, 1) # Azul principal
    darker_primary_color = (0.05, 0.2, 0.4, 1) # Nuevo azul más oscuro para el botón de finalizar
    secondary_color = (0.8, 0.1, 0.1, 1) # Rojo
    background_color = (0.95, 0.95, 0.95, 1) # Gris claro

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "controles"
        self.build_ui()
        
    def build_ui(self):
        with self.canvas.before:
            Color(*self.background_color)
            self.background_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_background, pos=self.update_background)
        
        main_layout = BoxLayout(orientation="vertical", spacing=dp(20), padding=dp(20))
        
        main_buttons_layout = BoxLayout(orientation='horizontal', size_hint_y=0.8, spacing=dp(20))
        
        # Botones de color (Azul y Rojo)
        plus_btn_azul = self.create_button(
            text='[b]+[/b]', markup=True, font_size=sp(200),
            background_color=self.primary_color, on_press=self.go_to_azul
        )
        main_buttons_layout.add_widget(plus_btn_azul)

        # Columna central
        center_column_layout = BoxLayout(orientation="vertical", size_hint=(0.4, 1), spacing=dp(10))
        
        # El contenedor de advertencia ahora ocupa más espacio para que el botón de finalizar sea más corto
        warning_container = RelativeLayout(size_hint_y=0.9)
        btn_triangulo = TrianguloButton(size_hint=(1, 1))
        btn_triangulo.bind(on_press=self.alerta_accion)
        
        exclamacion_label = Label(text='!', font_size=sp(80), color=(1, 1, 1, 1),
                                  size_hint=(None, None), size=(dp(50), dp(50)),
                                  pos_hint={'center_x': 0.5, 'center_y': 0.5})
        warning_container.add_widget(btn_triangulo)
        warning_container.add_widget(exclamacion_label)

        # El botón de finalizar utiliza un color más oscuro y es más corto
        btn_finalizar = FullScreenButton(
            text="FINALIZAR",
            background_color=self.darker_primary_color,
            font_size=sp(20),
            size_hint_y=0.1
        )
        btn_finalizar.bind(on_press=self.finalizar_accion)
        
        center_column_layout.add_widget(warning_container)
        center_column_layout.add_widget(btn_finalizar)
        
        main_buttons_layout.add_widget(center_column_layout)

        plus_btn_rojo = self.create_button(
            text='[b]+[/b]', markup=True, font_size=sp(200),
            background_color=self.secondary_color, on_press=self.go_to_rojo
        )
        main_buttons_layout.add_widget(plus_btn_rojo)

        main_layout.add_widget(main_buttons_layout)
        
        self.add_widget(main_layout)
        
    def create_button(self, text, markup=False, font_size=sp(32), background_color=(0,0,0,1), on_press=None):
        btn = FullScreenButton(
            text=text,
            background_color=background_color,
            font_size=font_size,
            markup=markup
        )
        if on_press:
            btn.bind(on_press=on_press)
        return btn

    def update_background(self, *args):
        self.background_rect.size = self.size
        self.background_rect.pos = self.pos

    def finalizar_accion(self, instance):
        print("Botón FINALIZAR presionado.")
        self.manager.current = "pantalla_login"

    def alerta_accion(self, instance):
        print("Botón de ALERTA presionado.")
        
    def go_to_azul(self, instance):
        print("Botón AZUL presionado. Navegando a Pantalla Azul.")
        self.manager.current = "pantalla_azul"
        
    def go_to_rojo(self, instance):
        print("Botón ROJO presionado. Navegando a Pantalla Roja.")
        self.manager.current = "pantalla_roja"
