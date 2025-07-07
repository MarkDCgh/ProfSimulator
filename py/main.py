import os
import tkinter as tk
from csv import reader
from pathlib import Path
import my_sqlite
      
class GUI: 
    # logo, pic, buttons
    def __init__(self, title, size): 
        '''Creates a new GUI window
        Args:
            title (str): title of the window
            size (str): size of the window
            window_type (str): type of premade window (Prof Simulator)
        '''
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(size)

    def NewBar(self, cascades, buttons):  
        """Creates a full bar (menu attached to root)
        Args:
            cascades (list): list of strings, each string is a cascade name
            buttons (list): list of dictionaries and function pointers, each dictionary contains buttons, each one with key(label) and value(command), each function pointer is a command for the cascade, so it won't have buttons
        """
        self.SetupMenu()
    
        i = 0
        for cascade in cascades:
            self.SetupMenu(cascade) 
            if isinstance(buttons[i], dict): 
                for button_name, button_func in buttons[i].items(): # iterates over dictionary of buttons(key(name) + value(command))
                    self.SetupMenuButton(button_name, button_func)
            else: 
                self.SetupMenuButton(cascade, buttons[i]) # assigns the function to the menu
            i += 1        
                    
    def NewLabel(self, attach_to_previous_menu=False, text="", font=('Helvetica', 12), padx=1, pady=1, width=0, height=0):
        """Creates a new label
        Args:
            attach_to_previous_menu (bool): if True, it will be attached to the previous menu, otherwise it will be attached to the root
            text (str): text of the label
            font (tuple): font of the label, name of font and size
            padx (int): padding in x direction
            pady (int): padding in y direction
            width (int): width of the label
            height (int): height of the label
        """
        if attach_to_previous_menu: 
            root = self.bar
        else: 
            root = self.root
            
        self.label = tk.Label(root, text=text, font=font, width=width, height=height)
        self.label.pack(padx=padx, pady=pady)
        
    def NewImage(self, path, padx=1, pady=1, side="top", zoom=1): 
        '''Creates a new image
        Args:
            path (str): path of the image, PADX AND PADY AND WAYS TO SET LABEL PARAMETER 
            padx (int): padding in x direction
            pady (int): padding in y direction
            side (str): side of the image, top, bottom, left, right
            zoom (int): zoom of the image, 1 = no zoom, 2 = double size, -1 = half size
        ''' 
        image = tk.PhotoImage(file=path) 
        
        if zoom > 1: 
            image = image.zoom(zoom, zoom)
        elif zoom <= -1:
            image = image.subsample(-zoom, -zoom)
            
        self.panel = tk.Label(self.root, image=image ) 
        self.panel.image = image # keep a reference to avoid garbage collection
        self.panel.pack(side=side, fill="both", padx=padx, pady=pady) # fills the whole window
        
    def SetupMenu(self, title=""): 
        '''Creates a new menu or cascade
        Args: 
            title (str): title of the menu or cascade, 
                if empty, it will be attached to root
                otherwise, it will be attached to the previous "attached to root" menu
        '''
        if title == "": # bar, menu often made to contain menus
            self.bar = tk.Menu(self.root) 
            self.root.config(menu=self.bar) 
        else: 
            self.menu = tk.Menu(self.bar, tearoff=0) # menu, often contained in a bar
            self.bar.add_cascade(menu=self.menu, label=title)
        
    def SetupMenuButton(self, label, command): 
        '''Creates a new button in the menu
        Args:
            label (str): label of the button
            command (function): function to be executed when the button is clicked
        '''
        self.menu.add_command(label=label, command=command)       
        
    def QuitRoot(self): 
        self.root.quit()
    
    def DestroyRoot(self): 
        self.root.destroy()

