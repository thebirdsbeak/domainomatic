# ~ To DO
#   ~ Open and revisit cases (i.e. load status)
#   ~ Add case metadata (e.g. closed...) use JSON?

# ~ Import pyqt5 modules
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QMessageBox

# ~ Import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# ~ Import external modules
import sys
import os
import csv
import webbrowser
import json
from time import sleep

# ~ Import internal modules
import webview
from dataload import read_csv, random_domain


class MainDialog(QtWidgets.QMainWindow, webview.Ui_MainWindow):
    
    ### Setup ###
    def __init__(self, parent=None):
        '''Initialises gui and sets button actions'''
        super(MainDialog, self).__init__(parent)
        self.setupUi(self)
        cwd = os.getcwd()

        # Default disabled
        self.newButton.setEnabled(False)
        self.actionNew_Domain.setEnabled(False)
        self.watchButton.setEnabled(False)
        self.actionWatch.setEnabled(False)
        self.emailButton.setEnabled(False)
        self.actionEmail.setEnabled(False)
        self.letterButton.setEnabled(False)
        self.actionLetter.setEnabled(False)
        self.udrpButton.setEnabled(False)
        self.actionUDRP.setEnabled(False)
        self.saveButton.setEnabled(False)
        self.actionSave.setEnabled(False)
        self.servicesCombo.setEnabled(False)
        self.marksCombo.setEnabled(False)
        self.priorityCombo.setEnabled(False)
        self.jurisdictionCombo.setEnabled(False)

        # Handy handy variables
        self.current_domain = 'file:///{}/index.html'.format(cwd)
        self.loaded_data = ''
        # Toolbar actions
        self.actionLoad_data.triggered.connect(self.load_data)
        self.actionOpen_case.triggered.connect(self.open_domain_case)
        # Button actions
        self.screenshotButton.clicked.connect(self.screenshot)
        self.loadButton.clicked.connect(self.load_data)
        self.openButton.clicked.connect(self.open_domain_case)
        self.saveButton.clicked.connect(self.save_domain)
        self.newButton.clicked.connect(self.new_domain)
    
        # Load site
        self.webView.load(QUrl(self.current_domain))
    
    
    def load_data(self):
        '''Main function handler'''
        self.loaded_data = self.select_source()
        self.newButton.setEnabled(True)
        self.actionNew_Domain.setEnabled(True)
        if self.loaded_data != "error":
            self.displayLabel.setText(self.loaded_data)
            domain_list = read_csv(self.loaded_data)
            randomised = random_domain(domain_list)
            self.load_domain(randomised)
                

    def select_source(self):
        '''Choose from available csvs'''
        target_files = []
        filename = QtWidgets.QFileDialog.getOpenFileName(self, "Choose source", "./assets")
        selected_file = filename[0]
        if selected_file != "":
            return selected_file    
        else:
            return "File opening aborted"
        
        
    def select_from_file(self):
        '''Select an individual domain'''
        domain_list = []
        with open(self.loaded_data, "r") as open_file:
            reader = csv.reader(open_file)
            for line in reader:
                domain_list.append(line)
            for i in domain_list:
                self.textBrowser.append(str(i[0]))
  
        
    def screenshot(self):
        '''Takes and saves screenshot'''
        driver = webdriver.Firefox()
        driver.get(self.current_domain)
        domain = self.current_domain.replace("http://", "").replace("https://", "")
        image_name = domain + ".png"
        driver.save_screenshot('./cases/'+domain+'/'+image_name)
        webbrowser.open('./cases/'+domain+'/'+image_name) # put to bottom of function if default browser is firefox
        driver.close() # put to bottom of function if default browser not firefox
        
    
    def save_domain(self):
        '''Makes a folder in cases for this domain'''
        current_domain = self.current_domain.replace("https://", "").replace("http://", "")
        for casefile in os.listdir('./cases/'):
            if casefile == current_domain:
                self.textBrowser.setText("")
                self.textBrowser.append("Case exists... overwritten.")
                self.domain_config(casefile, True)
        if current_domain not in os.listdir('./cases/'):
            self.domain_config(current_domain, False)
            

    def domain_config(self, domain_file, newfile):
        '''Generates / updates config file'''
        config_file = domain_file.replace(".", "_") + '.json'
        self.textBrowser.setText("")
        folder_name = './cases/{}'.format(domain_file)
        self.textBrowser.setText("")
        if newfile == False:
            os.mkdir(folder_name)
            self.textBrowser.append("Case created:")
        else:
            self.textBrowser.append("Case overwritten:")
        clean_file = domain_file.replace(".", "_")
        file_name = "{}/{}.json".format(folder_name, clean_file)
        self.json_io(file_name, domain_file)

    def json_io(self, file_name, domain_file):
        '''Saves/overwrites JSON file'''
        self.textBrowser.append(file_name)
        template_data = {"domain": domain_file, "inf_domain": False, "inf_content": False, "owned": False, "inactive": False, "services": False, "marks": False, "priority": False, "jurisdiction": False}

        # Checkboxes
        if self.domainCheck.isChecked() == True:
            template_data["inf_domain"] = True
        if self.contentCheck.isChecked() == True:
            template_data["inf_content"] = True        
        if self.ownedCheck.isChecked() == True:
            template_data["owned"] = True
        if self.inactiveCheck.isChecked() == True:
            template_data["inactive"] = True

        # Dropdowns
        template_data["services"] = self.servicesCombo.currentText()
        template_data["marks"] = self.marksCombo.currentText()
        template_data["priority"] = self.priorityCombo.currentText()
        template_data["jurisdiction"] = self.jurisdictionCombo.currentText()


        self.textBrowser.append(str(template_data))
        template_data = json.dumps(template_data)
        with open(file_name, "w") as updated_config:
            updated_config.write(str(template_data))

    def load_json(self, domain):
        for casefile in os.listdir('./cases/'):
            if casefile == domain:
                json_name = domain.replace(".", "_") + ".json"
                json_info = './cases/{}/{}'.format(domain, json_name)
                try:
                    with open(json_info, "r") as json_data:
                        j = json.load(json_data)
                        return(j)
                except Exception as e:
                    print(str(e))

    def open_domain_case(self):
        '''Open existing case - and loads it'''
        filename = QtWidgets.QFileDialog.getOpenFileName(self, "Choose source", "./cases")
        selected_domain = filename[0].split('/')[-1]
        if selected_domain.endswith("json"):
            selected_domain = selected_domain.replace(".json", "").replace("_", ".")
            self.load_domain(selected_domain)


