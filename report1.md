MESA AB Model

This AB model simulates a supermarket which has 5 counters and is expected to cater to 500 guests over a one-hour time period. 

This model serves as a decision support tool to determine the optimal amout of counters to keep open, in order to serve the customers as quickly as possible, within the hour. Each customer is worth $10 and each counter costs $300 to run. 
The customers take a period of time to get served, this time duration in seconds is selected randomly from a normal distribution around an average of 45 seconds.

<!-- Model -->
Model Set up
The Agents in this simulation fall into one of two types, Counters and Customers. These two classes of agents interact within the supermarket 'environment', which is governed by a few simple rules.
Each of the agent types have certain attributes and have certain behaviours, within the model.

The model used in this example is a QueueModel which inherits from the Mesa Model class. The model has atttributes such as ticks, number of customers and number of counters. 

The Model class subsumes the Agents and determines the flow of activities within the model. 
It also relies on a Scheduler and DataCollector - these are utility methods. The scheduler dictates the manner in which Customer Agents are generated in this model, while the DataCollector records the output of  contained in model functions.

<!-- Customers -->
Attributes: Customers have certain attributes such as the time it takes for them get served, the time they entered the supermaket, a balking tolerance

Behaviours: Once initialised with their attributes, Customers can 'select a counter' or 'pay n leave'.

The step function advances the model through the flow of selecting a counter and pay n leaving.

Notes:
Balking: the propensity of a Customer agent to leave a queue, if the number of Customers exceeds a given threshold.

<!-- Counters -->
The Counter class leverages a queue represented as a list.

Attributes: queue, active customer, entry time.

Behaviours: After initialisatioon, a Counter agent can Dequeue Customers after evaluating how long they've been in the queue for, relative to when the Customer was frist created, as well as the current model time.

The step function checks if an active customer exists and goes on to dequeue the active customer.

Results
The simulation records the number of customers arriving, up to a total of 500, as well as the number of customers who balked and those who were served. This is done using the Data collector in tandem with a set of bespoke functions.

The simulation is then run 10 times, using differnt values (5-15) for the number of counters in order to find the optimum number of counters to be run, to keep operating costs low and gross margin high, maximising profits.

The table above shows that 8 counters is the ideal for maximising earnings for the supermarket.
