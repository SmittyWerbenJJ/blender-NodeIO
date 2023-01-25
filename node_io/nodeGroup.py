from queue import Queue
import bpy
from .node import Node
from .nodelink import NodeLink
from .nodeTree import NodeTree


class NodeGroup(Node):
    def __init__(self, shaderNode: bpy.types.ShaderNode) -> None:
        super().__init__(shaderNode)
        self.subTree: bpy.types.NodeTree = shaderNode.node_tree
        self.createSubTree(shaderNode)

    def createSubTree(self, shaderNode):
        if self.subTree is None:
            return
            self.subTree = NodeTree().serialize_bpy_NodeTree(shaderNode)

    def serializeNodeTree(self, node_tree: bpy.types.NodeTree):
        """Serializes this Node tree into json format"""
        self.nodes = []
        self.links = []
        for blenderNode in node_tree.nodes:
            self.nodes.append(Node(blenderNode))
        for blenderLink in node_tree.links:
            self.links.append(NodeLink(blenderLink))

        # subtrees

        for node in node_tree.nodes:
            if node.bl_idname != "ShaderNodeGroup":
                continue
            self.subtrees.append(self.discoverSubtrees(node.node_tree))

        return self

    def discoverSubtrees(self, blender_node_tree):
        checked_blender_trees = []
        blender_trees_toCheck = Queue()
        blender_trees_toCheck.put(blender_node_tree)
        all_serialized_subtrees: list[NodeGroup] = []
        while not blender_trees_toCheck.empty():
            blender_subtree = blender_trees_toCheck.get()
            serialized_tree = NodeGroup().serializeNodeTree(blender_subtree)
            checked_blender_trees.append(blender_subtree)
            all_serialized_subtrees.append(serialized_tree)

            if len(serialized_tree.subtrees) > 0:
                for x in serialized_tree.subtrees:
                    blender_trees_toCheck.put(x)
        return all_serialized_subtrees

    def toJson():

        return {

        }
        # for node in self.nodes:
        #     if "subtree" in node.data:
        #         self.subtrees.append(NodeTree().serializeNodeTree(node.data["subtree"]))

    # def to_Json(self):
    #     return {
    #         "node_tree":self.name,
    #         "nodes"
    #     }
