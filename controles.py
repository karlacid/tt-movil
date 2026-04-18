from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.graphics import (
    Color, RoundedRectangle, Rectangle, Triangle,
    Line, Ellipse, SmoothLine
)
from kivy.metrics import dp, sp
from kivy.clock import Clock
from websocket_manager import WebSocketManager


def _activar_wake_lock():
    """Mantiene la pantalla encendida en Android."""
    try:
        from android.permissions import request_permissions, Permission
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        WindowManager  = autoclass('android.view.WindowManager$LayoutParams')
        activity = PythonActivity.mActivity
        activity.runOnUiThread(lambda: activity.getWindow().addFlags(
            WindowManager.FLAG_KEEP_SCREEN_ON
        ))
    except Exception:
        pass  


def _desactivar_wake_lock():
    try:
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        WindowManager  = autoclass('android.view.WindowManager$LayoutParams')
        activity = PythonActivity.mActivity
        activity.runOnUiThread(lambda: activity.getWindow().clearFlags(
            WindowManager.FLAG_KEEP_SCREEN_ON
        ))
    except Exception:
        pass
# ─────────────────────────────────────────────
#  COLORES GLOBALES  (igual que el original)
# ─────────────────────────────────────────────
C_FONDO       = (0.94, 0.93, 0.91, 1)   # gris beige
C_AZUL        = (0.10, 0.29, 0.56, 1)   # azul original
C_AZUL_HDR    = (0.06, 0.19, 0.40, 1)   # header panel azul
C_ROJO        = (0.69, 0.09, 0.09, 1)   # rojo original
C_ROJO_HDR    = (0.54, 0.06, 0.06, 1)   # header panel rojo
C_TOPBAR      = (0.10, 0.18, 0.32, 1)   # barra superior
C_FINALIZAR   = (0.05, 0.18, 0.38, 1)   # botón finalizar
C_BOTON       = (0.05, 0.18, 0.38, 1)   # botón genérico (mismo que finalizar)
C_ALERTA      = (0.96, 0.76, 0.09, 1)   # amarillo alerta
C_ALERTA_BRD  = (0.83, 0.63, 0.00, 1)
C_BLANCO      = (1, 1, 1, 1)

class RoundedColorWidget(Widget):
    def __init__(self, color, radius=dp(14), **kwargs):
        super().__init__(**kwargs)
        self._color = color
        self._radius = radius
        with self.canvas.before:
            Color(*color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size,
                                          radius=[radius])
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *a):
        self._rect.pos  = self.pos
        self._rect.size = self.size


class RoundedButton(Button):
    def __init__(self, bg_color=C_AZUL, radius=dp(12), **kwargs):
        super().__init__(**kwargs)
        self.background_color  = (0, 0, 0, 0)
        self.background_normal = ''
        self._bg = bg_color
        self._radius = radius
        with self.canvas.before:
            Color(*bg_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size,
                                          radius=[radius])
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *a):
        self._rect.pos  = self.pos
        self._rect.size = self.size


class PanelHeader(Widget):
    def __init__(self, color, nombre, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(42)
        self._color = color
        self._nombre = nombre
        self._score = 0

        with self.canvas:
            Color(*color)
            self._bg = Rectangle(pos=self.pos, size=self.size)

        self._lbl_nombre = Label(
            text=nombre,
            font_size=sp(13),
            bold=True,
            color=C_BLANCO,
            halign='left',
            valign='middle',
        )
        self._lbl_score = Label(
            text='0',
            font_size=sp(24),
            bold=True,
            color=C_BLANCO,
            halign='right',
            valign='middle',
        )
        self.add_widget(self._lbl_nombre)
        self.add_widget(self._lbl_score)
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *a):
        self._bg.pos  = self.pos
        self._bg.size = self.size
        pad = dp(12)
        h = self.height
        self._lbl_nombre.pos  = (self.x + pad, self.y)
        self._lbl_nombre.size = (self.width * 0.6, h)
        self._lbl_nombre.text_size = (self.width * 0.6, h)
        self._lbl_score.pos  = (self.x + self.width * 0.6, self.y)
        self._lbl_score.size = (self.width * 0.4 - pad, h)
        self._lbl_score.text_size = (self.width * 0.4 - pad, h)

    def set_score(self, val):
        self._score = val
        self._lbl_score.text = str(val)

