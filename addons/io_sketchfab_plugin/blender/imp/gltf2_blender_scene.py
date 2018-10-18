# Copyright 2018 The glTF-Blender-IO authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import bpy
from math import sqrt
from mathutils import Quaternion
from .gltf2_blender_node import *
from .gltf2_blender_skin import *
from .gltf2_blender_animation import *

class BlenderScene():

    @staticmethod
    def create(gltf, scene_idx, use_current=True, root_name=None):

        pyscene = gltf.data.scenes[scene_idx]

        # Create Yup2Zup empty
        name = root_name if root_name else "GLTF_model"
        obj_rotation = bpy.data.objects.new(name, None)
        obj_rotation.rotation_mode = 'QUATERNION'
        obj_rotation.rotation_quaternion = Quaternion((sqrt(2)/2, sqrt(2)/2,0.0,0.0))

        # Create a new scene only if not already exists in .blend file
        # TODO : put in current scene instead ?
        if pyscene.name not in [scene.name for scene in bpy.data.scenes]:
            if pyscene.name and not use_current:
                scene = bpy.data.scenes.new(pyscene.name)
            else:
                scene = bpy.context.scene
            scene.render.engine = "CYCLES"

            gltf.blender_scene = scene.name
        else:
            gltf.blender_scene = pyscene.name

        for selected in bpy.context.selected_objects:
            selected.select = False

        for node_idx in pyscene.nodes:
            BlenderNode.create(gltf, node_idx, None) # None => No parent


        # Now that all mesh / bones are created, create vertex groups on mesh
        if gltf.data.skins:
            for skin_id, skin in enumerate(gltf.data.skins):
                if hasattr(skin, "node_ids"):
                    BlenderSkin.create_vertex_groups(gltf, skin_id)

            for skin_id, skin in enumerate(gltf.data.skins):
                if hasattr(skin, "node_ids"):
                    BlenderSkin.assign_vertex_groups(gltf, skin_id)

            for skin_id, skin in enumerate(gltf.data.skins):
                if hasattr(skin, "node_ids"):
                    BlenderSkin.create_armature_modifiers(gltf, skin_id)

        if gltf.data.animations:
            for anim_idx, anim in enumerate(gltf.data.animations):
                for node_idx, node in enumerate(pyscene.nodes):
                    BlenderAnimation.anim(gltf, anim_idx, node_idx)


        # Parent root node to rotation object
        bpy.data.scenes[gltf.blender_scene].objects.link(obj_rotation)
        for node_idx in pyscene.nodes:
            bpy.data.objects[gltf.data.nodes[node_idx].blender_object].parent = obj_rotation

        # Place imported model on cursor
        obj_rotation.location = bpy.context.scene.cursor_location

        # Make object selected to allow to transform it directly after import
        try:
            for selected in bpy.context.selected_objects:
                selected.select = False

            bpy.context.scene.objects.active = obj_rotation
            obj_rotation.select = True
        except Exception as e:
            print(e)
            pass