# BEGIN GPL BLOCK    
#    Generate parametric Bamboo meshes
#    Copyright (C) 2017  Mark Fitzgibbon
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# END GPL BLOCK
bl_info = {
	"name":"Bamboo Generator",
	"description":"Generate parametric Bamboo",
	"version":(0,1,0),
	"blender":(2,78,0),
	"support":"TESTING",
	"category":"Object",
	"location":"Add",
	"author":"Mark Fitzgibbon"
}
import math
from math import radians

import bpy
from bpy.props import FloatProperty, IntProperty

import bmesh

class Bamboo:

	def __init__(self, radius1, segments, verticalSegs, segHeight, innerRadius, ringRadius, ringHeight):
		self.radius1 = radius1
		self.segments = segments
		self.stacks = verticalSegs
		self.segHeight = segHeight

		self.radius2 = ringRadius
		self.radiusInternal = innerRadius
		self.ringHeight = ringHeight

	def genMeshData(self):
		
		verts = []
		edges = []
		faces = []

		index = 0
		indexZ = 0

		angle = 360/self.segments

		polarX = lambda n: self.radius1 * math.cos(radians(angle*n))
		polarY = lambda n: self.radius1 * math.sin(radians(angle*n))

		ringX = lambda n: self.radius2 * math.cos(radians(angle*n))
		ringY = lambda n: self.radius2 * math.sin(radians(angle*n))

		coreX = lambda n: self.radiusInternal * math.cos(radians(angle*n))
		coreY = lambda n: self.radiusInternal * math.sin(radians(angle*n))


		#Vertexes
		while(indexZ <= self.stacks):
			index = 0
			while(index < self.segments):
				if (indexZ == 0 ):
					verts.append((polarX(index),polarY(index),(indexZ*self.segHeight)))
				else:
					verts.append((polarX(index),polarY(index),((indexZ-1)*self.segHeight + (self.segHeight - self.segHeight *self.ringHeight))))
				index += 1
			
			if(indexZ is not 0):
				index = 0
				while(index < self.segments):
					verts.append((ringX(index),ringY(index),(self.segHeight*(indexZ-1) +  (self.segHeight - self.segHeight * self.ringHeight/2))))
					index += 1
				index = 0
				while(index < self.segments):
					verts.append((polarX(index),polarY(index),(indexZ*self.segHeight)))
					index += 1
			indexZ += 1

		indexZ -=1

		while(indexZ >= 0):
			index = 0
			while(index < self.segments):
				verts.append((coreX(index),coreY(index),(indexZ*self.segHeight)))
				index +=1
			indexZ -=1


		#Non no-faced edges

		#Faces
		indexFace = 0
		while indexFace < ((self.stacks*3) + 1 + self.stacks):
			for n in range(0, (self.segments-1)):
				alpha = (indexFace * self.segments) + n
				bravo = (indexFace * self.segments) + n + 1
				delta = ((indexFace+1) * self.segments) + n
				charlie = ((indexFace+1) * self.segments) + n +1

				face = (alpha, bravo, charlie, delta)
				faces.append(face)

			#attach last face per row to first
			alpha = (indexFace * self.segments) + (self.segments-1)
			bravo = (indexFace * self.segments)
			delta = ((indexFace+1) * self.segments) + (self.segments-1)
			charlie = ((indexFace+1) * self.segments)

			face = (alpha, bravo, charlie, delta)
			faces.append(face)

			indexFace += 1

		#Last ring to first ring
		for n in range(0, (self.segments-1)):
			alpha =  n
			bravo =  n + 1
			delta =  len(verts) - self.segments + n 
			charlie =  len(verts) - self.segments + n + 1

			face = (alpha, delta, charlie, bravo)
			faces.append(face)

		faces.append((0, self.segments-1, len(verts)-1, len(verts) - self.segments))

		#Make arrays part of Bamboo object
		self.verts = verts
		self.edges = edges
		self.faces = faces


class BambooOperator(bpy.types.Operator):
	bl_idname = "object.bamboo"
	bl_label = "Bamboo Generator"
	bl_options = {'REGISTER', 'UNDO'}

	radius = FloatProperty(
		name ="Radius",
		min = 0.01,
		default = 1
		)

	innerRadius = FloatProperty(
		name = "Inner Radius",
		min = 0.01,
		default = .8)

	ringRadius = FloatProperty(
		name = "Ring Radius",
		min = 0.01,
		default = 1.1)
	ringHeight = FloatProperty(
		name = "Ring Height (percent)",
		min = 0.01,
		max = 1,
		default = .2)

	segments = IntProperty(
		name = "Segments",
		min = 3,
		default = 12
		)
	verticalSegs = IntProperty(
		name = "Vertical Segments",
		min = 1,
		default = 1
		)
	segHeight = FloatProperty(
		name = "Segment Height",
		min = 0.01,
		default = 2)


	def execute(self, context):
		mesh_data = bpy.data.meshes.new("bamboo_mesh_data")
		bamboo = Bamboo(self.radius, self.segments, self.verticalSegs, self.segHeight, self.innerRadius, self.ringRadius, self.ringHeight)
		bamboo.genMeshData()
		mesh_data.from_pydata(bamboo.verts, bamboo.edges, bamboo.faces)

		bm = bmesh.new()
		bm.from_mesh(mesh_data)

		mesh_data.update()

		mesh_obj = bpy.data.objects.new("Bamboo", mesh_data)
		mesh_obj.location = bpy.context.scene.cursor_location

		scene = bpy.context.scene
		scene.objects.link(mesh_obj)

		return {'FINISHED'}

def addToMenu(self, context):
	self.layout.operator(
		BambooOperator.bl_idname,
		text = "Bamboo Generator"
		)

def register():
	bpy.utils.register_class(BambooOperator)
	bpy.types.INFO_MT_add.append(addToMenu)

def unregister():
	bpy.utils.unregister_class(BambooOperator)
	bpy.types.INFO_MT_add.remove(addToMenu)

if __name__ == "__main__":
	register()