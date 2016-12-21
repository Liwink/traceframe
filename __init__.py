from __future__ import unicode_literals

import sys
import tempfile
import webbrowser
import pygraphviz as pgv


subgraph_set = {}
G = pgv.AGraph(strict=False, directed=True)


def _get_subgraph(filename):
    if filename not in subgraph_set:
        subgraph_set[filename] = G.add_subgraph(
            name='cluster' + filename,
            label=filename
        )
    return subgraph_set[filename]


def _format_subgraph(frame):
    filename = frame.f_code.co_filename
    if filename not in subgraph_set:
        subgraph_set[filename] = G.add_subgraph(
            name='cluster' + filename,
            label=filename
        )

    node = _format_node(frame)
    firstlineno = frame.f_code.co_firstlineno
    function = frame.f_code.co_name

    subgraph_set[filename].add_node(
        node,
        label='{0}:{1}'.format(firstlineno, function)
    )


def _format_node(frame):
    return '{0}:{1}:{2}'.format(frame.filename,
                                frame.firstlineno,
                                frame.function)


def _frame_stack(frame):
    node_set = set()
    stack = []

    while frame:
        node = _format_node(frame)
        if node in node_set:
            continue
        node_set.add(node)

        stack.insert(0, frame)
        frame = frame.f_back

    return stack

def cheese(frame=None, slient=False):

    if not frame:
        frame = sys._getframe().f_back


    stack = _frame_stack(frame)

    for frame in stack:
        _format_subgraph(frame)

    len_stack = len(stack)

    for index, start in enumerate(stack):

        if index + 1 == len_stack:
            break

        start_filename = start.f_code.co_filename
        start_lineno = start.f_lineno
        start_subgraph = subgraph_set[start_filename]

        end = stack[index + 1]
        end_filename = end.f_code.co_filename
        end_subgraph = subgraph_set[end_filename]

        if index == 0:
            color = 'green'
        elif index == len_stack - 2:
            color = 'red'
        else:
            color = 'black'

        G.add_edge(
            _format_node(start),
            _format_node(end),
            color=color,
            ltail=start_subgraph.name,
            lhead=end_subgraph.name,
            label='#{0} at {1}'.format(index + 1, start_lineno)
        )

    _, name = tempfile.mkstemp('.png')

    G.draw(name, prog='dot')
    G.close()

    if not slient:
        webbrowser.open('file://' + name)

    return name