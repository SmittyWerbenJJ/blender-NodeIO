from dataclasses import dataclass
import json
import bpy
from bpy.props import BoolProperty
from bpy.types import Scene
from mathutils import Vector
from .nodeSocket import NodeSocket


def getTypeFromBpyObject(object):
    """
    Get the Type as a string by checking the name between single quotes
    """
    quoteIndices = []
    type_datavalue = str(type(object))
    for i, c in enumerate(type_datavalue):
        if c == "'":
            quoteIndices.append(i)
    return type_datavalue[quoteIndices[0] + 1:quoteIndices[1]]


def is_jsonable(x):
    """
    check if object is json serializable
    from: https://stackoverflow.com/a/53112659
    """
    try:
        json.dumps(x)
        return True
    except (TypeError, OverflowError):
        return False


class Node:
    def __init__(self, shaderNode: bpy.types.ShaderNode = None) -> None:
        self.name = ""
        self.type = ""
        self.location = [0.0, 0.0]
        self.inputs: list[NodeSocket] = []
        self.outputs: list[NodeSocket] = []
        self.data: dict = {}

        if shaderNode is None:
            return

        self.setDataFromBpy(shaderNode)

    def setDataFromBpy(self, shaderNode: bpy.types.ShaderNode):
        self.name = shaderNode.name
        self.type = shaderNode.bl_idname
        self.location = shaderNode.location
        self.inputs = []
        self.outputs = []
        self.data = {}

        # input attributes
        for socket in shaderNode.inputs:
            sockettype = socket.type
            if sockettype == "VALUE":
                value = float(socket.default_value)
            elif sockettype == "RGBA":
                value = list(socket.default_value)
            elif sockettype == "VECTOR":
                value = list(socket.default_value)
            else:
                value = str(getattr(socket, "default_value", None))

            x = NodeSocket(socket.bl_idname, socket.name, value)
            self.inputs.append(x)

        # output attributes
        for socket in shaderNode.outputs:
            sockettype = socket.type

            if sockettype == "VALUE":
                value = float(socket.default_value)
            elif sockettype == "RGBA":
                value = list(socket.default_value)
            elif sockettype == "VECTOR":
                value = list(socket.default_value)
            else:
                value = str(getattr(socket, "default_value", None))
            x = NodeSocket(socket.bl_idname, socket.name, value)
            self.outputs.append(x)

        # data
        # Image paths for image Nodes
        if shaderNode.bl_idname == "ShaderNodeTexImage":
            if shaderNode.image is None:
                imgpath = None
            else:
                imgpath = bpy.path.abspath(shaderNode.image.filepath)
            self.data["image"] = imgpath

        # Sub-Node trees for shaderNodeGroups
        elif shaderNode.bl_idname == "ShaderNodeGroup":
            self.data["subtree"] = shaderNode.node_tree.name

        # other Nodes data
        else:
            for dataKey in dir(shaderNode):
                # data to be skipped
                datavalue = getattr(shaderNode, dataKey)
                string_datavalue = str(getattr(shaderNode, dataKey))
                type_datavalue = getTypeFromBpyObject(datavalue)

                if dataKey in ["image", "node_tree", "inputs", "outputs"]:
                    continue
                if dataKey.startswith("__"):
                    continue
                if string_datavalue.startswith("<bpy_struct"):
                    continue

                # format the data correctly

                # store colors and vectors as float arrays
                if type_datavalue in ["Color", "Vector"]:
                    datavalue = list(datavalue)

                if not is_jsonable(datavalue):
                    continue
                self.data[dataKey] = datavalue

    def setData(self, id, data, shadernode: bpy.types.ShaderNode):
        if shadernode is None:
            return

        try:
            if id == "image":
                # find image in blend file or load from path if not found
                setattr(shadernode, id, bpy.data.images.load(data, check_existing=True))
            elif id in ["Color", "Vector"]:
                setattr(shadernode, id, Vector(data))
            else:
                setattr(shadernode, id, data)
        except Exception as e:
            print(e)
            pass
            # print(f"[ERROR] Image not found: {data}")

    def toJson(self):
        return {
            "name": self.getName(),
            "type": self.getType(),
            "location": self.getLocation()[:],
            "inputs": self.getInputs(),
            "outputs": self.getOutputs(),
            "data": self.getData(),
        }

    def getName(self):
        return self.name

    def getType(self):
        return self.type

    def getLocation(self):
        return self.location

    def getInputs(self) -> list[NodeSocket]:
        newSockets = []
        for socket in self.inputs:

            if isinstance(socket, NodeSocket):
                newSockets.append(socket)
            else:
                value = socket["value"]
                if isinstance(value, str):
                    type = "NodeSocketShader"
                elif isinstance(value, float):
                    type = "NodeSocketFloat"
                elif isinstance(value, list):
                    type = "NodeSocketVector" if len(value) <= 3 else "NodeSocketColor"

                if value in [None, "None", "null"]:
                    if len(next(iter(socket.keys()))) == 0:
                        continue

                socket = NodeSocket(type, socket.name, value)
                newSockets.append(socket)

        # remove sockets without plausible values
        finalSockets = []
        for socket in newSockets.copy():
            if socket.value not in [None, "None", "null"]:
                finalSockets.append(socket)

        return finalSockets

    def getOutputs(self) -> list[NodeSocket]:
        newSockets = []
        for output in self.outputs:

            if isinstance(output, NodeSocket):
                newSockets.append(output)
            else:
                # make Node Socket

                # determine name
                name = output.name
                # determine value
                value = list(output.values())[0]

                # determine type
                if isinstance(value, str):
                    type = next(iter(output.keys()))
                elif isinstance(value, float):
                    type = "NodeSocketFloat"
                elif isinstance(value, list):
                    type = "NodeSocketVector" if len(value) <= 3 else "NodeSocketColor"

                # skip invalid sockets
                if value in [None, "None", "null"]:
                    continue
                newSockets.append(NodeSocket(type, name, value))

        # remove sockets without plausible values
        finalSockets = []
        for socket in newSockets.copy():
            if socket.value not in [None, "None", "null"]:
                finalSockets.append(socket)

        return finalSockets

    def getData(self):
        return self.data

    @classmethod
    def fromJson(cls, jsonObject: dict):
        node = Node()
        for key, value in jsonObject.items():
            if key in ["inputs", "outputs"]:
                for socket in value:
                    newSocket = NodeSocket.fromJson(socket)
                    if key == "inputs":
                        node.inputs.append(newSocket)
                    else:
                        node.outputs.append(newSocket)
            else:
                setattr(node, key, value)
        return node

    @classmethod
    def fromJsonList(cls, list):
        return [Node.fromJson(i) for i in list]


def register():
    # Scene.my_property2 = BoolProperty(default=True)
    pass


def unregister():
    # delattr(Scene, "my_property2")
    pass
