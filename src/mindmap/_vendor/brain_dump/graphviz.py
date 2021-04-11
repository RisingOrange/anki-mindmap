from ..pydot import pydot
from .parsers.indented_text_graph import parse as parse_text_graph


class Theme:
    SOLARIZED_BG_COLOR = '#012b37'

    BRIGHT_EDGE_COLORS = [  # Pallette from https://flatuicolors.com/palette/defo
        '#f1c40f',
        '#e67e22',
        '#8e44ad',
        '#e74c3c',
        '#2980b9',
        '#c0392b',
        '#1abc9c',
        '#27ae60',
        '#95a5a6',
    ]

    SOLARIZED_EDGE_COLORS = [  # Palette from http://ethanschoonover.com/solarized
        '#b58900',
        '#cb4b16',
        '#6c71c4',
        '#dc323f',
        '#268bd2',
        '#d33682',
        '#2aa198',
        '#859900',
        '#939393',
    ]

    def __init__(self, bg_color, label_color, edge_colors):
        self.graph_style = dict(
            layout='twopi',
            overlap='false',
            splines='curved',
            fontname='arial',
            bgcolor=bg_color,
            outputorder="edgesfirst",
        )
        self.label_color = label_color
        self.edge_colors = edge_colors

    def edge_style(self, graph, dest_node, width_percentage):
        color = self.edge_colors[dest_node.branch_id % len(self.edge_colors)]
        return dict(
            color=color,
            dir='none',
            penwidth=2 * (2 + graph.height - dest_node.depth)
        )

    def node_style(self, node, graph):
        node_text = ' '.join(node.content.strip().split()[:-1])
        label = (
            node_text
            if node_text and node_text != node.ROOT_DEFAULT_NAME
            else ''
        )
        return dict(
            group=node.branch_id,
            shape='plaintext',
            label=label,
            fontcolor=self.label_color,
            fontsize= 2 * (16 + graph.height - node.depth),
            fontname=self.graph_style['fontname'],  # not inherited by default
        )

class ShowNoteDistributionTheme(Theme):

    def edge_style(self, graph, dest_node, width_percentage):
        color = self.edge_colors[dest_node.branch_id % len(self.edge_colors)]
        return dict(
            color=color,
            dir='none',
            penwidth=max(130 * width_percentage, 7)
        )


THEMES = [
    'dark solarized',
    'bright'
]

def theme(name, scale_branches):
    if scale_branches:
        class_ = ShowNoteDistributionTheme
    else:
        class_ = Theme

    if name == 'dark solarized':
        return class_(Theme.SOLARIZED_BG_COLOR, 'white', Theme.SOLARIZED_EDGE_COLORS)
    if name == 'bright':
        return class_('white', 'black', Theme.BRIGHT_EDGE_COLORS)
    
    





def create_mindmap_img(graph_markdown, output_file_path, theme, root_label=None):
    graph = parse_text_graph(graph_markdown, root_label=root_label)
    pygraph = pydot.Dot(root=graph.content, **theme.graph_style)
    for node in graph:
        # avoid erroneous pydot 'port' detection + workaround this: https://github.com/erocarrera/pydot/issues/187
        content = pydot.quote_if_necessary(node.content)
        pygraph.add_node(pydot.Node(
            content, **theme.node_style(node, graph)))
        if node.parent:
            parent_content = node.parent.content if ':' not in node.parent.content else '"{}"'.format(
                node.parent.content)

            a_theme = theme.edge_style(
                graph, node, float(node.content.split()[-1]))
            pygraph.add_edge(pydot.Edge(parent_content, content, **a_theme))

    pygraph.write_svg(output_file_path)
