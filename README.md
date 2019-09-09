## How ro reproduce results

In this folder scripts to generate the supergraphs from source interaction graphs and to calculate rich-club coefficients are included. 
In order to use the code, please install all the dependencies:
- Main dependencies are defined in _requirements.txt_ file
- SNAP library for graph manipulation can be installed following instructions from its [website](http://snap.stanford.edu/snappy/index.html)

After dependencies installation, follows these instructions:
1. Run the script to generate supergraphs: ```python generate_supergraphs.py```
2. Run the script to calculate the rich-club coefficient for a specific set of graphs. 

Example: 
					```python richclubcoefficient.py --graph G --N 10``` 
               
computes the coefficient for the supergraphs (i: issues, p: pull-requests, c: commits) for the first 10 projects of the file.

Note that computation of coefficients is successfull only for a subset of the graphs (as stated in the paper), and it can take much time for the bigger graphs.
