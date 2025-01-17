import bpy # type: ignore
import bmesh # type: ignore
import csv
import os
import mathutils # type: ignore
from mathutils import Vector, Quaternion # type: ignore
from bpy_extras.io_utils import axis_conversion, orientation_helper # type: ignore
from bpy.props import ( # type: ignore
    BoolProperty,
    IntProperty,
    IntVectorProperty,
    StringProperty,
)
from bpy_extras.io_utils import ImportHelper # type: ignore
from bpy.props import StringProperty, BoolProperty, EnumProperty, CollectionProperty # type: ignore
from bpy.types import Operator # type: ignore
import numpy as np


bl_info = {
    "name": "CSV Importer",
    "author": "Puxtril, Ethnogeny",
    "version": (1, 4, 0),
    "blender": (2, 80, 0),
    "location": "File > Import-Export",
    "description": "Import CSV mesh dump",
    "category": "Import-Export",
}


@orientation_helper(axis_forward="-Y", axis_up="Z")
class Import_CSV(bpy.types.Operator):
    """Imports .csv meshes"""
    bl_idname = "object.import_csv"
    bl_label = "Import csv"
    bl_options = {"PRESET", "UNDO"}
    filepath: bpy.props.StringProperty(subtype="FILE_PATH") # type: ignore
    filter_glob: StringProperty(default="*.csv", options={"HIDDEN"}) # type: ignore

########################################################################
# General Properties

    mirrorVertX: bpy.props.BoolProperty(
        name="Mirror X",
        description="Mirror all the vertices across X axis",
        default=True,
    ) # type: ignore
    vertexOrder: bpy.props.BoolProperty(
        name="Flip Winding",
        description="Reorder vertices in counter-clockwise order",
        default=False,
    ) # type: ignore
    mirrorUV: bpy.props.BoolProperty(
        name="Mirror V",
        description="Flip UV Maps vertically",
        default=True,
    ) # type: ignore
    cleanMesh: bpy.props.BoolProperty(
        name="Clean Mesh",
        description="Remove doubles and enable smooth shading",
        default=True,
    ) # type: ignore
    showNormalize: bpy.props.BoolProperty(
        name="Show Normalize",
        description="Show options to normalize input values",
        default=False,
    ) # type: ignore
    skipFirstRow: bpy.props.BoolProperty(
        name="Skip Title",
        description="Skip first row of the .csv file",
        default=True,
    ) # type: ignore
    positionIndex: bpy.props.IntVectorProperty(
        name="Positions",
        description="Column numbers (0 indexed) of vertex positions",
        size=3,
        min=0,
        soft_max=20,
        default=(2, 3, 4),
    ) # type: ignore
    autoPosition: bpy.props.BoolProperty(
        name="Automatically find position",
        description="Automatically find vertex positions in the file and use that",
        default=True,
    ) # type: ignore
    autoUVs: bpy.props.BoolProperty(
        name="Automatically find UVs",
        description="Automatically find UV positions in the file and use that",
        default=True,
    ) # type: ignore

