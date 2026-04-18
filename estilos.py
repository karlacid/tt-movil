

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.metrics import dp, sp

# Fondos
C_FONDO         = (0.94, 0.93, 0.91, 1)   # beige principal de todas las pantallas

# Barra superior
C_TOPBAR        = (0.10, 0.18, 0.32, 1)   # azul muy oscuro

# Azules
C_AZUL          = (0.10, 0.29, 0.56, 1)   # azul principal (panel azul, badges)
C_AZUL_OSC      = (0.06, 0.19, 0.40, 1)   # azul oscuro (header panel azul)
C_AZUL_HDR      = (0.06, 0.19, 0.40, 1)   # borde interior panel azul (alias de C_AZUL_OSC)
C_AZUL_MED      = (0.20, 0.50, 0.80, 1)   # azul medio (bordes input, selección)

# Rojos
C_ROJO          = (0.69, 0.09, 0.09, 1)   # rojo principal (panel rojo)
C_ROJO_OSC      = (0.54, 0.06, 0.06, 1)   # rojo oscuro (header panel rojo)

# Botones
C_BOTON         = (0.05, 0.18, 0.38, 1)   # fondo botón principal / finalizar
C_BOTON_BRD     = (0.10, 0.29, 0.56, 1)   # borde botón principal

# Alerta
C_ALERTA        = (0.96, 0.76, 0.09, 1)   # amarillo triángulo alerta
C_ALERTA_BRD    = (0.83, 0.63, 0.00, 1)   # borde triángulo alerta

# Grises
C_GRIS          = (0.55, 0.55, 0.55, 1)   # juez ocupado
C_GRIS_BRD      = (0.42, 0.42, 0.42, 1)   # borde juez ocupado

# Texto
C_BLANCO        = (1, 1, 1, 1)
C_TEXTO_PPAL    = (0.10, 0.18, 0.32, 1)   # títulos oscuros
C_SUBTITULO     = (0.38, 0.46, 0.58, 1)   # texto secundario / labels
C_COPYRIGHT     = (0.55, 0.52, 0.48, 1)   # pie de página
C_ERROR         = (0.75, 0.10, 0.10, 1)   # mensajes de error
C_EXITO         = (0.10, 0.55, 0.25, 1)   # estado conectado / éxito

# Separador popup
C_POPUP_BORDE   = (0.80, 0.78, 0.74, 1)   # borde de popups

#  TIPOGRAFÍA
F_TITULO_GRANDE = sp(34)    # pantalla bienvenida
F_TITULO        = sp(24)    # títulos de pantalla (login, selecjuez)
F_SUBTITULO     = sp(15)    # subtítulos
F_LABEL         = sp(13)    # labels de campo
F_BOTON         = sp(15)    # texto botones principales
F_BOTON_SM      = sp(14)    # texto botones secundarios / popup
F_TOPBAR        = sp(11)    # nombre app en topbar
F_TOPBAR_SUB    = sp(10)    # sección actual en topbar
F_COPYRIGHT     = sp(10)    # pie de página
F_BADGE         = sp(9)     # badges pequeños
F_ERROR         = sp(12)    # mensajes de error inline

#  MÉTRICAS / ESPACIADO

R_PANEL         = dp(16)    # radio bordes paneles laterales
R_BOTON         = dp(12)    # radio bordes botones
R_INPUT         = dp(12)    # radio bordes inputs
R_POPUP         = dp(16)    # radio bordes popups

H_TOPBAR        = dp(32)    # altura barra superior
H_SEPARADOR     = dp(4)     # altura separador bicolor
H_BOTON         = dp(52)    # altura botones principales
H_BOTON_JUEZ    = dp(72)    # altura botones de juez
H_INPUT         = dp(52)    # altura inputs de texto
H_LOGO_SM       = dp(72)    # logo pequeño (selecjuez)
H_LOGO_MD       = dp(80)    # logo mediano (login)
H_LOGO_LG       = dp(110)   # logo grande (bienvenida)

PAD_H           = dp(30)    # padding horizontal estándar de pantallas
PAD_SEP_CENTRO  = dp(60)    # padding separador decorativo centrado
PAD_SEP_ANGOSTO = dp(80)    # padding separador decorativo angosto

#  COMPONENTES REUTILIZABLES

