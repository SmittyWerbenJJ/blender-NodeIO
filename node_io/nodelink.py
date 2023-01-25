from dataclasses import dataclass
import bpy


class NodeLink:
    def __init__(self, blenderNodeLink: bpy.types.NodeLink = None) -> None:
        if blenderNodeLink is None:
            self.from_node = None
            self.from_socket = None
            self.to_node = None
            self.to_socket = None
            return
        self.from_node = blenderNodeLink.from_node.name
        self.from_socket = blenderNodeLink.from_socket.name
        self.to_node = blenderNodeLink.to_node.name
        self.to_socket = blenderNodeLink.to_socket.name

    def to_dict(self):
        return {
            "from_node": self.from_node,
            "from_socket": self.from_socket,
            "to_node": self.to_node,
            "to_socket": self.to_socket
        }

    @classmethod
    def fromJson(cls, jsonDict: dict):
        node = NodeLink()
        for key, value in jsonDict.items():
            setattr(node, key, value)
        return node

    def toJson(self):
        return {
            "from_node": self.from_node,
            "from_socket": self.from_socket,
            "to_node": self.to_node,
            "to_socket": self.to_socket
        }

    @classmethod
    def fromStringList(cls, list):
        newLinks = []
        for item in list:
            newLink = NodeLink.fromJson(item)
            newLinks.append(newLink)
        return newLinks