########################################################################
# UV properties

    uvCount: bpy.props.IntProperty(
        name="UV Map Count",
        description="Number of UV maps to import",
        min=0,
        max=5,
        default=1,
    ) # type: ignore
    uvIndex0: bpy.props.IntVectorProperty(
        name="UV 1",
        description="Column numbers (0 indexed) of UV map",
        size=2,
        min=0,
        soft_max=20,
        default=(14, 15),
    ) # type: ignore
    uvNormalize0: bpy.props.IntProperty(
        name="Normalize UV 1",
        description="Divide inputs by this number",
        default=1
    ) # type: ignore
    uvIndex1: bpy.props.IntVectorProperty(
        name="UV 2",
        description="Column numbers (0 indexed) of UV map",
        size=2,
        min=0,
        soft_max=20,
        default=(0, 0),
    ) # type: ignore
    uvNormalize1: bpy.props.IntProperty(
        name="Normalize UV 2",
        description="Divide inputs by this number",
        default=1
    ) # type: ignore
    uvIndex2: bpy.props.IntVectorProperty(
        name="UV 3",
        description="Column numbers (0 indexed) of UV map",
        size=2,
        min=0,
        soft_max=20,
        default=(0, 0),
    ) # type: ignore
    uvNormalize2: bpy.props.IntProperty(
        name="Normalize UV 3",
        description="Divide inputs by this number",
        default=1
    ) # type: ignore
    uvIndex3: bpy.props.IntVectorProperty(
        name="UV 4",
        description="Column numbers (0 indexed) of UV map",
        size=2,
        min=0,
        soft_max=20,
        default=(0, 0),
    ) # type: ignore
    uvNormalize3: bpy.props.IntProperty(
        name="Normalize UV 4",
        description="Divide inputs by this number",
        default=1
    ) # type: ignore
    uvIndex4: bpy.props.IntVectorProperty(
        name="UV 5",
        description="Column numbers (0 indexed) of UV map",
        size=2,
        min=0,
        soft_max=20,
        default=(0, 0),
    ) # type: ignore
    uvNormalize4: bpy.props.IntProperty(
        name="Normalize UV 5",
        description="Divide inputs by this number",
        default=1
    ) # type: ignore

########################################################################
# Vertex Color3 Properties

    color3Count: bpy.props.IntProperty(
        name="Vertex Color RGB Count",
        description="Number of Vertex Colors (RGB) to import",
        min=0,
        max=5,
        default=0,
    ) # type: ignore
    color3Index0: bpy.props.IntVectorProperty(
        name="Vertex Color RGB 1",
        description="Column numbers (0 indexed) of Vertex Colors (RGB)",
        size=3,
        min=0,
        soft_max=20,
        default=(10, 11, 12),
    ) # type: ignore
    color3Normalize0: bpy.props.IntProperty(
        name="Normalize Color RGB 1",
        description="Divide inputs by this number",
        default=1
    ) # type: ignore
    color3Index1: bpy.props.IntVectorProperty(
        name="Vertex Color RGB 2",
        description="Column numbers (0 indexed) of Vertex Colors (RGB)",
        size=3,
        min=0,
        soft_max=20,
        default=(0, 0, 0),
    ) # type: ignore
    color3Normalize1: bpy.props.IntProperty(
        name="Normalize Color RGB 2",
        description="Divide inputs by this number",
        default=1
    ) # type: ignore
    color3Index2: bpy.props.IntVectorProperty(
        name="Vertex Color RGB 3",
        description="Column numbers (0 indexed) of Vertex Colors (RGB)",
        size=3,
        min=0,
        soft_max=20,
        default=(0, 0, 0),
    ) # type: ignore
    color3Normalize2: bpy.props.IntProperty(
        name="Normalize Colors RGB 3",
        description="Divide inputs by this number",
        default=1
    ) # type: ignore
    color3Index3: bpy.props.IntVectorProperty(
        name="Vertex Color RGB 4",
        description="Column numbers (0 indexed) of Vertex Colors (RGB)",
        size=3,
        min=0,
        soft_max=20,
        default=(0, 0, 0),
    ) # type: ignore
    color3Normalize3: bpy.props.IntProperty(
        name="Normalize Colors RGB 4",
        description="Divide inputs by this number",
        default=1
    ) # type: ignore
    color3Index4: bpy.props.IntVectorProperty(
        name="Vertex Color RGB 5",
        description="Column numbers (0 indexed) of Vertex Colors (RGB)",
        size=3,
        min=0,
        soft_max=20,
        default=(0, 0, 0),
    ) # type: ignore
    color3Normalize4: bpy.props.IntProperty(
        name="Normalize Colors RGB 5",
        description="Divide inputs by this number",
        default=1
    ) # type: ignore

