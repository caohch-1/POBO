import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
import math
import matplotlib.pyplot as plt
import random as rand

class RPOL_baseline(object):
    def __init__(self, tuningVariables, tasksNumber, keytasks, Bf, Bg, V):
        '''
        tuningVariables is the list of parameter arrays, e.g.
            tuningVariables = [np.arange(0,5,1), np.arange(0,5,1)]
        tasksNumber is the total number of tasks, e.g.
            taskNumber = 10
        keytasks is a list that contains the key tasks, e.g.
            keytasks = np.arange(0,3,1)
        '''
        #beta term
        self.Bf = Bf
        self.Bg = Bg
        self.Rf = 1
        self.Rg = 1
        self.betaf = 1e-9
        self.betag = 1e-9
        self.delta = 0.05
        self.keytasks = keytasks
        self.V_multipler = V

        #Dual penalty initialization and normalize term
        self.Q = 0

        #Rectified penalty initialization: for hard constraint
        self.Q_hat = 1

        #grid_term
        tuningVariables.insert(0, np.arange(tasksNumber))
        meshgrid = np.meshgrid(*tuningVariables, indexing='ij')
        self.meshgrid = np.array(meshgrid)
        self.X_grid = self.meshgrid.reshape(self.meshgrid.shape[0], -1, self.meshgrid.shape[1]).T
        self.index = 0

        #prior
        self.muf = np.zeros((self.X_grid.shape[1]))
        self.mug = np.zeros((self.X_grid.shape[1]))
        self.sigmaf = np.ones((self.X_grid.shape[1]))
        self.sigmag = np.ones((self.X_grid.shape[1]))

        #prior
        self.ft = np.ones((self.X_grid.shape[0], self.X_grid.shape[1]))
        self.gt = np.ones((self.X_grid.shape[0], self.X_grid.shape[1]))

        #round counter
        self.round = 0

        #decision list, reward list and cost list
        self.X = []
        self.RList = []
        self.CList = []
    
    def test(self):
        return

    def decision(self, task, Q):
        #GP update(update the task at timstep t-1)
        if self.round != 0:
            gpf = GaussianProcessRegressor()
            gpf.fit(self.X, self.RList)
            self.muf, self.sigmaf = gpf.predict(self.X_grid[task], return_std=True)

            gpg = GaussianProcessRegressor()
            gpg.fit(self.X, self.CList)
            self.mug, self.sigmag = gpg.predict(self.X_grid[task], return_std=True)

            self.ft[task] = self.muf + self.betaf * self.sigmaf
            self.gt[task] = self.mug - self.betag * self.sigmag

        self.round += 1
        indicator = 1 if task in self.keytasks else 0
        V = self.V_multipler * self.delta / (8 * self.betaf) * np.sqrt(self.round)

        self.index = np.argmax(self.ft[task] - Q * np.maximum(self.gt[task], 0))
        self.X.append(self.X_grid[task][self.index])
        return self.X[-1]

    def update(self, reward, cost, task):
        #update reward&cost
        self.RList.append(reward)
        self.CList.append(cost)

        #update beta
        gamma = math.log(self.round)
        self.betaf = self.Bf + self.Rf * np.sqrt(2 * (gamma + 1 + np.log(2 / self.delta)))
        self.betag = self.Bg + self.Rg * np.sqrt(2 * (gamma + 1 + np.log(2 / self.delta)))

        #update penalty
        # eta = 0.05*self.round
        eta = np.sqrt(self.round)
        epsilon = 0.0001 * (6 * self.betaf * np.sqrt(gamma) + 2) / np.sqrt(self.round)
        # print(f"[RPOL Inter.] epsilon: {epsilon}")

        # index that must be modified according to the problem
        self.Q = max(self.Q_hat + max(cost, 0), eta)