#        selected_domain = str(selected_domain[-1])
#        self.load_domain(selected_domain)

    
    def new_domain(self):
        '''New random domain from selected source file'''
        if self.loaded_data:
            domain_list = []
            with open(self.loaded_data, "r") as open_file:
                reader = csv.reader(open_file)
                for line in reader:
                    domain_list.append(line)
            randomised = random_domain(domain_list)
            self.load_domain(randomised)
        else:
            self.textBrowser.setText("")
            self.textBrowser.append("Can't load new domain, is source selected?")


    def load_domain(self, domain):
        '''Loads in given domain'''
        try:
            randomain = 'http://'+ domain
            self.webView.load(QUrl(randomain))
        except Exception as e:
            print(str(e))
            print("Data source error")
            try:
                randomain = 'http://'+randomised
                self.webView.load(QUrl(randomain))
            except Exception as e:
                print(str(e))
                print("Data source error")
        self.current_domain = randomain
        self.textBrowser.setText(randomain)
        self.watchButton.setEnabled(True)
        self.actionWatch.setEnabled(True)
        self.emailButton.setEnabled(True)
        self.actionEmail.setEnabled(True)
        self.letterButton.setEnabled(True)
        self.actionLetter.setEnabled(True)
        self.udrpButton.setEnabled(True)
        self.actionUDRP.setEnabled(True)
        self.saveButton.setEnabled(True)
        self.actionSave.setEnabled(True)
        self.servicesCombo.setEnabled(True)
        self.marksCombo.setEnabled(True)
        self.priorityCombo.setEnabled(True)
        self.jurisdictionCombo.setEnabled(True)


        domain = self.current_domain.replace("http://", "").replace("https://", "")
        json_file = domain.replace(".", "_") + ".json"
        if json_file in os.listdir("./cases/{}".format(domain)):
            json_settings = self.load_json(domain)
        else:
            json_settings = {"domain": domain, "inf_domain": False, "inf_content": False, "owned": False, "inactive": False, "services": "Services", "marks": "Marks", "priority": "Priority", "jurisdiction": "Jurisdiction"}

        self.display_json(json_settings)


    def display_json(self, json_settings):

        # Checkboxes
        if json_settings["inf_domain"] == True:
            self.domainCheck.setChecked(True)
        else:
            self.domainCheck.setChecked(False)
        if json_settings["inf_content"] == True:
            self.contentCheck.setChecked(True)
        else:
            self.contentCheck.setChecked(False)
        if json_settings["owned"] == True:
            self.ownedCheck.setChecked(True)
        else:
            self.ownedCheck.setChecked(False)
        if json_settings["inactive"] == True:
            self.inactiveCheck.setChecked(True)
        else:
            self.inactiveCheck.setChecked(False)

        # Dropdowns

        self.servicesCombo.setCurrentText(json_settings["services"])
        self.marksCombo.setCurrentText(json_settings["marks"])
        self.priorityCombo.setCurrentText(json_settings["priority"])
        self.jurisdictionCombo.setCurrentText(json_settings["jurisdiction"])

# ~ Launch !!!
app = QtWidgets.QApplication(sys.argv)
form = MainDialog()
form.show()
app.exec_()
