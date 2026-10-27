import xml.etree.ElementTree as ET
import math

from cross import *
from visualizing import *


# From EmbroideryProblem repo
def standard_edge(v1, v2):
    if v1[0] < v2[0]:
        edge = (v1, v2)
    elif v1[0] > v2[0]:
        edge = (v2, v1)
    else:
        if v1[1] < v2[1]:
            edge = (v1, v2)
        elif v1[1] > v2[1]:
            edge = (v2, v1)
        else:
            print('ERROR! Caught a self loop')
            print(v1, v2)
            exit(0)
    return edge


# From EmbroideryProblem repo
def edge_length(edge):
    # Assume a edge is a tuple of 2 tuples ((a,b), (c,d))
    x_diff = edge[0][0] - edge[1][0]
    y_diff = edge[0][1] - edge[1][1]
    return math.sqrt(x_diff**2 + y_diff**2)


def parse_oxs_xml(tree):
    root = tree.getroot()

    # Return a dictionary of adjacency lists, one for each palette color
    stitch_patterns = {}
    cross_patterns = {}
    colors = {}
    maxdim = 0

    for item in root.find("palette"):
        i = item.get("index")
        color = item.get("color")
        colors[i] = "#" + color

    for stitch in root.find("fullstitches"):
        i = stitch.get("palindex")
        x1 = int(stitch.get("x"))
        y1 = int(stitch.get("y"))
        x2 = x1 + 1
        y2 = y1 + 1

        if x2 > maxdim:
            maxdim = x2
        if y2 > maxdim:
            maxdim = y2
            

        nw = (x1, y1)
        ne = (x2, y1)
        sw = (x1, y2)
        se = (x2, y2)

        if i not in stitch_patterns:
            stitch_patterns[i] = {} 
        if i not in cross_patterns:
            cross_patterns[i] = {}
        
        pattern = stitch_patterns[i]
        crosses = cross_patterns[i]

        crosses[(x1, y1)] = 0

        # add stitches nw to se and sw to ne

        if nw not in pattern:
            pattern[nw] = []
        if se not in pattern[nw]:
            pattern[nw].append(se)

        if ne not in pattern: 
            pattern[ne] = []
        if sw not in pattern[ne]:
            pattern[ne].append(sw)

        if sw not in pattern:
            pattern[sw] = []
        if ne not in pattern[sw]:
            pattern[sw].append(ne)

        if se not in pattern:
            pattern [se] = []
        if nw not in pattern[se]:
            pattern[se].append(nw)
    
    return stitch_patterns, cross_patterns, colors, maxdim



def find_contiguous_regions(crosses):
    regions = []

    def dfs_connect(cross, region_so_far):
        s = (cross[0] + 1, cross[1])
        n = (cross[0] - 1, cross[1])
        w = (cross[0], cross[1] - 1)
        e = (cross[0], cross[1] + 1)

        if s in crosses and s not in region_so_far:
            region_so_far.add(s)
            crosses.remove(s)
            region_so_far = dfs_connect(s, region_so_far)
        if n in crosses and n not in region_so_far:
            region_so_far.add(n)
            crosses.remove(n)
            region_so_far = dfs_connect(n, region_so_far)
        if w in crosses and w not in region_so_far:
            region_so_far.add(w)
            crosses.remove(w)
            region_so_far = dfs_connect(w, region_so_far)
        if e in crosses and e not in region_so_far:
            region_so_far.add(e)
            crosses.remove(e)
            region_so_far = dfs_connect(e, region_so_far)
        if cross in crosses:
            crosses.remove(cross)
        return region_so_far

    while crosses:
        cross = crosses[0]
        region = dfs_connect(cross, {cross})
        regions.append(region)
        print(region)

    return regions

    