########################################################################
# Vertex Color Properties

    colorCount: bpy.props.IntProperty(
        name="Vertex Color Alpha Count",
        description="Number of Vertex Colors (Alpha) to import",
        min=0,
        max=5,
        default=0,
    ) # type: ignore
    colorIndex0: bpy.props.IntProperty(
        name="Vertex Color Alpha 1",
        description="Column number (0 indexed) of Vertex Color (Alpha)",
        min=0,
        soft_max=20,
        default=0,
    ) # type: ignore
    colorNormalize0: bpy.props.IntProperty(
        name="Normalize Color Alpha 1",
        description="Divide input by this number",
        default=1
    ) # type: ignore
    colorIndex1: bpy.props.IntProperty(
        name="Vertex Color Alpha 2",
        description="Column number (0 indexed) of Vertex Color (Alpha)",
        min=0,
        soft_max=20,
        default=0,
    ) # type: ignore
    colorNormalize1: bpy.props.IntProperty(
        name="Normalize Color Alpha 2",
        description="Divide input by this number",
        default=1
    ) # type: ignore
    colorIndex2: bpy.props.IntProperty(
        name="Vertex Color Alpha 3",
        description="Column number (0 indexed) of Vertex Color (Alpha)",
        min=0,
        soft_max=20,
        default=0,
    ) # type: ignore
    colorNormalize2: bpy.props.IntProperty(
        name="Normalize Color Alpha 3",
        description="Divide input by this number",
        default=1
    ) # type: ignore
    colorIndex3: bpy.props.IntProperty(
        name="Vertex Color Alpha 4",
        description="Column number (0 indexed) of Vertex Color (Alpha)",
        min=0,
        soft_max=20,
        default=0,
    ) # type: ignore
    colorNormalize3: bpy.props.IntProperty(
        name="Normalize Color Alpha 4",
        description="Divide input by this number",
        default=1
    ) # type: ignore
    colorIndex4: bpy.props.IntProperty(
        name="Vertex Color Alpha 5",
        description="Column number (0 indexed) of Vertex Color (Alpha)",
        min=0,
        soft_max=20,
        default=0,
    ) # type: ignore
    colorNormalize4: bpy.props.IntProperty(
        name="Normalize Color Alpha 5",
        description="Divide input by this number",
        default=1
    ) # type: ignore

    ###########################################
    # necessary to support multi-file import
    files: CollectionProperty(
        type=bpy.types.OperatorFileListElement,
        options={'HIDDEN', 'SKIP_SAVE'},
    ) # type: ignore

    directory: StringProperty(
        subtype='DIR_PATH',
    ) # type: ignore
    ###########################################