class TecnicaButton(Button):
    TECNICAS = {
        'frontal':     {'pts': 1, 'label': 'Patada\ntronco'},
        'circular':    {'pts': 2, 'label': 'Patada\ncabeza'},
        'giro_cuerpo': {'pts': 3, 'label': 'Giro\ntronco'},
        'giro_cabeza': {'pts': 4, 'label': 'Giro\ncabeza'},
    }

    def __init__(self, tipo, color_panel, color_combate, **kwargs):
        super().__init__(**kwargs)
        self.tipo           = tipo
        self.color_combate  = color_combate
        self.puntos         = self.TECNICAS[tipo]['pts']
        self.label_text     = self.TECNICAS[tipo]['label']

        self.background_color  = (0, 0, 0, 0)
        self.background_normal = ''
        self.text = ''

        _r, _g, _b, _ = color_panel
        btn_bg = (_r * 0.85 + 0.15, _g * 0.85 + 0.15, _b * 0.85 + 0.15, 1)

        with self.canvas.before:
            Color(*btn_bg)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size,
                                        radius=[dp(10)])

            Color(1, 1, 1, 0.25)
            self._border = Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, dp(10)),
                width=1
            )

        self._badge = Label(
            text=f'{self.puntos} pt' if self.puntos == 1 else f'{self.puntos} pts',
            font_size=sp(9),
            bold=True,
            color=(1, 1, 1, 0.85),
            halign='right',
            valign='bottom',
        )
        self.add_widget(self._badge)

        self._lbl = Label(
            text=self.label_text,
            font_size=sp(9),
            bold=True,
            color=(1, 1, 1, 0.80),
            halign='center',
            valign='bottom',
        )
        self.add_widget(self._lbl)

        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *a):
        self._bg.pos  = self.pos
        self._bg.size = self.size
        self._border.rounded_rectangle = (
            self.x, self.y, self.width, self.height, dp(10))

        # badge abajo-derecha
        bw, bh = dp(32), dp(16)
        self._badge.pos  = (self.right - bw - dp(4), self.y + dp(4))
        self._badge.size = (bw, bh)
        self._badge.text_size = (bw, bh)

        # label nombre abajo-centro
        self._lbl.pos  = (self.x, self.y + dp(4))
        self._lbl.size = (self.width, dp(24))
        self._lbl.text_size = (self.width, dp(24))

        # redibujar figura
        self.canvas.after.clear()
        self._dibujar_figura()

    def _dibujar_figura(self):
        cx = self.center_x
        cy = self.center_y + dp(8)        
        sc = min(self.width, self.height) * 0.018  # escala

        with self.canvas.after:
            Color(1, 1, 1, 0.95)

            if self.tipo == 'frontal':
                self._figura_frontal(cx, cy, sc)
            elif self.tipo == 'circular':
                self._figura_circular(cx, cy, sc)
            elif self.tipo == 'giro_cuerpo':
                self._figura_giro_cuerpo(cx, cy, sc)
            elif self.tipo == 'giro_cabeza':
                self._figura_giro_cabeza(cx, cy, sc)

    def _figura_frontal(self, cx, cy, s):
        r = s * 5
        # cabeza
        Ellipse(pos=(cx-s*3 - r, cy + s*10 - r), size=(r*2, r*2))
        # tronco recto
        Line(points=[cx-s*3, cy+s*10, cx-s*3, cy-s*2], width=s*1.6, cap='round')
        # pierna de apoyo
        Line(points=[cx-s*3, cy-s*2, cx, cy-s*13], width=s*1.6, cap='round')
        # brazo atrás
        Line(points=[cx-s*3, cy+s*5, cx-s*9, cy+s*2], width=s*1.5, cap='round')
        # pierna pateadora: muslo
        Line(points=[cx-s*3, cy-s*2, cx+s*3, cy+s*3], width=s*1.6, cap='round')
        # pantorrilla extendida al tronco rival
        Line(points=[cx+s*3, cy+s*3, cx+s*12, cy+s*3], width=s*1.8, cap='round')
        # impacto al tronco
        ri = s * 3.5
        Color(1, 1, 1, 0.25)
        Ellipse(pos=(cx+s*12-ri*1.6, cy+s*3-ri), size=(ri*3.2, ri*2))
        Color(1, 1, 1, 0.6)
        ri2 = s * 2
        Ellipse(pos=(cx+s*12-ri2, cy+s*3-ri2), size=(ri2*2, ri2*2))

    
    def _figura_circular(self, cx, cy, s):
        r = s * 5
        # cabeza
        Ellipse(pos=(cx - r, cy + s*10 - r), size=(r*2, r*2))
        # tronco
        Line(points=[cx, cy+s*10, cx, cy-s*2], width=s*1.6, cap='round')
        # pierna de apoyo
        Line(points=[cx, cy-s*2, cx+s*4, cy-s*14], width=s*1.6, cap='round')
        # brazo atrás equilibrio
        Line(points=[cx, cy+s*5, cx+s*6, cy+s*2], width=s*1.5, cap='round')
        # muslo pateador sube alto
        Line(points=[cx, cy-s*2, cx-s*5, cy+s*6], width=s*1.6, cap='round')
        # pantorrilla a la altura de la cabeza rival
        Line(points=[cx-s*5, cy+s*6, cx-s*11, cy+s*10], width=s*1.8, cap='round')
        # cabeza rival (círculos concéntricos)
        rh = s * 5
        Color(1, 1, 1, 0.15)
        Ellipse(pos=(cx-s*11-rh, cy+s*10-rh), size=(rh*2, rh*2))
        Color(1, 1, 1, 0.35)
        rh2 = s * 3.2
        Ellipse(pos=(cx-s*11-rh2, cy+s*10-rh2), size=(rh2*2, rh2*2))
        Color(1, 1, 1, 0.65)
        rh3 = s * 1.8
        Ellipse(pos=(cx-s*11-rh3, cy+s*10-rh3), size=(rh3*2, rh3*2))
        Color(1, 1, 1, 1.0)
        rh4 = s * 0.9
        Ellipse(pos=(cx-s*11-rh4, cy+s*10-rh4), size=(rh4*2, rh4*2))

    
    def _figura_giro_cuerpo(self, cx, cy, s):
        import math
        r = s * 5
        # cabeza
        Ellipse(pos=(cx-s*3 - r, cy + s*10 - r), size=(r*2, r*2))
        # tronco inclinado
        Line(points=[cx-s*3, cy+s*10, cx+s*2, cy-s*1], width=s*1.6, cap='round')
        # pierna de apoyo
        Line(points=[cx+s*2, cy-s*1, cx+s*5, cy-s*13], width=s*1.6, cap='round')
        # brazo traccionando
        Line(points=[cx-s*3, cy+s*5, cx-s*9, cy+s*2], width=s*1.5, cap='round')
        # muslo pateador
        Line(points=[cx+s*2, cy-s*1, cx+s*7, cy+s*4], width=s*1.6, cap='round')
        # pantorrilla al tronco rival
        Line(points=[cx+s*7, cy+s*4, cx+s*13, cy+s*6], width=s*1.8, cap='round')
        # impacto al tronco
        ri = s * 3.5
        Color(1, 1, 1, 0.25)
        Ellipse(pos=(cx+s*13-ri*1.6, cy+s*6-ri), size=(ri*3.2, ri*2))
        Color(1, 1, 1, 0.6)
        ri2 = s * 2
        Ellipse(pos=(cx+s*13-ri2, cy+s*6-ri2), size=(ri2*2, ri2*2))
        # ── arco-flecha de giro encerrando al muñeco ──
        ax = cx - s*1
        ay = cy + s*2
        ar = s * 13   # radio grande para rodear al muñeco
        Color(1, 1, 1, 0.55)
        pts = []
        start_deg = 40
        end_deg   = 310
        steps     = 28
        for i in range(steps + 1):
            angle = math.radians(start_deg + (end_deg - start_deg) * i / steps)
            pts.append(ax + ar * math.cos(angle))
            pts.append(ay + ar * math.sin(angle))
        Line(points=pts, width=s*0.7, cap='round', joint='round')
        # punta de flecha pequeña al final
        ea    = math.radians(end_deg)
        tip_x = ax + ar * math.cos(ea)
        tip_y = ay + ar * math.sin(ea)
        tang  = math.radians(end_deg + 90)
        aw    = s * 2.5
        Line(points=[
            tip_x, tip_y,
            tip_x + aw * math.cos(tang + math.radians(145)),
            tip_y + aw * math.sin(tang + math.radians(145)),
        ], width=s*0.7, cap='round')
        Line(points=[
            tip_x, tip_y,
            tip_x + aw * math.cos(tang - math.radians(145)),
            tip_y + aw * math.sin(tang - math.radians(145)),
        ], width=s*0.7, cap='round')

    
    def _figura_giro_cabeza(self, cx, cy, s):
        import math
        r = s * 5
        # cabeza
        Ellipse(pos=(cx-s*4 - r, cy + s*9 - r), size=(r*2, r*2))
        # tronco
        Line(points=[cx-s*4, cy+s*9, cx+s*1, cy-s*2], width=s*1.6, cap='round')
        # pierna de apoyo
        Line(points=[cx+s*1, cy-s*2, cx+s*4, cy-s*13], width=s*1.6, cap='round')
        # brazo atrás
        Line(points=[cx-s*4, cy+s*5, cx-s*10, cy+s*1], width=s*1.5, cap='round')
        # muslo pateador sube
        Line(points=[cx+s*1, cy-s*2, cx+s*5, cy+s*4], width=s*1.6, cap='round')
        # pantorrilla hacia cabeza rival
        Line(points=[cx+s*5, cy+s*4, cx+s*13, cy+s*9], width=s*1.8, cap='round')
        # cabeza rival (círculos concéntricos)
        rh = s * 6
        Color(1, 1, 1, 0.15)
        Ellipse(pos=(cx+s*13-rh, cy+s*9-rh), size=(rh*2, rh*2))
        Color(1, 1, 1, 0.30)
        rh2 = s * 4
        Ellipse(pos=(cx+s*13-rh2, cy+s*9-rh2), size=(rh2*2, rh2*2))
        Color(1, 1, 1, 0.60)
        rh3 = s * 2.5
        Ellipse(pos=(cx+s*13-rh3, cy+s*9-rh3), size=(rh3*2, rh3*2))
        Color(1, 1, 1, 1.0)
        rh4 = s * 1.2
        Ellipse(pos=(cx+s*13-rh4, cy+s*9-rh4), size=(rh4*2, rh4*2))
        # ── arco-flecha de giro encerrando al muñeco ──
        ax = cx - s*2
        ay = cy + s*2
        ar = s * 13
        Color(1, 1, 1, 0.55)
        pts = []
        start_deg = 40
        end_deg   = 310
        steps     = 28
        for i in range(steps + 1):
            angle = math.radians(start_deg + (end_deg - start_deg) * i / steps)
            pts.append(ax + ar * math.cos(angle))
            pts.append(ay + ar * math.sin(angle))
        Line(points=pts, width=s*0.7, cap='round', joint='round')
        ea    = math.radians(end_deg)
        tip_x = ax + ar * math.cos(ea)
        tip_y = ay + ar * math.sin(ea)
        tang  = math.radians(end_deg + 90)
        aw    = s * 2.5
        Line(points=[
            tip_x, tip_y,
            tip_x + aw * math.cos(tang + math.radians(145)),
            tip_y + aw * math.sin(tang + math.radians(145)),
        ], width=s*0.7, cap='round')
        Line(points=[
            tip_x, tip_y,
            tip_x + aw * math.cos(tang - math.radians(145)),
            tip_y + aw * math.sin(tang - math.radians(145)),
        ], width=s*0.7, cap='round')


