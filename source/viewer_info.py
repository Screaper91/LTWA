from tkinter import StringVar, ttk
from typing import Callable, Tuple, Any

from Zoom import Zoom_Advanced, MultiImageZoom
from PIL import Image

class CursorPositionInfo:
	def __init__(self, frame: Zoom_Advanced, callback: Callable[[Tuple[Any,Any]], str]):
		self._callback = callback
		self.text = StringVar()
		self.text.set("Here is text with info about where the cursor is")
		self.label = ttk.Label(frame.canvas, textvariable=self.text).place(relx=1, y=0, anchor='ne')
		frame.canvas.bind('<Motion>', self.moved)
		frame.canvas.bind('<Enter>', self.moved)
		self.frame = frame

	def moved(self, event):
		pos = self.frame.get_pos_on_image(event.x, event.y)
		self.text.set(self._callback(pos))

def show_exact_position(position: Tuple[Any, Any]):
	return "({x}, {z})".format(x = position[0], z = position[1])

class TransformedPosition:
	def __init__(self, min_x = 0, min_y = 0, scale_x = 1.0, scale_y = 1.0):
		self._minX = min_x
		self._minY = min_y
		self._scaleX = scale_x
		self._scaleY = scale_y

	def transform(self, position: tuple):
		return (position[0] * self._scaleX + self._minX), (position[1] * self._scaleY + self._minY)

class CoordinateFormatter:
	def __init__(self, isRawChunkPos: bool, **kwargs):
		if "minChunkPos" in kwargs:
			minChunkPos: tuple = kwargs["minChunkPos"]
			minBlockPos = minChunkPos[0] * 16, minChunkPos[1] * 16
		elif "minBlockPos" in kwargs:
			minBlockPos: tuple = kwargs["minBlockPos"]
			minChunkPos = minBlockPos[0] / 16, minBlockPos[1] / 16
		else:
			minBlockPos = minChunkPos = 0, 0

		if isRawChunkPos:
			chunkScalar = 1; blockScalar = 16
		else:
			chunkScalar = 1 / 16; blockScalar = 1
		self._chunkTransformation = TransformedPosition(minChunkPos[0], minChunkPos[1], chunkScalar, chunkScalar)
		self._blockTransformation = TransformedPosition(minBlockPos[0], minBlockPos[1], blockScalar, blockScalar)

	def format(self, position: Tuple[Any, Any]):
		cx, cz = self._chunkTransformation.transform(position)
		bx, bz = self._blockTransformation.transform(position)
		return "Block: ({}, y, {})\nChunk: ({}, {})".format(int(bx) - 1, int(bz) - 1, int(cx) - 1, int(cz) - 1)

class BiomeInfo:
	def __init__(self, frame: Zoom_Advanced, image: Image.Image, biomes, ignore_indices = None, isRawChunkPos = False, **kwargs):
		self._biomes = biomes
		self._image = image
		self._frame = frame
		self._coords = CoordinateFormatter(isRawChunkPos, **kwargs)
		self._ignore = {ignore_indices} if isinstance(ignore_indices, (int,None)) else ignore_indices
		
	def format(self, position: tuple):
		biome_info: str = ""
		try:
			index: int = self._image.getpixel(position)
			if index not in self._ignore:
				biome_info = "\n" + self._biomes[index]
		except IndexError:
			pass
		return self._coords.format(position) + biome_info
