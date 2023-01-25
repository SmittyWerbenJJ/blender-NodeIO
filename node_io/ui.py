# Blender Add-on Template
# Contributor(s): Aaron Powell (aaron@lunadigital.tv)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
from bpy.types import Panel

#
# Add additional functions here
#

IDNAME_MAIN="NODEIO_PT_main"
class NODEIO_MainPanel():
    """Panel Shared prosp"""
    # bl_label = "NodeIO"
    # bl_idname = "material_PT_nodeio"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    bl_options = {"DEFAULT_CLOSED"}


class NODEIO_PT_Default(NODEIO_MainPanel, Panel):
    """Creates a Panel in the Material properties window"""
    bl_idname = IDNAME_MAIN
    bl_label = 'NodeIO'

    def draw(self, context):
        row = self.layout.row()
        # row.label(text="NODEIOImport / Export Material Node Trees ", icon='NODETREE')


class NODEIO_PT_Import(NODEIO_MainPanel, Panel):
    """Creates a Panel in the Material properties window"""
    bl_idname = "NODEIO_PT_import"
    bl_label = 'NodeIO: Import'
    bl_parent_id = IDNAME_MAIN

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row()
        row.label(text="Nodes Import", icon='IMPORT')
        row = box.row()
        row.operator("smitty.import_material_nodes")


class NODEIO_PT_Export(NODEIO_MainPanel, bpy.types.Panel):
    """Creates a Panel in the Material properties window"""
    bl_label = 'NodeIO: export'
    bl_idname = "NODEIO_PT_export"
    bl_parent_id = IDNAME_MAIN
    

    def draw(self, context):
        layout = self.layout
        obj = context.object
        active_material = obj.active_material

        if active_material is None:
            node_count = 0
        else:
            node_count = len(active_material.node_tree.nodes)

        box = layout.box()
        row = box.row()
        row.label(text="Nodes Export", icon='EXPORT')
        row = box.row()

        col = row.column(align=True)
        col.label(text="Active material is: ")
        # row.enabled = False
        col = row.column(align=True)
        col.enabled = False
        col.prop(obj, "active_material", text="")

        row = box.row()
        row.label(text="Nodes in Mateial:" + str(node_count))

        row = box.row()
        row.operator("smitty.export_material_nodes")


def register():
    bpy.utils.register_class(NODEIO_PT_Default)
    bpy.utils.register_class(NODEIO_PT_Import)
    bpy.utils.register_class(NODEIO_PT_Export)


def unregister():
    bpy.utils.unregister_class(NODEIO_PT_Export)
    bpy.utils.unregister_class(NODEIO_PT_Import)
    bpy.utils.unregister_class(NODEIO_PT_Default)
