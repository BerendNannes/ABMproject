# Gentrification model

Our gentrification model is an Agent-based model which tries to capture the dynamics of gentrification using agents with only economic properties and a global status variable of the environment which is partially dependent on the changes in the economic state of all agents. The environment represents a single neighborhood and the agents represent the residential properties within this neighborhood.

The model is implemented in model.py and can be run interactively by running "python run.py" in the command line. The implementation makes use of the mesa library, which is an open-source Agent-based modeling library in python.

An analysis of the model is presented in the analysis.ipynb notebook. 
The global sensitivity analysis is presented in the sensitivity.ipynb notebook.
