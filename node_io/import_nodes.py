import json
from queue import SimpleQueue
from typing import Tuple
import bpy
import os
from .node import Node
from .nodelink import NodeLink
from .nodeTree import NodeTree

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, CollectionProperty


class ImporttMaterialNodes(bpy.types.Operator, ImportHelper):
    """Tooltip"""
    bl_idname = "smitty.import_material_nodes"
    bl_label = "Import Node Tree from file"
    bl_options = {'REGISTER', 'UNDO'}

    filter_glob: StringProperty(
        default='*.nodetree',
        options={'HIDDEN'}
    )
    # some_boolean: BoolProperty(
    #     name='Do a thing',
    #     description='Do a thing with the file you\'ve selected',
    #     default=True,
    # )

    directory = StringProperty(subtype='DIR_PATH')

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        object = context.object
        node_tree, material, report = importNodeTree(self.filepath)
        self.report(report[0], report[1])
        return {'FINISHED'}


def importNodeTree(filepath):
    report = ({"INFO"}, "No Errors")
    node_tree: NodeTree = None
    newMaterial: bpy.data.materials
    materialname, _ = os.path.splitext(os.path.basename(filepath))

    # parse the material file
    node_tree = parse_node_file(filepath)

    # invalid file error
    if node_tree is None:
        report = ({"ERROR"}, "Selected File is Invalid")
        return (node_tree, None, report)

    # create material
    newMaterial = node_tree.createMaterial()
    return node_tree, newMaterial, report


def parse_node_file(filepath) -> "NodeTree":
    """ Read Json File and Parse into a NodeTree object"""
    with open(filepath, "r", encoding="utf8") as jsonfile:
        jsonstring = json.load(jsonfile)
        nodetree = NodeTree.de_Serialize_Json(jsonstring)
        nodetree.name = os.path.splitext(os.path.basename(filepath))[0]
        return nodetree


def register():
    bpy.utils.register_class(ImporttMaterialNodes)


def unregister():
    bpy.utils.unregister_class(ImporttMaterialNodes)