class PanelLateral(BoxLayout):
    def __init__(self, color_panel, color_header, nombre, color_combate, **kwargs):
        super().__init__(orientation='vertical', spacing=0, **kwargs)
        self._color_panel   = color_panel
        self._color_combate = color_combate

        # fondo del panel
        with self.canvas.before:
            Color(*color_panel)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size,
                                        radius=[dp(16)])
        self.bind(pos=self._upd_bg, size=self._upd_bg)

        # header
        self.header = PanelHeader(color=color_header, nombre=nombre)
        self.add_widget(self.header)

        
        grid = GridLayout(cols=2, spacing=dp(6), padding=dp(8))
        tipos = ['frontal', 'circular', 'giro_cuerpo', 'giro_cabeza']
        self.botones = []
        for tipo in tipos:
            btn = TecnicaButton(
                tipo=tipo,
                color_panel=color_panel,
                color_combate=color_combate,
            )
            btn.bind(on_press=self._on_tecnica)
            grid.add_widget(btn)
            self.botones.append(btn)
        self.add_widget(grid)

        
        btn_null = RoundedButton(
            text='ANULAR ÚLTIMO PUNTO',
            font_size=sp(9),
            bold=True,
            color=(1, 1, 1, 0.55),
            bg_color=(0, 0, 0, 0.25),
            radius=dp(8),
            size_hint_y=None,
            height=dp(28),
        )
        btn_null.bind(on_press=self._on_anular)

        null_wrap = BoxLayout(
            padding=[dp(8), 0, dp(8), dp(8)],
            size_hint_y=None,
            height=dp(36),
        )
        null_wrap.add_widget(btn_null)
        self.add_widget(null_wrap)

    def _upd_bg(self, *a):
        self._bg.pos  = self.pos
        self._bg.size = self.size

    def _on_tecnica(self, btn):
        WebSocketManager().enviar_punto(self._color_combate, btn.puntos)
        
        pantalla = self._get_pantalla()
        if pantalla:
            pantalla.sumar_punto(self._color_combate, btn.puntos)

    def _on_anular(self, *a):
        WebSocketManager().enviar_punto(self._color_combate, None)

    def _get_pantalla(self):
        parent = self.parent
        while parent:
            if isinstance(parent, PantallaControles):
                return parent
            parent = parent.parent
        return None