class TopBar(BoxLayout):
    def __init__(self, subtitulo='', **kwargs):
        super().__init__(
            orientation='horizontal',
            size_hint_y=None,
            height=H_TOPBAR,
            padding=[dp(14), 0],
            **kwargs
        )
        with self.canvas.before:
            Color(*C_TOPBAR)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._upd, size=self._upd)

        self.add_widget(Label(
            text='PETOTECH SYSTEM',
            font_size=F_TOPBAR,
            bold=True,
            color=(0.54, 0.69, 0.85, 1),
            halign='left',
            valign='middle',
        ))
        self.add_widget(Label(
            text=subtitulo,
            font_size=F_TOPBAR_SUB,
            color=(0.38, 0.50, 0.65, 1),
            halign='right',
            valign='middle',
        ))

    def _upd(self, *a):
        self._bg.pos  = self.pos
        self._bg.size = self.size

    def set_subtitulo(self, texto):
        self.children[0].text = texto


class SeparadorBicolor(Widget):
    
    def __init__(self, **kwargs):
        super().__init__(size_hint_y=None, height=H_SEPARADOR, **kwargs)
        with self.canvas:
            Color(*C_AZUL)
            self._left  = Rectangle()
            Color(*C_ROJO)
            self._right = Rectangle()
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *a):
        mid = self.x + self.width / 2
        self._left.pos   = (self.x, self.y)
        self._left.size  = (self.width / 2, self.height)
        self._right.pos  = (mid, self.y)
        self._right.size = (self.width / 2, self.height)


class BotonPrincipal(Button):
    
    def __init__(self, bg=None, brd=None, **kwargs):
        super().__init__(**kwargs)
        bg  = bg  or C_BOTON
        brd = brd or C_BOTON_BRD

        self.background_normal = ''
        self.background_color  = (0, 0, 0, 0)
        self.color             = C_BLANCO
        self.bold              = True
        self.font_size         = F_BOTON
        self.size_hint_y       = None
        self.height            = H_BOTON

        with self.canvas.before:
            Color(*bg)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size,
                                        radius=[R_BOTON])
            Color(*brd)
            self._brd = Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, R_BOTON),
                width=1.4,
            )
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *a):
        self._bg.pos  = self.pos
        self._bg.size = self.size
        self._brd.rounded_rectangle = (
            self.x, self.y, self.width, self.height, R_BOTON)


class TituloLabel(Label):
   
    def __init__(self, **kwargs):
        kwargs.setdefault('markup',      True)
        kwargs.setdefault('font_size',   F_TITULO)
        kwargs.setdefault('color',       C_TEXTO_PPAL)
        kwargs.setdefault('halign',      'center')
        kwargs.setdefault('valign',      'middle')
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height',      dp(36))
        # envolver en negrita si no viene ya con markup
        if '[b]' not in kwargs.get('text', ''):
            kwargs['text'] = f"[b]{kwargs.get('text', '')}[/b]"
        super().__init__(**kwargs)
        self.bind(size=self.setter('text_size'))


class SubtituloLabel(Label):
    
    def __init__(self, **kwargs):
        kwargs.setdefault('font_size',   F_SUBTITULO)
        kwargs.setdefault('color',       C_SUBTITULO)
        kwargs.setdefault('halign',      'center')
        kwargs.setdefault('valign',      'middle')
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height',      dp(26))
        super().__init__(**kwargs)
        self.bind(size=self.setter('text_size'))


class CopyrightLabel(Label):
    
    def __init__(self, **kwargs):
        kwargs.setdefault('text',        'Copyright © 2025 - PetoTech System')
        kwargs.setdefault('font_size',   F_COPYRIGHT)
        kwargs.setdefault('color',       C_COPYRIGHT)
        kwargs.setdefault('halign',      'center')
        kwargs.setdefault('valign',      'middle')
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height',      dp(20))
        super().__init__(**kwargs)


def separador_decorativo(padding_lateral=PAD_SEP_CENTRO):
    
    wrap = BoxLayout(
        size_hint_y=None,
        height=H_SEPARADOR,
        padding=[padding_lateral, 0],
    )
    wrap.add_widget(SeparadorBicolor())
    return wrap


def separador_popup():
    
    wrap = BoxLayout(size_hint_y=None, height=dp(3), padding=[dp(40), 0])
    with wrap.canvas.before:
        Color(*C_AZUL)
        wrap._l = Rectangle()
        Color(*C_ROJO)
        wrap._r = Rectangle()

    def _upd(inst, *a):
        mid = inst.x + inst.width / 2
        inst._l.pos  = (inst.x, inst.y)
        inst._l.size = (inst.width / 2, inst.height)
        inst._r.pos  = (mid, inst.y)
        inst._r.size = (inst.width / 2, inst.height)

    wrap.bind(pos=_upd, size=_upd)
    return wrap