import numpy as np
import logging
from icecream import ic

logger = logging.getLogger('Polynomial_regression')

class polynomial_regression():
    """
    Convolves electric field with antenna response to get the voltage output of the antenna

    Module that should be used to convert simulations to data.
    It assumes that at least one efield is given per channel as input. It will
    convolve the electric field with the corresponding antenna response for the
    incoming direction specified in the channel object.
    The station id, defines antenna location and antenna type.

    """

    def __init__(self, log_level=logging.NOTSET):
        self.train_y_list   = []
        self.input_x_list   = []
        self.input_y_list   = []
        self.weights        = []
        
        self.exp_level      = []
        self.coefficient    = []

        self.error          = 0

        self.learningR      = []

        self.sample_size    = 0
        self.iteration      = 0

        self.first_err      = 0

        self.__debug        = None

    def get_expect_y(self):
        train_y=[]
        for i in range(self.sample_size):
            x       = self.input_x_list[i]
            y_exp   = 0
            for ic,coeff in enumerate(self.coefficient):
                exp     = self.exp_level[ic]
                y_exp   += coeff*(x**exp)
            train_y.append(y_exp)
        return np.array(train_y)

    def get_error(self):
        m       = self.sample_size
        error   = np.sum((self.weights*(self.train_y_list-self.input_y_list))**2)/m
        return error

    def calc_d_err_perExp(self,exp):
        if exp>0:
            diff    = np.sum(self.weights*(self.train_y_list-self.input_y_list)*(self.input_x_list**(exp)))/self.sample_size
        else:
            diff    = np.sum(self.weights*(self.train_y_list-self.input_y_list))/self.sample_size
        return diff
    
    def get_d_err(self):
        d_err   = []
        for exp in self.exp_level:
            d_err.append(self.calc_d_err_perExp(exp))
        return np.array(d_err)

    

    def begin(self, exp_max, x_lst, y_lst, coeff_start=[], y_weights=None):

        self.exp_level  = np.arange(exp_max+1)
        self.input_x_list   = np.array(x_lst)
        self.input_y_list   = np.array(y_lst)
        if y_weights is None:
            self.weights    = np.full_like(y_lst,1)
        else:
            self.weights        = y_weights
        if coeff_start is []:
            self.coefficient    = np.full_like(self.exp_level,1)
        else:
            self.coefficient    = np.array(coeff_start)
        self.sample_size    = len(self.input_x_list)
        self.train_y_list   = self.get_expect_y()
        self.learningR      = 0.01
        # ic(type(self.weights),np.shape(self.weights))
        self.error          = self.get_error()
        self.first_err      = self.error

    def get_next_generation(self):
        new_coeff   = self.coefficient-self.learningR*self.get_d_err()
        return new_coeff
    
    def run(self):
        while self.iteration<10000:
            self.coefficient    = self.get_next_generation()
            self.train_y_list   = self.get_expect_y()
            error               = self.error
            new_error           = self.get_error()
            # ic(self.coefficient)
            # ic(error)
            # ic(new_error)
            # print()
            self.iteration+=1
            self.error=new_error
            if self.first_err/self.error>=10e5:
                return self.coefficient,new_error,error,self.iteration
        return self.coefficient,new_error,error,self.iteration


