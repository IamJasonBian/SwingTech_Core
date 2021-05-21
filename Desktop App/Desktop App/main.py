from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label


import pandas as pd

from Usb_Client import transfer


#Have the user input in ergonomic data
class LoginWindow(Screen):

    current = ""
    

    def loginBtn(self):
        global height_input
        global strength_input
        global repo_input
        
        height_input = self.ids.height_input.text
        strength_input = self.ids.strength_input.text
        repo_input = self.ids.repo_input.text
        
        sm.current = "connect"

#Main connection window
class MainWindow(Screen):
    current = ""          

    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)  
        #Hide extract data on enter
        self.ids.Analyze.opacity = 0
        self.ids.Analyze.disabled = True
        

    def logOut(self):
        sm.current = "main"

    def on_enter(self, *args):

         pass 
    
    def ConnectBtn(self):
        
        status = self.ids.Sync
        
        status.text = "Searching for Raspberry pi, please wait ..."
        
        
        status.text = "Sensor is connected!"
            
        #Show extract data
        self.ids.Analyze.opacity = 1
        self.ids.Analyze.disabled = False
            
            
        #Connection Disabled until sensor is found:
        #print("Testing Connection")
        #if(transfer(repo_input) == "Connected"):
            #status.text = "Sensor is connected!"
            #Show extract data
            #self.ids.Analyze.opacity = 1
            #self.ids.Analyze.disabled = False
        #else:
            #status.text = "Connection failed, check usb connection"

    
    def AnalyzeBtn(self):
        
        status = self.ids.Sync
        
        status.text = "Loading Machine learning libraries, please wait ..."
        from ML_Plot import predict_type
        
        status.text = "Running Classifiers, please wait ..."
        
        cx = pd.read_csv(repo_input + '\\Data.csv')
        
        print("Running Predictor")
        
        swings_df = predict_type(cx)
        status.text = "Saving Classifiers, please wait ..."
        swings_df.to_csv('selected.csv')
            
        status.text = "Classifiers Saved"
        sm.current = "analyze"

        
#list of all swings to possiblely analyze
class AnalyzeWindow(Screen):
    current=""
    def __init__(self, **kwargs):
        super(AnalyzeWindow, self).__init__(**kwargs)
        
    def on_enter(self, *args):

        self.allSwingsList()
        #self.ids.coinList.data = [{'value': str(i)} for i in range (20)]
        pass

    def allSwingsList(self, page=None):
        #Generate ML list:
        global swings_df
        swings_df = pd.read_csv('selected.csv')
                
        allCoins = []
        Type = []
        MaxSpeed = []
        MaxAccel = []
        SwingAngle = []
        
        swings_df = swings_df.groupby('ID').agg({'ID': 'max', 'type_str': 'max', 
                                     'Max_Speed': 'max', 'accelerometer': 'max', 'Max_Angle': 'max'})
    
        swings_df = swings_df.rename(columns={"Index": "ID", 
                                              "type_str": "stroke_type", "Max_Speed": 
                                                  "Max_Speed", "accelerometer": "Max_Accel"})
        
        allCoins = swings_df['ID'].tolist()
        Type = swings_df['stroke_type'].tolist()
        MaxSpeed = round(swings_df['Max_Speed']*2.236 ,3).tolist()
        MaxAccel = round(swings_df['Max_Accel'] ,3).tolist()
        SwingAngle = round(swings_df['Max_Angle'], 3).tolist()
        
        allCoins = [str(i) for i in allCoins]
        Type = [str(i) for i in Type]
        MaxSpeed = [str(i) for i in MaxSpeed]
        MaxAccel = [str(i) for i in MaxAccel]
        SwingAngle = [str(i) for i in SwingAngle]
                
        total_2 = [{"value": [v,w,x,y,z]} for v,w,x,y,z in zip(allCoins, Type, MaxSpeed, MaxAccel, SwingAngle)]
        
        
        print(allCoins)
        
        self.ids.coinList.data = total_2
        
        
        global data
        data =  self.ids.coinList.data
        
        pass
    def searchSwing(self, searchText=None):
        pass
    def BackBtn(self):
        sm.current = "connect"
        

    
class GraphWindow(Screen):
    img_src = 'FourInOne.png'
    def __init__(self, **kwargs):
        super(GraphWindow, self).__init__(**kwargs)
        
        #img_src = self.ids.Image.source
        #img_src = 'FourInOne.png'
        
    def AnalyzeBtn(self):
        
        self.ids.Image.source = ''
        
        sm.current = "analyze"
    def on_enter(self, *args):
        
        self.ids.Image.reload()
        
        pass 


class WindowManager(ScreenManager):
   
    def RunGraph(self, instance):
        
        from ML_Plot import plot_four
        x = instance
        print(x)
        swings_df = pd.read_csv('selected.csv')
        single_swing_df = swings_df[swings_df['ID'] == int(x)]
        plot_four(single_swing_df)
        
        sm.current = "graph"
    
    pass


def invalidLogin():
    pop = Popup(title='Invalid User Parameters',
                  content=Label(text='Invalid Height, age, or repo location.'),
                  size_hint=(None, None), size=(400, 400))
    pop.open()


kv = Builder.load_file("my.kv")
sm = WindowManager()


screens = [LoginWindow(name="main"), MainWindow(name="connect"), 
           AnalyzeWindow(name="analyze"), GraphWindow(name="graph")]
for screen in screens:
    sm.add_widget(screen)

sm.current = "main"

class MyMainApp(App):
    
    def build(self):
        return sm


if __name__ == "__main__":  
    MyMainApp().run()
