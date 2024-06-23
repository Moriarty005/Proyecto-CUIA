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

    """
    Constructor de la clase controlador
    
    :param model, Modelo con el que interactuar (base de datos)
    :param app, Vista co la que interactuar (Kivy)
    """
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

    """
    Método que mueve al usuario a la pantalla de listado de eventos
    """
    def moveToEventsPage(self):
        print('Nos movemos a la pagina de eventos')
        events_screen = self.app.screen_manager.get_screen('events')
        events_screen.cargar_data_eventos(self.model.traer_eventos())
        self.app.screen_manager.current = 'events'

    """
    Método que mueve al usuario a la pantalla de registro de usuario
    """
    def moveToRegisterPage(self):
        print('Nos movemos a la pagina de regsitro')
        self.previous_page = 'login'
        self.app.screen_manager.current = 'register'

    """
    Método que mueve al usuario a la pantalla de Home
    """
    def moveToHomePage(self):
        print('Nos movemos a la pagina de home')
        self.previous_page = 'home'
        self.app.screen_manager.current = 'home'

    """
    Método que mueve al usuario a la pantalla anterior
    """
    def moveToPreviousPage(self):
        print('Nos movemos a la pagina anterior')
        if(self.previous_page != None):
            self.app.screen_manager.current = self.previous_page

    """
    Método que mueve al usuario a la pantalla de información ampliada de un evento concreto
    """
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

    """
    Método que mueve al usuario a la pantalla de reconocimiento facial para la reserva de un evento
    """
    def moveToFaceRecognitionPage(self):
        print('Nos movemos a la pagina de la camara p[ara hacer reconocimiento facial')
        self.previous_page = 'eventInfo'
        camara_screen = self.app.screen_manager.get_screen('camara')
        camara_screen.show_button = True
        camara_screen.on_enter = lambda: self.playWebcam(self.reconocimiento_facial)
        self.app.screen_manager.current = 'camara'

    """
    Método que mueve al usuario a la pantalla de foto para codificar su cara en el registro
    """
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

    """
    Método que comprueba las credenciales del usuario y lo logea en el sistema moviéndolo a la pantalla Home
    
    :param username, nombre de usuario
    :param password, contraseña del usuario
    """
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


    """
    Método que registra un nuevo usuario en el sistema
    
    :param username, nomre de usuario
    :param password, contraseña del usuario (No se utiliza)
    :param name, nombre real del usuario
    :param surname, apellidos del usuario
    :param dni, DNI del usuario
    :param email, email del usuario
    """
    #TODO hashear la contraseña y meterla en la base de datos
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

    """
    Método de cierra la sesión del usuario devolviéndolo a la pantalla de login
    """
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

    """
    Método que crea el evento que abre la cámara
    
    :param function, funcion que le pasamos al evento, puede ser la función de reconocimiento facial o la de tomar la foto
    """
    def playWebcam(self, function):
        print("DEBUG:: creamos la hebra y activamos la camara")
        self.capture = cuia.myVideo(self.my_cam, self.best_cap)
        self.event_camara = Clock.schedule_interval(partial(self.update, function), 1.0 / 30.0)  # Update at 30 FPS
        self.running_cam = True

    """
    Método que dada una foto codifica la cara que haya en ella y la guarda en la variable correspondiente
    """
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

    """
    Método que actualiza en la pantalla de la cámara de la aplicación los frames que trae la cámara del dispositivo
    
    :param funcion, funcion que ejecutará cierta operación sobre un frame
    """
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

    """
    Método que mediante un booleano comprueba si se ha hecho una foto para el registro de usuario, guardando la foto y utiliazndo el método codificarCaraUsuario para
    mantener la cara codificada en el sistema
    """
    def hacerFoto(self, frame, id_evento):
        if self.foto:
            print("Hacemos la foto")
            camara_screen = self.app.screen_manager.get_screen('camara')
            camara_screen.ids.action_button.background_color = 0, 1, 0, 1
            cv2.imwrite('media/cara_usuario.jpg', frame)
            self.codificarCaraUsuario(frame)
            self.foto = False

    """
    Pone a true el booleano que controla la captura de frame cuando se hace una foto
    """
    def capturar_frame(self):
        self.foto = True

    """
    Método que mediante OpenCV, FaceDetectorYN y FaceRecognizerSF detecta las cara que haya en un frame dado
    
    :param frame, imagen dada sobre la que aplicar el reconocimiento facial
    """
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

    """
    Método que libera todos los recursos de la cámara cuando deja de utilizarse
    """
    def leaveCamera(self, *args):
        self.event_camara.cancel()
        self.capture.release()
        self.foto = None

    """
    Metodo que cierra la cámara y que mueve al usuario a la pantalla anterior que se estuviese utilizando
    """
    def cerrarCam(self):
        self.leaveCamera()
        self.moveToPreviousPage()
        self.event_camara.release()

    '''
    ############################################
    Funciones de reconocimiento de voz
    ############################################
    '''

    """
    Método que comprueba el estado de la funcionalidad de reconocimiento de voz mediante el estado del botón de la interfaz
    
    :param toggle_button, boton de la interfaz del que comprobar el estado
    """
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

    """
    Método que, mientras esté activado el reconocimiento de voz, reconoce lo que dice el usuario y lo procesa para saber a qué pantalla moverse
    """
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


    """
    Método que dada una palabra detectada mediante el reconocimiento de voz mueve al usuario a cierta pantalla
    """
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