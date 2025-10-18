from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp, sp
from kivy.core.window import Window


class PantallaColor(Screen):
    """
    Pantalla con 5 botones en hilera horizontal,
    centrados y con el mismo margen izquierdo y derecho.
    El 1 es más claro y el 5 más oscuro.
    """
    def __init__(self, name, start_color, end_color, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.start_color = start_color
        self.end_color = end_color
        self.build_ui()

    def build_ui(self):
        # Fondo gris
        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_bg, pos=self.update_bg)

        # Layout principal
        main_layout = BoxLayout(orientation="vertical")

        # Espaciador superior
        main_layout.add_widget(BoxLayout(size_hint_y=0.5))

        # Layout horizontal con espaciadores laterales
        row_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(200))

        # Espaciador izquierdo
        row_layout.add_widget(BoxLayout(size_hint_x=1))

        # Hilera de botones
        botones_layout = BoxLayout(
            orientation="horizontal",
            spacing=dp(20),
            size_hint=(None, 1),
            height=dp(200),
        )

        # Aumenta el ancho total del layout de los botones
        botones_layout.width = (dp(200) * 5) + (dp(20) * 4)

        for i in range(1, 6):
            # 1 claro → 5 oscuro
            t = (i - 1) / 4.0
            r = self.start_color[0] + (self.end_color[0] - self.start_color[0]) * t
            g = self.start_color[1] + (self.end_color[1] - self.start_color[1]) * t
            b = self.start_color[2] + (self.end_color[2] - self.start_color[2]) * t
            color_btn = (r, g, b, 1)

            btn = Button(
                text=str(i),
                font_size=sp(64), # Aumenta el tamaño de la fuente para que se vea bien
                color=(1, 1, 1, 1),
                background_normal="",
                background_color=color_btn,
                size_hint=(None, None),
                size=(dp(175), dp(175)),  # Aumenta el tamaño del botón
            )
            # Asigna una función específica para cada botón que incluye el número
            btn.bind(on_press=lambda instance, num=i: self.boton_presionado(instance, num))
            botones_layout.add_widget(btn)

        row_layout.add_widget(botones_layout)

        # Espaciador derecho
        row_layout.add_widget(BoxLayout(size_hint_x=1))

        main_layout.add_widget(row_layout)

        # Espaciador inferior
        main_layout.add_widget(BoxLayout(size_hint_y=0.5))

        self.add_widget(main_layout)

    def update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def boton_presionado(self, instance, numero_boton):
        """
        Función que se ejecuta cuando se presiona un botón.
        Indica qué botón fue presionado y luego regresa a la pantalla de controles.
        """
        print(f"Botón {numero_boton} presionado en la pantalla {self.name}")
        
        # Aquí puedes agregar más funcionalidades específicas para cada botón
        # Por ejemplo, enviar comandos a hardware, cambiar estados, etc.
        
        # Mensaje específico según el color de la pantalla
        if "azul" in self.name:
            print(f"Puntaje azul establecida en {numero_boton}")
        elif "roja" in self.name:
            print(f"Puntaje roja establecida en  {numero_boton}")
        
        # Regresar a la pantalla de controles
        self.manager.current = "controles"

    def go_back(self, instance):
        """Función alternativa para compatibilidad"""
        self.manager.current = "controles"