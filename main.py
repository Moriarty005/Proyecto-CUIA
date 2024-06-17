# main.py
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp

from modelo.model import UserModel
from controlador.controller import Controller

class CamaraScreen(Screen):
    pass

class LoginScreen(Screen):
    pass

class HomeScreen(Screen):
    pass

class EventsScreen(Screen):

    def cargar_data_eventos(self, data):
        print(str(data))
        self.ids.eventos.data = [{"id_evento": str(item[0]), "first_label_text": str(item[1]), "second_label_text": str(item[4])} for item in data]

class EventInfoScreen(Screen):
    pass

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
        self.screen_manager.add_widget(HomeScreen(name='home'))
        self.screen_manager.add_widget(EventsScreen(name='events'))
        self.screen_manager.add_widget(EventInfoScreen(name='eventInfo'))
        self.screen_manager.add_widget(CamaraScreen(name='camara'))
        return self.screen_manager

if __name__ == '__main__':
    Builder.load_file('vista/loginScreen.kv')
    Builder.load_file('vista/homeScreen.kv')
    Builder.load_file('vista/eventosScreen.kv')
    Builder.load_file('vista/infoEventoScreen.kv')
    Builder.load_file('vista/camara.kv')
    MainApp().run()
