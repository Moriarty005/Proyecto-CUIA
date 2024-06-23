# controller.py
import json
import threading

import numpy as np
from kivy.clock import Clock
from kivy.core.image import Texture
from kivy.properties import partial

import controlador.cuia as cuia
import cv2

import speech_recognition as sr


class Controller:

    previous_page = None
    best_cap = None

    def __init__(self, model, app):
        self.model = model
        self.app = app
        self.my_cam = 0
        self.best_cap = cuia.bestBackend(self.my_cam)
        self.running_cam = False
        self.capture = None
        self.event_camara = None
        self.face_code = None
        self.id_usuario = 0
        self.foto = False
        self.speech_recognizer = None
        self.event_voz = None
        self.microfono = None
        self.esta_escuchando = False

    '''
    ############################################
    Funciones para movernos entre las pantallas
    ############################################
    '''

    def moveToEventsPage(self):
        print('Nos movemos a la pagina de eventos')
        events_screen = self.app.screen_manager.get_screen('events')
        events_screen.cargar_data_eventos(self.model.traer_eventos())
        self.app.screen_manager.current = 'events'

    def moveToRegisterPage(self):
        print('Nos movemos a la pagina de regsitro')
        self.previous_page = 'login'
        self.app.screen_manager.current = 'register'

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
        event_info_screen.setIdEvento(id)
        self.app.screen_manager.current = 'eventInfo'

    def moveToFaceRecognitionPage(self):
        print('Nos movemos a la pagina de la camara p[ara hacer reconocimiento facial')
        self.previous_page = 'eventInfo'
        camara_screen = self.app.screen_manager.get_screen('camara')
        camara_screen.show_button = True
        camara_screen.on_enter = lambda: self.playWebcam(self.reconocimiento_facial)
        self.app.screen_manager.current = 'camara'

    def moveToTakePhotoPage(self):
        print('Nos movemos a la pagina de la camara para tomar una foto')
        self.previous_page = 'register'
        camara_screen = self.app.screen_manager.get_screen('camara')
        camara_screen.show_button = False
        camara_screen.on_enter = lambda: self.playWebcam(self.hacerFoto)
        self.app.screen_manager.current = 'camara'

    '''
    ############################################
    Funciones de lógica de la aplicación referentes a login y registro de usuarios
    ############################################
    '''
    def login(self, username, password):
        id_user = self.model.validate_user(username, password)
        if id_user != None:
            print('Login successful')
            self.id_usuario = id_user
            self.app.screen_manager.current = 'home'
            self.previous_page = 'home'
            self.face_code = self.model.get_codificacion_cara(id_user)
            python_list = json.loads(self.face_code)
            self.face_code = np.array(python_list)
            print("DEBUG:: codigo de la cara que nos traemos de la base de datos: "+str(self.face_code))
            login_screen = self.app.screen_manager.get_screen('login')
            login_screen.ids.error_label.text = ''
        else:
            print('No existe ese usuario')
            login_screen = self.app.screen_manager.get_screen('login')
            login_screen.ids.error_label.text = 'Invalid username or password'


    #TODO hacer el metodo que registre el usuario, comprobando que todos los campos son correctos
    def register(self, username, password, name, surname, dni, email):
        evento_screen = self.app.screen_manager.get_screen('register')
        if self.face_code is None or username == None or name == None or dni == None or email == None:
            #print("DEBUG:: da error porque falta algo")
            #print(f"DEBUG:: username: {username}\n password: {password}\n name: {name}\n dni: {dni}\n email: {email}\n Foto:{str(self.face_code)}")
            evento_screen.ids.error_label.text = "Tiene que rellenar los campos obligatorios y hacerse la foto"
        else:
            evento_screen.ids.error_label.text = ''
            print("DEBUG:: añadimos usuario y su foto")
            self.model.aniadir_usuario(username, name, surname, dni, email)
            self.model.guardar_codificacion_cara_usuario(username, self.face_code)
            self.moveToPreviousPage()

        #TODO hacer boton para ir hacia atras

    def logout(self):
        print('Logged out')
        self.previous_page = None
        self.running_cam = False
        self.capture = None
        self.event_camara = None
        self.face_code = None
        self.id_usuario = 0
        self.foto = False
        self.speech_recognizer = None
        self.event_voz = None
        self.microfono = None
        self.esta_escuchando = False
        if self.event_voz:
            self.event_voz.join()
        self.app.screen_manager.current = 'login'

    '''
    ############################################
    Funciones de reconocimiento facial
    ############################################
    '''

    def playWebcam(self, function):
        print("DEBUG:: creamos la hebra y activamos la camara")
        self.capture = cuia.myVideo(self.my_cam, self.best_cap)
        self.event_camara = Clock.schedule_interval(partial(self.update, function), 1.0 / 30.0)  # Update at 30 FPS
        self.running_cam = True

    def codificarCaraUsuario(self, frame):
        # Cargamos la cara que queremos comparar
        #Codificamos la cara
        fr = cv2.FaceRecognizerSF.create("dnn/face_recognition_sface_2021dec.onnx", "")
        h2, w2, _ = frame.shape
        detector2 = cv2.FaceDetectorYN.create("dnn/face_detection_yunet_2023mar.onnx", config="", input_size=(w2, h2),
                                              score_threshold=0.7)
        ret, cara_usuario = detector2.detect(frame)
        usuario_crop = fr.alignCrop(frame, cara_usuario[0])
        self.face_code = fr.feature(usuario_crop)
        print("DEBUG: La cara docificada del usuario es: "+str(self.face_code))

    def update(self, funcion, dt):

        ret, frame = self.capture.read()
        if not ret: #En caso de que no se retorne nada de la camara abortamos
            print("Error: no se pudo leer el frame de la cámara.")
            return

        camara_screen = self.app.screen_manager.get_screen('camara') #Nos traemos la pantalla de la camara a una variable para poder modificar la imagen y meterle el frame de la camara
        evento_screen = self.app.screen_manager.get_screen('eventInfo') #Obtenemos el id del evento a reservar

        funcion(frame, evento_screen.getIdEvento())

        try:
            # Convertir la imagen de BGR a la textura de Kivy
            buf = cv2.flip(frame, 0).tobytes()
            image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            camara_screen.ids.camera_view.texture = image_texture
        except Exception as e:
            print("Error al poner la textura: ", e)

    def hacerFoto(self, frame, id_evento):
        if self.foto:
            print("Hacemos la foto")
            camara_screen = self.app.screen_manager.get_screen('camara')
            camara_screen.ids.action_button.background_color = 0, 1, 0, 1
            cv2.imwrite('media/cara_usuario.jpg', frame)
            self.codificarCaraUsuario(frame)
            self.foto = False

    def capturar_frame(self):
        self.foto = True

    def reconocimiento_facial(self, frame, id_evento):

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
        #try:
        for cara in caras:
            c = cara.astype(int)
            caracrop = fr.alignCrop(frame, cara)
            codcara = fr.feature(caracrop)

            self.face_code = np.array(self.face_code, dtype=np.float32)
            codcara = np.array(codcara, dtype=np.float32)

            semejanza = fr.match(self.face_code, codcara, cv2.FaceRecognizerSF_FR_COSINE)
            if semejanza > 0.5:
                color = (0, 255, 0)
                self.model.hacer_reserva(self.id_usuario, id_evento)
                self.cerrarCam() #En caso de que se haya reconocido una cara cerramos la ventana, agregamos la reserva y devolvemos al usuario al homeScreen
            else:
                color = (0, 0, 255)

            cv2.rectangle(frame, (c[0], c[1]), (c[0] + c[2], c[1] + c[3]), color, 3)
            cv2.putText(frame, str(round(semejanza, 2)), (c[0], c[1] + 25), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (255, 255, 255), 1, cv2.LINE_AA)
        #except Exception as e:
        #    print("Error al detectar caras en el reconocimiento: ", e)

    def leaveCamera(self, *args):
        self.event_camara.cancel()
        self.capture.release()
        self.foto = None

    def cerrarCam(self):
        self.leaveCamera()
        self.moveToPreviousPage()
        self.event_camara.release()

    '''
    ############################################
    Funciones de reconocimiento de voz
    ############################################
    '''

    def on_toggle_button_state(self, toggle_button):
        # Aquí puedes manejar el cambio de estado del ToggleButton
        state = toggle_button.state
        if state == 'down':
            print("El valor del toggle button es down")
            self.event_voz = threading.Thread(target=self.recognize_speech)
            self.speech_recognizer = sr.Recognizer()
            self.microfono = sr.Microphone()
            self.esta_escuchando = True
            self.event_voz.start()
        else:
            self.esta_escuchando = False
            self.event_voz.join()
            print("El valor del toggle button es normal")

    def recognize_speech(self):
        while self.esta_escuchando:
            with self.microfono as source:
                self.speech_recognizer.adjust_for_ambient_noise(source, duration=0.5)  # listen for 1 second to calibrate the energy threshold for ambient noise levels
                print("Say something!")
                audio = self.speech_recognizer.listen(source)

            try:
                results = self.speech_recognizer.recognize_google(audio, language="es-ES", show_all=True)
                print("DEBUG:: Lo que se ha dicho pero sin procesar: ", results)
                if isinstance(results, dict):
                    if len(results.get('alternative', [])) > 0:
                        most_likely_result = results['alternative'][0]['transcript']
                    else:
                        most_likely_result = "No se reconoció ninguna palabra"
                else:
                    most_likely_result = "Google Speech Recognition no devolvió resultados esperados"
                print("DEBUG:: Que se ha dicho: "+most_likely_result)
                #Clock.schedule_once(lambda dt: self.mover_con_voz(results), 0)

                print(most_likely_result)
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))


    def mover_con_voz(self, palabra):
        if "home" in palabra.lower():
            self.moveToHomePage()
        elif "eventos" in palabra.lower():
            self.moveToEventsPage()
        elif "retroceder" in palabra.lower():
            self.moveToPreviousPage()
        elif "desconectar" in palabra.lower():
            self.logout()
        else:
            print("No se reconoció ningún comando válido")