class RPOLforkey_baseline(object):
    def __init__(self, tuningVariables, tasksNumber, keytasks, Bf, Bg, BG, V):
        '''
        tuningVariables is the list of parameter arrays, e.g.
            tuningVariables = [np.arange(0,5,1), np.arange(0,5,1)]
        tasksNumber is the total number of tasks, e.g.
            taskNumber = 10
        keytasks is a list that contains the key tasks, e.g.
            keytasks = np.arange(0,3,1)
        '''
        #beta term
        self.Bf = Bf
        self.Bg = Bg
        self.BG = BG
        self.Rf = 1
        self.Rg = 1
        self.RG = 1
        self.betaf = 1e-9
        self.betag = 1e-9
        self.betaG = 1e-9
        self.delta = 0.05
        self.keytasks = keytasks
        self.V_multipler = V

        #Dual penalty initialization and normalize term
        self.Q = 0

        #Rectified penalty initialization: for hard constraint
        self.Q_hat = 1

        #grid_term
        tuningVariables.insert(0, np.arange(tasksNumber))
        meshgrid = np.meshgrid(*tuningVariables, indexing='ij')
        self.meshgrid = np.array(meshgrid)
        self.X_grid = self.meshgrid.reshape(self.meshgrid.shape[0], -1, self.meshgrid.shape[1]).T
        self.index = 0

        #prior
        self.muf = np.zeros((self.X_grid.shape[1]))
        self.mug = np.zeros((self.X_grid.shape[1]))
        self.muG = np.zeros((self.X_grid.shape[1]))
        self.sigmaf = np.ones((self.X_grid.shape[1]))
        self.sigmag = np.ones((self.X_grid.shape[1]))
        self.sigmaG = np.ones((self.X_grid.shape[1]))

        #prior
        self.ft = np.ones((self.X_grid.shape[0], self.X_grid.shape[1]))
        self.gt = np.ones((self.X_grid.shape[0], self.X_grid.shape[1]))
        self.Gt = np.ones((self.X_grid.shape[0], self.X_grid.shape[1]))

        #round counter
        self.round = 0

        #decision list, reward list and cost list
        self.X = []
        self.RList = []
        self.CList = []
        self.HList = []
    
    def test(self):
        return

    def decision(self, task, Q, hatQ):
        #GP update(update the task at timstep t-1)
        if self.round != 0:
            gpf = GaussianProcessRegressor()
            gpf.fit(self.X, self.RList)
            self.muf, self.sigmaf = gpf.predict(self.X_grid[task], return_std=True)

            gpg = GaussianProcessRegressor()
            gpg.fit(self.X, self.CList)
            self.mug, self.sigmag = gpg.predict(self.X_grid[task], return_std=True)
            
            gpG = GaussianProcessRegressor()
            gpG.fit(self.X, self.HList)
            self.muG, self.sigmaG = gpG.predict(self.X_grid[task], return_std=True)

            self.ft[task] = self.muf + self.betaf * self.sigmaf
            self.gt[task] = self.mug - self.betag * self.sigmag
            self.Gt[task] = self.muG - self.betaG * self.sigmaG

        self.round += 1
        V = self.V_multipler * self.delta / (8 * self.betaf) * np.sqrt(self.round)

        self.index = np.argmax(self.ft[task] - Q * np.maximum(self.gt[task], 0) - hatQ * np.maximum(self.Gt[task], 0))
        self.X.append(self.X_grid[task][self.index])
        return self.X[-1]

    def update(self, reward, cost, hardcost, task):
        #update reward&cost
        self.RList.append(reward)
        self.CList.append(cost)
        self.HList.append(hardcost)

        #update beta
        gamma = math.log(self.round)
        self.betaf = self.Bf + self.Rf * np.sqrt(2 * (gamma + 1 + np.log(2 / self.delta)))
        self.betag = self.Bg + self.Rg * np.sqrt(2 * (gamma + 1 + np.log(2 / self.delta)))
        self.betaG = self.BG + self.RG * np.sqrt(2 * (gamma + 1 + np.log(2 / self.delta)))

        #update penalty
        # eta = 0.05*self.round
        eta = np.sqrt(self.round)
        epsilon = 0.0001 * (6 * self.betaf * np.sqrt(gamma) + 2) / np.sqrt(self.round)
        # print(f"[RPOL Inter.] epsilon: {epsilon}")

        # index that must be modified according to the problem
        self.Q = max(self.Q_hat + max(cost, 0), eta)
        self.Q_hat = max(self.Q_hat + max(hardcost, 0), eta)

