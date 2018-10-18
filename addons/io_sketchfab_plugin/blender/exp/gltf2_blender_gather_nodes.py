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


from io_scene_gltf2.blender.exp.gltf2_blender_gather_cache import cached
from io_scene_gltf2.blender.exp import gltf2_blender_gather_skins
from io_scene_gltf2.blender.exp import gltf2_blender_gather_cameras
from io_scene_gltf2.blender.exp import gltf2_blender_gather_mesh

from io_scene_gltf2.blender.exp import gltf2_blender_extract

from io_scene_gltf2.io.com import gltf2_io


@cached
def gather_node(blender_object, export_settings):
    if not __filter_node(blender_object, export_settings):
        return None

    node = gltf2_io.Node(
        camera=__gather_camera(blender_object, export_settings),
        children=__gather_children(blender_object, export_settings),
        extensions=__gather_extensions(blender_object, export_settings),
        extras=__gather_extras(blender_object, export_settings),
        matrix=__gather_matrix(blender_object, export_settings),
        mesh=__gather_mesh(blender_object, export_settings),
        name=__gather_name(blender_object, export_settings),
        rotation=None,
        scale=None,
        skin=__gather_skin(blender_object, export_settings),
        translation=None,
        weights=__gather_weights(blender_object, export_settings)
    )
    node.translation, node.rotation, node.scale = __gather_trans_rot_scale(blender_object, export_settings)

    return node


def __filter_node(blender_object, export_settings):
    if blender_object.users == 0:
        return False
    if export_settings['gltf_selected'] and not blender_object.select:
        return False
    if not export_settings['gltf_layers'] and not blender_object.layers[0]:
        return False
    if blender_object.dupli_group is not None and not blender_object.dupli_group.layers[0]:
        return False

    return True


def __gather_camera(blender_object, export_settings):
    return gltf2_blender_gather_cameras.gather_camera(blender_object, export_settings)


def __gather_children(blender_object, export_settings):
    children = []
    # standard children
    for child_object in blender_object.children:
        node = gather_node(child_object, export_settings)
        if node is not None:
            children.append(node)
    # blender dupli objects
    if blender_object.dupli_type == 'GROUP' and blender_object.dupli_group:
        for dupli_object in blender_object.dupli_group.objects:
            node = gather_node(dupli_object, export_settings)
            if node is not None:
                children.append(node)

    return children


def __gather_extensions(blender_object, export_settings):
    return {}


def __gather_extras(blender_object, export_settings):
    return None


def __gather_matrix(blender_object, export_settings):
    # return blender_object.matrix_local
    return []


def __gather_mesh(blender_object, export_settings):
    return gltf2_blender_gather_mesh.gather_mesh(blender_object, export_settings)


def __gather_name(blender_object, export_settings):
    if blender_object.dupli_type == 'GROUP' and blender_object.dupli_group:
        return  "Duplication_Offset_" + blender_object.name
    return blender_object.name


def __gather_trans_rot_scale(blender_object, export_settings):
    trans, rot, sca = gltf2_blender_extract.decompose_transition(blender_object.matrix_local, 'NODE', export_settings)
    if blender_object.dupli_type == 'GROUP' and blender_object.dupli_group:
        trans = -gltf2_blender_extract.convert_swizzle_location(blender_object.dupli_group.dupli_offset, export_settings)
    translation, rotation, scale = (None, None, None)
    if trans[0] != 0.0 or trans[1] != 0.0 or trans[2] != 0.0:
        translation = [trans[0], trans[1], trans[2]]
    if rot[0] != 0.0 or rot[1] != 0.0 or rot[2] != 0.0 or rot[3] != 1.0:
        rotation = [rot[0], rot[1], rot[2], rot[3]]
    if sca[0] != 1.0 or sca[1] != 1.0 or sca[2] != 1.0:
        scale = [sca[0], sca[1], sca[2]]
    return translation, rotation, scale


def __gather_skin(blender_object, export_settings):
    if "Armature" in blender_object.modifiers:
        # Skins and meshes must be in the same glTF node, which is different from how blender handles armatures
        return gltf2_blender_gather_skins.gather_skin(blender_object.modifiers["Armature"].object, export_settings)


def __gather_weights(blender_object, export_settings):
    return None

