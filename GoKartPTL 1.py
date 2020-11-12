from tkinter import *
from time import sleep
import requests
import json
import urllib.parse
from pprint import pprint
import threading


class MyFirstGUI:
    def __init__(self, master):
        self.master = master
        master.title("Gokart Labbet PTL")

        lbl1 = Label(master, text = "1. Type in the sensors MacIDs in Sensorer.txt, seperate with commas(,) and save\n(The MacIDs are written on the sensors and start with 8389)", justify = LEFT, height = "2")
        lbl1.grid(column = 0 , row = 0 , sticky = "w")

        lbl2 = Label(master, text = "2. Wait for all yellow lamps on the sensors to stop blinking \nStart the program by pressing 'Run Program'", justify = LEFT ,height = "2")
        lbl2.grid(column = 0 , row = 1 , sticky = "w")

        lbl3 = Label(master, text = "3. If you run out of material press 'Pause Program' and refill the material", height = "2")
        lbl3.grid(column = 0 , row = 2 , sticky = "w")

        lbl4 = Label(master, text = "4. To start the program again press 'Resume Program'", height = "2")
        lbl4.grid(column = 0 , row = 3 , sticky = "w")

        lbl5 = Label(master, text = "5. To start from a different sensor press 'Skip Sensor' to jump to the next", justify = LEFT, height = "2")
        lbl5.grid(column = 0 , row = 4 , sticky = "w")

        lbl6 = Label(master, text = "6. If a change has to be made to the picking order press 'Stop Program'\nand repeat from step 1", justify = LEFT, height = "2")
        lbl6.grid(column = 0 , row = 5 , sticky = "w")

        self.btnrun = Button(master, text="Run Program", command=self.runprg, bg = "lime green", width = "15", height = "2")
        self.btnrun.grid(column = 1 , row = 0)

        self.btnunpaus = Button(master, text="Resume Program", command=self.resumeprg, bg = "lime green", width = "15", height = "2")
        self.btnunpaus.grid(column = 1 , row = 1)

        self.btnpaus = Button(master, text="Pause Program", command=self.pausprg, bg = "brown1", width = "15", height = "2")
        self.btnpaus.grid(column = 1 , row = 2)

        self.btnstop = Button(master, text="Stop Program", command=self.stopprg, bg = "brown1", width = "15", height = "2")
        self.btnstop.grid(column = 1 , row = 3)

        self.btnskip = Button(master, text="Skip Sensor", command=self.skipsnsr, width = "15", height = "2")
        self.btnskip.grid(column = 1 , row = 4)

        self.btnclose = Button(master, text="Close", command=self.close, bg = "red", width = "15", height = "2")
        self.btnclose.grid(column = 1 , row = 6)

        lbl7 = Label(master, text = "Created By HIS Student Axel Engblom")
        lbl7.grid(column = 0 , columnspan = 2, row = 7)
        "Varibler för knappar"
        self.runprogram = 0
        self.skip = 0
        self.back = 0
        self.pausprog = 0
        self.lamps = []
        #Adresser dit datan skall skickas
        self.main_api = "http://localhost:8080/rest/binar/"
        self.call_api = "get/modules"
        self.post_api = "io/put/"
        self.call_api_spec = "get/module/"
        self.header = {"Content-type" : "application/json"}
        #Datan som skall skickas
        self.payloadon = {'Idx' : 0, 'Data' : 1, 'Params':[{"Color": 2}]}
        self.payloadoff = {'Idx' : 0, 'Data' : 0, 'Params':[{"Color": 0}]}
        self.payloadfault = {'Idx' : 0, 'Data' : 1, 'Params':[{"Color": 1}]}
        self.payloadspec = {'Type' : 'Input', 'Idx' : 0}
        self.payloadspeco = { 'Type' : 'Output', 'Idx' : 0}
        self.current_lamp = 0
        self.last_lamp = 0


    def runprg(self):
        if self.runprogram == 0:
            self.sensorfile = open("Sensorer.txt", "r")
            self.sensors = self.sensorfile.read()
            self.lamps = self.sensors.split(",")
            self.sensorfile.close()
            self.pausprog = 0
            self.runprogram = 1
            self.thread = threading.Thread(target=self.program)
            self.thread.start()

    def pausprg(self):
        if self.pausprog == 0:
            self.pausprog = 1

    def resumeprg(self):
        if self.pausprog == 1:
            self.pausprog = 0


    def skipsnsr(self):
        if self.runprogram == 1:
            self.skip = 1
            sleep (0.2)
            self.skip = 0

    def stopprg(self):
        if self.runprogram == 1:
            self.runprogram = 0
            self.current_lamp = 0
            self.turn_off_lampS(self.lamps)

    def close(self):
        self.runprogram = 0
        self.turn_off_lampS(self.lamps)
        self.master.quit()

    def is_sensor_active(self,macid):#avläser vilken sensor som är aktiv
            spec_data = requests.post(self.main_api + self.call_api_spec + macid, json=self.payloadspec, headers=self.header)
            spec_datajson = spec_data.json()
            data_read = spec_datajson['Input']['Data']

            return data_read == 1

    def turn_on_lamp(self, macid):#tänder lampa
        requests.post(self.main_api + self.post_api + macid, json=self.payloadon, headers=self.header)

    def turn_off_lamp(self, macid):#släcker lampa
        requests.post(self.main_api + self.post_api + macid, json=self.payloadoff, headers=self.header)

    def turn_off_lampS(self, macids):#släcker lamporna
        for macid in macids:
            requests.post(self.main_api + self.post_api + macid, json=self.payloadoff, headers=self.header)

    def turn_on_all_red(self, macids):#tänder alla röda lampor
        for macid in macids:
            requests.post(self.main_api + self.post_api + macid, json=self.payloadfault, headers=self.header)

    def any_incorrect_sensor_active(self, lamps, current_lamp, last_lamp):#avläser om inkorrekt sensor är aktiv
        for i in range(len(self.lamps)):
            if i != self.current_lamp and self.is_sensor_active(self.lamps[i]):
                return True
        return False

    def program(self):

        for lamp in self.lamps:
            self.turn_off_lamp(lamp)

            self.turn_on_lamp(self.lamps[self.current_lamp])
        while self.runprogram == 1:
            if self.is_sensor_active(self.lamps[self.current_lamp]) or self.skip == 1:
                self.turn_off_lamp(self.lamps[self.current_lamp])
                self.last_lamp = self.current_lamp #används inte
                self.current_lamp +=1
                if self.current_lamp == len(self.lamps):
                    self.current_lamp = 0
                self.turn_on_lamp(self.lamps[self.current_lamp])
                sleep (1)
            while self.any_incorrect_sensor_active(self.lamps, self.current_lamp, self.last_lamp):
                self.turn_on_all_red(self.lamps)
                sleep (1)
                self.turn_off_lampS(self.lamps)
                self.turn_on_lamp(self.lamps[self.current_lamp])
            while self.pausprog == 1:
                pass
            else:
                sleep (0.1)

root = Tk()
my_gui = MyFirstGUI(root)
root.protocol("WM_DELETE_WINDOW", my_gui.close)
root.resizable(False, False)
root.mainloop()
