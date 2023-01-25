from queue import Queue
import uuid
import bpy
from .node import Node
from .nodelink import NodeLink
from .errors import *
from dataclasses import dataclass
VERSION = "0.0.1"


@dataclass
class Subtree:
    inputs: list[str]
    outputs: list[str]


class NodeTree:
    def __init__(self) -> None:
        self.name: str = ""
        self.nodes: list[Node] = []
        self.links: list[NodeLink] = []
        self.subtrees: list[NodeTree] = []

    @classmethod
    def serialize_bpy_NodeTree(cls, node_tree: bpy.types.NodeTree, materialname=""):
        """Serializes this Blender Node  tree (and nested nodeGroups) into our Node Tree Format"""
        newTree = NodeTree()
        newTree.name = materialname
        for blenderNode in node_tree.nodes:
            newTree.nodes.append(Node(blenderNode))
            if blenderNode.bl_idname == "ShaderNodeGroup":
                newTree.subtrees.append(
                    NodeTree.serialize_bpy_NodeTree(
                        blenderNode.node_tree,
                        blenderNode.node_tree.name))
        for blenderLink in node_tree.links:
            newTree.links.append(NodeLink(blenderLink))

        return newTree

    @classmethod
    def de_Serialize_Json(cls, jsonstring) -> "NodeTree":
        """deSerializes our Node Tree Format into a native Blender Node tree.
        also deSerializes nested Node Groups into a native Blender Node Tree

        Args:
            jsonstring (str): our Node Tree format as a json String

        Raises:
            VersionError: when the version from the json string is incompatible

        Returns:
            NodeTree (dict[NodeTree,list[NodeTree]) : a dict containing a materialNodeTree and a list of NodeGroupNodeTrees
        """

        # if version2Tuple(jsonstring["file_version"]) < version2Tuple(VERSION):
        #     raise VersionError

        tmpNodeTree = NodeTree()
        tmpNodeTree.nodes = Node.fromJsonList(jsonstring["nodes"])
        tmpNodeTree.links = NodeLink.fromStringList(jsonstring["links"])
        tmpNodeTree.name = jsonstring["node_tree"]
        for subtree in jsonstring["subtrees"]:
            tmpNodeTree.subtrees.append(NodeTree.de_Serialize_Json(subtree))
        return tmpNodeTree

    @classmethod
    def findNodeGroupsinBlenderNodeTree(cls, node_tree: bpy.types.NodeTree):
        """find all node groups in blender-nodeTree
        """
        nodes = []
        for node in node_tree.nodes:
            if node.bl_idname == "ShaderNodeGroup":
                nodes.append(node)
        return nodes

    def findNodeGroupsInTree_custom(self):
        """returns a list of group nodes in a node tree
        """
        return [node for node in self.nodes if node.getType() == "ShaderNodeGroup"]

    # def findNodeGroupsNested(self):
    #     if self.bl_idname == 'ShaderNodeTree':
    #         next = NodeTree.findNodeGroupsinBlenderNodeTree(self)
    #     else:
    #         next = [bpy.data.node_groups[self.name]]
    #     discovered = []
    #     while len(next) > 0:
    #         itm = next.pop(0)
    #         for x in NodeTree.findNodeGroupsinBlenderNodeTree(itm):
    #             discovered.append(x)
    #             next.append(x.node_tree)
    #     return discovered

    # def addblendersubtree(self, subtree):
        # subtrees = NodeTree.findNodeGroupsinBlenderNodeTree(subtree)
        # allsubtrees = []
        # if len(subtrees) == 0
        # return []
        # for subtree in subtrees:
        #     NodeTree.findNodeGroupsinBlenderNodeTree(subtree)
        #     allsubtrees +=
        # return allsubtrees

        # return allsubtrees

    def toJson(self):
        return {
            # "file_version": VERSION,
            "node_tree": self.name,
            "nodes": [n.toJson() for n in self.nodes],
            "links": self.links,
            "subtrees": [st.toJson() for st in self.subtrees]
        }

    def createMaterial(self):
        """Create Material From this Node Tree

        Returns:
            bpy.type.Material: the new or existing material
        """
        # create new material
        suid = str(uuid.uuid4())
        newMaterial = bpy.data.materials.new(self.name + suid)
        newMaterial.use_nodes = True
        newMaterial.node_tree.nodes.clear()

        # remap existing materials to the new one
        if bpy.data.materials.find(self.name) != -1:
            bpy.data.materials[self.name].user_remap(newMaterial)
            bpy.data.materials.remove(bpy.data.materials[self.name])
        bpy.data.materials[self.name + suid].name = self.name

        # import subTrees
        for subtree in self.subtrees:
            createNodeGroup(subtree)

        # load nodes and links
        for node in self.nodes:
            addNodeToTree(node, newMaterial.node_tree)

        # make the links
        for link in self.links:
            addLinkToTree(link, newMaterial.node_tree)

        return newMaterial

    def getNodeGroupsNested(self):
        """Find All Node-groups in all nodes,

        Returns:
            list(node_tree): _description_
        """
        discovered = []
        next = []
        nodeTreeQueue = Queue()

        # get first level node groups
        for grp in self.findNodeGroupsInTree_custom():
            nodeTreeQueue.put(grp)

        # start looking for nested node groups
        while not nodeTreeQueue.empty():
            node_tree = nodeTreeQueue.get(0)
            discovered.append(node_tree.name)
            # reference node tree, either in blend file or from same path of this node tree
            for grp_ in node_tree.findNodeGroupsInTree_custom():
                if grp.getName() not in discovered:
                    nodeTreeQueue.put(grp_)
        return discovered