class RPOL(object):
    def __init__(self, tuningVariables, tasksNumber, keytasks, Bf, Bg, V):
        '''
        tuningVariables is the list of parameter arrays, e.g.
            tuningVariables = [np.arange(0,5,1), np.arange(0,5,1)]
        tasksNumber is the total number of tasks, e.g.
            taskNumber = 10
        keytasks is a list that contains the key tasks, e.g.
            keytasks = np.arange(0,3,1)
        '''
        #beta term
        self.Bf = Bf
        self.Bg = Bg
        self.Rf = 1
        self.Rg = 1
        self.betaf = 1e-9
        self.betag = 1e-9
        self.delta = 0.05
        self.keytasks = keytasks
        self.V_multipler = V

        #Dual penalty initialization and normalize term
        self.Q = 0

        #Rectified penalty initialization: for hard constraint
        self.Q_hat = 1

        #grid_term
        tuningVariables.insert(0, np.arange(tasksNumber))
        meshgrid = np.meshgrid(*tuningVariables, indexing='ij')
        self.meshgrid = np.array(meshgrid)
        self.X_grid = self.meshgrid.reshape(self.meshgrid.shape[0], -1, self.meshgrid.shape[1]).T
        self.index = 0

        #prior
        self.muf = np.zeros((self.X_grid.shape[1]))
        self.mug = np.zeros((self.X_grid.shape[1]))
        self.sigmaf = np.ones((self.X_grid.shape[1]))
        self.sigmag = np.ones((self.X_grid.shape[1]))

        #prior
        self.ft = np.ones((self.X_grid.shape[0], self.X_grid.shape[1]))
        self.gt = np.ones((self.X_grid.shape[0], self.X_grid.shape[1]))

        #round counter
        self.round = 0

        #decision list, reward list and cost list
        self.X = []
        self.RList = []
        self.CList = []
    
    def test(self):
        return

    def decision(self, task):
        #GP update(update the task at timstep t-1)
        if self.round != 0:
            gpf = GaussianProcessRegressor()
            gpf.fit(self.X, self.RList)
            self.muf, self.sigmaf = gpf.predict(self.X_grid[task], return_std=True)

            gpg = GaussianProcessRegressor()
            gpg.fit(self.X, self.CList)
            self.mug, self.sigmag = gpg.predict(self.X_grid[task], return_std=True)

            self.ft[task] = self.muf + self.betaf * self.sigmaf
            self.gt[task] = self.mug - self.betag * self.sigmag

        self.round += 1
        indicator = 1 if task in self.keytasks else 0
        V = self.V_multipler * self.delta / (8 * self.betaf) * np.sqrt(self.round)

        self.index = np.argmax(self.ft[task] - 1 / V * self.Q * self.gt[task] - self.Q_hat * np.maximum(self.gt[task], 0) * indicator)
        # print(f"[RPOL Inter.] Reward = self.ft[task]: \n{self.ft[task]}")
        # print(f"[RPOL Inter.] V: {V}, self.Q: {self.Q}")
        # print(f"[RPOL Inter.] Predicted cost list: \n{self.gt[task]}")
        # print(f"[RPOL Inter.] Dual penalty =  1 / V * self.Q * self.gt[task]: \n{1 / V * self.Q * self.gt[task]}")
        # print(f"[RPOL Inter.] IDList = self.ft[task] - 1 / V * self.Q * self.gt[task] : \n{self.ft[task] - 1 / V * self.Q * self.gt[task] - self.Q_hat * np.maximum(self.gt[task], 0) * indicator}")
        
        # self.index = np.argmax(self.ft[task] - self.Q * np.maximum(self.gt[task], 0))
        # print(f"[RPOL Inter.] Reward = self.ft[task]: \n{self.ft[task]}")
        # print(f"[RPOL Inter.] self.Q: {self.Q}")
        # print(f"[RPOL Inter.] Predicted cost: \n{self.gt[task]}")
        # print(f"[RPOL Inter] Dual Penalty = self.Q * np.maximum(self.gt[task], 0): \n{self.Q * np.maximum(self.gt[task], 0)}")
        # print(f"[RPOL Inter.] IDList = self.ft[task] - self.Q * np.maximum(self.gt[task], 0) : \n{self.ft[task] - self.Q * np.maximum(self.gt[task], 0)}")
        
        self.X.append(self.X_grid[task][self.index])
        return self.X[-1]

    def update(self, reward, cost, task):
        #update reward&cost
        self.RList.append(reward)
        self.CList.append(cost)

        #update beta
        gamma = math.log(self.round)
        self.betaf = self.Bf + self.Rf * np.sqrt(2 * (gamma + 1 + np.log(2 / self.delta)))
        self.betag = self.Bg + self.Rg * np.sqrt(2 * (gamma + 1 + np.log(2 / self.delta)))

        #update penalty
        eta = 0.05*self.round
        epsilon = 0.0001 * (6 * self.betaf * np.sqrt(gamma) + 2) / np.sqrt(self.round)
        # print(f"[RPOL Inter.] epsilon: {epsilon}")

        # index that must be modified according to the problem
        self.Q = max(self.Q + self.gt[task][self.index] + epsilon, 0)
        self.Q_hat = max(self.Q_hat + max(cost, 0), eta)
 
