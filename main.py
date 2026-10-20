import xml.etree.ElementTree as ET
import math
from graphics import *



class Cross:
    def __init__(self, xy):
        self.x = xy[0]
        self.y = xy[1]
    
        self.N = (self.x, self.y - 1)
        self.E = (self.x + 1, self.y)
        self.S = (self.x, self.y + 1)
        self.W = (self.x - 1, self.y)

        self.NE = (self.x + 1, self.y)
        self.NW = (self.x, self.y)
        self.SW = (self.x, self.y + 1)
        self.SE = (self.x + 1, self.y + 1)

        self.xy = (self.x, self.y)


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


def visualize(patterns, colors, maxdim):
    win = GraphWin(width = 800, height = 800)

    win.setCoords(0, maxdim, maxdim, 0)

    for graph in patterns:
        color = colors[graph]
        for vertex in patterns[graph]:
            pt1 = Point(vertex[0], vertex[1])
            pt1.setWidth
            #pt1.draw(win)
            for edge in patterns[graph][vertex]:
                pt2 = Point(edge[0], edge[1])
                #pt2.draw(win)
                line = Line(pt1, pt2)

                line.setOutline(color)
                line.setWidth(10)
                line.draw(win)

    win.getMouse()
    win.close()


def visualize_path(patterns, maxdim):
    win = GraphWin(width = 800, height = 800)

    win.setCoords(0, maxdim, maxdim, 0)

    for edge in patterns:
        v1 = edge[0]
        v2 = edge[1]
        pt1 = Point(v1[0], v1[1])
        pt1.setWidth
        pt2 = Point(v2[0], v2[1])
        line = Line(pt1, pt2)

        if v1[0] == v2[0] or v1[1] == v2[1]:
            line.setOutline("red")
            line.setWidth(5)
        else:
            line.setOutline("blue")
            line.setWidth(10)
            

        line.draw(win)

    win.getMouse()
    win.close()


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


def main():
    tree = ET.parse(r"square.oxs")
    
    stitches, crosses, colors, maxdim = parse_oxs_xml(tree)
    visualize(stitches, colors, maxdim+1)

    for p in crosses:
        pattern = crosses[p]

        # TODO: Actually choose first cross from pattern
        first_cross = Cross((1, 1))
        pattern, stitch_route, cv = contiguous_region_path(pattern, first_cross, first_cross.SW, "", [])
        print(stitch_route)
        visualize_path(stitch_route, maxdim+1)
    
    


if __name__ == "__main__":
    main()

