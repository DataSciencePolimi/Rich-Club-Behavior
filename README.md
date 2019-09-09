## How ro reproduce results

Scripts to calculate rich-club coefficients are included, as well as to generate the supergraphs from source interaction graphs (Github activities: commits, PR, issues). More details in the paper: "Analyzing Rich-Club Behavior in Open Source Projects".

In order to use the code, please install all the dependencies:
- Main dependencies are defined in _requirements.txt_ file
- SNAP library for graph manipulation can be installed following instructions from its [website](http://snap.stanford.edu/snappy/index.html)

After dependencies installation, follow these instructions:
1. Run the script to generate supergraphs: ```python generate_supergraphs.py```
2. Run the script to calculate the rich-club coefficient for a specific set of graphs. 
	Parameters:
	- ```--graph```: select the source graphs for coefficient calculation. Available values: _G_ (supergraph); _i_ (issues); _p_ (pull-requests); _c_ (commits)
	- ```--N```: number of graphs for which run the calculation (based on analyzed projects in the paper, refer to _project.csv_ for the complete list)

Example: 
			```python richclubcoefficient.py --graph G --N 10``` 
               
computes the coefficient for the supergraphs for the first 10 projects.

Note that computation of coefficients is not always successfull (as stated in the paper), and it can take much time for big graphs.
