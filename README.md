# CS-338-Project-1: Golden Globes Twitter analyzer

## Github Repository:
https://github.com/Felipe-Caldeira/CS-337-Project-1

## Instructions:

### Installation:

Set up a conda environment with Python 3.8.

```
conda create -n new_env_name python=3.8
```

Install modules.

```
pip install -r requirements.txt
```

If the autograder is missing a `sqlite3` DLL file, you can fix it by manually installing the DLL file from online and placing it in the DLLs folder in the Anaconda directory.
https://www.sqlite.org/download.html

There may be some issues installing the spacy. If so, comment out those modules from requirements.txt, and run:

```
pip install spacy
python -m spacy download en_core_web_sm
```


### Running the autograder:

```
python -c 'import gg_api; gg_api.pre_ceremony(2013)'
python autograder.py 2013
```

etc. for each year desired

## Additional Goals

Note how it prints out the Twitter consensus of who was the best dressed at the end of the preceremony. It also downloads pictures of the best dressed into a folder called "simple_images".

We also run sentiment analysis on the hosts in the preceremony. We look for the most common sentiment out of a large, standard list of emotions and print it out, along with an example Tweet with that sentiment.
