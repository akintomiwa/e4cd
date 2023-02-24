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
from EV.agent import EV, ChargeStation
import EV.model as model

"""
This is the main file for the EV ABM simulator.
It is used to run the model and collect the data.

"""

def select_mode():
    print("\nWelcome to the ec4d EV ABM Simulator v 0.3.5-alpha.\n\nPlease respond with 'q' to quit")
    u_input = ''
    while u_input != 'q':
        u_input = input("\nDo you want to run the model with default parameters? \t")
        if u_input == 'y':
            print("Running model with default parameters.\n")
            model_run = model.EVModel(ticks=72, no_evs=10, no_css=5)
            print("Running model..\n")
            for i in range(72):
                model_run.step()
            print("Model run complete.\nPlease check the log file in the output folder for the results.")
            break
        elif u_input == 'n':
            print("Running model with custom parameters.\n")
            get_params()
            run_model()
            break
        else:
            print("Please enter a valid input.\n")
            continue

def is_digit(n):
    try:
        int(n)
        return True
    except ValueError:
        return False

def get_params():
    print("Please input custom parameters for the ec4d EV ABM Simulator v 0.3.5-alpha.\n Please respond with 'q' to quit")
    global u_input 
    u_input = ''
    global evcount
    evcount = ''
    global cscount 
    cscount = ''
    global timestep
    timestep = ''
    while u_input != 'q':
        u_input = input("How many EVs do you want to simulate? \t")
        if is_digit(u_input) == True:
            evcount = int(u_input)
            u_input = input("How many charging points do you want to simulate? \t")
            if is_digit(u_input) == True:
                cscount = int(u_input)
                u_input = input("How many timesteps do you want to simulate? \t")
                if is_digit(u_input) == True:
                    timestep = int(u_input)
        break
    print(f"Model parameters: \n EVs: {evcount}, Charging Points: {cscount}, Timesteps: {timestep} \n")
    # return evcount, cpcount, timestep

def run_model():
        print("Starting model run.\n")
        model_run = model.EVModel(ticks=timestep, no_evs=evcount, no_css=cscount)
        print("Running model..\n")
        for i in range(timestep):
            model_run.step()
        print("Model run complete.\nPlease check the log file in the output folder for the results.")


if __name__ == '__main__':
    select_mode()
    # get_params()                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              
    # run_model()


# validate an email with regex, comment each line