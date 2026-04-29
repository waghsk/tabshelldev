#%%
import sys, os
from pathlib import Path
# Directory containing the current file
base_dir = Path(__file__).resolve().parent
# Add a relative path (e.g., ../lib)
#lib_path = base_dir #/ 'emerge_helper_od'
#sys.path.insert(0, str(lib_path))

graphviz_bin = r"H:\\bins\\Graphviz-14.1.4-win32\\bin"

# ✅ Add to PATH (not sys.path)
os.environ["PATH"] = graphviz_bin + os.pathsep + os.environ["PATH"]

from graphviz import Digraph
class GraphvizTree():
    

    def __init__(self):
        self.elements={}
        self.links=[]
        return
    
    def add_link(self,from_node_name='root',to_node_name='',to_node_content=''):
        if to_node_name=='':
            raise 'to_node_name is empty'
        if to_node_content=='':
            raise 'to_node_content is empty'
        from_node_name='root' if from_node_name is None else from_node_name

        if from_node_name == 'root':
            self.elements[to_node_name]=to_node_content
            return self
        
        if from_node_name != 'root':
            if from_node_name not in self.elements:
                raise f"{from_node_name} is not in the tree. Add link to it first"
          
        if to_node_name not in self.elements:
            self.elements[to_node_name]=to_node_content

        
        self.links.append({'from':from_node_name,'to':to_node_name})

        return self

    def draw_flow_graphviz(self):
        """
        elements: dict {node_id: label}
        links: list of dicts [{'from': id1, 'to': id2}]
        Returns a Graphviz Digraph for inline display in Jupyter.
        """

        dot = Digraph(
            graph_attr={"rankdir": "TB"},
            node_attr={"fontname": "Helvetica"}
        )

        # Add nodes
        for key, label in self.elements.items():
            shape = "diamond" if "?" in label else "box"
            dot.node(str(key), label, shape=shape)

        # Add edges
        for link in self.links:
            dot.edge(str(link["from"]), str(link["to"]))

        return dot
    

def test_GraphvizTree():
    gt=GraphvizTree()
    gt.add_link('root','random selection','n=500')\
        .add_link('random selection','inclusion','n=200')\
        .add_link('random selection','exclusion','n=300')\
        .add_link('inclusion','enrolled','n=100')\
            .draw_flow_graphviz()


