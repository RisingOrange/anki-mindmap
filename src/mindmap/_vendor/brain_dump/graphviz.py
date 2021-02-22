import locale
from ..pydot import pydot

from .parsers.indented_text_graph import parse as parse_text_graph


class DarkSolarizedTheme:
    DARKGREYBLUE = '#012b37'
    # Palette from http://ethanschoonover.com/solarized
    YELLOW = '#b58900'
    ORANGE = '#cb4b16'
    VIOLET = '#6c71c4'
    RED = '#dc323f'
    BLUE = '#268bd2'
    MAGENTA = '#d33682'
    CYAN = '#2aa198'
    GREEN = '#859900'
    GREY = '#939393'

    EDGE_COLORS = [YELLOW, ORANGE, VIOLET, RED, BLUE, MAGENTA, CYAN, GREEN, GREY]

    def __init__(self, layout, font):
        self.graph_style = dict(
            layout=layout,
            overlap='false',
            splines='curved',
            fontname=font,
            bgcolor=self.DARKGREYBLUE,
            outputorder="edgesfirst",
        )

    def edge_style(self, dest_node, graph_height):
        color = self.EDGE_COLORS[dest_node.branch_id % len(self.EDGE_COLORS)]
        return dict(
            color=color,
            dir='none',
            penwidth=2 * (2 + graph_height - dest_node.depth),
        )

    def node_style(self, node, graph_height):
        color = 'white'
        label = node.content.strip() if node.content and node.content != node.ROOT_DEFAULT_NAME else ''
        return dict(
            group=node.branch_id,
            shape='plaintext',
            label=label,
            fontcolor=color,
            fontsize=2 * (16 + graph_height - node.depth),
            fontname=self.graph_style['fontname'], # not inherited by default
        )


def create_solarized_mindmap_img(input_filepath, output_file_path, theme=DarkSolarizedTheme('twopi', 'arial'), root_label=None):
    assert locale.getdefaultlocale()[1] == 'UTF-8' # needed to print 'Duplicate content' warning without error and to bypass pydot Dot.write default raw formatting on line 1769
    with open(input_filepath) as txt_file:
        text = txt_file.read()
    graph = parse_text_graph(text, root_label=root_label)
    create_mindmap(graph, output_file_path, theme=theme)

def create_mindmap(graph, output_svg_path, theme):
    graph_height = graph.height
    pygraph = pydot.Dot(root=graph.content, **theme.graph_style)
    for node in graph:
        content = pydot.quote_if_necessary(node.content) # avoid erroneous pydot 'port' detection + workaround this: https://github.com/erocarrera/pydot/issues/187
        pygraph.add_node(pydot.Node(content, **theme.node_style(node, graph_height)))
        if node.parent:
            parent_content = node.parent.content if ':' not in node.parent.content else '"{}"'.format(node.parent.content)
            pygraph.add_edge(pydot.Edge(parent_content, content, **theme.edge_style(node, graph_height)))
    pygraph.write_svg(output_svg_path, prog='twopi')

