# # imports
# import seaborn as sns
# from random import choice
# import warnings
# warnings.simplefilter("ignore")
# from plotly.offline import iplot
# # from statemachine import StateMachine, State
# from transitions import Machine
# import random
# from transitions.extensions import GraphMachine

# import EV.agent as agent
from EV.agent import EV, Cpoint
import EV.model as model

"""
This is the main file for the EV ABM simulator.
It is used to run the model and collect the data.

"""

def is_digit(n):
    try:
        int(n)
        return True
    except ValueError:
        return False

def get_params():
    print("Welcome to the ec4d EV ABM Simulator v 0.0.2-alpha.\n Please respond with 'q' to quit")
    global u_input 
    u_input = ''
    global evcount
    evcount = ''
    global cpcount 
    cpcount = ''
    global timestep
    timestep = ''
    while u_input != 'q':
        u_input = input("How many EVs do you want to simulate? \t")
        if is_digit(u_input) == True:
            evcount = int(u_input)
            u_input = input("How many charging points do you want to simulate? \t")
            if is_digit(u_input) == True:
                cpcount = int(u_input)
                u_input = input("How many timesteps do you want to simulate? \t")
                if is_digit(u_input) == True:
                    timestep = int(u_input)
        break
    print(f"Model parameters: \n EVs: {evcount}, Charging Points: {cpcount}, Timesteps: {timestep} \n")
    # return evcount, cpcount, timestep

def run_model():
        print("Starting model run.\n")
        model_run = model.EVModel(ticks=timestep, no_evs=evcount, no_cps=cpcount)
        print("Running model..\n")
        for i in range(timestep):
            model_run.step()
        print("Model run complete.\nPlease check the log file in the output folder for the results.")


if __name__ == '__main__':
    get_params()                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              
    run_model()


# validate an email with regex, comment each line