########################################################################
# Operator Functions

    def execute(self, context):
        for current_file in self.files:
            filepath = os.path.join(self.directory, current_file.name)

            transformMatrix = axis_conversion(
                from_forward=self.axis_forward,
                from_up=self.axis_up,
            ).to_4x4()

            # Only parse what it shown in the importer UI
            color3Args = [self.color3Index0, self.color3Index1, self.color3Index2, self.color3Index3, self.color3Index4]
            colorArgs = [self.colorIndex0, self.colorIndex1, self.colorIndex2, self.colorIndex3, self.colorIndex4]

            if self.autoPosition:
                ## read csv first row for position
                
                with open(filepath) as f:
                    reader = csv.reader(f)
                    for line in reader:
                        for rowIndex, rowValue in enumerate(line):
                            if "POSITION" in rowValue:
                                self.positionIndex = (rowIndex, rowIndex + 1 ,rowIndex + 2)
                                break
                

            if self.autoUVs:
                self.uvCount = 0
                uvArgs = []
                with open(filepath) as f:
                    reader = csv.reader(f)
                    for line in reader:
                        for rowIndex, rowValue in enumerate(line):
                            if "TEXCOORD" in rowValue: # If the row has the word for UV maps
                                if self.uvCount > 5: break # The OG code had 5 UVs, i don't see a need to exceed that, it will handle more anyway.
                                if uvArgs != []: # loop doesn't exist if the list is blank 
                                    if len(uvArgs[-1]) == 2: # I don't wan't to do a comparison for higher values cus it will be broken anyway
                                        uvArgs.append([rowIndex])
                                    else:
                                        uvArgs[-1].append(rowIndex) # If the inner list only has one value, complete it. This of course is assuming the csv export of the uvmaps is one after the other.
                                        self.uvCount += 1
                                else:
                                    uvArgs.append([rowIndex])
                        break

            else:
                uvArgs = [self.uvIndex0, self.uvIndex1, self.uvIndex2, self.uvIndex3, self.uvIndex4]

            verts, faces, uvs, color3s, colors = importCSV(
                filepath,
                self.positionIndex,
                uvArgs[: self.uvCount],
                color3Args[: self.color3Count],
                colorArgs[: self.colorCount],
                self.mirrorVertX,
                self.mirrorUV,
                self.vertexOrder,
                self.skipFirstRow,
            )

            # Don't do anything if not shown
            if self.showNormalize:
                uvsNormalizeArgs = [self.uvNormalize0, self.uvNormalize1, self.uvNormalize2, self.uvNormalize3, self.uvNormalize4]
                color3sNormalizeArgs = [self.color3Normalize0, self.color3Normalize1, self.color3Normalize2, self.color3Normalize3, self.color3Normalize4]
                colorsNormalizeArgs = [self.colorNormalize0, self.colorNormalize1, self.colorNormalize2, self.colorNormalize3, self.colorNormalize4]
            else:
                uvsNormalizeArgs = [1, 1, 1, 1, 1]
                color3sNormalizeArgs = [1, 1, 1, 1, 1]
                colorsNormalizeArgs = [1, 1, 1, 1, 1]

            meshObj = createMesh(
                verts,
                faces,
                uvs,
                uvsNormalizeArgs[: self.uvCount],
                color3s,
                color3sNormalizeArgs[: self.color3Count],
                colors,
                colorsNormalizeArgs[: self.colorCount],
                transformMatrix,
                current_file,
                filepath
            )

            meshObj = customSplitNormals(filepath, meshObj,transformMatrix, verts)

            if self.cleanMesh:
                tempBmesh = bmesh.new()
                tempBmesh.from_mesh(meshObj.data)
                bmesh.ops.remove_doubles(tempBmesh, verts=tempBmesh.verts, dist=0.0001)
                for face in tempBmesh.faces:
                    face.smooth = True
                tempBmesh.to_mesh(meshObj.data)
                tempBmesh.clear()

                meshObj.data.use_auto_smooth = True
                meshObj.data.update()
            
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def draw(self, context):
        generalBox = self.layout.box()
        generalBox.prop(self, "axis_forward")
        generalBox.prop(self, "axis_up")
        row1 = generalBox.row()
        row1.prop(self, "mirrorVertX")
        row1.prop(self, "mirrorUV")
        row2 = generalBox.row()
        row2.prop(self, "cleanMesh")
        row2.prop(self, "vertexOrder")
        row3 = generalBox.row()
        row3.prop(self, "showNormalize")
        row3.prop(self, "skipFirstRow")

        indexBox = self.layout.box()
        indexBoxRow0 = indexBox.row()
        indexBoxRow0.column().prop(self, "autoPosition")
        
        
        if self.autoPosition == False:
            indexBoxRow = indexBox.row()
            indexBoxRow.column().prop(self, "positionIndex")

        uvBox = self.layout.box()
        uvBoxRow0 = uvBox.row()
        uvBoxRow0.prop(self, "autoUVs")
        if self.autoUVs == False:
            uvBox.prop(self, "uvCount")
            for i in range(self.uvCount):
                uvBox.prop(self, f"uvIndex{i}")
                if self.showNormalize:
                    uvBox.prop(self, f"uvNormalize{i}")

        color3Box = self.layout.box()
        color3Box.prop(self, "color3Count")
        for i in range(self.color3Count):
            color3Box.prop(self, f"color3Index{i}")
            if self.showNormalize:
                color3Box.prop(self, f"color3Normalize{i}")

        colorBox = self.layout.box()
        colorBox.prop(self, "colorCount")
        for i in range(self.colorCount):
            colorBox.prop(self, f"colorIndex{i}")
            if self.showNormalize:
                colorBox.prop(self, f"colorNormalize{i}")


