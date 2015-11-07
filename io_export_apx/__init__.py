bl_info = {
     "name":         "HairWorks Exporter (.apx)",
     "author":       "Emile Greyling",
     "blender":      (2,7,5),# October ninth, twenty fifteen.
     "version":      (0,0,1),
     "location":     "File > Export > HairWorks (.apx)",
     "description":  "Export hair data to HairWorks file (.apx)",
     "warning": "",
     "category":     "Import-Export"
 }


import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty
from bpy.types import Operator
from mathutils import *
from math import *

def EmptyUV():
    li = list();
    li.append(0.0);
    li.append(0.0);
    return self;

def findElement(element,List):
        try:
            index=List.index(element)
            return index
        except ValueError:
            return -1

def VecAbsolute(v):
        v1 = list();
        v1.append (abs(v.x));
        v1.append (abs(v.y));
        v1.append (abs(v.z));
        v2 = Vector(v1);
        return v2;

def distance(vec1, vec2):
 return sqrt((vec1.x - vec2.x)**2 + (vec1.y - vec2.y)**2 + (vec1.z - vec2.z)**2);

def getClosest(vec, vecList):
 closest = vecList[0];
 index = 0;
 for i in range (0, len(vecList)):
  if distance(vecList[i], vec) < distance(vec, closest):
   closest = vecList[i];
   index = i;
 return index;

