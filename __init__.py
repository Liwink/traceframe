from __future__ import unicode_literals

import sys
import tempfile
import webbrowser
import pygraphviz as pgv


G = pgv.AGraph(strict=False, directed=True)


def _format_subgraph_set(stack):
    subgraph_set = {}

    for frame in stack:
        filename = frame.f_code.co_filename
        if filename not in subgraph_set:
            subgraph_set[filename] = G.add_subgraph(
                name='cluster' + filename,
                label=filename
            )

        node = _format_node(frame)
        firstlineno = frame.f_code.co_firstlineno
        function = frame.f_code.co_name

        # Node is inherit str (wow so `G.add_edge(str1, str2)`
        subgraph_set[filename].add_node(
            node,
            label='{0}:{1}'.format(firstlineno, function)
        )

    return subgraph_set


def _format_node(frame):
    return '{0}:{1}:{2}'.format(frame.f_code.co_filename,
                                frame.f_code.co_firstlineno,
                                frame.f_code.co_name)


def _frame_stack(frame):
    node_set = set()

    while frame:
        node = _format_node(frame)
        if node in node_set:
            continue
        node_set.add(node)

        yield frame
        frame = frame.f_back


def _add_edge(start, end, color, index):
    start_lineno = start.f_lineno

    G.add_edge(
        _format_node(start),
        _format_node(end),
        color=color,
        ltail='cluster' + start.f_code.co_filename,
        lhead='cluster' + end.f_code.co_filename,
        label='#{0} at {1}'.format(index + 1, start_lineno)
    )


def cheese(frame=None, slient=False):

    if not frame:
        frame = sys._getframe().f_back


    stack = list(_frame_stack(frame))
    subgraph_set = _format_subgraph_set(stack)

    len_stack = len(stack)
    stack.reverse()

    for index, start in enumerate(stack):

        if index + 1 == len_stack:
            break

        if index == 0:
            color = 'green'
        elif index == len_stack - 2:
            color = 'red'
        else:
            color = 'black'

        _add_edge(start, stack[index + 1], color, index)

    _, name = tempfile.mkstemp('.png')

    G.draw(name, prog='dot')
    G.close()

    if not slient:
        webbrowser.open('file://' + name)

    return name


if __name__ == '__main__':
    # test
    def outer():
        def inner():
            cheese()
        inner()

    outer()
