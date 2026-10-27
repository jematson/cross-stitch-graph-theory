from graphics import *
import time

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


def cross_parity(cross):
    """ Return true for an even parity cross, false for odd """
    return ( (cross[0] + cross[1]) % 2 ) == 0


def visualize_from_crosses(pattern, maxdim):
    win = GraphWin(width = 800, height = 800)
    win.setCoords(0, maxdim, maxdim, 0)

    for cross in pattern:
        nw = Point(cross[0], cross[1])
        sw = Point(cross[0], cross[1] + 1)
        ne = Point(cross[0] + 1, cross[1])
        se = Point(cross[0] + 1, cross[1] + 1)

        color = "blue"# if cross_parity(cross) else "green"

        under = Line(sw, ne)
        under.setOutline(color)
        under.setWidth(10)
        under.draw(win)

        over = Line(nw, se)
        over.setOutline(color)
        over.setWidth(10)
        over.draw(win)

    win.getMouse()
    win.close()



def visualize_path(patterns, maxdim, sleeptime, linewidth):
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
            line.setWidth(linewidth)
        else:
            line.setOutline("blue")
            line.setWidth(linewidth)
            
        line.draw(win)
        time.sleep(sleeptime)

    win.getMouse()
    win.close()