class TopBar(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(32),
            padding=[dp(14), 0],
            spacing=dp(10),
            **kwargs
        )
        with self.canvas.before:
            Color(*C_TOPBAR)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._upd, size=self._upd)

        self.add_widget(Label(
            text='PETOTECH SYSTEM',
            font_size=sp(10),
            bold=True,
            color=(0.54, 0.69, 0.85, 1),
            halign='left',
            valign='middle',
        ))
        self.lbl_combate = Label(
            text='COMBATE',
            font_size=sp(10),
            color=(0.42, 0.56, 0.72, 1),
            halign='center',
            valign='middle',
        )
        self.add_widget(self.lbl_combate)
        self.add_widget(Label(
            text='JUEZ',
            font_size=sp(10),
            color=(0.42, 0.56, 0.72, 1),
            halign='right',
            valign='middle',
        ))

    def _upd(self, *a):
        self._bg.pos  = self.pos
        self._bg.size = self.size

    def set_info(self, combate_id, juez_id):
        self.lbl_combate.text = f'COMBATE #{combate_id}  ·  JUEZ {juez_id}'


class Marcador(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(
            orientation='vertical',
            size_hint_y=None,
            height=dp(72),
            **kwargs
        )
        with self.canvas.before:
            Color(*C_BLANCO)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size,
                                        radius=[dp(12)])
        self.bind(pos=self._upd, size=self._upd)

        row = BoxLayout(orientation='horizontal', padding=[dp(8), dp(6)])

        # azul
        azul_col = BoxLayout(orientation='vertical', spacing=dp(1))
        self._lbl_azul_tag = Label(
            text='AZUL', font_size=sp(9), bold=True,
            color=(0.06, 0.19, 0.40, 1), halign='center', valign='middle',
        )
        self._lbl_azul_num = Label(
            text='0', font_size=sp(36), bold=True,
            color=(0.10, 0.29, 0.56, 1), halign='center', valign='middle',
        )
        azul_col.add_widget(self._lbl_azul_tag)
        azul_col.add_widget(self._lbl_azul_num)

        sep = Label(text='—', font_size=sp(16), color=(0.75, 0.75, 0.75, 1),
                    size_hint_x=None, width=dp(24), halign='center', valign='middle')

        # rojo
        rojo_col = BoxLayout(orientation='vertical', spacing=dp(1))
        self._lbl_rojo_tag = Label(
            text='ROJO', font_size=sp(9), bold=True,
            color=(0.54, 0.06, 0.06, 1), halign='center', valign='middle',
        )
        self._lbl_rojo_num = Label(
            text='0', font_size=sp(36), bold=True,
            color=(0.69, 0.09, 0.09, 1), halign='center', valign='middle',
        )
        rojo_col.add_widget(self._lbl_rojo_tag)
        rojo_col.add_widget(self._lbl_rojo_num)

        row.add_widget(azul_col)
        row.add_widget(sep)
        row.add_widget(rojo_col)
        self.add_widget(row)

        # barra bicolor inferior
        barra = BoxLayout(size_hint_y=None, height=dp(4))
        with barra.canvas.before:
            Color(*C_AZUL)
            self._barra_azul = Rectangle()
            Color(*C_ROJO)
            self._barra_rojo = Rectangle()
        barra.bind(pos=self._upd_barra, size=self._upd_barra)
        self._barra_widget = barra
        self.add_widget(barra)

    def _upd(self, *a):
        self._bg.pos  = self.pos
        self._bg.size = self.size

    def _upd_barra(self, inst, *a):
        mid = inst.x + inst.width / 2
        self._barra_azul.pos  = (inst.x, inst.y)
        self._barra_azul.size = (inst.width / 2, inst.height)
        self._barra_rojo.pos  = (mid, inst.y)
        self._barra_rojo.size = (inst.width / 2, inst.height)

    def set_scores(self, azul, rojo):
        self._lbl_azul_num.text = str(azul)
        self._lbl_rojo_num.text = str(rojo)



class TriangleAlertButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.text = ''

        with self.canvas.before:
            Color(*C_ALERTA_BRD)
            self.tri_sombra = Triangle(points=[0]*6)
            Color(*C_ALERTA)
            self.tri = Triangle(points=[0]*6)

        with self.canvas.after:
            Color(0.35, 0.22, 0, 1)
            self.exc_rect = Rectangle(pos=(0, 0), size=(0, 0))
            self.exc_dot  = Rectangle(pos=(0, 0), size=(0, 0))

        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *a):
        cx, cy = self.center_x, self.center_y
        w  = min(self.width, self.height) * 0.72
        h  = w * 0.866
        bo = dp(3)

        self.tri_sombra.points = [
            cx,           cy + h/2 + bo,
            cx - w/2 - bo, cy - h/2 - bo,
            cx + w/2 + bo, cy - h/2 - bo,
        ]
        self.tri.points = [
            cx,      cy + h/2,
            cx - w/2, cy - h/2,
            cx + w/2, cy - h/2,
        ]

        ew = max(dp(5), min(self.width, self.height) * 0.07)
        eh = h * 0.42
        ds = max(dp(7), min(self.width, self.height) * 0.09)
        sp_v = max(dp(7), min(self.width, self.height) * 0.07)

        self.exc_rect.pos  = (cx - ew/2, cy - eh/2 + sp_v)
        self.exc_rect.size = (ew, eh)
        self.exc_dot.pos   = (cx - ds/2, cy - h/2 + sp_v * 0.75)
        self.exc_dot.size  = (ds, ds)



