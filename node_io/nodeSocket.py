from dataclasses import dataclass
import json

from mathutils import Vector


@dataclass
class NodeSocket:
    type: str
    name: str
    value: any

    def __init__(self,type,name,value) -> None:
        self.type=type
        self.name=name
        self.value = None if value in["none","None","NONE","Null"] else value

    def toJson(self):
        return {
            "type": self.type,
            "name": self.name,
            "value": self.value
        }

    @classmethod
    def fromJson(cls, jsonString):
        node = NodeSocket(None, None, None)
        for key, value in jsonString.items():
            setattr(node, key, value)
        return node

    def getValue(self):
        if self.type == "NodeSocketColor":
            return self.value
        elif self.type == "NodeSocketFloat":
            return self.value
        elif self.type == "NodeSocketShader":
            return self.value
        elif self.type == "NodeSocketVector":
            return Vector(self.value)
        else:
            return self.value

    @classmethod
    def getValueFromPrimitive(cls, value):
        jval = json.loads(value)
        return jval
