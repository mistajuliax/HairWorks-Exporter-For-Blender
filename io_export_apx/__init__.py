# -*- coding: utf-8 -*-

import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty
from bpy.types import Operator
from mathutils import Matrix
from .Template import template
import numpy as np

bl_info = {
     "name":         "HairWorks Exporter (.apx)", #https://github.com/mistajuliax/HairWorks-Exporter-For-Blender
     "author":       "Emile Greyling & Aaron Thompson", #code cleanup & port to 2.91 by Aaron Thompson
     "blender":      (2,91,0),# December 5, 2020.
     "version":      (0,0,2),
     "location":     "File > Export > HairWorks (.apx)",
     "description":  "Export hair data to HairWorks file (.apx)",
     "warning":      "",
     "support":      "COMMUNITY",
     "category":     "Import-Export",
 }

def getClosest(vec, vecList):
    vec = np.asarray(vec)
    vecList = np.asarray(vecList)
    diff = vecList - vec
    distance = np.linalg.norm(diff, axis=-1)
    return np.argmin(distance)


def create_hairworks_file(context, filepath):
    kwargs = {}
    
    #%% numHairs totalVerts
    ctxt_object = bpy.context.object.evaluated_get(context.evaluated_depsgraph_get())
    hairs = ctxt_object.particle_systems[0].particles
    kwargs['numHairs'] = len(hairs)
    kwargs['totalVerts'] = sum([len(p.hair_keys) for p in hairs])
    
    #%% hair_verts
    hair_verts = [] #list of vertices of all hairs
    meshCoords = [] #root vertex of each guide hair
    for hair in hairs:
        meshCoords.append(hair.hair_keys[0].co)
        for key in hair.hair_keys:
            hair_verts.append([key.co.x, key.co.y, key.co.z])
    kwargs['hair_verts'] = ', '.join([' '.join(map(str, vert)) for vert in hair_verts])
    
    #%% endIndices
    i = -1
    end_indices = [] #list of vertex indices of hair tips
    for hair in hairs:
        i += len(hair.hair_keys)
        end_indices.append(i)
    kwargs['endIndices'] = ' '.join(map(str, end_indices))
    
    #%% numFaces n_faceIndices faceIndices
    growth_mesh = ctxt_object.data
    face_indices = [] #list of indices into meshCoords for each vertex of each face
                      #  assuming {growth_mesh.vertices} == {meshCoords}
    for face in growth_mesh.polygons:
        for vertex in face.vertices:
            face_indices.append(getClosest(growth_mesh.vertices[vertex].co, meshCoords)) #maybe handle quads and tris?
    kwargs['numFaces'] = len(growth_mesh.polygons)
    kwargs['n_faceIndices'] = len(face_indices)
    kwargs['faceIndices'] = ' '.join(map(str, face_indices))
    
    #%% n_UVs UVs
    UVs = []
    uv_act = growth_mesh.uv_layers.active
    uv_layer = uv_act.data if uv_act is not None else [0.0, 0.0]
    for face in growth_mesh.polygons:
        for li in face.loop_indices:
            UVs.append(uv_layer[li].uv)
    kwargs['n_UVs'] = len(UVs)
    kwargs['UVs'] = ', '.join(' '.join(map(str, [uv.x, uv.y])) for uv in UVs)
    
    #%% numBones 
    bones = []
    poseBones = []
    usedBones = []
    if ctxt_object.parent.type == "ARMATURE":
        bones = ctxt_object.parent.data.bones
        poseBones = ctxt_object.parent.pose.bones
        for bone in bones:
            if bone.name in [g.name for g in ctxt_object.vertex_groups]:
                usedBones.append(bone)
    kwargs['numBones'] = len(usedBones)
    
    #%% boneIndices boneWeights
    boneIndices = []
    boneWeights = []
    for vertex in growth_mesh.vertices:
        boneIndices.append(np.zeros(4, dtype=int))
        boneWeights.append(np.zeros(4, dtype=float))
        i = 0
        for bone in usedBones:
            for g in vertex.groups[:4]:
                if g.group == ctxt_object.vertex_groups[bone.name].index and i < 4:
                    boneIndices[-1][i] = ctxt_object.vertex_groups[bone.name].index
                    boneWeights[-1][i] = g.weight
                    i += 1
    kwargs['boneIndices'] = ', '.join(' '.join(map(str, x)) for x in boneIndices)
    kwargs['boneWeights'] = ', '.join(' '.join(map(str, x)) for x in boneWeights)
    
    #%% boneNameList
    kwargs['boneNameList'] = '\n            '.join('<value type="String">{}</value>'.format(bone.name) for bone in usedBones)


    #%% bindPoses
    poses = []
    for bone in usedBones:
        for index, pose in enumerate(poseBones):
            if bone.name == pose.name:
                par_mat_inv = bones[bone.name].parent.matrix_local.inverted_safe() if bones[bone.name].parent else Matrix()
                matrix = par_mat_inv @ bones[bone.name].matrix_local
                if bones[bone.name].parent is not None :
                    matrix = ctxt_object.matrix_parent_inverse.inverted() * bones[bone.name].parent.matrix_local * matrix
                matrix.transpose()
                poses.append(matrix)
    kwargs['bindPoses'] = '\n            '.join(' '.join(map(str, np.array(matrix).flat)) for matrix in poses)
    
    #%% num_boneParents boneParents
    boneParents = []
    for pose in poseBones:
        if pose.parent is not None:
            for index, bone in enumerate(usedBones):
                if pose.parent.name == bone.name:
                    boneParents.append(ctxt_object.vertex_groups[bone.name].index)
    if len(boneParents) == 0:
        boneParents.append (-1)
    kwargs['num_boneParents'] = len(boneParents)
    kwargs['boneParents'] = ' '.join(map(str, boneParents))
    
    #%% write the template with generated values
    with open(filepath, 'w', encoding = 'utf-8') as f:
        f.write(template.format(**kwargs))
    return {'FINISHED'}

class ExportHairWorks(Operator, ExportHelper):
    bl_idname       = "export_hairworks_file.apx"
    bl_label        = "Export"
    bl_options      = {'PRESET'}
    filename_ext    = ".apx"
    filter_glob: StringProperty(
            default="*.apx",
            options={"HIDDEN"},
            )

    def execute(self, context):
        return create_hairworks_file(context, self.filepath)

def menu_func(self, context):
    self.layout.operator(ExportHairWorks.bl_idname, text="HairWorks (.apx)")

def register():
    bpy.utils.register_class(ExportHairWorks)
    bpy.types.TOPBAR_MT_file_export.append(menu_func)

def unregister():
    bpy.utils.unregister_class(ExportHairWorks)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func)

if __name__ == "__main__":
    register()
    bpy.ops.export_hairworks_file.apx('INVOKE_DEFAULT')