def create_hairworks_file(context, filepath):
  object = bpy.context.object;
  group_names = [g.name for g in object.vertex_groups];
  bones = list();
  boneWeights = list();
  poseBones = list();
  usedBones = list();
  ob = object.parent;
  if ob.type == 'ARMATURE':
    armature = ob.data;
    armObj = ob;
    bones = armature.bones;
    poseBones = ob.pose.bones;
  for bone in bones:
   if bone.name in group_names:
    usedBones.append (bone);
  mesh = object.data;
  Coords = [v.co for v in mesh.vertices];
  numFaces = len(mesh.polygons);
  hairs = object.particle_systems[0].particles;
  numHairs = len(hairs);
  vertsPerHair = len(bpy.context.object.particle_systems[0].particles[0].hair_keys);
  totalVerts = numHairs * vertsPerHair;
  currentIndex = 0;
  endIndex = -1;
  indices = list();
  UVs = list();
  meshCoords = list();
  uv_act = mesh.uv_layers.active;
  uv_layer = uv_act.data if uv_act is not None else EmptyUV();
  for face in mesh.polygons:
   for li in face.loop_indices:
    UVs.append(uv_layer[li].uv);
  outfile = open(filepath, 'w', encoding = 'utf-8');
  outfile.write('<!DOCTYPE NvParameters>\n');
  outfile.write('<NvParameters numObjects="4" version="1.0" >\n');
  outfile.write('<value name="" type="Ref" className="HairWorksInfo" version="1.1" checksum="">\n');
  outfile.write('  <struct name="">\n');
  outfile.write('    <value name="fileVersion" type="String">1.1</value>\n');
  outfile.write('    <value name="toolVersion" type="String"></value>\n');
  outfile.write('    <value name="sourcePath" type="String"></value>\n');
  outfile.write('    <value name="authorName" type="String"></value>\n');
  outfile.write('    <value name="lastModified" type="String"></value>\n');
  outfile.write('  </struct>\n');
  outfile.write('</value>\n');
  outfile.write('<value name="" type="Ref" className="HairSceneDescriptor" version="1.1" checksum="">\n');
  outfile.write('  <struct name="">\n');
  outfile.write('    <value name="densityTexture" type="String"></value>\n');
  outfile.write('    <value name="rootColorTexture" type="String"></value>\n');
  outfile.write('    <value name="tipColorTexture" type="String"></value>\n');
  outfile.write('    <value name="widthTexture" type="String"></value>\n');
  outfile.write('    <value name="rootWidthTexture" null="1" type="String"></value>\n');
  outfile.write('    <value name="tipWidthTexture" null="1" type="String"></value>\n');
  outfile.write('    <value name="stiffnessTexture" type="String"></value>\n');
  outfile.write('    <value name="rootStiffnessTexture" type="String"></value>\n');
  outfile.write('    <value name="clumpScaleTexture" type="String"></value>\n');
  outfile.write('    <value name="clumpRoundnessTexture" type="String"></value>\n');
  outfile.write('    <value name="clumpNoiseTexture" null="1" type="String"></value>\n');
  outfile.write('    <value name="waveScaletexture" type="String"></value>\n');
  outfile.write('    <value name="waveFreqTexture" type="String"></value>\n');
  outfile.write('    <value name="strandTexture" type="String"></value>\n');
  outfile.write('    <value name="lengthTexture" type="String"></value>\n');
  outfile.write('    <value name="specularTexture" type="String"></value>\n');
  outfile.write('  </struct>\n');
  outfile.write('</value>\n');
  outfile.write('<value name="" type="Ref" className="HairAssetDescriptor" version="1.1" checksum="">\n');
  outfile.write('  <struct name="">\n');
  outfile.write('    <value name="numGuideHairs" type="U32">' + str(numHairs) + '</value>\n');
  outfile.write('    <value name="numVertices" type="U32">' + str(totalVerts) + '</value>\n');
  outfile.write('    <array name="vertices" size="' + str(totalVerts) +'" type="Vec3">\n      ');
  for i, h in enumerate(hairs):
    for j, hv in enumerate(h.hair_keys):
        if j == 0:
         meshCoords.append (hv.co);
        currentIndex += 1;
        outstr = str(float(round(hv.co.x, 9))) + ' ' + str(float(round (hv.co.y, 9))) + ' ' + str(float(round (hv.co.z, 9)));
        if currentIndex != totalVerts:
         outstr += ', ';
         if currentIndex % 16 == 0 and currentIndex != 0:
          outstr += '\n      ';
        else :
         outstr += '\n';
        outfile.write (outstr);
  outfile.write('    </array>\n');
  outfile.write('    <array name="endIndices" size="' + str(numHairs) + '" type="U32">\n      ');
  for i in range (0, numHairs):
   endIndex += vertsPerHair;
   outfile.write(str(endIndex) + ' ');
   if (i + 1) % 32 == 0 and i != 0:
    outfile.write ('\n      ');
  for face in mesh.polygons:
   indices.append (getClosest(mesh.vertices[face.vertices[0]].co, meshCoords));
   indices.append (getClosest(mesh.vertices[face.vertices[1]].co, meshCoords));
   indices.append (getClosest(mesh.vertices[face.vertices[2]].co, meshCoords));
  outfile.write('\n    </array>\n');
  outfile.write('    <value name="numFaces" type="U32">' + str(numFaces) + '</value>\n');
  outfile.write('    <array name="faceIndices" size="' + str(len(indices)) + '" type="U32">\n      ');
  for i in range (0, len(indices)):
   outfile.write(str(indices[i]) + ' ');
   if (i + 1) % 32 == 0 and i != 0 :
    outfile.write ('\n      ');
  outfile.write('\n    </array>\n');
  outfile.write('    <array name="faceUVs" size="' + str(len(UVs)) + '" type="Vec2">\n      ');
  for i in range (0, len(UVs)):
   outstr = str(round (UVs[i].x, 9)) + ' ' + str(round (UVs[i].y, 9));
   if (i + 1) != len(UVs):
    outstr += ', ';
   else :
    outstr += '\n';
   if (i + 1) % 32 == 0 and i!= 0:
    if i != len(UVs) - 1:
     outstr += '\n      ';
    else:
     outstr+='\n';
   outfile.write (outstr);
  outfile.write('    </array>\n');
  outfile.write('    <value name="numBones" type="U32">' + str(len(usedBones)) + '</value>\n');
  outfile.write('    <array name="boneIndices" size="' + str(numHairs) + '" type="Vec4">\n      ');
  boneIndices = list();
  for vertex in mesh.vertices:
   numAppended = 0;
   for bone in usedBones:
    for g in vertex.groups:
     if g.group == object.vertex_groups[bone.name].index and numAppended < 4 :
      boneIndices.append(object.vertex_groups[bone.name].index);
      boneWeights.append (g.weight);
      numAppended += 1;
   while len(boneIndices) % 4 != 0 :
    boneIndices.append (0);
    boneWeights.append (0);
  for i in range (0, len(boneIndices)):
   outstr = str(boneIndices[i]);
   if i < len(boneIndices) - 1:
    if (i + 1) % 4 == 0 :
     outstr += ', ';
    else :
     outstr += ' ';
   else :
    outstr+='\n';
   if (i + 1) % 64 == 0 and i != 0:
     outstr += '\n      ';
   outfile.write(outstr);
  outfile.write('    </array>\n');
  outfile.write('    <array name="boneWeights" size="' + str(numHairs) + '" type="Vec4">\n      ');
  for i in range (0, len(boneWeights)):
   outstr = str(round (boneWeights[i], 9));
   if i < len(boneWeights) - 1:
    if (i + 1) % 4 == 0 :
     outstr += ', ';
    else :
     outstr += ' ';
   else :
    outstr+='\n';
   if (i + 1) % 64 == 0 and i != 0:
     outstr += '\n      ';
   outfile.write(outstr);
  numChars = 0;
  for index, bone in enumerate(usedBones):
   if len(bone.name) < 8:
    numChars += 8;
   else :
    numChars += len(bone.name) + 1; 
  outfile.write('    </array>\n');
  outfile.write('    <array name="boneNames" size="' + str(numChars) + '" type="U8">\n      ');
  currentChars = 0;
  for index, bone in enumerate(usedBones) :
   outstr = bone.name;
   while len(outstr) < 8:
    outstr += chr(0);
   if ord(outstr[len(outstr) - 1]) != 0:
    outstr += chr(0);
   for i in range (0, len(outstr)):
    outfile.write(str(ord(outstr[i])) + ' ');
    if (currentChars + 1) % 64 == 0 and index != len(usedBones) - 1: 
       outfile.write ('\n      ');
    else:
     if index == len(usedBones) - 1 and i == len(outstr) - 1:
      outfile.write('\n');
    currentChars += 1;
  outfile.write('    </array>\n');
  outfile.write('    <array name="boneNameList" size="' + str(len(usedBones)) + '" type="String">\n');
  for bone in usedBones:
    outfile.write('      <value type="String">' + bone.name + '</value>\n');
  outfile.write('   </array>\n');
  outfile.write('   <array name="bindPoses" size="' + str(len(usedBones)) + '" type=' + '"Mat44"' + '>\n      ');
  for bone in usedBones:
   for index, pose in enumerate (poseBones):
    if bone.name == pose.name:
     for j in range (0, 4):
      par_mat_inv = armature.bones[bone.name].parent.matrix_local.inverted_safe() if armature.bones[bone.name].parent else Matrix();
      matrix = par_mat_inv * armature.bones[bone.name].matrix_local;
      if armature.bones[bone.name].parent is not None :
       matrix = object.matrix_parent_inverse.inverted() * armature.bones[bone.name].parent.matrix_local * matrix;
      matrix.transpose();
      outfile.write(str(round(matrix[j].x, 9)) + ' ' + str(round (matrix[j].y, 9)) + ' ' + str(round (matrix[j].z, 9)) + ' ' + str(round (matrix[j].w, 9)) + ' ');
      if j == 3:
       if index != len(poseBones) - 1:
        outfile.write('\n      ');
       else :
        outfile.write('\n');
  boneParents = list();
  for pose in poseBones:
   if pose.parent is not None:
    for index, bone in enumerate(usedBones):
     if pose.parent.name == bone.name:
      boneParents.append(object.vertex_groups[bone.name].index);
  if len(boneParents) == 0:
   boneParents.append (-1);
  outfile.write('    </array>\n');
  outfile.write('    <array name="boneParents" size="' + str(len(boneParents)) + '" type="I32">\n      ');
  for i in range (0, len(boneParents)):
   outfile.write(str(boneParents[i]) + ' ');
  outfile.write('\n    </array>\n');
  outfile.write('    <value name="numBoneSpheres" type="U32">0</value>\n');
  outfile.write('    <array name="boneSpheres" size="0" type="Struct" structElements="boneSphereIndex(I32),boneSphereRadius(F32),boneSphereLocalPos(Vec3)"></array>\n');
  outfile.write('    <value name="numBoneCapsules" type="U32">0</value>\n');
  outfile.write('    <array name="boneCapsuleIndices" size="0" type="U32"></array>\n');
  outfile.write('    <value name="numPinConstraints" type="U32">0</value>\n');
  outfile.write('    <array name="pinConstraints" size="0" type="Struct" structElements="boneSphereIndex(I32),boneSphereRadius(F32),boneSphereLocalPos(Vec3)"></array>\n');
  outfile.write('    <value name="sceneUnit" type="F32">1</value>\n');
  outfile.write('    <value name="upAxis" type="U32">2</value>\n');
  outfile.write('    <value name="handedness" type="U32">1</value>\n');
  outfile.write('  </struct>\n');
  outfile.write('</value>\n');
  outfile.write('<value name="" type="Ref" className="HairInstanceDescriptor" version="1.1" checksum="">\n');
  outfile.write('  <struct name="">\n');
  outfile.write('    <array name="materials" size="4" type="Struct">\n');
  for i in range (0, 4):
   outfile.write('      <struct>\n');
   outfile.write('        <value name="name" null="1" type="String"></value>\n');
   outfile.write('        <value name="densityTextureChan" type="U32">0</value>\n');
   outfile.write('        <value name="widthTextureChan" type="U32">0</value>\n');
   outfile.write('        <value name="rootWidthTextureChan" type="U32">0</value>\n');
   outfile.write('        <value name="tipWidthTextureChan" type="U32">0</value>\n');
   outfile.write('        <value name="clumpScaleTextureChan" type="U32">0</value>\n');
   outfile.write('        <value name="clumpNoiseTextureChan" type="U32">0</value>\n');
   outfile.write('        <value name="clumpRoundnessTextureChan" type="U32">0</value>\n');
   outfile.write('        <value name="waveScaleTextureChan" type="U32">0</value>\n');
   outfile.write('        <value name="waveFreqTextureChan" type="U32">0</value>\n');
   outfile.write('        <value name="lengthTextureChan" type="U32">0</value>\n');
   outfile.write('        <value name="stiffnessTextureChan" type="U32">0</value>\n');
   outfile.write('        <value name="rootStiffnessTextureChan" type="U32">0</value>\n');
   outfile.write('        <value name="splineMultiplier" type="U32">4</value>\n');
   outfile.write('        <value name="width" type="F32">1</value>\n');
   outfile.write('        <value name="widthNoise" type="F32">0</value>\n');
   outfile.write('        <value name="clumpNoise" type="F32">0</value>\n');
   outfile.write('        <value name="clumpNumSubclumps" type="U32">0</value>\n');
   outfile.write('        <value name="clumpRoundness" type="F32">1</value>\n');
   outfile.write('        <value name="clumpScale" type="F32">0</value>\n');
   outfile.write('        <value name="clumpPerVertex" type="Bool">true</value>\n');
   outfile.write('        <value name="density" type="F32">0.25</value>\n');
   outfile.write('        <value name="lengthNoise" type="F32">0</value>\n');
   outfile.write('        <value name="lengthScale" type="F32">1</value>\n');
   outfile.write('        <value name="widthRootScale" type="F32">1</value>\n');
   outfile.write('        <value name="widthTipScale" type="F32">0.5</value>\n');
   outfile.write('        <value name="waveRootStraighten" type="F32">0</value>\n');
   outfile.write('        <value name="waveScale" type="F32">0</value>\n');
   outfile.write('        <value name="waveScaleNoise" type="F32">0.5</value>\n');
   outfile.write('        <value name="waveFreq" type="F32">3</value>\n');
   outfile.write('        <value name="waveFreqNoise" type="F32">0.5</value>\n');
   outfile.write('        <value name="waveScaleStrand" type="F32">1</value>\n');
   outfile.write('        <value name="waveScaleClump" type="F32">0</value>\n');
   outfile.write('        <value name="enableDistanceLOD" type="Bool">true</value>\n');
   outfile.write('        <value name="distanceLODStart" type="F32">5</value>\n');
   outfile.write('        <value name="distanceLODEnd" type="F32">10</value>\n');
   outfile.write('        <value name="distanceLODFadeStart" type="F32">1000</value>\n');
   outfile.write('        <value name="distanceLODDensity" type="F32">0</value>\n');
   outfile.write('        <value name="distanceLODWidth" type="F32">1</value>\n');
   outfile.write('        <value name="enableDetailLOD" type="Bool">true</value>\n');
   outfile.write('        <value name="detailLODStart" type="F32">2</value>\n');
   outfile.write('        <value name="detailLODEnd" type="F32">1</value>\n');
   outfile.write('        <value name="detailLODDensity" type="F32">1</value>\n');
   outfile.write('        <value name="detailLODWidth" type="F32">1</value>\n');
   outfile.write('        <value name="colorizeLODOption" type="U32">0</value>\n');
   outfile.write('        <value name="useViewfrustrumCulling" type="Bool">true</value>\n');
   outfile.write('        <value name="useBackfaceCulling" type="Bool">false</value>\n');
   outfile.write('        <value name="backfaceCullingThreshold" type="F32">-0.200000003</value>\n');
   outfile.write('        <value name="usePixelDensity" type="Bool">true</value>\n');
   outfile.write('        <value name="alpha" type="F32">0</value>\n');
   outfile.write('        <value name="strandBlendScale" type="F32">1</value>\n');
   outfile.write('        <value name="baseColor" type="Vec4">0 0 0 0</value>\n');
   outfile.write('        <value name="diffuseBlend" type="F32">0.5</value>\n');
   outfile.write('        <value name="diffuseScale" type="F32">1</value>\n');
   outfile.write('        <value name="diffuseHairNormalWeight" type="F32">0</value>\n');
   outfile.write('        <value name="diffuseBoneIndex" type="U32">0</value>\n');
   outfile.write('        <value name="diffuseBoneLocalPos" type="Vec3">0 0 0</value>\n');
   outfile.write('        <value name="diffuseNoiseFreqU" type="F32">64</value>\n');
   outfile.write('        <value name="diffuseNoiseFreqV" type="F32">64</value>\n');
   outfile.write('        <value name="diffuseNoiseScale" type="F32">0</value>\n');
   outfile.write('        <value name="diffuseNoiseGain" type="F32">0</value>\n');
   outfile.write('        <value name="textureBrightness" type="F32">1</value>\n');
   outfile.write('        <value name="diffuseColor" type="Vec4">0 0 0 0</value>\n');
   outfile.write('        <value name="rootColor" type="Vec4">1 1 1 1</value>\n');
   outfile.write('        <value name="tipColor" type="Vec4">1 1 1 1</value>\n');
   outfile.write('        <value name="glintStrength" type="F32">0</value>\n');
   outfile.write('        <value name="glintCount" type="F32">256</value>\n');
   outfile.write('        <value name="glintExponent" type="F32">2</value>\n');
   outfile.write('        <value name="rootAlphaFalloff" type="F32">0</value>\n');
   outfile.write('        <value name="rootTipColorWeight" type="F32">0.5</value>\n');
   outfile.write('        <value name="rootTipColorFalloff" type="F32">1</value>\n');
   outfile.write('        <value name="shadowSigma" type="F32">0.200000003</value>\n');
   outfile.write('        <value name="specularColor" type="Vec4">1 1 1 1</value>\n');
   outfile.write('        <value name="specularPrimary" type="F32">0.100000001</value>\n');
   outfile.write('        <value name="specularNoiseScale" type="F32">0</value>\n');
   outfile.write('        <value name="specularEnvScale" type="F32">0.25</value>\n');
   outfile.write('        <value name="specularPrimaryBreakup" type="F32">0</value>\n');
   outfile.write('        <value name="specularSecondary" type="F32">0.0500000007</value>\n');
   outfile.write('        <value name="specularSecondaryOffset" type="F32">0.100000001</value>\n');
   outfile.write('        <value name="specularPowerPrimary" type="F32">100</value>\n');
   outfile.write('        <value name="specularPowerSecondary" type="F32">20</value>\n');
   outfile.write('        <value name="strandBlendMode" type="U32">0</value>\n');
   outfile.write('        <value name="useTextures" type="Bool">true</value>\n');
   outfile.write('        <value name="useShadows" type="Bool">false</value>\n');
   outfile.write('        <value name="shadowDensityScale" type="F32">0.5</value>\n');
   outfile.write('        <value name="castShadows" type="Bool">true</value>\n');
   outfile.write('        <value name="receiveShadows" type="Bool">true</value>\n');
   outfile.write('        <value name="backStopRadius" type="F32">0.1</value>\n');
   outfile.write('        <value name="bendStiffness" type="F32">0</value>\n');
   outfile.write('        <value name="interactionStiffness" type="F32">0</value>\n');
   outfile.write('        <value name="pinStiffness" type="F32">1</value>\n');
   outfile.write('        <value name="collisionOffset" type="F32">0</value>\n');
   outfile.write('        <value name="useCollision" type="Bool">false</value>\n');
   outfile.write('        <value name="useDynamicPin" type="Bool">false</value>\n');
   outfile.write('        <value name="damping" type="F32">0.0399999991</value>\n');
   outfile.write('        <value name="friction" type="F32">0</value>\n');
   outfile.write('        <value name="massScale" type="F32">1</value>\n');
   outfile.write('        <value name="gravity" type="Vec3">0 -1 0</value>\n');
   outfile.write('        <value name="inertiaScale" type="F32">0</value>\n');
   outfile.write('        <value name="inertiaLimit" type="F32">0</value>\n');
   outfile.write('        <value name="rootStiffness" type="F32">0.5</value>\n');
   outfile.write('        <value name="tipStiffness" type="F32">0</value>\n');
   outfile.write('        <value name="simulate" type="Bool">true</value>\n');
   outfile.write('        <value name="stiffness" type="F32">0.5</value>\n');
   outfile.write('        <value name="stiffnessStrength" type="F32">1</value>\n');
   outfile.write('        <value name="stiffnessDamping" type="F32">0</value>\n');
   outfile.write('        <value name="stiffnessCurve" type="Vec4">1 1 1 1</value>\n');
   outfile.write('        <value name="stiffnessStrengthCurve" type="Vec4">1 1 1 1</value>\n');
   outfile.write('        <value name="stiffnessDampingCurve" type="Vec4">1 1 1 1</value>\n');
   outfile.write('        <value name="bendStiffnessCurve" type="Vec4">1 1 1 1</value>\n');
   outfile.write('        <value name="interactionStiffnessCurve" type="Vec4">1 1 1 1</value>\n');
   outfile.write('        <value name="wind" type="Vec3">0 0 0</value>\n');
   outfile.write('        <value name="windNoise" type="F32">0</value>\n');
   outfile.write('        <value name="visualizeBones" type="Bool">false</value>\n');
   outfile.write('        <value name="visualizeBoundingBox" type="Bool">false</value>\n');
   outfile.write('        <value name="visualizeCapsules" type="Bool">false</value>\n');
   outfile.write('        <value name="visualizeControlVertices" type="Bool">false</value>\n');
   outfile.write('        <value name="visualizeCullSphere" type="Bool">false</value>\n');
   outfile.write('        <value name="visualizeDiffuseBone" type="Bool">false</value>\n');
   outfile.write('        <value name="visualizeFrames" type="Bool">false</value>\n');
   outfile.write('        <value name="visualizeGrowthMesh" type="Bool">false</value>\n');
   outfile.write('        <value name="visualizeGuideHairs" type="Bool">false</value>\n');
   outfile.write('        <value name="visualizeHairInteractions" type="Bool">false</value>\n');
   outfile.write('        <value name="visualizeHairSkips" type="U32">0</value>\n');
   outfile.write('        <value name="visualizeLocalPos" type="Bool">false</value>\n');
   outfile.write('        <value name="visualizePinConstraints" type="Bool">false</value>\n');
   outfile.write('        <value name="visualizeShadingNormals" type="Bool">false</value>\n');
   outfile.write('        <value name="visualizeSkinnedGuideHairs" type="Bool">false</value>\n');
   outfile.write('        <value name="drawRenderHairs" type="Bool">true</value>\n');
   outfile.write('        <value name="enable" type="Bool">true</value>\n');
   outfile.write('      </struct>\n');
   outfile.write('    </array>\n');
   outfile.write('  </struct>\n');
   outfile.write('</value>\n');
   outfile.write('</NvParameters>');
  outfile.close();
  return {'FINISHED'}
                   
class ExportHairWorks(bpy.types.Operator, ExportHelper):
    bl_idname       = "export_hairworks_file.apx";
    bl_label        = "Export";
    bl_options      = {'PRESET'};
    filename_ext    = ".apx";
    filter_glob = StringProperty(
            default="*.apx",
            options={'HIDDEN'},
            )

    def execute(self, context):
     return create_hairworks_file(context, self.filepath);

def menu_func(self, context):
 self.layout.operator(ExportHairWorks.bl_idname, text="HairWorks (.apx)");

def register():
 bpy.utils.register_class(ExportHairWorks);
 bpy.types.INFO_MT_file_export.append(menu_func);

def unregister():
 bpy.utils.unregister_class(ExportHairWorks);
 bpy.types.INFO_MT_file_export.remove(menu_func);

if __name__ == "__main__":
 register();
 bpy.ops.export_hairworks_file.apx('INVOKE_DEFAULT');