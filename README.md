# CS-338-Project-1: Golden Globes Twitter analyzer

## Instructions:

### Installation:

```
pip3 install -r requirements.txt
```

### Running the autograder:

```
python3 -c 'import gg_api; gg_api.pre_ceremony(2013)'
python3 autograder.py 2013
python3 sentiment_analysis.py 2013
```

etc. for each year desired

## Additional Goals

Note how it prints out the Twitter consensus of who was the best dressed at the end of the preceremony. It also downloads pictures of the best dressed into a folder called "simple_images".

We also run sentiment analysis on the hosts in the file `sentiment_analysis.py`. We take the average of the sentiment in all host-related tweets and print it out. The sentiment is on a scale of -1.0 (very negative) to 1.0 (very positive).
