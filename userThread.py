#!/usr/bin/python3
from Building import Building
import threading
import time 
class userThread(threading.Thread):
    def __init__(self,building):
        threading.Thread.__init__(self)
        self.building=building
    
    def run(self):
        newUsers = self.building.generateUser()
        self.building.users['1'] += newUsers
        self.building.meanWaitingTime = self.building.totalWaitingTime / self.building.totalTravels
        self.building.totalUsers += len(newUsers)
        #affichage
        time.sleep(1)