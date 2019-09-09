import pandas as pd
import numpy as np
import snap
from tqdm import tqdm

def generateTables(targetpath, netfile, net):
    #split file into node and edge file
    net_file = open(targetpath+netfile+'.csv', 'r') 
    nodes_file = open(targetpath+netfile+'_nodes.csv', 'w')
    nodes_file.write('id\tusername\n')
    edges_file = open(targetpath+netfile+'_edges.csv', 'w')
    edges_file.write('source\ttarget\n')

    n_nodes = net.GetNodes()
    n_edges = net.GetEdges()

    line_num = 0 
    for line in net_file:
        if line_num>=4 and line_num < (n_nodes+4) : # 4 headers
            nodes_file.write(line)
        elif line_num >= (n_nodes+6) and line_num < (n_nodes+6+n_edges): #skip #END
            edges_file.write(line)
        line_num = line_num + 1

graphpath = 'graphs/'        
gitpath = graphpath + 'commits/'
issuespath  = graphpath + 'issues/'
prpath = graphpath + 'pullrequests/'
outpath = graphpath + 'supergraphs/'

projects = pd.read_csv('project.csv')
projects['mappedname'] = projects['name'].apply(lambda x: x.replace('/', '__').replace('-', '_'))

N = projects.shape[0]
for index, row in tqdm(projects.iterrows()):

    # Git commits graph
    pname = row['mappedname']
    gitpnodes = pd.read_csv(gitpath + pname + '_nodes.csv')[['id', 'username']]
    gitpnodes['username'] = gitpnodes['username'].apply(lambda x: x if len(x.split(' '))== 1 else x.split(' ')[0][:-1])
    gitpedges = pd.read_csv(gitpath + pname + '_edges.csv')

    r1 = gitpedges.merge(gitpnodes, left_on='source', right_on='id').drop(['id','source'], axis=1).rename({'username': 'source'}, axis=1)
    r2 = r1.merge(gitpnodes, left_on='target', right_on='id').drop(['id','target'], axis=1).rename({'username': 'target'}, axis=1)
    r2 = r2.drop('weight', axis=1)
   
    pid = row['id']
    
    # Github issues graph
    issuesnodes = pd.read_csv(issuespath + str(pid) + '_is_nodes_reduced.csv')
    issuesedges = pd.read_csv(issuespath + str(pid) + '_is_edges_reduced.csv')[['source', 'target']]
    
    # Github pull requests graph
    prnodes = pd.read_csv(prpath + str(pid) + '_pr_nodes_reduced.csv')
    predges = pd.read_csv(prpath + str(pid) + '_pr_edges_reduced.csv')[['source', 'target']]

    # Merge in a single nodes and edges files
    usernodes = pd.DataFrame(list(issuesnodes['id']) + list(gitpnodes['username']) + list(prnodes['id']), 
                                                                                 columns=['username']).drop_duplicates()
    useredges = pd.concat([r2, issuesedges, predges]).drop_duplicates()
    usernodes.to_csv('temp/mergednodes.csv', index=None)
    useredges.to_csv('temp/mergededges.csv', index=None)

    # Build graph from temp files using SNAP library
    context = snap.TTableContext()
    e_schema = snap.Schema()
    e_schema.Add(snap.TStrTAttrPr("source", snap.atStr))
    e_schema.Add(snap.TStrTAttrPr("target", snap.atStr))
    n_schema = snap.Schema()
    n_schema.Add(snap.TStrTAttrPr("username", snap.atStr))

    edgetable = snap.TTable.LoadSS(e_schema, 'temp/mergededges.csv', context, ",", snap.TBool(True))
    nodetable = snap.TTable.LoadSS(n_schema, 'temp/mergednodes.csv', context, ",", snap.TBool(True))


    edgeattrv = snap.TStrV()
    nodeattrv = snap.TStrV()
    nodeattrv.Add("username")

    net = snap.ToNetwork(snap.PNEANet, edgetable, "source", "target", edgeattrv, nodetable, "username", nodeattrv, 
                         snap.aaFirst)

    # Need to remove self-edges to compute rich club coefficient
    snap.DelSelfEdges(net)

    # Store the results
    name = str(pid) + '_usergraph'
    snap.SaveEdgeListNet(net, outpath + name + '.csv', 'Network of issues, PR and commits')
    generateTables(outpath, name, net)