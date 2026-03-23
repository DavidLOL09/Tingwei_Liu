import numpy as np
import logging
from icecream import ic
import time

logger = logging.getLogger('Polynomial_regression')

class polynomial_regression():


    def __init__(self, log_level=logging.NOTSET):
        self.zoom           = False
        self.train_y_list   = [] # y_expectation
        self.input_x_list   = []
        self.input_y_list   = []
        self.weights        = []
        self.gradients      = []
        self.signal_inertia = 0
        self.noise_inertia  = 0
        self.signal_const   = 0.9
        self.noise_const    = 0.99
        self.descent        = 'Adam' # Adam, Normal
        self.coorection     = []

        
        self.exp_level      = []
        self.coefficient    = []

        self.error          = 0

        self.learningR      = []

        self.sample_size    = 0
        self.iteration      = 0

        self.first_err      = 0

        self.__debug        = None

    def get_expect_y(self,coefficient=None):
        train_y=[]
        if coefficient is None:
            coefficient = self.coefficient
        for i in self.input_x_list:
            train_y.append(np.sum(i*coefficient))
        return np.array(train_y)

    def get_error(self,y_list=None):
        if y_list is None:
            y_list=self.train_y_list
        error   = np.sum((self.weights*(y_list-self.input_y_list))**2)/self.sample_size
        return error

    def calc_d_err_perX(self,coeff):
        diff    = np.sum(self.weights*(self.train_y_list-self.input_y_list)*(self.input_x_list[:,coeff]))/self.sample_size
        return diff
    
    def get_d_err(self):
        d_err   = []
        for coeff in range(0,len(self.coefficient)):
            d_err.append(self.calc_d_err_perX(coeff))
        return np.array(d_err)

    def get_zoom(self):
        ic(f'zoom:{self.zoom}')
        return self.input_x_list

        
    def initialize_x(self,x_lst:np.array,regression):
        # regression = multiple linear, polynomial
        train_x_lst = []
        if regression == 'multiple linear':
            for loc_x in x_lst:
                train_x_lst.append(np.insert(loc_x,0,1))
            return np.array(train_x_lst)
        
        elif regression == 'polynomial':
            for x in x_lst:
                loc_x   = []
                for exp in self.exp_level:
                    loc_x.append(x**exp)
                train_x_lst.append(np.array(loc_x))
            return np.array(train_x_lst)

        elif regression == 'legrendre':
            pass 


    def get_init_coeff(self,x_lst:np.array,y_lst:np.array,weight:np.array):
        weight = np.diag(weight)
        return np.linalg.pinv(x_lst.T @ weight @ x_lst) @ x_lst.T @ weight @ y_lst
    
    def initialize_coeff(self,demo_size):
        index_lst   = []
        x_lst   = self.input_x_list
        y_lst   = self.input_y_list
        demo_x  = []
        demo_y  = []
        for i in range(0,demo_size):
            index=int(i*self.sample_size/demo_size)
            demo_x.append(x_lst[index])
            demo_y.append(y_lst[index])
            ic(index)
        return self.get_init_coeff(np.array(demo_x),np.array(demo_y))

    


    def begin(self, exponent_lst, x_lst, y_lst, regression='multiple linear',demo_size=10, y_weights=None, zoom=False, descent='Adam', learningR = 0.1):

        self.learningR  = learningR
        self.descent    = descent
        self.exp_level  = exponent_lst
        if zoom:
            x_lst       = np.linspace(0,1,len(x_lst))
            self.input_x_list = self.initialize_x(np.array(x_lst),regression)
            ic(self.input_x_list)
            self.zoom = zoom
        else:
            self.input_x_list   = self.initialize_x(np.array(x_lst),regression)
        self.input_y_list   = np.array(y_lst)
        if y_weights is None:
            self.weights    = np.full_like(y_lst,1)
        else:
            self.weights        = y_weights
        self.sample_size    = len(self.input_x_list)
        # self.coefficient    = self.initialize_coeff(demo_size)
        self.coefficient    = [0,0,0,0]
        # self.coefficient    = np.full_like(self.input_x_list[0],0)
        ic(self.coefficient)
        self.train_y_list   = self.get_expect_y()
        ic(len(self.train_y_list),len(self.input_y_list))
        # ic(type(self.weights),np.shape(self.weights))
        self.error          = self.get_error()
        self.first_err      = self.error
        self.gradients      = self.get_d_err()

    def get_correction(self):
        correction = 0
        self.gradients=self.get_d_err()
        if self.descent == 'Normal':  
            correction = self.learningR*self.gradients
        elif self.descent == 'Adam':
            signal          = self.signal_inertia/(1-self.signal_const**(self.iteration+1))
            noise           = self.noise_inertia/(1-self.noise_const**(self.iteration+1))

            correction      = self.learningR*(signal/(np.sqrt(noise)+10E-8))

            self.signal_inertia = self.signal_const*self.signal_inertia+(1-self.signal_const)*self.gradients
            self.noise_inertia  = self.noise_const*self.noise_inertia+(1-self.noise_const)*self.gradients**2
        if type(correction) is type(0):
            raise KeyError(f'Gradient Descent method Not Found')
        return correction



    def get_next_generation(self):
        # ic(self.coefficient)
        # ic(self.get_d_err())
        # ic(self.sample_size)
        # ic('\n')

        
        new_coeff = self.coefficient-self.get_correction()
        return new_coeff

    
    def run(self):
        while self.iteration<100000:
            last_e              = self.error
            self.coefficient    = self.get_next_generation()
            self.train_y_list   = self.get_expect_y()
            self.error          = self.get_error()
            # ic(self.gradients)
            ic(self.error)
            # error               = self.error
            # ic(self.coefficient)
            # ic(error)
            # ic(new_error)
            # print()
            self.iteration+=1
            if self.error/self.first_err<=10e-8:
                ic('error<10e-5 than the start')
                return self.coefficient,self.error,self.iteration,self.input_x_list
        ic('iteration maximum')
        return self.coefficient,self.error,self.iteration,self.input_x_list


