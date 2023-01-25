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


from . import node_io
import bpy
bl_info = {
    "name": "blender-Node IO",
    "description": "Import Export of Material Node Trees",
    "author": "SmittyWerbenJJ",
    "version": (1, 0),
    "blender": (3, 3, 0),
    "location": "Properties > Material > NodeIO",
    "warning": "",  # used for warning icon and text in add-ons panel
    "wiki_url": "https://github.com/SmittyWerbenJJ/blender-NodeIO",
    "tracker_url": "https://github.com/SmittyWerbenJJ/blender-NodeIO/issues",
    "support": "COMMUNITY",
    "category": "Material"
}


def register():
    node_io.register()


def unregister():
    node_io.unregister()
