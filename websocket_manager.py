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
    nombre_dispositivo = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WebSocketManager, cls).__new__(cls)
            cls._instance.ws = None
            cls._instance.is_connected = False
            cls._instance.ws_thread = None

            import uuid
            cls._instance.nombre_dispositivo = f"Celular_{str(uuid.uuid4())[:8]}"
        return cls._instance

    def connect(self):
        if self.is_connected:
            return

        ws_url = f"ws://{SERVER_IP}:{SERVER_PORT}{WS_ENDPOINT}"
        Logger.info(f"Conectando a {ws_url}")

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
            Logger.info(f"Enviado: {message}")
        else:
            Logger.error("No conectado al WebSocket")

    def enviar_punto(self, color, puntos):
        if puntos is None:
            msg = f"PUNTUAR:NULL,{color.upper()}"
        else:
            msg = f"PUNTUAR:{puntos},{color.upper()}"
        self._send_message(msg)

    def enviar_incidencia(self, tipo="GENERAL"):
        self._send_message(f"INCIDENCIA:{tipo}")

    def enviar_juez_seleccionado(self, juez_numero):
        msg = f"SELECCIONAR_JUEZ:{self.nombre_dispositivo},{juez_numero}"
        self._send_message(msg)
        Logger.info(f"Solicitando juez {juez_numero}")

    def _on_open(self, ws):
        Logger.info("WebSocket conectado")
        self.is_connected = True

    def _on_message(self, ws, message):
        Logger.info(f"Recibido: {message}")
        mensaje = message.strip()

        if mensaje.startswith("ESTADO_JUECES:"):
            estado = mensaje.replace("ESTADO_JUECES:", "").strip()
            self.jueces_ocupados = set()

            if estado:
                pares = estado.split(",")
                for par in pares:
                    if "-" in par:
                        juez_id, nombre = par.split("-", 1)
                        if juez_id.isdigit():
                            self.jueces_ocupados.add(int(juez_id))

            Clock.schedule_once(lambda dt: self._refrescar_seleccion())

        elif mensaje == "JUEZ_OCUPADO":
            Clock.schedule_once(lambda dt: self._mostrar_error_ocupado())

        elif mensaje == "POSICION_INVALIDA":
            Clock.schedule_once(lambda dt: self._mostrar_error_posicion_invalida())

        

        elif mensaje == "RESET_COMPLETO":
            Clock.schedule_once(self._manejar_reset, 0)
        
        elif mensaje == "RESET_PUNTOS":
            Clock.schedule_once(self._manejar_reset_puntos, 0)

        elif mensaje.startswith("INCIDENCIA_REGISTRADA:"):
            juez_num = mensaje.split(":")[1]
            Logger.info(f"Incidencia registrada para juez {juez_num}")

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

    def _mostrar_error_posicion_invalida(self):
        try:
            app = App.get_running_app()
            pantalla = app.root.get_screen("selecjuez")
            pantalla.mostrar_error_posicion_invalida()
        except Exception as e:
            Logger.error(f"Error mostrando mensaje: {e}")

    def _manejar_reset(self, dt):
        try:
            app = App.get_running_app()
            if app.root.current == "controles":
                pantalla = app.root.get_screen("controles")
                pantalla.reset_ui()
        except Exception as e:
            Logger.error(f"Error en reset: {e}")

    def _manejar_reset_puntos(self, dt):
        try:
            app = App.get_running_app()
            if app.root.current == "controles":
                pantalla = app.root.get_screen("controles")
                pantalla.reset_puntos_visuales()
        except Exception as e:
            Logger.error(f"Error en reset puntos: {e}")

    def _on_error(self, ws, error):
        Logger.error(f"WebSocket error: {error}")

    def _on_close(self, ws, code, msg):
        Logger.info("WebSocket desconectado")
        self.is_connected = False
        self.ws = None
        self.ws_thread = None
