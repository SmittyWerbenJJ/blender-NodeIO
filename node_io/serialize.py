import json
from typing import Tuple
from .nodelink import NodeLink
from .node import Node

class Serialize:

    @classmethod
    def toJson(nodes:list[Node],links:list[NodeLink]):
        return {
            "nodes":[n.to_dict() for n in nodes],
            "links":[l.to_dict() for l in links]
        }

    @classmethod
    def fromJson(cls,jsonstring:str)->Tuple[list[Node],list[NodeLink]]:
        nodes =[]
        links = []
        for n in jsonstring["nodes"]:
            node=Node.fromJson(n)
            nodes.append(node)

        for l in jsonstring["links"]:
            link=NodeLink.fromJson(l)
            links.append(link)

        return {0:nodes,1:links}