def importCSV(
    filepath: str,
    posIndicies: tuple,
    uvMapsIndicies: list,
    color3sIndicies: list,
    colorsIndicies: list,
    mirrorVertX: bool,
    mirrorUV: bool,
    flipVertOrder: bool,
    skipFirstRow: bool,
):
    # list<tuple3<float>>
    vertices = []
    
    # list<tuple3<int>>
    faces = []

    # list<list<tuple2<int>>>
    uvs = []

    for _ in range(len(uvMapsIndicies)):
        uvs.append([])
    # list<list<tuple3<float>>>
    color3s = []
    for _ in range(len(color3sIndicies)):
        color3s.append([])
    # list<list<float>>
    colors = []
    for _ in range(len(colorsIndicies)):
        colors.append([])

    x_mod = -1 if mirrorVertX else 1

    with open(filepath) as f:
        reader = csv.reader(f)

        if skipFirstRow:
            next(reader)

        curFace = []
        for rowIndex, row in enumerate(reader):
            curVertexIndex = rowIndex

            # Position
            curPos = (
                readFloatFromArray(row, posIndicies[0]) * x_mod / 10, # divide by 4 is changing the size, nothing else
                readFloatFromArray(row, posIndicies[1]) / 10,
                readFloatFromArray(row, posIndicies[2]) / 10
            )
            vertices.append(curPos)

            # UV Maps
            for i in range(len(uvMapsIndicies)):
                curUV = (
                    readFloatFromArray(row, uvMapsIndicies[i][0]),
                    readFloatFromArray(row, uvMapsIndicies[i][1])
                )
                if mirrorUV:
                    curUV = (curUV[0], 1 - curUV[1])
                uvs[i].append(curUV)

            # Vertex Colors3
            for i in range(len(color3sIndicies)):
                curColor3 = (
                    readFloatFromArray(row, color3sIndicies[i][0]),
                    readFloatFromArray(row, color3sIndicies[i][1]),
                    readFloatFromArray(row, color3sIndicies[i][2])
                )
                color3s[i].append(curColor3)

            # Vertex Colors
            for i in range(len(colorsIndicies)):
                curColor = readFloatFromArray(row, colorsIndicies[i])
                colors[i].append(curColor)

            # Append Faces
            curFace.append(curVertexIndex)
            if len(curFace) > 2:
                if flipVertOrder:
                    faces.append((curFace[2], curFace[1], curFace[0]))
                else:
                    faces.append(curFace)
                curFace = []

        return vertices, faces, uvs, color3s, colors


def createMesh(
    vertices: list,
    faces: list,
    uvs: list,
    uvsNormalize: list,
    color3s: list,
    color3sNormalize: list,
    colors: list,
    colorsNormalize: list,
    transformMatrix,
    current_file,
    filepath
):
    mesh = bpy.data.meshes.new(current_file.name.split(".")[0])
    mesh.from_pydata(vertices, [], faces)

    obj = bpy.data.objects.new(current_file.name.split(".")[0], mesh)

    # UV Maps
    for uvIndex in range(len(uvs)):
        uvLayer = mesh.uv_layers.new(name=f"UV{uvIndex}")
        for vertexIndex in range(len(uvLayer.data)):
            curUVs = uvs[uvIndex][vertexIndex]
            curUVsNorm = list(map(lambda x: x / uvsNormalize[uvIndex], curUVs))
            uvLayer.data[vertexIndex].uv = curUVsNorm

    # Vertex Colors3
    for color3Index in range(len(color3s)):
        color3Layer = mesh.vertex_colors.new(name=f"rgb{color3Index}")
        for vertexIndex in range(len(color3Layer.data)):
            curCol3 = color3s[color3Index][vertexIndex]
            curCol3Norm = list(map(lambda x: x / color3sNormalize[color3Index], curCol3))
            color3Layer.data[vertexIndex].color = [curCol3Norm[0], curCol3Norm[1], curCol3Norm[2], 0]

    # Vertex Colors
    for colorIndex in range(len(colors)):
        colorLayer = mesh.vertex_colors.new(name=f"alpha{colorIndex}")
        for vertexIndex in range(len(colorLayer.data)):
            curCol = colors[colorIndex][vertexIndex]
            curColNorm = curCol / colorsNormalize[colorIndex]
            colorLayer.data[vertexIndex].color = [curColNorm, curColNorm, curColNorm, 0]
    
    obj.data.transform(transformMatrix)
    obj.matrix_world = mathutils.Matrix()
    bpy.context.scene.collection.objects.link(obj)
    return obj

