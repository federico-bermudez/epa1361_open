#!/usr/bin/env python
# coding: utf-8

# ## 2. Lake model: Exploring the behavior of a decision-making system
# 
# Explore the lake problem, connect it to the workbench, investigate system behavior, analyze trade-offs, and learn about parallelization.
# 
# See also [this general introduction to the workbench](https://waterprogramming.wordpress.com/2017/11/01/using-the-exploratory-modelling-workbench/) as a source of inspiration for completing the assignment below
# 
# ### Overview of this notebook
# - Learn about the Lake Problem, a decision-making example about pollution management
#   - Connect the Python implementation of the lake model to the EMA workbench
#   - Define and explore uncertainties and decision levers in the model
# - Investigate the behavior of the system under various scenarios and policies
#   - Visualize and analyze trade-offs between outcomes
# - Experiment with parallelization techniques to improve computational efficiency

# ### The Lake model
# The exploratory modeling workbench includes an [examples folder](https://github.com/quaquel/EMAworkbench/tree/master/ema_workbench/examples). This folder contains a variety of examples that demonstrate the functionality of the workbench. Many of these examples have been drawn from published cases. Here, we use the Lake Problem as an example for demonstrating some of the key functionality of the workbench.
# 
# We demonstrate some of the key capabilities of the exploratory modeling workbench using the Lake problem. The lake problem is a stylized and hypothetical decision problem where the population of a city has to decide on the amount of annual pollution it will put into a lake. It the pollution in the lake passes a threshold, it will suffer irreversible eutrophication (nutrient overenrichment).
# 
# #### Model
# This can be modeled as a system of ordinary differential equations (ODEs) as follows:
# 
# \begin{equation}
#     X_{(t+1)}=X_t+a_t+\frac{(X_t^q)}{(1+X_t^q )}- bX_t+\epsilon_t
# \end{equation}
# 
# where
#  - $X_t$ is the pollution at time $t$
#  - $a_t$ is the rate of anthropogenic pollution at time $t$
#  - $b$ is the lake’s natural removal rate
#  - $q$ is the lake's natural recycling rate
#  - $\epsilon_t$ is the rate of natural pollution at time $t$.
# 
# The rate of anthropogenic pollution $a_t$ is the decision variable and is somewhere between 0, and 0.1. So $a_t \in [0,0.1]$. The natural pollution $\epsilon_t$ is modeled, following Singh et al. (2015), as a log normal distribution with mean $\mu$ and standard deviation $\sigma$.
# 
# 
# #### Outcomes
# There are four outcomes of interest.
#  1. The first is the average concentration of phosphor in the lake.
# 
# \begin{equation}
#     f_{phosphorus}=  \frac{1}{\left\vert{T}\right\vert} \sum\limits_{t\in{T}} X_t 
# \end{equation}
# 
#    where $\left\vert{T}\right\vert$ is the cardinality of the set of points in time.
# 
#  2. The second objective is the economic benefit derived from polluting the lake. Following Singh et al. (2015), this is defined as the discounted benefit of pollution mines the costs of having a polluted lake
# 
# \begin{equation}
#     f_{economic} = \sum\limits_{t \in {T}}\alpha a_t \delta^t 
# \end{equation}
# 
#    where $\alpha$ is the utility derived from polluting and $\delta$ is the discount rate. By default, $\alpha$ is 0.04.
# 
#   3. The third objective is related to the year-over-year change in the anthropogenic pollution rate.
# 
# \begin{equation}
#     f_{inertia} =\frac{1}{\left\vert{T}\right\vert-1} \sum\limits_{t=1}^{\left\vert{T}\right\vert} I(|a_{t}-a_{t-1} |>\tau)   
# \end{equation}
# 
#    where $I$ is an indicator function that is 0 if the statement is false, and 1 if the statement is true, $\tau$ is the threshold that is deemed undesirable, and is for illustrative purposes et to 0.2. Effectively, f_{inertia} is the fraction of years when the absolute value of the change in anthropogenic pollution is larger then $\tau$.
# 
#  4. The fourth objective is the fraction of years when the pollution in the lake is below the critical threshold.
# 
# \begin{equation}
#     f_{reliability} =  \frac{1}{\left\vert{T}\right\vert} \sum\limits_{t \in T}I(X_{t}<X_{crit} ) 
# \end{equation}
# 
#    where $I$ is an indicator function that is 0 if the statement is false, and 1 if the statement is true, $X_{crit}$ is the critical threshold of pollution and is a function of both $b$ and $q$.
# 
# #### Uncertainty
# The lake problem is characterized by both stochastic uncertainty and deep uncertainty.
#  - The stochastic uncertainty arises from the natural inflow. To reduce this stochastic uncertainty, multiple replications are performed and the average over the replications is taken.
#  - Deep uncertainty is presented by uncertainty about the mean $\mu$ and standard deviation $\sigma$ of the lognormal distribution characterizing the natural inflow, the natural removal rate of the lake $\beta$, the natural recycling rate of the lake $q$, and the discount rate $\delta$. The table below specifies the ranges for the deeply uncertain factors, as well as their best estimate or default values.

