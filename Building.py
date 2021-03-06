#!/usr/bin/python3
from User import User
from elevator import Elevator
from scipy.stats import poisson,exponnorm
import time
import numpy
import threading
from prettytable import PrettyTable
from os import system, name 
import argparse
import csv
import tkinter as tk
from kbhit import KBHit

kb = KBHit()

class userThread(threading.Thread):
    def __init__(self,building):
        threading.Thread.__init__(self)
        self.building=building
        self.csvfile = object
    
    def createCsv(self):
        nomCsv = ""
        nomCsv += str(self.building.elevators[0].typeAlgo) + "_" + str(self.building.elevators[0].typeIdle)+ "_nbElevator"+str(len(self.building.elevators))
        
        self.csvfile = open("%s.csv"%nomCsv, 'w', newline='')
        with self.csvfile:
            spamwriter = csv.writer(self.csvfile, delimiter=' ',quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for attente in self.building.tpsAttendu:
                doubAtten = str(attente).replace(".",",")
                spamwriter.writerows([doubAtten])
        
    def display(self):
        disp = PrettyTable()
               
        asc=[]
        for y in range(len(self.building.elevators)):
            ascenseur = [" "," "," "," "," "," "," "]
            asc.append(ascenseur)
        
        nbUser = [0,0,0,0,0,0,0]
        nbEtage = [1,2,3,4,5,6,7]
        i=0
        j=0
        nbUtilisateursActuel = 0
        
        for key, value in self.building.users.items():
            nbEtage[i] = str(key)
            nbUser[i] = len(value)
            nbUtilisateursActuel += len(value)
            i +=1
        disp.clear()
        disp.add_column("Numero Etage",nbEtage)
        for ascenseur in asc:
            for i in range(len(ascenseur)):
                ascenseur[i] = " "
            batonnet = "|" * len(self.building.elevators[j].users)
            if len(self.building.elevators[j].users) == 0:
                batonnet = " X "
            if (self.building.elevators[j].idle):
                batonnet = " zzz "
            ascenseur[self.building.elevators[j].floor - 1] = " %s"%batonnet
            nbUtilisateursActuel += len(self.building.elevators[j].users)
            j+=1
            disp.add_column("Ascenseur numero %s "%j,ascenseur)
                
        disp.add_column("Nombre de travailleurs dans l'etage",nbUser)
        
        algo = self.building.elevators[0].typeAlgo            
        print("Algorithme choisi : ",algo)
        print("Idle choisi",self.building.typeIdle)
        print("Il y a un total de ",self.building.totalUsers," utilisateurs qui sont entres dans le batiment")
        print("Il y a actuellement ",nbUtilisateursActuel,"utilisateur dans le batiment")
        print("Temps total attendu ",self.building.totalWaitingTime)
        print("Temps moyen attendu ",self.building.meanWaitingTime)
        print("Nombre Total de voayages effectue par les ascenseurs ",self.building.totalTravels)
        print("Appels d'ascenseur ",len(self.building.calls))
       
        

        
        print(disp)
        
    def clear(self):
        if name == 'nt': 
            system('cls')
        else:
            system('clear')
    
    def run(self):
        userCooldown = 6
        while True : 
            #generer new Users
            
           
            if(userCooldown == 6):
                userCooldown = 0
                newUsers = self.building.generateUser()
                for user in newUsers:
                    if(user.floorWanted not in self.building.calls):
                        #Appel des ascenseurs + sortie de idle si besoin
                        self.building.calls.append(1)
                        for elev in self.building.elevators:
                            elev.idle = False
                self.building.users['1'] += newUsers
                self.building.totalUsers += len(newUsers)

            #Calcul moyenne
            if self.building.totalTravels != 0 :
                self.building.meanWaitingTime = self.building.totalWaitingTime / self.building.totalTravels

            #Check si des Users ont fini de travailler
            for floor in self.building.users.values():
                for user in floor:
                    self.building.getBackHome(user)

            #Vide + remplir ascenseur quand arrive a un etage
            for elev in self.building.elevators:
                newUsers = self.building.getIntoElevator(elev.floor)
                leavers = elev.loadUsers(newUsers)
                for user in leavers:
                    self.building.arrivedAt(user, elev.floor)
                    if(elev.floor != 1):
                        self.building.users[str(elev.floor)].append(user)
                if(elev.floor in self.building.calls):
                    self.building.calls.remove(elev.floor)

            #On simule le deplacement de l'ascenseur
            time.sleep(0.16)
            #Puis on le deplace
            for elev in self.building.elevators:
                elev.move(self.building.proposeFloor())

            #affichage
            #L'ascenseur met 10 secondes pour passer d'un etage a l'autre en comptant l'ouverture et la fermeture des portes
            # On dit que 1min = 1 seconde
            # donc 10 secondes conrresponds ici a 0.16 secondes
            
            self.clear()
            
            self.display()
            if kb.kbhit():
                if ord(kb.getch()) == 27:
                    self.createCsv()
                    break
            userCooldown += 1

        
            

class Building:
    #elevators : list<Elevator> /
    #users : dict<Int,User> 
    def __init__(self, nbElevator, typeAlgo,lamb = 0.5,expo = 60,typeIdle = "noMoveIdle" ):
        self.elevators = []
        self.users = {
            '1' : [],
            '2' : [],
            '3' : [],
            '4' : [],
            '5' : [],
            '6' : [],
            '7' : []
        }
        self.totalUsers = 0
        self.totalTravels = 0
        self.totalWaitingTime = 0
        self.meanWaitingTime = 0
        self.calls = []
        self.expo = expo
        self.exp = exponnorm(expo)
        self.lamb = lamb
        self.typeIdle = typeIdle
        self.tpsAttendu = []

        for i in range(nbElevator):
            newElevator = Elevator(False,False,[],1,typeAlgo,self.typeIdle)
            self.elevators.append(newElevator)

        userT = userThread(self)
        userT.start()


    def generateUser(self):
        prob = numpy.random.poisson(self.lamb)
        users = []
        if prob != 0 :
            for i in range(prob):
                user = User(numpy.random.randint(2,8),time.time(),0,self.exp.rvs())
                users.append(user)
        return users
        
    
    def proposeFloor(self):
        if(len(self.calls) ==0 ):
            return -1
        return self.calls[0]


    def arrivedAt(self, user, floor):
        user.end = time.time()
        diff = user.end - user.begin
        self.tpsAttendu.append(diff)
        self.totalWaitingTime += diff
        self.totalTravels += 1
        if(floor == 1):
            del user
        else:
            user.begin = 0
            user.working = True

    def getBackHome(self, user):
        if(user.end + user.workingTime >= time.time()):
            user.begin = time.time()
            user.end = 0
            if(user.floorWanted not in self.calls):
                self.calls.append(user.floorWanted)
                for elev in self.elevators:
                    elev.idle = False
            user.floorWanted = 1
            user.working = False

    def getIntoElevator(self, floor):
        inTransit = []
        for user in self.users[str(floor)]:
            if(not user.working):
                inTransit.append(user)
                self.users[str(floor)].remove(user)
        return inTransit

parser = argparse.ArgumentParser(description='Mise en place des parametres')
parser.add_argument("--nbAscenseur", default=2, type=int, help="Nombre d'ascenseurs dans le building")
parser.add_argument("--typeAlgorithme", default="FCFS",choices = ["FCFS","SSTF"], type=str, help="type d'algorithme, FCFS ou SSTF True pour le premier false pour le second")
parser.add_argument("--lamb", default=0.5, type=float, help="Lambda necessaire pour la generation d'utilisateurs entrant dans le building")
parser.add_argument("--expo", default=60, type=int, help="Exponentielle generant le temps durant laquelle la personne va travailler dans le batiment")
parser.add_argument("--typeIdle", default="noMoveIdle",choices=["movingIdle","noMoveIdle", "goDownIdle","goUpIdle"], type=str, help="Type de Ralenti : MovingIdle va a 4eme etage, noMoveIdle ne bouge pas de l'etage ou il a laisser le dernier utilisateur GoUpIdle/GoDownIdle : Va un etage au dessus/en dessous de l'etage actuel")


args = parser.parse_args()

nbAscenseur = args.nbAscenseur
typeAlgorithme = args.typeAlgorithme
lamb = args.lamb
expo = args.expo
typeIdle = args.typeIdle


myBuilding = Building(nbAscenseur,typeAlgorithme,lamb,expo,typeIdle)