def customSplitNormals(filepath, obj, transformMatrix, verticesList):
    #obj.data.customdata_custom_splitnormals_add()

    # Normal custom verts on each axis
    obj.data.normals_split_custom_set([(0, 0, 0) for l in obj.data.loops])
    
    quats = []
    # Set normal for selected vertices
    normals = []
    skipFirst = True
    ### Make this all not hardcoded ###
    with open(filepath) as f:
        reader = csv.reader(f)
        
        if skipFirst == True:
            skipFirst = False
            next(reader)
        for line in reader:
            for columnIndex, column in enumerate(line):
                if columnIndex == 7:
                    
        ## Divide the normals? 
                    #normals.append(Vector((float(line[columnIndex])/255, float(line[columnIndex+1])/255, float(line[columnIndex+2])/255)).normalized()) #, float(line[columnIndex+3])/255
                    #print(normals)
                    
                    
                    x = float(line[columnIndex])/255
                    y = float(line[columnIndex + 1])/255
                    z = float(line[columnIndex + 2])/255
                    w = float(line[columnIndex + 3])/255
                    
                    #X, Y, Z = quaternion_to_euler_angle_vectorized2(w, x, y, z)
                    
                    quats.append(Quaternion((w,x,y,z)))
                    
                    #new_verts = [quat1 @ v.co for v in ob.data.vertices]
                    
                    #for normIndex, normal in enumerate(quats):  # is dedendant on the number of quaternions appended to list, brain not braining rn for better loop
        for vIndex, v in enumerate(verticesList):
            ## It's blender keeps the vertices index in the same order they are in the csv whe you do .from_pydata()
            
            #quat = quats[vIndex].conjugated()
            quat = quats[vIndex].normalized().conjugated()
            
            
            

            #co_final = obj.matrix_world @ v.normal
            # ! Might not even need euler, matrix from the Quaternion might still be what I'm looking for.
                        
            normals.append(transformMatrix @ obj.data.vertices[vIndex].normal @ quat.to_matrix())
            #normals.append(obj.data.vertices[vIndex].normal @ quat.to_matrix())
            #normals.append(quat[0])
            
                        # per vertex rotate the already existing vector
                    
#            if len(normals) >= 36954:   ## FOR TESTING OCTANE ONLY
#                print(normals)
#                print(quat)
#                break
                
                
                
                #if len(normals) % 1000 == 0:
                    #print(len(normals))
    
    #normals.transform(transformMatrix)
        # Goddammit i have to vector type everything so the multiplications works?
    #for i, normal in enumerate(normals):
        #normals[i] = normals[i] @ transformMatrix
        
    obj.data.calc_normals_split()
    obj.data.normals_split_custom_set_from_vertices(normals) 
    obj.data.update()
    
    print(obj.data.loops[0].normal)
    return obj


# IndexError and ValueError can be thrown here
# But wrap it in a generic `Exception` because... why not
def readFloatFromArray(arr, index, default = 0.0):
    try:
        return float(arr[index])
    except Exception:
        return default
    
def quaternion_to_euler_angle_vectorized2(w, x, y, z):
    ysqr = y * y

    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + ysqr)
    X = np.degrees(np.arctan2(t0, t1))

    t2 = +2.0 * (w * y - z * x)

    t2 = np.clip(t2, a_min=-1.0, a_max=1.0)
    Y = np.degrees(np.arcsin(t2))

    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (ysqr + z * z)
    Z = np.degrees(np.arctan2(t3, t4))

    return X, Y, Z


def menuItem(self, context):
    self.layout.operator(Import_CSV.bl_idname, text="Mesh CSV (.csv)")


def register():
    bpy.utils.register_class(Import_CSV)
    bpy.types.TOPBAR_MT_file_import.append(menuItem)


def unregister():
    bpy.utils.unregister_class(Import_CSV)
    bpy.types.TOPBAR_MT_file_import.remove(menuItem)


if __name__ == "__main__":
    register()
