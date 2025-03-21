# Programming III

Data processing Programming III course for the master Data Science for Life Science. See also [Time Series](https://fennaf.gitbook.io/bfvm22prog1/time-series) and [Streaming Data](https://fennaf.gitbook.io/bfvm22prog1/streaming-data).

This repo has the following directories:

- `assessment`: In this folder you find all the Notebooks that you need to work on in preperation for the lessons(formative) and the final assignment (summative).
- `demos`: Lots of notebooks that we are using during the module, or not. Feel free to open one that seems to offer what you are interested in.
- `exercises`: Notebooks with some extra exercises (hence the name).
- `scripts`: Demo scripts such client server communication scripts. All the *on-the-fly-scripts* that we will work on during the lectures will also be put into this directory.


## Create a virtual environment to install the dependencies

Login the linux grid. Open the terminal. Choose a path and a name for your virtual environment, for instance `.venv/dsls`. Have a look at [the file `requirements.txt`](requirements.txt) to see what we are using.


```
#create a new environment
python3 -m venv {path/to/new/virtual/environment} {name}

#activate the virtualenv
source {path/to/new/virtual/environment}{name}/bin/activate 

#install the necessary requirements
python -m pip install -r requirements.txt

#create jupyter notebook kernel for venv
python -m ipykernel install --user --name={name}
```

Make sure that you use the created kernel in your jupyter notebook or visual studio code (you should be able to do that by now).

contact information: f.feenstra@pl.hanze.nl