# ### Assignment
# _If you at any moment get stuck on this assignment, the [General Introduction](https://emaworkbench.readthedocs.io/en/latest/indepth_tutorial/general-introduction.html) of the EMAworkbench is a good source of inspiration._
# 
# 1. Given the Python implementation of the lake problem in [`lakemodel_function.py`](lakemodel_function.py), adapt this code and connect it to the workbench.
# 
# For the uncertainties, use the following table
# 
# |Parameter	|Range	        |Default value|
# |-----------|--------------:|------------:|
# |$\mu$    	|0.01 – 0.05	|0.02         |
# |$\sigma$	|0.001 – 0.005 	|0.0017       |
# |$b$      	|0.1 – 0.45	    |0.42         |
# |$q$	    |2 – 4.5	    |2            |
# |$\delta$	|0.93 – 0.99	|0.98         |
# 
# For now, assume that for each year a release decision is made. The release is between 0 and 0.1. Carefully look at line 24 in `lakemodel_function.py` to identify the name to use for each lever.

# In[5]:



from lakemodel_function import lake_problem
import numpy as np 
from ema_workbench import (RealParameter, ScalarOutcome, Constant,
                           Model)
 

# Instantiate the model

model = Model('lakeproblem', function=lake_problem)

# Specify uncertainties

model.uncertainties = [RealParameter('mean', 0.01, 0.05),
                       RealParameter('stdev', 0.001, 0.005),
                       RealParameter('b',0.1,0.45),
                       RealParameter('q',2,4.5),
                       RealParameter('delta',0.93,0.99)]


# Set levers, one for each time step

model.levers = [RealParameter("c1", -2, 2),
                RealParameter("c2", -2, 2),
                RealParameter("r1", 0, 2),
                RealParameter("r2", 0, 2),
                RealParameter("w1", 0, 1)]
def process_p(values):
    values = np.asarray(values)
    values = np.mean(values, axis=0)
    return np.max(values)
# Specify outcomes

model.outcomes = [ScalarOutcome('max_P'),
                  ScalarOutcome('utility'),
                  ScalarOutcome('inertia'),
                  ScalarOutcome('reliability')
]


# why is this needed?
model.constants = [
    Constant("alpha", 0.41),
    Constant("nsamples", 150),
]


# 2. Explore the behavior of the system in the absence of any release using 1000 scenarios, and the default sampling approach.
#     * visualize the outcomes of interest, are there any apparent trade-offs?
#     * can you visually identify the uncertainties that drive system behavior?
# 

# In[6]:


from ema_workbench import MultiprocessingEvaluator, ema_logging, perform_experiments
if __name__ == "__main__":
    ema_logging.log_to_stderr(ema_logging.INFO)


    with MultiprocessingEvaluator(model) as evaluator:
        results = evaluator.perform_experiments(scenarios=1000, policies=4)

#from ema_workbench import SequentialEvaluator

#with SequentialEvaluator(model) as evaluator:
#    experiments, outcomes = evaluator.perform_experiments(scenarios=1000)

# Hint: A great moment to take another look at the examples!


# In[ ]:





# In[13]:


import pandas as pd
data = pd.DataFrame(outcomes)


# In[18]:


import seaborn as sns
import matplotlib.pyplot as plt
sns.pairplot(data, vars=list(outcomes.keys()))
plt.show()


# 3. Explore the behavior of the system over 1000 scenarios for 4 randomly sampled candidate strategies.
#     * visualize the outcomes of interest
#     * what can you say about how the release decision influences the system?

# In[ ]:





# 4. If you have not used parallelization in the foregoing, try to adapt your code to use parallelization. The workbench comes with two evaluators for parallelization. The `MultiProcessingingEvaluator` and the `IpyparallelEvaluator`. When can you use each? Adapt your code from above and sue the `MultiProcessingingEvaluator`. Use the `time` or `timeit` library to check how much faster the computation for 1000 scenarios completes.
# 
# #### A note on parallelization in Jupyter notebooks
# Using multiprocessing within a Jupyter notebook is tricky. On Linux it will work in general just fine. On a Mac it depends on the version of macOS and the version of Python. If you are on the latest version of macOS in combination with Python 3.8, it might work but no guarantees. On older versions of Python it should work fine. On Windows it is always a problem.
# 
# The underlying explanation is quite technical. It has to do with how your operating system creates the additional python processes. On Windows, and the latest version of macOS in combination with Python 3.8. A completely new Python process is spawned. This new process does **not** inherit what is defined in memory of the parent process. The new child process will try to replicate what is in memory of the parent process by executing many of the import statements that have also been executed within the python process. Thus, if you define a model in the main process, it is not guaranteed to be known in the child processes. This is in particular true if you define the model within a jupyter notebook. Then the child processes will **never** know this function. Within jupyter notebooks, therefore, the best practice is to define your model within a `.py` file and import this `.py` file into the notebook. Now, each of the child processes will also execute this import statement and thus know the function.
# 

# In[ ]:





# #### Conclusion
# ...
