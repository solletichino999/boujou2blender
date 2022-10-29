import bpy
from mathutils import Matrix, Vector
import math


from bpy_extras.io_utils import ExportHelper
from bpy.props import (
        StringProperty,
        CollectionProperty,
        )
from bpy.types import (
        Operator,
        OperatorFileListElement,
        )


# Define the Scale Factor of the scene
scale_factor = 1


#
def file_loader(fileName, scale_factor):
	file = open(fileName, 'r')
	lines = file.readlines()
	file.close()

	#check if header is correct (dont think it is necessary, delete if you like...)
	if 'boujou export' not in lines[0]:
		print ('ERROR: incorrect file header.')
		print ('line 0:')
		print (' - expecting "# boujou export: text"')
		print (' - found ' + lines[0])


	#set up variables
	camera_data = []
	vertex_data = []
	resolution = []
	filmback = []
	camera_read = False
	vertex_read = False

	#set resolution and filmback
	res_line = lines[12].split()
	resolution.append(int(res_line[2]))
	resolution.append(int(res_line[3]))
	filmback_line = lines[13].split()
	filmback.append(float(filmback_line[2]))
	filmback.append(float(filmback_line[3]))

	#loop
	for line in lines:

		################################################################################
		#read camera data to list
		################################################################################
		if camera_read == True:
			coords = line.split()
			if len(coords) == 0:
				camera_read = False
				print(str(len(camera_data)) + ' frames exported')
				print('End of camera block reached')
			else:
				coords = [float(i) for i in coords]
				coords[9] = coords[9] * scale_factor
				coords[10] = coords[10] * scale_factor
				coords[11] = coords[11] * scale_factor
				camera_data.append(coords)

		if ('#R(0,0)' in line):
			print('Camera block found')
			camera_read = True


		################################################################################
		#read vertex data to list
		################################################################################
		if vertex_read == True:
			coords = line.split()
			if '#End of boujou export file' in line:
				vertex_read = False
				print (str(len(vertex_data)) + ' vertices found')
				print ('End of vertex block reached')
			else:
				coords = [(float(i) * scale_factor) for i in coords]
				if len(coords) > 0:
					vertex_data.append(coords)

		if ('#x\ty\tz' in line):
			print ('Vertex block found')
			vertex_read = True

	return resolution, filmback, camera_data, vertex_data


def scene_setup(resolution, camera_data):
	bpy.context.scene.render.resolution_x = resolution[0]
	bpy.context.scene.render.resolution_y = resolution[1]
	bpy.context.scene.render.resolution_percentage = 100
	bpy.context.scene.render.fps = 30 #not really needed, make sure you export frames not movie to match composite clip
	bpy.context.scene.frame_start = 1
	bpy.context.scene.frame_end = len(camera_data)
	
	
def geometry_setup(vertex_data):
	if len(vertex_data) > 0:
		m = bpy.data.meshes.new('Boujou_Pointcloud') #new mesh
		m.vertices.add(len(vertex_data)) #add vertex
		for i in range(0,len(vertex_data)):
			m.vertices[i].co = (vertex_data[i][0], vertex_data[i][1], vertex_data[i][2]) #set each vertex position
		point_object = bpy.data.objects.new('Boujou_Pointcloud', m) # create object
		bpy.context.collection.objects.link(point_object) #link object to scene
		return point_object
	else:
		return None


def camera_setup(filmback, camera_data):
	cam = bpy.data.cameras.new('Boujou_Camera')
	cam.sensor_width = filmback[0]
	cam_obj = bpy.data.objects.new('Boujou_Camera', cam)
	bpy.context.collection.objects.link(cam_obj)

	a = 1
	for i in camera_data:
		#set up transform matrix from list
		rX = (i[0], i[1], i[2], 0.0)
		rY = (i[3], i[4], i[5], 0.0)
		rZ = (i[6], i[7], i[8], 0.0)
		tR = (i[9], i[10], i[11], 1.0)

		foc_len = i[12] #focal length for animated focal length

		#create and transpose matrix
		m = rX, rY, rZ, tR
		transform_matrix = Matrix(m)
		transform_matrix.transpose()


		cam_obj.matrix_basis = transform_matrix #set rotation to matrix
		rot = cam_obj.rotation_euler #get euler rotation from updated camera rotation
		print (rot)
		print (' ')
		rot[0] = rot[0] - math.pi #rotate camera 180 degrees around x axis
		cam_obj.keyframe_insert(data_path = 'rotation_euler', frame = (a)) #set rotation keyframe

		cam_obj.location = tR[:-1]
		cam_obj.keyframe_insert(data_path = 'location', frame = (a)) #set location keyframe
		
		cam.lens = foc_len
		cam.keyframe_insert(data_path = 'lens', frame = (a)) #set focal lens keyframe
		a += 1
	
	return cam, cam_obj


# Run the Boujou script after loading the .txt file
def runCode(textFileName):
    
    ####################execution######################
    filename = textFileName #Imported text file name
    #scale_factor = 1

    resolution, filmback, camera_data, vertex_data = file_loader(filename, scale_factor)

    scene_setup(resolution, camera_data)

    point_object = geometry_setup(vertex_data)

    cam, cam_obj = camera_setup(filmback, camera_data)

    print ('############################################################################################')
    print ('###########################Boujou 5 to Blender 2.93 importer################################')
    print ('############################################################################################')    


# Load the text file
class SlideshowAddSlide(bpy.types.Operator, ExportHelper):
    bl_idname = "slideshow.add_slide"
    bl_label = "Import Boujou Txt File"
    bl_options = {'REGISTER', 'UNDO'}
    files: CollectionProperty(
            name="File Path",
            type=OperatorFileListElement,
            )
    directory: StringProperty(
            subtype='DIR_PATH',
            )

    filename_ext = ".txt"

    def execute(self, context):
        import os
        directory = self.directory
        for file_elem in self.files:
            filepath = os.path.join(directory, file_elem.name)
            print(filepath)
            runCode(filepath)
        return {'FINISHED'}