class RPOLforkey(object):
    def __init__(self, tuningVariables, tasksNumber, keytasks, Bf, Bg, BG, V):
        '''
        tuningVariables is the list of parameter arrays, e.g.
            tuningVariables = [np.arange(0,5,1), np.arange(0,5,1)]
        tasksNumber is the total number of tasks, e.g.
            taskNumber = 10
        keytasks is a list that contains the key tasks, e.g.
            keytasks = np.arange(0,3,1)
        '''
        #beta term
        self.Bf = Bf
        self.Bg = Bg
        self.BG = BG
        self.Rf = 1
        self.Rg = 1
        self.RG = 1
        self.betaf = 1e-9
        self.betag = 1e-9
        self.betaG = 1e-9
        self.delta = 0.05
        self.keytasks = keytasks
        self.V_multipler = V

        #Dual penalty initialization and normalize term
        self.Q = 0

        #Rectified penalty initialization: for hard constraint
        self.Q_hat = 1

        #grid_term
        tuningVariables.insert(0, np.arange(tasksNumber))
        meshgrid = np.meshgrid(*tuningVariables, indexing='ij')
        self.meshgrid = np.array(meshgrid)
        self.X_grid = self.meshgrid.reshape(self.meshgrid.shape[0], -1, self.meshgrid.shape[1]).T
        self.index = 0

        #prior
        self.muf = np.zeros((self.X_grid.shape[1]))
        self.mug = np.zeros((self.X_grid.shape[1]))
        self.muG = np.zeros((self.X_grid.shape[1]))
        self.sigmaf = np.ones((self.X_grid.shape[1]))
        self.sigmag = np.ones((self.X_grid.shape[1]))
        self.sigmaG = np.ones((self.X_grid.shape[1]))

        #prior
        self.ft = np.ones((self.X_grid.shape[0], self.X_grid.shape[1]))
        self.gt = np.ones((self.X_grid.shape[0], self.X_grid.shape[1]))
        self.Gt = np.ones((self.X_grid.shape[0], self.X_grid.shape[1]))

        #round counter
        self.round = 0

        #decision list, reward list and cost list
        self.X = []
        self.RList = []
        self.CList = []
        self.HList = []
    
    def test(self):
        return

    def decision(self, task):
        #GP update(update the task at timstep t-1)
        if self.round != 0:
            gpf = GaussianProcessRegressor()
            gpf.fit(self.X, self.RList)
            self.muf, self.sigmaf = gpf.predict(self.X_grid[task], return_std=True)

            gpg = GaussianProcessRegressor()
            gpg.fit(self.X, self.CList)
            self.mug, self.sigmag = gpg.predict(self.X_grid[task], return_std=True)
            
            gpG = GaussianProcessRegressor()
            gpG.fit(self.X, self.HList)
            self.muG, self.sigmaG = gpG.predict(self.X_grid[task], return_std=True)

            self.ft[task] = self.muf + self.betaf * self.sigmaf
            self.gt[task] = self.mug - self.betag * self.sigmag
            self.Gt[task] = self.muG - self.betaG * self.sigmaG

        self.round += 1
        V = self.V_multipler * self.delta / (8 * self.betaf) * np.sqrt(self.round)

        self.index = np.argmax(self.ft[task] - 1 / V * self.Q * self.gt[task] - self.Q_hat * np.maximum(self.Gt[task], 0))
        self.X.append(self.X_grid[task][self.index])
        return self.X[-1]

    def update(self, reward, cost, hardcost, task):
        #update reward&cost
        self.RList.append(reward)
        self.CList.append(cost)
        self.HList.append(hardcost)

        #update beta
        gamma = math.log(self.round)
        self.betaf = self.Bf + self.Rf * np.sqrt(2 * (gamma + 1 + np.log(2 / self.delta)))
        self.betag = self.Bg + self.Rg * np.sqrt(2 * (gamma + 1 + np.log(2 / self.delta)))
        self.betaG = self.BG + self.RG * np.sqrt(2 * (gamma + 1 + np.log(2 / self.delta)))

        #update penalty
        eta = 0.05*self.round
        epsilon = 0.0001 * (6 * self.betaf * np.sqrt(gamma) + 2) / np.sqrt(self.round)
        # print(f"[RPOL Inter.] epsilon: {epsilon}")

        # index that must be modified according to the problem
        self.Q = max(self.Q + self.gt[task][self.index] + epsilon, 0)
        self.Q_hat = max(self.Q_hat + max(hardcost, 0), eta)

