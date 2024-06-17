# controller.py

from kivy.clock import Clock
from kivy.core.image import Texture

import controlador.cuia as cuia
import cv2


class Controller:

    previous_page = None
    my_cam = 0
    best_cap = None

    def __init__(self, model, app):
        self.model = model
        self.app = app
        self.my_cam = 0
        self.best_cap = cuia.bestBackend(self.my_cam)
        self.running_cam = False
        self.capture = None
        self.event = None

    def login(self, username, password):
        if self.model.validate_user(username, password):
            print('Login successful')
            self.app.screen_manager.current = 'home'
            self.previous_page = 'home'

            login_screen = self.app.screen_manager.get_screen('login')
            login_screen.ids.error_label.text = ''
        else:
            print('Invalid credentials')
            login_screen = self.app.screen_manager.get_screen('login')
            login_screen.ids.error_label.text = 'Invalid username or password'

    def logout(self):
        print('Logged out')
        self.previous_page = None
        self.app.screen_manager.current = 'login'

    def moveToEventsPage(self):
        print('Nos movemos a la pagina de eventos')
        events_screen = self.app.screen_manager.get_screen('events')
        events_screen.cargar_data_eventos(self.model.traer_eventos())
        self.app.screen_manager.current = 'events'

    def moveToHomePage(self):
        print('Nos movemos a la pagina de home')
        self.previous_page = 'home'
        self.app.screen_manager.current = 'home'

    def moveToPreviousPage(self):
        print('Nos movemos a la pagina anterior')
        if(self.previous_page != None):
            self.app.screen_manager.current = self.previous_page

    def moveToEventInfoPage(self, id):
        print('Nos movemos a la pagina de info del evento con id: '+id)
        self.previous_page = 'events'
        info_evento = self.model.traer_evento_por_id(id)
        #print("DEBUG:: valores que nos traemos de la base de datos del evento en concreto"+str(info_evento))
        event_info_screen = self.app.screen_manager.get_screen('eventInfo')
        event_info_screen.ids.nombre_evento.text = str(info_evento[1])
        event_info_screen.ids.recinto_evento.text = str(info_evento[2])
        event_info_screen.ids.direccion_evento.text = str(info_evento[3])
        event_info_screen.ids.fecha_evento.text = str(info_evento[4])
        self.app.screen_manager.current = 'eventInfo'

    def moveToCamPage(self):
        print('Nos movemos a la pagina de la camara')
        self.app.screen_manager.current = 'camara'

    def playWebcam(self):
        print("DEBUG:: creamos la hebra")
        self.capture = cv2.VideoCapture(0)
        self.event = Clock.schedule_interval(self.update, 1.0 / 30.0)  # Update at 30 FPS
        self.running_cam = True

    def update(self, dt):
        ret, frame = self.capture.read()
        camara_screen = self.app.screen_manager.get_screen('camara')
        if ret:
            # Convert the image from BGR to RGB
            buf = cv2.flip(frame, 0).tobytes()
            image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            camara_screen.ids.camera_view.texture = image_texture

    def leaveCamera(self, *args):
        self.event.cancel()
        self.capture.release()

    def cerrarCam(self):
        self.running_cam = False
        self.moveToEventsPage()