def version2Tuple(versionStr):
    tpl = tuple(map(int, versionStr.split(".")))
    return tpl


def createNodeGroup(nodegroupNodeTree: "NodeTree"):
    """ create a nodeGroup from this NodeTree"""

    if bpy.data.node_groups.find(nodegroupNodeTree.name) != -1:
        newBlenderNodeTree = bpy.data.node_groups[nodegroupNodeTree.name]
        newBlenderNodeTree.nodes.clear()
        newBlenderNodeTree.inputs.clear()
        newBlenderNodeTree.outputs.clear()
    else:
        newBlenderNodeTree = bpy.data.node_groups.new(nodegroupNodeTree.name, "ShaderNodeTree")

    # import subTrees
    for subtree in nodegroupNodeTree.subtrees:
        createNodeGroup(subtree)

    # add other Nodes
    for node in nodegroupNodeTree.nodes:
        addNodeToTree(node, newBlenderNodeTree)

        # populate nodeTree Inputs
        if node.getType() == "NodeGroupInput":
            for socket in node.getOutputs():
                newBlenderNodeTree.inputs.new(socket.type, socket.name)

        # populate nodeTree Outputs
        elif node.getType() == "NodeGroupOutput":
            for socket in node.getInputs():
                newBlenderNodeTree.outputs.new(socket.type, socket.name)

    # add links to nodes
    for link in nodegroupNodeTree.links:
        addLinkToTree(link, newBlenderNodeTree)


def addNodeToTree(node: Node, node_tree: bpy.types.NodeTree):
    # add node to tree
    newNode = node_tree.nodes.new(node.getType())
    newNode.location = node.getLocation()
    newNode.name = node.getName()
    newNode.label = node.getName()

    if node.getType() == "ShaderNodeGroup":
        # add subtree to this node group
        newNode.node_tree = bpy.data.node_groups[node.getData()["subtree"]]
    else:
        # set socket inputs&outputs values for this node

        for socket in node.getInputs():
            if socket.value is not None:
                val = socket.getValue()
                if hasattr(newNode.inputs[socket.name], "default_value"):
                    newNode.inputs[socket.name].default_value = val

        for socket in node.getOutputs():
            if socket.value is not None:
                val = socket.getValue()
                if hasattr(newNode.outputs[socket.name], "default_value"):
                    newNode.outputs[socket.name].default_value = val

        # set other node properties
        ddata = node.getData()
        for id, data in ddata.items():
            node.setData(id, data, newNode)

    return newNode


def addLinkToTree(link: NodeLink, node_tree: bpy.types.NodeTree):
    from_socket = node_tree.nodes[link.from_node].outputs[link.from_socket]
    to_socket = node_tree.nodes[link.to_node].inputs[link.to_socket]
    node_tree.links.new(from_socket, to_socket)
