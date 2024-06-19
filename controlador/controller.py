# controller.py
import sift
from kivy.clock import Clock
from kivy.core.image import Texture

import controlador.cuia as cuia
import cv2

import speech_recognition as sr


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
        self.face_code = None
        self.id_usuario = 0

    def login(self, username, password):
        id_user = self.model.validate_user(username, password)
        if id_user != None:
            print('Login successful')
            self.id_usuario = id_user
            self.app.screen_manager.current = 'home'
            self.previous_page = 'home'

            login_screen = self.app.screen_manager.get_screen('login')
            login_screen.ids.error_label.text = ''
        else:
            print('No existe ese usuario')
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
        print("DEBUG:: creamos la hebra y activamos la camara")
        self.capture = cuia.myVideo(self.my_cam, self.best_cap)
        self.codificarCaraUsuario()
        self.event = Clock.schedule_interval(self.update, 1.0 / 30.0)  # Update at 30 FPS
        self.running_cam = True

    def codificarCaraUsuario(self):
        # Cargamos la cara que queremos comparar
        foto_usuario = cv2.imread("media/xinio.jpeg") #TODO traernos la foto de la base de datos
        foto_usuario = cv2.resize(foto_usuario, dsize=None, fx=0.5, fy=0.5)
        #Codificamos la cara
        fr = cv2.FaceRecognizerSF.create("dnn/face_recognition_sface_2021dec.onnx", "")
        h2, w2, _ = foto_usuario.shape
        detector2 = cv2.FaceDetectorYN.create("dnn/face_detection_yunet_2023mar.onnx", config="", input_size=(w2, h2),
                                              score_threshold=0.7)
        ret, cara_usuario = detector2.detect(foto_usuario)
        usuario_crop = fr.alignCrop(foto_usuario, cara_usuario[0])
        self.face_code = fr.feature(usuario_crop)

    def update(self, dt):

        ret, frame = self.capture.read()
        if not ret: #En caso de que no se retorne nada de la camara abortamos
            print("Error: no se pudo leer el frame de la cámara.")
            return

        camara_screen = self.app.screen_manager.get_screen('camara') #Nos traemos la pantalla de la camara a una variable para poder modificar la imagen y meterle el frame de la camara

        self.reconocimiento_facial(frame)

        try:
            # Convertir la imagen de BGR a la textura de Kivy
            buf = cv2.flip(frame, 0).tobytes()
            image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            camara_screen.ids.camera_view.texture = image_texture
        except Exception as e:
            print("Error al detectar caras: ", e)

    def reconocimiento_facial(self, frame):
        h, w, _ = frame.shape
        detector = cv2.FaceDetectorYN.create("dnn/face_detection_yunet_2023mar.onnx", config="", input_size=(w, h),
                                             score_threshold=0.7)
        fr = cv2.FaceRecognizerSF.create("dnn/face_recognition_sface_2021dec.onnx", "")
        ret, caras = detector.detect(frame)

        # Seccion de debug porque da un fallo de tamaños
        '''print("Frame original - Tipo de imagen: ", type(frame))
        print("Frame original - Forma de la imagen: ", frame.shape)
        print("Frame original - Tipo de datos de la imagen: ", frame.dtype)
        print("Imagen RGB - Tipo de imagen: ", type(ellen))
        print("Imagen RGB - Forma de la imagen: ", ellen.shape)
        print("Imagen RGB - Tipo de datos de la imagen: ", ellen.dtype)'''
        # Fin de la seccion de debug

        # comparamos las cara y hacemos que se dibuje un rectangulo en la que concuerde
        for cara in caras:
            c = cara.astype(int)
            caracrop = fr.alignCrop(frame, cara)
            codcara = fr.feature(caracrop)
            semejanza = fr.match(self.face_code, codcara, cv2.FaceRecognizerSF_FR_COSINE)
            if semejanza > 0.5:
                color = (0, 255, 0)
                #self.cerrarCam() #En caso de que se haya reconocido una cara cerramos la ventana, agregamos la reserva y devolvemos al usuario al homeScreen
            else:
                color = (0, 0, 255)

            cv2.rectangle(frame, (c[0], c[1]), (c[0] + c[2], c[1] + c[3]), color, 3)
            cv2.putText(frame, str(round(semejanza, 2)), (c[0], c[1] + 25), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (255, 255, 255), 1, cv2.LINE_AA)

    '''def update(self, dt):
        ret, frame = self.capture.read()
        camara_screen = self.app.screen_manager.get_screen('camara')

        if not ret:
            print("Error: no se pudo leer el frame de la cámara.")
            return

        # Verificar el frame original
        print("Frame original - Tipo de imagen: ", type(frame))
        print("Frame original - Forma de la imagen: ", frame.shape)
        print("Frame original - Tipo de datos de la imagen: ", frame.dtype)

        # Imprimir algunos valores de los píxeles
        print("Frame original - Valores de los primeros 5 píxeles:", frame[0, :5, :])

        # Convertir el frame de BGR a RGB
        ellen_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Verificar el tipo de imagen, la forma y el tipo de datos después de la conversión
        print("Imagen RGB - Tipo de imagen: ", type(ellen_rgb))
        print("Imagen RGB - Forma de la imagen: ", ellen_rgb.shape)
        print("Imagen RGB - Tipo de datos de la imagen: ", ellen_rgb.dtype)

        # Imprimir algunos valores de los píxeles después de la conversión
        print("Imagen RGB - Valores de los primeros 5 píxeles:", ellen_rgb[0, :5, :])

        # Asegurarse de que la imagen está en formato RGB
        if ellen_rgb.shape[2] != 3:
            print("Error: la imagen no tiene 3 canales (RGB).")
            return

        cv2.imwrite('debug_frame.jpg', frame)
        cv2.imwrite('debug_ellen_rgb.jpg', ellen_rgb)

        try:
            # Detectar caras en la imagen RGB
            caras_ellen = fr.face_locations(frame)
            print("Caras detectadas: ", caras_ellen)

            # Si se detecta alguna cara, dibujar un rectángulo alrededor de cada una
            if caras_ellen:
                for c in caras_ellen:
                    cv2.rectangle(frame, (c[3], c[0]), (c[1], c[2]), (0, 255, 0), 2)

            # Convertir la imagen de BGR a la textura de Kivy
            buf = cv2.flip(frame, 0).tobytes()
            image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            camara_screen.ids.camera_view.texture = image_texture
        except Exception as e:
            print("Error al detectar caras: ", e)'''

    def leaveCamera(self, *args):
        self.event.cancel()
        self.capture.release()
        self.face_code = None

    def cerrarCam(self):
        self.leaveCamera()
        self.moveToHomePage()