def complete_graph(pattern):
    front_edges = {}
    back_edges = {}

    for v1 in pattern.keys():

        # Get front edges
        adj_list = pattern[v1]
        for adj in adj_list:
            edge = standard_edge(v1, adj)
            if edge not in front_edges:
                front_edges[edge] = edge_length(edge)

        # Fill in all possible back edges
        for v2 in pattern:
            if v1 != v2:
                edge = standard_edge(v1, v2)
                if edge not in back_edges:
                    back_edges[edge] = edge_length(edge)

    return front_edges, back_edges


# Find stitching route for a contiguous region, starting and ending at the same point via a depth-first traversal
def contiguous_region_path(pattern, current_cross, current_vertex, came_from, stitch_route):
    # Start with under-diagonal stitch
    # current_vertex should be SW or NE corner
    
    # SW
    if current_vertex == current_cross.SW:
        # Add SW->NE stitch to route
        next_vertex = current_cross.NE

    # NE
    elif current_vertex == current_cross.NE:
        # add NE->SW stitch to route
        next_vertex = current_cross.SW

    # Not SW or NE, error?
    else:
        print("Huh?")

    stitch_route.append((current_vertex, next_vertex))
    pattern[current_cross.xy] = 1
    current_vertex = next_vertex

    last_stitch = True

    # Check North cross exists and isn't filled yet
    if ( current_cross.N in pattern ) and ( pattern[current_cross.N] == 0 ):
        last_stitch = False

        stitch_route.append((current_vertex, current_cross.NW))
        current_vertex = current_cross.NW
        pattern, stitch_route, current_vertex = contiguous_region_path(pattern, Cross(current_cross.N), current_vertex, "South", stitch_route)

    # Check East cross
    if ( current_cross.E in pattern ) and ( pattern[current_cross.E] == 0 ):
        last_stitch = False

        stitch_route.append((current_vertex, current_cross.SE))
        current_vertex = current_cross.SE
        pattern, stitch_route, current_vertex = contiguous_region_path(pattern, Cross(current_cross.E), current_vertex, "West", stitch_route)

    # Check South cross
    if ( current_cross.S in pattern ) and ( pattern[current_cross.S] == 0 ):
        last_stitch = False

        stitch_route.append((current_vertex, current_cross.SE))
        current_vertex = current_cross.SE
        pattern, stitch_route, current_vertex = contiguous_region_path(pattern, Cross(current_cross.S), current_vertex, "North", stitch_route)

    # Check West cross
    if ( current_cross.W in pattern ) and ( pattern[current_cross.W] == 0 ):
        last_stitch = False

        stitch_route.append((current_vertex, current_cross.NW))
        current_vertex = current_cross.NW
        pattern, stitch_route, current_vertex = contiguous_region_path(pattern, Cross(current_cross.W), current_vertex, "East", stitch_route)


    # Complete over-diagonal on current_cross and return
    if came_from == "North" or came_from == "West":
        stitch_route.append((current_vertex, current_cross.SE))
        current_vertex = current_cross.SE
        stitch_route.append((current_vertex, current_cross.NW))
        current_vertex = current_cross.NW
    else:
        stitch_route.append((current_vertex, current_cross.NW))
        current_vertex = current_cross.NW
        stitch_route.append((current_vertex, current_cross.SE))
        current_vertex = current_cross.SE
    
    pattern[current_cross.xy] = 2
    return pattern, stitch_route, current_vertex


# 
def contiguous_region_path_with_start_and_end():
    print()


def main():
    tree = ET.parse(r"oxs_files/disconboxes.oxs")
    
    stitches, crosses, colors, maxdim = parse_oxs_xml(tree)
    #visualize(stitches, colors, maxdim+1)


    for p in crosses:
        pattern = crosses[p]

        find_contiguous_regions(list(pattern.keys()))

        visualize_from_crosses(pattern, maxdim+1)

        # TODO: Actually choose first cross from pattern
        first_cross = Cross((1, 1))
        pattern, stitch_route, cv = contiguous_region_path(pattern, first_cross, first_cross.SW, "", [])
        visualize_path(stitch_route, maxdim+1, 0, 1)
    
    


if __name__ == "__main__":
    main()