class CKB(object):
    def __init__(self, meshgrid, tuningVariables, tasksNumber, Bf, Bg, V, keytasks):
        #beta term
        self.Bf = Bf
        self.Bg = Bg
        self.Rf = 1
        self.Rg = 1
        self.delta = 0.05
        self.V_multipler = V

        #penalty initialization
        self.phi = 0
        self.rho = 4*self.Bf/0.01
        self.V = self.V_multipler * self.Bf*math.sqrt(500)/self.rho

        #grid_term
        tuningVariables.insert(0, np.arange(tasksNumber))
        meshgrid = np.meshgrid(*tuningVariables, indexing='ij')
        self.meshgrid = np.array(meshgrid)
        self.X_grid = self.meshgrid.reshape(self.meshgrid.shape[0], -1).T

        #prior
        self.muf = np.array([0. for _ in range(self.X_grid.shape[0])])
        self.mug = np.array([0. for _ in range(self.X_grid.shape[0])])
        self.sigmaf = np.array([1 for _ in range(self.X_grid.shape[0])])
        self.sigmag = np.array([1 for _ in range(self.X_grid.shape[0])])

        #prior
        self.ft = np.array([1 for _ in range(self.X_grid.shape[0])])
        self.gt = np.array([1 for _ in range(self.X_grid.shape[0])])

        #round counter
        self.round = 0

        #decision list, reward list and cost list
        self.X = []
        self.RList = []
        self.CList = []

    def decision(self, task):
        self.round += 1
        index = np.argmax(self.ft - self.phi * self.gt)
        self.X.append(self.X_grid[index])

        #penlaty update
        self.phi = np.clip(self.phi + 1 / self.V * self.gt[index], 0, self.rho)
        return self.X[-1]

    def update(self, reward, cost):
        #update reward&cost
        self.RList.append(reward)
        self.CList.append(cost)

        #update beta
        gamma = math.log(self.round)
        betaf = self.Bf + self.Rf * np.sqrt(2 * (gamma + 1 + np.log(2 / self.delta)))
        betag = self.Bg + self.Rg * np.sqrt(2 * (gamma + 1 + np.log(2 / self.delta)))

        #GP update
        gpf = GaussianProcessRegressor()
        gpf.fit(self.X, self.RList)
        self.muf, self.sigmaf = gpf.predict(self.X_grid, return_std=True)

        gpg = GaussianProcessRegressor()
        gpg.fit(self.X, self.CList)
        self.mug, self.sigmag = gpg.predict(self.X_grid, return_std=True)

        self.ft = self.muf + betaf * self.sigmaf
        self.gt = self.mug - betag * self.sigmag
        
