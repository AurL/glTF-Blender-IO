# Copyright (c) 2017 The Khronos Group Inc.
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

#
# Imports
#

import bpy

from ...io.exp.gltf2_io_export import *
from ...io.com.gltf2_io import Gltf

from .gltf2_blender_generate import *
from  io_scene_gltf2.blender.com import gltf2_blender_json

#
# Globals
#

#
# Functions
#

def prepare(export_settings):
    """
    Stores current state of Blender and prepares for export, depending on the current export settings.
    """
    if bpy.context.active_object is not None and bpy.context.active_object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    
    filter_apply(export_settings)
    
    export_settings['gltf_original_frame'] = bpy.context.scene.frame_current 
    
    export_settings['gltf_use_no_color'] = []
    
    export_settings['gltf_joint_cache'] = {}
    
    if not export_settings['gltf_current_frame']:
        bpy.context.scene.frame_set(0)

    
def finish(export_settings):
    """
    Brings back Blender into its original state before export and cleans up temporary objects.
    """
    if export_settings['temporary_meshes'] is not None:
        for temporary_mesh in export_settings['temporary_meshes']:
            bpy.data.meshes.remove(temporary_mesh)
            
    bpy.context.scene.frame_set(export_settings['gltf_original_frame'])  


def save(operator,
         context,
         export_settings):
    """
    Starts the glTF 2.0 export and saves to content either to a .gltf or .glb file.
    """

    print_console('INFO', 'Starting glTF 2.0 export')
    bpy.context.window_manager.progress_begin(0, 100)
    bpy.context.window_manager.progress_update(0)
    
    #
    
    prepare(export_settings)
    
    #

    glTF = Gltf(
        accessors=[],
        animations=[],
        asset=None,
        buffers=[],
        buffer_views=[],
        cameras=[],
        extensions={},
        extensions_required=[],
        extensions_used=[],
        extras=None,
        images=[],
        materials=[],
        meshes=[],
        nodes=[],
        samplers=[],
        scene=-1,
        scenes=[],
        skins=[],
        textures=[]
    )

    generate_glTF(operator, context, export_settings, glTF)

    #

    def dict_strip(obj):
        o = obj
        if isinstance(obj, dict):
            o = {}
            for k, v in obj.items():
                if v is None:
                    continue
                elif isinstance(v, list) and len(v) == 0:
                    continue
                o[k] = dict_strip(v)
        elif isinstance(obj, list):
            o = []
            for v in obj:
                o.append(dict_strip(v))
        elif isinstance(obj, float):
            # force floats to int, if they are integers (prevent INTEGER_WRITTEN_AS_FLOAT validator warnings)
            if int(obj) == obj:
                return int(obj)
        return o

    save_gltf(dict_strip(glTF.to_dict()), export_settings, gltf2_blender_json.BlenderJSONEncoder)
        
    #
    
    finish(export_settings)
    
    #

    print_console('INFO', 'Finished glTF 2.0 export')
    bpy.context.window_manager.progress_end()
    print_newline()

    return {'FINISHED'}
