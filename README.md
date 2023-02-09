# An Agent Based Model (ABM) for modelling Electric vehicle driver behaviour


This particular ABM model considers EVs which undertake urban or 'interurban trips' of a set length. The state of each EV is moderated by a state machine and cycles between states such as idle, travelling, in queue and charging. 
During multi-day runs of the model, the EVs' odometers are reset at the end of every day. 

This is an early version of the project and remains under development.

The model can be run in any of the following ways:
a. as a series of successive cells in the ev_apm_simplest_mobile.ipynb file
b. as an intractive CLI program using the start.py module.

The model is written in Python 3.7 and uses the following libraries.