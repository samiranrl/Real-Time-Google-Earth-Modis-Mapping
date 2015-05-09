from kivy.app import App
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from functools import partial
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.properties import ListProperty
import os
from kivy.lang import Builder
import sys
import subprocess


from kivy.logger import Logger


def f(val):
    os.startfile("gujaratplot.py")

def g(val):
    os.startfile("globalplot.py")
    
    
def h(val):
    os.startfile("highresimg.py")
    


class CustomBtn(Widget):

     pressed = ListProperty([0, 0])

     def on_touch_down(self, touch):
         if self.collide_point(*touch.pos):
             self.pressed = touch.pos
             # we consumed the touch. return False here to propagate
             # the touch further to the children.
             return True
         return super(CustomBtn, self).on_touch_down(touch)

     def on_pressed(self, instance, pos):
         v=subprocess.check_output("uname -a",shell=True)
         result=Popup(title="RESULT",content=Label(text="kernel is\n" + v))
         result.open()


Builder.load_string('''
<FloatLayout>
    canvas.before:
        BorderImage:
            # BorderImage behaves like the CSS BorderImage
            border: 10, 10, 10, 10
            source: 'mm.png'
            
            pos: self.pos
            size: self.size

<Button>:
    size_hint: None, None
    size: 300,50




            ''')




class ForestFireDetect(App):
    icon = 'flame-icon.png'
    

    
    
    
    def create_clock(self, widget, touch, *args):
        callback = partial(self.menu, touch)
        Clock.schedule_once(callback, 2)
        touch.ud['event'] = callback

    def delete_clock(self, widget, touch, *args):
        Clock.unschedule(touch.ud['event'])

    def menu(self, touch, *args):
        menu = BoxLayout(
                size_hint=(None, None),
                orientation='vertical',
                center=touch.pos)
        
        Button1 = Button(text='C: Forest Fire Analysis of Gujarat',size=(2,2))
        Button1.bind(on_release=f)
        
        Button2 = Button(text='B: Global Fire Plot')
        Button2.bind(on_release=g)

        Button3 = Button(text='A: High Res Satellite Image')
        Button3.bind(on_release=h)  
        
        close = Button(text='Close')
        close.bind(on_release=partial(self.close_menu, menu))
        
        menu.add_widget(Button3)
        menu.add_widget(Button2)
        menu.add_widget(Button1)
        menu.add_widget(close)
        
        self.root.add_widget(menu)
        
        

    def close_menu(self, widget, *args):
        self.root.remove_widget(widget)

    def build(self):
        self.root = FloatLayout()
        self.root.bind(
            on_touch_down=self.create_clock,
            on_touch_up=self.delete_clock)
        


if __name__ == '__main__':
    ForestFireDetect().run()