class LeyendaBar(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(38),
            **kwargs
        )
        with self.canvas.before:
            Color(0.91, 0.89, 0.86, 1)
            self._bg = Rectangle(pos=self.pos, size=self.size)
            Color(0.81, 0.78, 0.74, 1)
            self._top_line = Line(width=1)
        self.bind(pos=self._upd, size=self._upd)

        items = [
            ('1 pt',  'Patada frontal'),
            ('2 pts', 'Circular cuerpo'),
            ('3 pts', 'Giro al cuerpo'),
            ('5 pts', 'Giro a la cabeza'),
        ]
        for pts, nombre in items:
            col = BoxLayout(orientation='vertical', spacing=dp(1),
                            padding=[dp(4), dp(4)])
            col.add_widget(Label(
                text=pts, font_size=sp(11), bold=True,
                color=(0.10, 0.18, 0.32, 1),
                halign='center', valign='bottom',
            ))
            col.add_widget(Label(
                text=nombre, font_size=sp(8),
                color=(0.48, 0.44, 0.40, 1),
                halign='center', valign='top',
            ))
            self.add_widget(col)

    def _upd(self, *a):
        self._bg.pos  = self.pos
        self._bg.size = self.size
        self._top_line.points = [self.x, self.top, self.right, self.top]



class PantallaControles(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'controles'
        self._score_azul = 0
        self._score_rojo = 0
        self.build_ui()

    # ── construcción ──────────────────────────
    def build_ui(self):
        with self.canvas.before:
            Color(*C_FONDO)
            self._bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._upd_bg, pos=self._upd_bg)

        root = BoxLayout(orientation='vertical', spacing=0)

        # barra superior
        self.topbar = TopBar()
        root.add_widget(self.topbar)

        # zona central
        contenido = BoxLayout(
            orientation='horizontal',
            padding=dp(10),
            spacing=dp(10),
        )

        # panel rojo (izquierda)
        self.panel_rojo = PanelLateral(
            color_panel=C_ROJO,
            color_header=C_ROJO_HDR,
            nombre='ROJO',
            color_combate='ROJO',
        )
        contenido.add_widget(self.panel_rojo)

        # columna central
        centro = BoxLayout(
            orientation='vertical',
            size_hint_x=None,
            width=dp(180),
            spacing=dp(8),
        )

        self.marcador = Marcador()
        centro.add_widget(self.marcador)

        self.btn_alerta = TriangleAlertButton()
        self.btn_alerta.bind(on_press=self.alerta_accion)
        centro.add_widget(self.btn_alerta)

        self.btn_finalizar = RoundedButton(
            text='FINALIZAR',
            font_size=sp(13),
            bold=True,
            color=C_BLANCO,
            bg_color=C_FINALIZAR,
            radius=dp(12),
            size_hint_y=None,
            height=dp(46),
        )
        self.btn_finalizar.bind(on_press=self.mostrar_confirmacion)
        centro.add_widget(self.btn_finalizar)

        contenido.add_widget(centro)

        # panel azul (derecha)
        self.panel_azul = PanelLateral(
            color_panel=C_AZUL,
            color_header=C_AZUL_HDR,
            nombre='AZUL',
            color_combate='AZUL',
        )
        contenido.add_widget(self.panel_azul)

        root.add_widget(contenido)

        self.add_widget(root)

    def _upd_bg(self, *a):
        self._bg.pos  = self.pos
        self._bg.size = self.size

    # ── marcador ──────────────────────────────
    def sumar_punto(self, color, pts):
        if pts is None:
            return
        if color == 'AZUL':
            self._score_azul += pts
            self.panel_azul.header.set_score(self._score_azul)
        else:
            self._score_rojo += pts
            self.panel_rojo.header.set_score(self._score_rojo)
        self.marcador.set_scores(self._score_azul, self._score_rojo)

    def reset_puntos_visuales(self):
        self._score_azul = 0
        self._score_rojo = 0
        self.marcador.set_scores(0, 0)
        self.panel_azul.header.set_score(0)
        self.panel_rojo.header.set_score(0)

    def reset_ui(self):
        self.reset_puntos_visuales()

    # ── on_enter ──────────────────────────────
    def on_enter(self):
        _activar_wake_lock()          
        ws = WebSocketManager()
        self.topbar.set_info(
            ws.combate_id or '—',
            ws.juez_id or '—',
        )

    # ── POPUP INCIDENCIA ──────────────────────
    def alerta_accion(self, instance):
        WebSocketManager().enviar_incidencia()
        self._popup_info(
            titulo='Incidencia',
            mensaje='¡Incidencia reportada!',
        )

    # ── POPUP FINALIZAR ───────────────────────
    def mostrar_confirmacion(self, instance):
        content = BoxLayout(orientation='vertical', spacing=dp(12),
                            padding=[dp(24), dp(20), dp(24), dp(20)])

        # separador bicolor decorativo
        sep = BoxLayout(size_hint_y=None, height=dp(3),
                        padding=[dp(40), 0])
        with sep.canvas.before:
            Color(*C_AZUL)
            sep._l = Rectangle()
            Color(*C_ROJO)
            sep._r = Rectangle()
        def _upd_sep(inst, *a):
            mid = inst.x + inst.width / 2
            inst._l.pos  = (inst.x, inst.y)
            inst._l.size = (inst.width / 2, inst.height)
            inst._r.pos  = (mid, inst.y)
            inst._r.size = (inst.width / 2, inst.height)
        sep.bind(pos=_upd_sep, size=_upd_sep)
        content.add_widget(sep)

        content.add_widget(Widget(size_hint_y=None, height=dp(8)))

        lbl = Label(
            text='¿Finalizar el combate?',
            color=(0.10, 0.18, 0.32, 1),
            font_size=sp(17),
            bold=True,
            halign='center', valign='middle',
            size_hint_y=None, height=dp(30),
        )
        lbl.bind(size=lbl.setter('text_size'))
        content.add_widget(lbl)

        lbl_sub = Label(
            text='Esta acción cerrará la sesión del juez.',
            color=(0.38, 0.46, 0.58, 1),
            font_size=sp(12),
            halign='center', valign='middle',
            size_hint_y=None, height=dp(22),
        )
        lbl_sub.bind(size=lbl_sub.setter('text_size'))
        content.add_widget(lbl_sub)

        content.add_widget(Widget(size_hint_y=None, height=dp(8)))

        botones = BoxLayout(spacing=dp(12), size_hint_y=None, height=dp(48))

        btn_si = self._make_btn('FINALIZAR', C_FINALIZAR, C_AZUL)
        btn_no = self._make_btn('CANCELAR', C_ROJO, C_ROJO_HDR)

        botones.add_widget(btn_si)
        botones.add_widget(btn_no)
        content.add_widget(botones)

        popup = self._make_popup(content, size=(dp(420), dp(230)))
        btn_no.bind(on_press=popup.dismiss)
        btn_si.bind(on_press=lambda x: self.confirmar_finalizar(popup))
        popup.open()

    def confirmar_finalizar(self, popup):
        popup.dismiss()
        _desactivar_wake_lock()       
        ws = WebSocketManager()
        if ws.juez_id:
            ws.jueces_ocupados.discard(ws.juez_id)
            ws.juez_id = None
        ws.disconnect()
        self.manager.current = 'pantalla_login'

  
    def _popup_info(self, titulo, mensaje):
        content = BoxLayout(orientation='vertical', spacing=dp(12),
                            padding=[dp(24), dp(20), dp(24), dp(20)])

        # separador bicolor decorativo
        sep = BoxLayout(size_hint_y=None, height=dp(3),
                        padding=[dp(40), 0])
        with sep.canvas.before:
            Color(*C_AZUL)
            sep._l = Rectangle()
            Color(*C_ROJO)
            sep._r = Rectangle()
        def _upd_sep(inst, *a):
            mid = inst.x + inst.width / 2
            inst._l.pos  = (inst.x, inst.y)
            inst._l.size = (inst.width / 2, inst.height)
            inst._r.pos  = (mid, inst.y)
            inst._r.size = (inst.width / 2, inst.height)
        sep.bind(pos=_upd_sep, size=_upd_sep)
        content.add_widget(sep)

        content.add_widget(Widget(size_hint_y=None, height=dp(8)))

        lbl = Label(
            text=titulo,
            color=(0.10, 0.18, 0.32, 1),
            font_size=sp(17),
            bold=True,
            halign='center', valign='middle',
            size_hint_y=None, height=dp(28),
        )
        lbl.bind(size=lbl.setter('text_size'))
        content.add_widget(lbl)

        lbl_msg = Label(
            text=mensaje,
            color=(0.38, 0.46, 0.58, 1),
            font_size=sp(13),
            halign='center', valign='middle',
            size_hint_y=None, height=dp(28),
        )
        lbl_msg.bind(size=lbl_msg.setter('text_size'))
        content.add_widget(lbl_msg)

        content.add_widget(Widget(size_hint_y=None, height=dp(8)))

        btn_ok = self._make_btn('ACEPTAR', C_BOTON, C_AZUL)
        content.add_widget(btn_ok)

        popup = self._make_popup(content, size=(dp(380), dp(210)))
        btn_ok.bind(on_press=popup.dismiss)
        popup.open()

    def _make_btn(self, texto, bg, brd):
        """Botón redondeado consistente con el resto de la app."""
        btn = Button(
            text=texto,
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=C_BLANCO,
            bold=True,
            font_size=sp(14),
            size_hint_y=None,
            height=dp(48),
        )
        with btn.canvas.before:
            Color(*bg)
            btn._bg = RoundedRectangle(pos=btn.pos, size=btn.size,
                                       radius=[dp(12)])
            Color(*brd)
            btn._brd = Line(
                rounded_rectangle=(btn.x, btn.y, btn.width, btn.height, dp(12)),
                width=1.2
            )
        def _upd(inst, *a):
            inst._bg.pos  = inst.pos
            inst._bg.size = inst.size
            inst._brd.rounded_rectangle = (
                inst.x, inst.y, inst.width, inst.height, dp(12))
        btn.bind(pos=_upd, size=_upd)
        return btn

    def _make_popup(self, content, size=(dp(420), dp(240))):
        popup = Popup(
            title='',
            title_size=sp(1),
            content=content,
            size_hint=(None, None),
            size=size,
            separator_height=0,
            background='',
            auto_dismiss=False,
        )
        with popup.canvas.before:
            Color(*C_FONDO)
            popup._bg = RoundedRectangle(
                pos=popup.pos, size=popup.size, radius=[dp(16)])
            Color(0.80, 0.78, 0.74, 1)
            popup._brd = Line(
                rounded_rectangle=(popup.x, popup.y,
                                   popup.width, popup.height, dp(16)),
                width=1
            )

        def _upd(inst, _):
            inst._bg.pos  = inst.pos
            inst._bg.size = inst.size
            inst._brd.rounded_rectangle = (
                inst.x, inst.y, inst.width, inst.height, dp(16))

        popup.bind(pos=_upd, size=_upd)
        return popup