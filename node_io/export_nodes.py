import itertools
import json
from queue import SimpleQueue
import uuid
import bpy
import os
import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import *
from dataclasses import dataclass
from .nodeTree import NodeTree


@dataclass
class ExportJob:
    name: str
    nodetree: NodeTree
    type: str


class ExportMaterialNode(bpy.types.Operator):
    """Exports the material nodes for the Active Material"""
    bl_idname = "smitty.export_material_nodes"
    bl_label = "Export Node Tree to File"

    nodes_path = "//nodes/"

    filename_ext_nodetree = ".nodetree"
    filename_ext_subtree = ".nodesubtree"

    # export_texture_paths: BoolProperty(
    #     name="Export Texture paths",
    #     description="Exports the Texture paths used in Texture nodes",
    #     default=True,
    # )

    export_all_materials: BoolProperty(
        name="Export all Materials",
        description="Enabled: Export all materials on this Object\nDisabled: Export active Material on this Object",
        default=True
    )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def invoke(self, context, event):
        return bpy.context.window_manager.invoke_props_dialog(self)
        # context.w wm invoke_props_popup
        # pass

    def execute(self, context):
        print("exporting Nodes")

        exportJobs = gather_node_trees(
            context.object,
            self.export_all_materials
        )

        for exportjob in exportJobs:
            save_node_graph_to_file(
                exportjob.nodetree,
                bpy.path.abspath(self.nodes_path),
                exportjob.name
            )
        return {'FINISHED'}


def getNodeGroupsInMaterial(material: bpy.types.Material) -> list[bpy.types.NodeGroup]:
    # gather node groups,nested
    discoveredNodeGroups = NodeTree.findNodeGroupsinBlenderNodeTree(material.node_tree)
    nextgroupNodes = SimpleQueue()

    # add groups to search queue
    for nodegroups in discoveredNodeGroups:
        nextgroupNodes.put(nodegroups)

    # find nested node groups
    while not nextgroupNodes.empty():
        nodegroup = nextgroupNodes.get()
        _nodegroups = NodeTree.findNodeGroupsinBlenderNodeTree(nodegroup.node_tree)
        for grp in _nodegroups:
            if grp not in discoveredNodeGroups:
                discoveredNodeGroups.append(grp)
            else:
                nextgroupNodes.put(grp)

    return discoveredNodeGroups


def exportImagesInMaterialSlot(object: bpy.types.Object, materialSlot, exportDir):
    material = object.material_slots[materialSlot].material

    for node in material.node_tree.nodes:
        if node.type == "TEX_IMAGE":
            image = node.image
            if image is not None:
                newImagePath = os.path.join(exportDir, image.name)
            image.save_render(newImagePath)


def gather_node_trees(object: bpy.types.Object, do_all_materials=False) -> list[ExportJob]:
    """ gather all the node trees either from the objects active material, or all object materials"""
    materials_to_check = []
    materialJobs = []
    nodeGroupJobs = []

    if do_all_materials:
        for slot in object.material_slots:
            materials_to_check.append(slot.material)
        materials_to_check = list(set(materials_to_check))
    else:
        materials_to_check.append(object.active_material)

    for material in materials_to_check:
        mj = ExportJob(material.name, NodeTree.serialize_bpy_NodeTree(material.node_tree, material.name), "material")
        if mj.name not in [i.name for i in materialJobs]:
            materialJobs.append(mj)

    return materialJobs


def save_node_graph_to_file(material_data, output_folder, mat_name):
    # Create the output folder for the material, if it doesn't exist
    material_folder = f'{output_folder}'
    if not os.path.exists(material_folder):
        os.makedirs(material_folder)

    # Save the data to a file
    save_data_to_file(f'{material_folder}\\{mat_name}.nodetree', material_data)


def save_subgraph_to_file(material_data, output_folder, mat_name):
    # Create the output folder for the material, if it doesn't exist
    material_folder = f'{output_folder}'
    if not os.path.exists(material_folder):
        os.makedirs(material_folder)

    # Save the data to a file
    save_data_to_file(f'{material_folder}\\{mat_name}.subtree', material_data)


def save_data_to_file(filepath, data):
    with open(rf'{filepath}', 'w') as f:
        json.dump(data, f, indent=2, default=lambda o: o.toJson())


def register():
    bpy.utils.register_class(ExportMaterialNode)


def unregister():
    bpy.utils.unregister_class(ExportMaterialNode)