class CKBforkey(object):
    def __init__(self, meshgrid, tuningVariables, tasksNumber, Bf, Bg ,BG, V, keytasks):
        #beta term
        self.Bf = Bf
        self.Bg = Bg
        self.BG = BG
        self.Rf = 1
        self.Rg = 1
        self.RG = 1
        self.delta = 0.05
        self.V_multipler = V

        #penalty initialization
        self.phi = 0
        self.phihard = 0
        self.rho = 4*self.Bf/0.01
        self.V = self.V_multipler * self.Bf*math.sqrt(500)/self.rho

        #grid_term
        tuningVariables.insert(0, np.arange(tasksNumber))
        meshgrid = np.meshgrid(*tuningVariables, indexing='ij')
        self.meshgrid = np.array(meshgrid)
        self.X_grid = self.meshgrid.reshape(self.meshgrid.shape[0], -1).T

        #prior
        self.muf = np.array([0. for _ in range(self.X_grid.shape[0])])
        self.mug = np.array([0. for _ in range(self.X_grid.shape[0])])
        self.muG = np.array([0. for _ in range(self.X_grid.shape[0])])
        self.sigmaf = np.array([1 for _ in range(self.X_grid.shape[0])])
        self.sigmag = np.array([1 for _ in range(self.X_grid.shape[0])])
        self.sigmaG = np.array([1 for _ in range(self.X_grid.shape[0])])

        #prior
        self.ft = np.array([1 for _ in range(self.X_grid.shape[0])])
        self.gt = np.array([1 for _ in range(self.X_grid.shape[0])])
        self.Gt = np.array([1 for _ in range(self.X_grid.shape[0])])

        #round counter
        self.round = 0

        #decision list, reward list and cost list
        self.X = []
        self.RList = []
        self.CList = []
        self.HList = []

    def decision(self, task):
        self.round += 1
        index = np.argmax(self.ft - self.phi * self.gt - self.phihard * self.Gt)
        self.X.append(self.X_grid[index])

        #penlaty update
        self.phi = np.clip(self.phi + 1 / self.V * self.gt[index], 0, self.rho)
        self.phihard = np.clip(self.phihard + 1 / self.V * self.Gt[index], 0, self.rho)
        return self.X[-1]

    def update(self, reward, cost, hardcost):
        #update reward&cost
        self.RList.append(reward)
        self.CList.append(cost)
        self.HList.append(hardcost)

        #update beta
        gamma = math.log(self.round)
        betaf = self.Bf + self.Rf * np.sqrt(2 * (gamma + 1 + np.log(2 / self.delta)))
        betag = self.Bg + self.Rg * np.sqrt(2 * (gamma + 1 + np.log(2 / self.delta)))
        betaG = self.BG + self.RG * np.sqrt(2 * (gamma + 1 + np.log(2 / self.delta)))

        #GP update
        gpf = GaussianProcessRegressor()
        gpf.fit(self.X, self.RList)
        self.muf, self.sigmaf = gpf.predict(self.X_grid, return_std=True)

        gpg = GaussianProcessRegressor()
        gpg.fit(self.X, self.CList)
        self.mug, self.sigmag = gpg.predict(self.X_grid, return_std=True)
        
        gpG = GaussianProcessRegressor()
        gpG.fit(self.X, self.HList)
        self.muG, self.sigmaG = gpG.predict(self.X_grid, return_std=True)

        self.ft = self.muf + betaf * self.sigmaf
        self.gt = self.mug - betag * self.sigmag
        self.Gt = self.muG - betaG * self.sigmaG

