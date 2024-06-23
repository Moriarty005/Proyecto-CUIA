# main.py
from kivy.lang import Builder
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp

from modelo.model import UserModel
from controlador.controller import Controller

class LoginScreen(Screen):
    pass

class RegisterScreen(Screen):
    pass

class HomeScreen(Screen):
    pass

class EventsScreen(Screen):

    #TODO numerar los eventos

    def cargar_data_eventos(self, data):
        print(str(data))
        self.ids.eventos.data = [{"id_evento": str(item[0]), "info": "Evento: "+str(item[1])+"\n"+"Fecha del evento: "+str(item[4])} for item in data]

class EventInfoScreen(Screen):

    id_evento = StringProperty('')

    def setIdEvento(self, id):
        self.id_evento = str(id)

    def getIdEvento(self):
        return self.id_evento

class CamaraScreen(Screen):

    show_button = BooleanProperty(False)

    def __init__(self, controlador, **kwargs):
        super(CamaraScreen, self).__init__(**kwargs)
        self.controlador = controlador

    def hacer_foto(self):
        print("DEBUG:: entramos al metodo de la clase en el main")
        self.controlador.capturar_frame()


class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = UserModel()
        self.controller = Controller(self.model, self)

    def build(self):
        self.theme_cls.primary_palette = 'Blue'
        self.theme_cls.theme_style = 'Dark'
        self.screen_manager = ScreenManager()
        self.screen_manager.add_widget(LoginScreen(name='login'))
        self.screen_manager.add_widget(RegisterScreen(name='register'))
        self.screen_manager.add_widget(HomeScreen(name='home'))
        self.screen_manager.add_widget(EventsScreen(name='events'))
        self.screen_manager.add_widget(EventInfoScreen(name='eventInfo'))
        self.screen_manager.add_widget(CamaraScreen(self.controller, name='camara'))

        return self.screen_manager

if __name__ == '__main__':
    Builder.load_file('vista/loginScreen.kv')
    Builder.load_file('vista/registerScreen.kv')
    Builder.load_file('vista/homeScreen.kv')
    Builder.load_file('vista/eventosScreen.kv')
    Builder.load_file('vista/infoEventoScreen.kv')
    Builder.load_file('vista/camara.kv')

    MainApp().run()
