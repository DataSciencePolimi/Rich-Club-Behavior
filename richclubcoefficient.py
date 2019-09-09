import pandas as pd
import networkx as nx
import snap
import json
import argparse
import sys
from tqdm import tqdm

sourcepath = 'graphs/'
outpath = 'coefficients/'

def get_lists(rc):
    x = []
    y = []
    for k in rc:
        x.append(k)
        y.append(rc[k])
    
    return (x, y)

def get_supergraph(path):
    # open edgelist using networkx
    Data = open(path + '{}_usergraph_edges.csv'.format(p), "r")
    next(Data, None) 
    Graphtype = nx.Graph()

    G = nx.parse_edgelist(Data, delimiter='\t', create_using=Graphtype,
                          nodetype=int, data=(('weight', float),))
    return G
    
def get_activity_graph(path, atype):
        context = snap.TTableContext()
        e_schema = snap.Schema()
        e_schema.Add(snap.TStrTAttrPr("source", snap.atStr))
        e_schema.Add(snap.TStrTAttrPr("target", snap.atStr))
        e_schema.Add(snap.TStrTAttrPr("count", snap.atStr))
        n_schema = snap.Schema()
        n_schema.Add(snap.TStrTAttrPr("id_user", snap.atStr))
        n_schema.Add(snap.TStrTAttrPr("id", snap.atStr))

        edgetable = snap.TTable.LoadSS(e_schema, path + '{}_{}_edges_reduced.csv'.format(p, atype), context, ",", snap.TBool(True))
        nodetable = snap.TTable.LoadSS(n_schema, path + '{}_{}_nodes_reduced.csv'.format(p, atype), context, ",", snap.TBool(True))


        edgeattrv = snap.TStrV()
        nodeattrv = snap.TStrV()

        net = snap.ToNetwork(snap.PNEANet, edgetable, "source", "target", edgeattrv, nodetable, "id", nodeattrv, snap.aaFirst)
        snap.DelSelfEdges(net)
        snap.SaveEdgeList(net, 'temp/{}_temp_edgelist.csv'.format(atype))
        
        Data = open('temp/{}_temp_edgelist.csv'.format(atype), 'r')
        Graphtype = nx.Graph()

        G = nx.parse_edgelist(Data, delimiter='\t', create_using=Graphtype, nodetype=int, data=(('weight', float),), comments='#')
        
        return G
        
def get_commits_graph(path):
        context = snap.TTableContext()
        e_schema = snap.Schema()
        e_schema.Add(snap.TStrTAttrPr("source", snap.atStr))
        e_schema.Add(snap.TStrTAttrPr("target", snap.atStr))
        e_schema.Add(snap.TStrTAttrPr("weight", snap.atStr))
        n_schema = snap.Schema()
        n_schema.Add(snap.TStrTAttrPr("id", snap.atStr))
        n_schema.Add(snap.TStrTAttrPr("username", snap.atStr))
        n_schema.Add(snap.TStrTAttrPr("size", snap.atStr))

        edgetable = snap.TTable.LoadSS(e_schema, path + '{}_edges.csv'.format(pname), context, ",", snap.TBool(True))
        nodetable = snap.TTable.LoadSS(n_schema, path + '{}_nodes.csv'.format(pname), context, ",", snap.TBool(True))


        edgeattrv = snap.TStrV()
        nodeattrv = snap.TStrV()

        net = snap.ToNetwork(snap.PNEANet, edgetable, "source", "target", edgeattrv, nodetable, "id", nodeattrv, snap.aaFirst)
        snap.DelSelfEdges(net)
        snap.SaveEdgeList(net, 'temp/commits_temp_edgelist.csv')
        
        Data = open('temp/commits_temp_edgelist.csv', 'r')
        Graphtype = nx.Graph()
        G = nx.parse_edgelist(Data, delimiter='\t', create_using=Graphtype, nodetype=int, data=(('weight', float),), comments='#')
        
        return G
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Rich-club coefficient calculation.')
    parser.add_argument('--graph', type=str, default='G', help='Source graph for coefficient computation')
    parser.add_argument('--N', type=int, default=20, help='Number of projects for which compute the coefficient')
    
    
    args = parser.parse_args()
    
    projects = pd.read_csv('project.csv')[:args.N]
    
    # rich-club coefficient dictionary
    # each project is referred using the id_project as keys
    rcc = {}
    
    # select path for source graphs
    if args.graph == 'G':
        path = sourcepath + 'supergraphs/'
        outname = 'supergraph'
    elif args.graph == 'i':
        path = sourcepath + 'issues/'
        outname = 'issues'
    elif args.graph == 'p':
        path = sourcepath + 'pullrequests/'
        outname = 'pullrequests'
    elif args.graph == 'c':
        path = sourcepath + 'commits/'
        outname = 'commits'
    else:
        print('Error in input parameter: only G, i, p, c are allowed')
        sys.exit(1)
    
    num = projects.shape[0]
    for index, row in tqdm(projects.iterrows()):
        p = str(row['id'])
        pname = row['name']
        
        try:
            if args.graph == 'G':
                G = get_supergraph(path)
               
            elif args.graph == 'i':
                G = get_activity_graph(path, 'is')
            
            elif args.graph == 'p':
                G = get_activity_graph(path, 'pr')
                
            elif args.graph == 'c':
                G = get_commits_graph(path)
            
            rc = nx.algorithms.richclub.rich_club_coefficient(G, normalized=True)
            k, phi = get_lists(rc)
            
            rcc[p] = {}
            rcc[p]['k'] = k
            rcc[p]['phi'] = phi
        except Exception as e:
            print('Cannot calculate coefficient for this project: {}'.format(p))
        
        
    # for each project a dictionary {k:[], rho:[]} is defined with the list of degrees and correspondent coefficient values
    with open(outpath + 'rcc_{}.json'.format(outname), 'w') as fp:
        json.dump(rcc, fp)
                    