class Controller: 
    def __init__(self, gui_title, gui_size='500x500',  database_path='', type='',): 
        '''Creates a new Controller
        Args:
            gui_title (str): title of the GUI
            gui_size (str): size of the GUI
            database_path (str): path to the database
            type (str): type of premade GUI and DB(Prof Simulator)
        '''
        self.gui = GUI(gui_title, gui_size)
        self.db = my_sqlite.SQLite(database_path)
        
        if type == 'Prof Simulator': 
            if os.path.getsize(database_path) == 0: # creates and populate new db only if it's first access
                self.GenerateProfSimulatorDb()
            self.SetupProfSimulatorGui()
            
    def GuiMainloop (self): 
        self.gui.root.mainloop()
        
    def CorrectsDataTypesOfStrTuple(self, old_tuple):
        '''Takes a tuple as a parameter and returns a tuple with corrected data types for each element,\n
        Supports integer, float and bool changes\n
        Strings that start with ' and end with ' are converted to strings, despite the possible data type\n
        Args:
            old_tuple (tuple): tuple to be transformed
        '''
        temp_list = [] #temponary list to use append method
        for value in old_tuple:
            #string case
            if value[0] == "'" and value[-1] == "'":
                temp_list.append(value.replace("'", "")) # removes ' from string
            # boolean case
            elif value == 'True' or value == 'False':
                temp_list.append(bool(value)) 
            # float case
            elif value.find('.') != -1:
                temp_list.append(float(value))
            # integer
            elif value.isnumeric():
                temp_list.append(int(value))
            # other
            else: 
                temp_list.append(value)
                                 
        return tuple(temp_list) # returns tuple from converted list 
    
    # codice orrendo, non so come migliorarlo, l'importante è che funziona
    def FromFilesInFolderToBlobTuple(self, folder_path): 
        '''Given a folder path that contains images, it returns a tuple which each image in blob data type
        Args:   
            folder_path (str): path to the folder
            images (bool): if True, it will only return images, if False, it will return all files in the folder
        Returns:
            tuple: tuple of images in blob data type
        '''
        temp_list = [] #temponary list to use append method
        
        for path in Path(folder_path).iterdir(): # iterates for all files in the folder, gets each file path
                with open(path, 'rb') as file: 
                    temp_list.append(file.read())    
            
        return tuple(temp_list)
    
    def GenerateProfSimulatorDb(self): 
        '''Creates the tables for the Prof Simulator, then populates them, all with premade files (csv and jpeg)\n
        All columns of all tables are populated with csv files\n
        Only image column of images table is populated apart to handle blob files
        '''     
        with open('db\\tables_generation.csv', 'r') as file: # creates tables
            myreader = reader(file)
            for table, columns in myreader:
                self.db.CreateTable(table, columns)
        file.close()
        
        with open('db\\tables_population.csv', 'r') as file: # populates tables with csv
            myreader = reader(file)
            for table, columns, values in myreader: 
                tuple_values = self.CorrectsDataTypesOfStrTuple( tuple( values.split(", "))) 
                self.db.InsertIntoTable(table, columns, tuple_values) 
        file.close()        
                
        tuple_values = self.FromFilesInFolderToBlobTuple('img\\Pics') 
        for i, value in enumerate(tuple_values): # iterates over the images and inserts them into the database 
            self.db.ChangeValuesInTable('images', 'image', (value,), f'image_id={i+1}') 
        
    def SetupProfSimulatorGui(self):
        # Cascades, buttons made to show other buttons
        self._prof_window_cascades = ['Menu', 'Classes'] 
        self._class_window_cascades = ['Menu', 'Students', 'Homework', 'Notes']
        self._student_window_cascades = ['Menu', 'Grades', 'Notes']
        
        # Buttons, the ones opened by each cascade
        self._menu_cascade_buttons = {
            'Profile': self.ProfWindow, 
            'Exit': self.gui.root.quit
        }

        self._classes_cascade_buttons = {}
        classes = self.db.ReadFromTable('classes', 'year, section') # get all classes from database
        for class_ in classes:
            self._classes_cascade_buttons.update({f'{class_[0]}{class_[1]}': lambda: self.ClassWindow(class_)}) # creates a button for each class, with the name of the class as label and the function to open the class window as command
            
        # Windows, each one has it's own bar, so it's own cascades
        self._prof_window_buttons = [
            self._menu_cascade_buttons,
            self._classes_cascade_buttons
        ]
        
        self._class_window_buttons = [
            self._menu_cascade_buttons,
            {'John Smith': self.StudentWindow}, 
            lambda: self.HomeworkWindow(), 
            lambda: self.NotesWindow()
        ]
        
        self._student_window_buttons = [
            self._menu_cascade_buttons,
            lambda: self.GradesWindow(), 
            lambda: self.NotesWindow()
        ]
    
        self.ProfWindow()
        
    def ProfWindow(self, prof_id = 1):
        self.gui.NewBar(self._prof_window_cascades, self._prof_window_buttons) 
        # self.gui.NewImage('img\\logo.png', 0, 0, "right", -5) # logo of the app
        # self.gui.NewImage('img\\Pics\\4.jpg', 0, 0, "left", 5) does not support jpg format

    def ClassWindow(self, class_): 
        self.gui.NewBar(self._class_window_cascades, self._class_window_buttons) 
    
    def StudentWindow(self):
        pass
    
    def HomeworkWindow(self):
        pass
    
    def NotesWindow(self):
        pass
    
    def GradesWindow(self):
        pass
        
    # take input from gui class
    # give output to gui class
    # take input from database class
    # give output to database class

def main():
    controller = Controller('PROF SIMULATOR', '500x500', 'db\\file.db', 'Prof Simulator') 
    controller.GuiMainloop()
    
if __name__ == '__main__': 
    main()



