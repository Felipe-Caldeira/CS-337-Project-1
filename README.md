# CS-338-Project-1: Golden Globes Twitter analyzer

## Instructions:

### Installation:

Set up a conda environment with Python 3.8.

```
conda create -n new_env_name python=3.8
```

```
pip install -r requirements.txt
```

If the autograder is missing a `sqlite3` DLL file, you can fix it by manually installing the DLL file from online and placing it in the DLLs folder in the Anaconda directory.

### Running the autograder:

```
python -c 'import gg_api; gg_api.pre_ceremony(2013)'
python autograder.py 2013
python sentiment_analysis.py 2013
```

etc. for each year desired

## Additional Goals

Note how it prints out the Twitter consensus of who was the best dressed at the end of the preceremony. It also downloads pictures of the best dressed into a folder called "simple_images".

We also run sentiment analysis on the hosts in the file `sentiment_analysis.py`. We take the average of the sentiment in all host-related tweets and print it out. The sentiment is on a scale of -1.0 (very negative) to 1.0 (very positive).
