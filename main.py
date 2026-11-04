import xml.etree.ElementTree as ET
import math
import sys

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




def parse_oxs_xml(tree):
    root = tree.getroot()

    # Return a dictionary of adjacency lists, one for each palette color
    cross_patterns = {}
    colors = {}
    maxdim = 0

    for item in root.find("palette"):
        i = item.get("index")
        color = item.get("color")
        colors[i] = "#" + color

    for stitch in root.find("fullstitches"):
        i = stitch.get("palindex")
        x = int(stitch.get("x"))
        y = int(stitch.get("y"))

        if x > maxdim:
            maxdim = x + 2
        if y > maxdim:
            maxdim = y + 2

        if i not in cross_patterns:
            cross_patterns[i] = {}
        
        crosses = cross_patterns[i]

        crosses[(x, y)] = 0

    return cross_patterns, colors, maxdim



def find_contiguous_regions(crosses):
    regions = []

    def dfs_connect(cross, region_so_far):
        s = (cross[0] + 1, cross[1])
        n = (cross[0] - 1, cross[1])
        w = (cross[0], cross[1] - 1)
        e = (cross[0], cross[1] + 1)

        if s in crosses and s not in region_so_far:
            region_so_far.append(s)
            crosses.remove(s)
            region_so_far = dfs_connect(s, region_so_far)
        if n in crosses and n not in region_so_far:
            region_so_far.append(n)
            crosses.remove(n)
            region_so_far = dfs_connect(n, region_so_far)
        if w in crosses and w not in region_so_far:
            region_so_far.append(w)
            crosses.remove(w)
            region_so_far = dfs_connect(w, region_so_far)
        if e in crosses and e not in region_so_far:
            region_so_far.append(e)
            crosses.remove(e)
            region_so_far = dfs_connect(e, region_so_far)
        if cross in crosses:
            crosses.remove(cross)
        return region_so_far

    while crosses:
        cross = crosses[0]
        region = dfs_connect(cross, [cross])
        regions.append(region)

    return regions



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
def contiguous_region_path_with_start_and_end(start_cross, end_cross, region):
    if cross_parity(start_cross) != cross_parity(end_cross):
        print("START AND END MUST BE SAME PARITY")
        return
    
    # Find single-pass line from start to end
    final_path = [start_cross]

    def final_path_recurse(curr_cross, current_path):
        # Base case: reached end cross
        if curr_cross == end_cross:
            return current_path, True

        # 

        # N
        N = (curr_cross[0], curr_cross[1] - 2)
        if N in region and N not in current_path:
            current_path.append(N)
            current_path, done = final_path_recurse(N, current_path)
            if done:
                return current_path, True
            else:
                current_path.remove(curr_cross)

        # NE
        NE = (curr_cross[0] + 1, curr_cross[0] - 1)
        if NE in region and NE not in current_path:
            current_path.append(NE)
            current_path, done = final_path_recurse(NE, current_path)
            if done:
                return current_path, True
            else:
                current_path.remove(curr_cross)

        # E
        E = (curr_cross[0] + 2, curr_cross[1])
        if E in region and E not in current_path:
            current_path.append(E)
            current_path, done = final_path_recurse(E, current_path)
            if done:
                return current_path, True
            else:
                current_path.remove(curr_cross)

        # SE
        SE = (curr_cross[0] + 1, curr_cross[1] + 1)
        if SE in region and SE not in current_path:
            current_path.append(SE)
            current_path, done = final_path_recurse(SE, current_path)
            if done:
                return current_path, True
            else:
                current_path.remove(curr_cross)

        # S
        S = (curr_cross[0], curr_cross[1] + 2)
        if S in region and S not in current_path:
            current_path.append(S)
            current_path, done = final_path_recurse(S, current_path)
            if done:
                return current_path, True
            else:
                current_path.remove(curr_cross)

        # SW
        SW = (curr_cross[0] - 1, curr_cross[1] + 1)
        if SW in region and SW not in current_path:
            current_path.append(SW)
            current_path, done = final_path_recurse(SW, current_path)
            if done:
                return current_path, True
            else:
                current_path.remove(curr_cross)
        # W
        W = (curr_cross[0] - 2, curr_cross[1])
        if W in region and W not in current_path:
            current_path.append(W)
            current_path, done = final_path_recurse(W, current_path)
            if done:
                return current_path, True
            else:
                current_path.remove(curr_cross)

        # NW
        NW = (curr_cross[0] - 1, curr_cross[1] - 1)
        if NW in region and NW not in current_path:
            current_path.append(NW)
            current_path, done = final_path_recurse(NW, current_path)
            if done:
                return current_path, True
            else:
                current_path.remove(curr_cross)
        
        return current_path, False

    final_path = final_path_recurse(start_cross, final_path)

    return final_path

    # From a cross, the next possible ones are the diagonals or one away



    # DFS filling in from that line


def main():
    sys.setrecursionlimit(10**6)

    tree = ET.parse(r"oxs_files/square.oxs")
    
    crosses, colors, maxdim = parse_oxs_xml(tree)


    for p in crosses:
        pattern = crosses[p]
        color = colors[p]

        regions = find_contiguous_regions(list(pattern.keys()))

        #visualize_from_crosses(pattern, color, maxdim+1)
        l, done = contiguous_region_path_with_start_and_end((1, 1), (3, 3), regions[0])
        print(l)
        visualize_from_crosses(l, color, maxdim+1)

        # for region in regions:
        #     print(len(region))
        #     first_cross = Cross(region[0])
        #     pattern, stitch_route, cv = contiguous_region_path(pattern, first_cross, first_cross.SW, "", [])
        #     visualize_path(stitch_route, maxdim=maxdim+1, sleeptime=0, linewidth=1)
    
    


if __name__ == "__main__":
    main()

