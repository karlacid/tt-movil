import websocket
import threading
import requests
import json
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.app import App

SERVER_IP = "localhost" # Cambiar por la IP del servidor
SERVER_PORT = "8080"
WS_ENDPOINT = "/ws/juez"
LOGIN_API_ENDPOINT = "/api/auth/juez/login"

class WebSocketManager:
    _instance = None

    juez_id = None
    jueces_ocupados = set()
    nombre_dispositivo = None
    combate_id = None  # Nuevo: almacena el ID del combate

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WebSocketManager, cls).__new__(cls)
            cls._instance.ws = None
            cls._instance.is_connected = False
            cls._instance.ws_thread = None
            cls._instance.combate_id = None

            import uuid
            cls._instance.nombre_dispositivo = f"Celular_{str(uuid.uuid4())[:8]}"
        return cls._instance

    def login_and_connect(self, password, on_success=None, on_error=None):
        """
        Realiza login con la contraseña y luego conecta al WebSocket
        """
        def hacer_login():
            try:
                # 1. Hacer login para obtener el combateId
                login_url = f"http://{SERVER_IP}:{SERVER_PORT}{LOGIN_API_ENDPOINT}"
                headers = {'Content-Type': 'application/json'}
                data = {'password': password}
                
                Logger.info(f"Intentando login en {login_url}")
                response = requests.post(login_url, json=data, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    result = response.json()
                    self.combate_id = result.get('combateId')
                    
                    Logger.info(f"Login exitoso. CombateId: {self.combate_id}")
                    
                    # 2. Conectar al WebSocket con el combateId
                    Clock.schedule_once(lambda dt: self._conectar_websocket(on_success, on_error), 0)
                    
                else:
                    error_msg = "Contraseña incorrecta"
                    try:
                        error_data = response.json()
                        error_msg = error_data.get('message', error_msg)
                    except:
                        pass
                    
                    Logger.error(f"Login fallido: {error_msg}")
                    if on_error:
                        Clock.schedule_once(lambda dt: on_error(error_msg), 0)
                        
            except requests.exceptions.Timeout:
                Logger.error("Timeout en login")
                if on_error:
                    Clock.schedule_once(lambda dt: on_error("Timeout de conexión"), 0)
            except requests.exceptions.ConnectionError:
                Logger.error("Error de conexión al servidor")
                if on_error:
                    Clock.schedule_once(lambda dt: on_error("No se pudo conectar al servidor"), 0)
            except Exception as e:
                Logger.error(f"Error en login: {e}")
                if on_error:
                    Clock.schedule_once(lambda dt: on_error(f"Error: {str(e)}"), 0)
        
        # Ejecutar login en hilo separado
        login_thread = threading.Thread(target=hacer_login)
        login_thread.daemon = True
        login_thread.start()

    def _conectar_websocket(self, on_success=None, on_error=None):
        """
        Conecta al WebSocket usando el combateId obtenido del login
        """
        if self.is_connected:
            Logger.info("Ya está conectado al WebSocket")
            if on_success:
                on_success()
            return

        if self.combate_id is None:
            Logger.error("No hay combateId. Debe hacer login primero.")
            if on_error:
                on_error("No hay combateId")
            return

        # Construir URL con el combateId
        ws_url = f"ws://{SERVER_IP}:{SERVER_PORT}{WS_ENDPOINT}/{self.combate_id}"
        Logger.info(f"Conectando a WebSocket: {ws_url}")

        self.ws = websocket.WebSocketApp(
            ws_url,
            on_open=lambda ws: self._on_open(ws, on_success),
            on_message=self._on_message,
            on_error=lambda ws, error: self._on_error(ws, error, on_error),
            on_close=self._on_close
        )

        self.ws_thread = threading.Thread(target=self.ws.run_forever)
        self.ws_thread.daemon = True
        self.ws_thread.start()

    def connect(self):
        """
        Método legacy - ahora se debe usar login_and_connect
        """
        Logger.warning("Usar login_and_connect() en lugar de connect()")
        if self.combate_id:
            self._conectar_websocket()
        else:
            Logger.error("Debe hacer login primero con login_and_connect()")

    def disconnect(self):
        if self.ws and self.is_connected:
            self.ws.close()
        self.combate_id = None

    def _send_message(self, message):
        if self.ws and self.is_connected:
            self.ws.send(message)
            Logger.info(f"Enviado: {message}")
        else:
            Logger.error("No conectado al WebSocket")

    def enviar_punto(self, color, puntos):
        # Si puntos es None, enviar -1
        if puntos is None:
            msg = f"PUNTUAR:-1,{color.upper()}"
        else:
            msg = f"PUNTUAR:{puntos},{color.upper()}"
        self._send_message(msg)

    def enviar_incidencia(self):
        """Envía una incidencia sin especificar color"""
        msg = "INCIDENCIA"
        self._send_message(msg)

    def enviar_juez_seleccionado(self, juez_numero):
        msg = f"SELECCIONAR_JUEZ:{juez_numero}"
        self._send_message(msg)
        Logger.info(f"Solicitando juez {juez_numero}")

    def _on_open(self, ws, on_success=None):
        Logger.info(f"WebSocket conectado al combate {self.combate_id}")
        self.is_connected = True
        if on_success:
            Clock.schedule_once(lambda dt: on_success(), 0)

    def _on_message(self, ws, message):
        Logger.info(f"Recibido: {message}")
        mensaje = message.strip()

        if mensaje.startswith("ESTADO_JUECES:"):
            estado = mensaje.replace("ESTADO_JUECES:", "").strip()
            self.jueces_ocupados = set()

            if estado and estado != "[]":
                # Parsear el estado de los jueces
                estado_limpio = estado.strip("[]")
                if estado_limpio:
                    jueces = estado_limpio.split(",")
                    for juez in jueces:
                        juez = juez.strip()
                        if juez.isdigit():
                            self.jueces_ocupados.add(int(juez))

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

    def _on_error(self, ws, error, on_error_callback=None):
        Logger.error(f"WebSocket error: {error}")
        if on_error_callback:
            Clock.schedule_once(lambda dt: on_error_callback(str(error)), 0)

    def _on_close(self, ws, code, msg):
        Logger.info(f"WebSocket desconectado (code: {code}, msg: {msg})")
        self.is_connected = False
        self.ws = None
        self.ws_thread = None