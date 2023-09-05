from flask import Flask, request, jsonify
from flask_cors import CORS
from multiprocessing import Event
from flask import send_from_directory
import os
import datetime
import random

class RestAPI():

    __app : Flask = None

    def __init__(self,scheduler = None):
        # self.__app = Flask(__name__, static_folder='AutoHaus_UserInterface')
        self.__app = Flask(__name__)
        
        CORS(self.__app)

        self.schedulerState = True

        self.__userInterfacePath = "AutoHaus_UserInterface/"

        print(f"static folder path: {self.__app.static_folder}")
    
        static_files = [f for f in os.listdir(self.__app.static_folder) if os.path.isfile(os.path.join(self.__app.static_folder, f))]
        print(static_files)


        self.pins = []
        pintCount = 5
        #add pins in style {"dataPin1":X,"dataPin2":X,"mode":"I2C","pinID":X}
        for i in range(pintCount):
            self.pins.insert(0,{"dataPin1":i,"dataPin2":i,"mode":"I2C","pinID":i})

        self.sensors = []
        sensorCount = 5
        #add sensors in style {"active":true,"class":"DummyClass","collection":"DummyCollectionX","intervall":1,"name":"DummySensorX","pinID":1}
        for i in range(sensorCount):
            self.sensors.insert(0,{"active":True,"class":"DummyClass","collection":"DummyCollection"+str(i),"intervall":1,"name":"DummySensor"+str(i),"pinID":i})

      
        self.dummySensorData = []
        self.dummyActorrData = []
        dummyDataCount = 10000
        self.dummyValue1 = 10.0
        self.dummyValue2 = 5.0
        self.startDateTime = datetime.datetime.now()
        #add dummyData in style {"data":{"dummy":random},"timestamp":startDateTime} after that increment startDateTime by 10 seconds
        for i in range(dummyDataCount):
            change1 = random.uniform(-0.5,0.5)
            self.dummyValue1 = self.dummyValue1 + change1

            change2 = random.uniform(-0.3,0.3)
            self.dummyValue2 = self.dummyValue2 + change2

            self.dummySensorData.insert(0,{"data":{"dummy1":self.dummyValue1,"dummy2":self.dummyValue2},"time":self.startDateTime})

            randomState = random.randint(0,1)
            if(randomState == 0):
                randomState = False
            else:
                randomState = True

            self.dummyActorrData.insert(0,{"data":{"state":randomState},"time":self.startDateTime})

            self.startDateTime += datetime.timedelta(seconds=10)



        self.actuators = []
        actuatorCount = 5
        #add actuators in style {"active":true,"collection":"DummyActuator","config":{},"initialState":false,"name":"DummyActuatorX","type":"Dummy_Actuator"}
        for i in range(actuatorCount):
            self.actuators.insert(0,{"active":True,"collection":"DummyActuator"+str(i),"config":{},"initialState":False,"name":"DummyActuator"+str(i),"type":"Dummy_Actuator"})
        

        self.logics = []
        logicCount = 2
        #add logics in style {"active":true,"controller":{"config":{"invert":false,"threshold":0},"controller":"BinaryController"},"inputs":[{"input":"inX","parameter":"data","sensor":"InputSensorX"}],"name":"DummyLogikX","outputs":[{"actuator":"DummyActuatorX"}]}
        for i in range(logicCount):
            self.logics.insert(0,{"active":True,"controller":{"config":{"invert":False,"threshold":0},"controller":"BinaryController"},"inputs":[{"input":"inX","parameter":"data","sensor":"InputSensorX"}],"name":"DummyLogikX","outputs":[{"actuator":"DummyActuatorX"}]})


        self.__app.route("/pins",methods=["GET"])(self.getPins)
        self.__app.route("/sensors",methods=["GET"])(self.getSensors)
        self.__app.route("/sensorsWithData/<length>",methods=["GET"])(self.getSensorsWithData)
        self.__app.route("/actuators",methods=["GET"])(self.getActuators)
        self.__app.route("/actuatorsWithData/<length>",methods=["GET"])(self.getActuatorsWithData)
        self.__app.route("/logics",methods=["GET"])(self.getLogics)
        self.__app.route("/data/<collection>/<length>",methods=["GET"])(self.getDataFromCollection)
        self.__app.route("/collections",methods=["GET"])(self.getAllCollections)
        self.__app.route("/stopScheduler",methods=["GET"])(self.stopScheduler)
        self.__app.route("/startScheduler",methods=["GET"])(self.startScheduler)
        self.__app.route("/schedulerInfo",methods=["GET"])(self.getSchedulerInfo)
        self.__app.route("/systemInfo",methods=["GET"])(self.getSystemInfo)
        self.__app.route("/setActuator/<name>/<state>")(self.setActuator)

    def addDataToDummyData(self,addCount):
        for i in range(addCount):
            change1 = random.uniform(-0.5,0.5)
            self.dummyValue1 = self.dummyValue1 + change1

            change2 = random.uniform(-0.5,0.5)
            self.dummyValue2 = self.dummyValue2 + change2

            self.dummySensorData.append({"data":{"dummy1":self.dummyValue1,"dummy2":self.dummyValue2},"time":self.startDateTime})
            self.startDateTime += datetime.timedelta(seconds=60)

    def getPins(self):
        # result = list(self.__mongoHandler.getAllPins())
        return jsonify(self.pins)        

    def getSensors(self):
        return jsonify(self.sensors)

    def getSensorsWithData(self,length):
        sensors = self.sensors
        for sensor in sensors:
            #add the last dummyDatas to the sensor as data 
            sensor["data"] = self.dummySensorData[0:int(length)]
        return jsonify(sensors)

    def getActuators(self):
        result = list(self.__configHandler.getActuators())
        return jsonify(result)
    
    def setActuator(self,name,state):
        

        print(f"setActuator {name} to {state}")

        stateBool = (state.lower() == "true")
        #ret is random True or False
        ret = random.randint(0,1)
        ret = (ret == 1)
        
        if(ret == True):
            return jsonify({"success":True})
        else:
            return jsonify({"success":False,"error":ret})

    def getActuatorsWithData(self,length):
        actuators = list(self.__configHandler.getActuators(onlyActive=False))
        for actuator in actuators:
            actuator["data"] = list(self.__mongoHandler.getDataFromCollection(actuator["collection"],int(length)))
            actuator["collectionSize"] = self.__mongoHandler.getDataStackSize(actuator["collection"])
        return jsonify(actuators)

    def getLogics(self):
        result = self.logics
        return jsonify(result)
    
    def getDataFromCollection(self, collection:str, length : int):
        self.addDataToDummyData(1)
        result = self.dummySensorData[0:int(length)]
        # for r in result:
        #     r.pop("_id")   
        return jsonify(result)

    def getAllCollections(self):
        result = list(self.__mongoHandler.getAllCollections())
        return jsonify(result)

    def getSchedulerInfo(self):
        if(self.__scheduler == None):
            return jsonify({"success":False,"error":"Kein Scheduler konfiguriert"})
        return jsonify({"status":self.__scheduler.statusScheduler()})

    def startScheduler(self):
        if(self.__scheduler == None):
            return jsonify({"success":False,"error":"Kein Scheduler konfiguriert"})
        
        self.__scheduler.startScheduler()
        return jsonify({"success":True})

    def stopScheduler(self):
        if(self.__scheduler == None):
            return jsonify({"success":False,"error":"Kein Scheduler konfiguriert"})
        
        self.__scheduler.stopScheduler()
        return jsonify({"success":True})
    

    def getSystemInfo(self):
        result = {}
        actuators = self.actuators
        for actuator in actuators:
            actuator["data"] = self.dummyActorrData[0:1]
            actuator["collectionSize"] = len(self.dummyActorrData)

        sensors = self.sensors
        for sensor in sensors:
            sensor["data"] = self.dummySensorData[0:1]
            sensor["collectionSize"] = len(self.dummySensorData)

        logics = self.logics

        scheduler = {"status":self.schedulerState,"available":True}
            
        return jsonify({"scheduler":scheduler,"sensors":sensors,"actuators":actuators,"logics":logics})


    def run(self):
        self.__app.run(host="0.0.0.0")
    

if __name__ == "__main__":
    restApi = RestAPI()
    restApi.run()