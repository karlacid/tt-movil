import websocket
import threading
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.app import App

SERVER_IP = "192.168.100.8"
SERVER_PORT = "8080"
WS_ENDPOINT = "/ws/juez"
LOGIN_API_ENDPOINT = "/api/auth/juez/login"



class WebSocketManager:
    _instance = None

    juez_id = None
    jueces_ocupados = set()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WebSocketManager, cls).__new__(cls)
            cls._instance.ws = None
            cls._instance.is_connected = False
            cls._instance.ws_thread = None
        return cls._instance

    def connect(self):
        if self.is_connected:
            return

        ws_url = f"ws://{SERVER_IP}:{SERVER_PORT}{WS_ENDPOINT}"
        Logger.info(f"WS: Conectando a {ws_url}...")

        self.ws = websocket.WebSocketApp(
            ws_url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )

        self.ws_thread = threading.Thread(target=self.ws.run_forever)
        self.ws_thread.daemon = True
        self.ws_thread.start()

    def disconnect(self):
        if self.ws and self.is_connected:
            self.ws.close()

    def _send_message(self, message):
        if self.ws and self.is_connected:
            self.ws.send(message)
            Logger.info(f"📤 Enviado: {message}")
        else:
            Logger.error("❌ NO conectado al WebSocket")

    # ✅ PUNTOS
    def enviar_punto(self, color, puntos):
        msg = f"PUNTUAR:{puntos},{color.upper()}"
        self._send_message(msg)

    # ✅✅✅ INCIDENCIA CORREGIDA
    def enviar_incidencia(self, tipo="GENERAL"):
        Logger.info("🚨 BOTÓN INCIDENCIA PRESIONADO")
        self._send_message(f"INCIDENCIA:{tipo}")

    def enviar_juez_seleccionado(self, juez):
        self._send_message(f"SELECCIONAR_JUEZ:{juez}")
        Logger.info(f"Solicitando Juez {juez}")

    def _on_open(self, ws):
        Logger.info("✅ WS CONECTADO")
        self.is_connected = True

    def _on_message(self, ws, message):
        Logger.info(f"📩 WS Recibido: {message}")
        mensaje = message.strip()

        if mensaje.startswith("ESTADO_JUECES:"):
            estado = mensaje.replace("ESTADO_JUECES:", "").strip()

            if estado and estado != "[]":
                numeros = estado.strip("[]").split(",")
                self.jueces_ocupados = {int(n.strip()) for n in numeros if n.strip().isdigit()}
            else:
                self.jueces_ocupados = set()

            Clock.schedule_once(lambda dt: self._refrescar_seleccion())

        elif mensaje == "JUEZ_OCUPADO":
            Clock.schedule_once(lambda dt: self._mostrar_error_ocupado())

        elif mensaje == "HABILITAR_PUNTOS":
            Clock.schedule_once(self._activar_botones, 0)

        elif mensaje == "RESET_COMPLETO":
            Clock.schedule_once(self._manejar_reset, 0)

        # ✅✅✅ RESPUESTA DE INCIDENCIA
        elif mensaje == "INCIDENCIA_OK":
            Logger.info("✅ Incidencia registrada correctamente")

        elif mensaje == "INCIDENCIA_ERROR":
            Logger.error("❌ Error al registrar incidencia")

    def _refrescar_seleccion(self):
        try:
            app = App.get_running_app()
            pantalla = app.root.get_screen("selecjuez")
            pantalla.actualizar_estado()
        except Exception as e:
            Logger.error(f"Error refrescando jueces: {e}")

    def _mostrar_error_ocupado(self):
        try:
            app = App.get_running_app()
            pantalla = app.root.get_screen("selecjuez")
            pantalla.mostrar_error_ocupado()
        except Exception as e:
            Logger.error(f"Error mostrando mensaje: {e}")

    def _activar_botones(self, dt):
        try:
            app = App.get_running_app()
            pantalla = app.root.get_screen("controles")
            pantalla.habilitar_botones()
        except Exception as e:
            Logger.error(f"Error activando botones: {e}")

    def _manejar_reset(self, dt):
        try:
            app = App.get_running_app()
            if app.root.current == "controles":
                pantalla = app.root.get_screen("controles")
                pantalla.reset_ui()
        except Exception as e:
            Logger.error(f"Error en reset: {e}")

    def _on_error(self, ws, error):
        Logger.error(f"❌ WS Error: {error}")

    def _on_close(self, ws, code, msg):
        Logger.info("❌ WS DESCONECTADO")
        self.is_connected = False
        self.ws = None
        self.ws_thread = None
