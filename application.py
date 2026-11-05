from math import ceil, floor
from tkinter import BooleanVar, Canvas, Listbox, Tk, StringVar, Label, Toplevel, Menu, filedialog
from tkinter import ttk

from PIL import Image, ImageTk, ImageDraw
from typing import *
from numpy import concatenate, ndarray, unique, empty, int32, ndindex, squeeze, array
#from cubiomes import Generator as BiomeGenerator

from Long_Term_World_Analysis import WorldExplorer, create_rectangles, merged_deque
from Zoom import Zoom_Advanced as Zoomed
from Zoom import MultiImageZoom
from viewer_info import CoordinateFormatter, CursorPositionInfo, BiomeInfo
from biomes import Biome, cubiomes_palette

Range = Tuple[int, int, int, int, int]

def create_range(start_block_x: int, start_block_z: int, width_x_meters: int, height_z_meters: int, target_depth_y: int, scale: int = 1) -> Range:
	return start_block_x // scale, start_block_z // scale, width_x_meters // scale, height_z_meters // scale, target_depth_y if scale == 1 else target_depth_y // 4

def create_chunk_range(start_chunk_x: int, start_chunk_z: int, end_chunk_x: int, end_chunk_z: int, target_depth_y: int, scale_meters: int = 1):
	return create_range(start_chunk_x * 16, start_chunk_z * 16, (end_chunk_x - start_chunk_x + 1) * 16, (end_chunk_z - start_chunk_z + 1) * 16, target_depth_y, scale_meters)

def get_palette(biome_palette, transparent_index = None, default_alpha = 255, *error_color: int):
	palette: List[int] = []
	for id in biome_palette.biomes:
		palette.extend(Biome.parse(id).amidst_color)
	if isinstance(transparent_index, int) and transparent_index > -1:
		for i in range(len(palette),0,-3):
			palette.insert(i, default_alpha)
		if transparent_index < len(biome_palette.biomes):
			palette[transparent_index * 4 + 3] = 0
		else:
			while len(palette) < transparent_index * 4:
				palette.extend((0, 0, 0, default_alpha))
			palette.extend((0, 0, 0, 0))
		if error_color:
			palette.extend(error_color)
		return palette, "RGBA"
	else:
		return palette, "RGB"

def view_generated_biomes(root: Tk, path: str, include_underground=False):
		root.title("Biome Viewer")

		world = WorldExplorer(path)

		rectangles, bounds = world.get_chunk_boxes()
		#rectangles, bounds = world.get_3d_chunk_positions()
		min_x, min_z = bounds[0], bounds[1]

		biome_palette = world._world.biome_palette

		img = Image.new('P', ((bounds[2]-min_x)*16, (bounds[3]-min_z)*16), world.transparent)

		lone_chunk = Image.new('P', (16, 16))
		print("Reading biomes from chunks...")
		count = len(rectangles)
		i = 1
		underground_layers: Union[Dict[Tuple[int, int], ndarray],Set[Tuple[int,int]]] = {} if include_underground else set()
		for entry in rectangles:
			if len(entry) == 2:
				cx, cz = entry
				top_data, layers = world.get_chunk_biomes(cx, cz, include_underground=include_underground)
				if not isinstance(layers, bool):
					underground_layers[entry] = layers
				elif layers:
					underground_layers.add(entry)
				lone_chunk.putdata(top_data.ravel())
				img.paste(lone_chunk, ((cx - min_x) * 16, (cz - min_z) * 16))
			else:
				top_data, layers = world.get_chunk_rect_biomes(entry[0], entry[1], entry[2]-entry[0]+1, entry[3]-entry[1]+1, include_underground=include_underground)
				rect_img = Image.fromarray(top_data.T)
				if include_underground:
					underground_layers.update(layers)
				else:
					underground_layers.union(layers)
#				create_palette(rect_img, biome_palette)
				img.paste(rect_img, ((entry[0] - min_x) * 16, (entry[1] - min_z) * 16))
			print(i, "/", count)
			i += 1
		
		palette, mode = get_palette(biome_palette, world.transparent, 255, *(255, 0, 0, 255))
		img.putpalette(palette, mode)
		

		if underground_layers and isinstance(underground_layers, dict):
			nw_corner = min_x, min_z
			rectangles, bounds = create_rectangles(underground_layers.keys())
			min_x, min_z = bounds[0], bounds[1]

			img_layers = ImageLayers('P', ((bounds[2]-min_x)*16, (bounds[3]-min_z)*16), world.transparent)
			
			for entry in rectangles:
				i = 0
				if len(entry) == 2:
					layers = underground_layers.pop(entry)
					rect_img = lone_chunk
				else:
					if entry[1] == entry[3]:
						temp = [underground_layers.pop((x, entry[1])) for x in range(entry[0], entry[2] + 1)]
						layers: ndarray = concatenate(temp, axis=0)
					elif entry[0] == entry[2]:
						temp = [underground_layers.pop((entry[0], z)) for z in range(entry[1], entry[3] + 1)]
						layers = concatenate(temp, 1)
					else:
						layers = concatenate([concatenate([underground_layers.pop((x,z)) for z in range(entry[1], entry[3] + 1)],axis=1) for x in range(entry[0], entry[2] + 1)],axis=0)
					rect_img = Image.new('P', layers.shape, world.transparent)
				layers = layers.T
				# Fill layer with data
				destination = ((entry[0] - min_x) * 16, (entry[1] - min_z) * 16)
				data = SequencePopper(list(layers.ravel()),world.transparent)
				while True:
					if not data:
						break
					rect_img.putdata([val for val in data])
					img_layers[i].paste(rect_img, destination)
					i += 1
			
			palette, mode = get_palette(biome_palette, world.transparent, 192)
			palette[-1] = 127
			for layer in img_layers:
				layer.putpalette(palette, mode)
			zoom = MultiImageZoom(root, img, False)
			offset = ((min_x - nw_corner[0]) * 16, (min_z - nw_corner[1]) * 16)
			return CursorPositionInfo(zoom, BiomeInfo3d(zoom, img, ImageCycler(zoom, img_layers, offset), biome_palette, world.transparent, minChunkPos=nw_corner, layers_offset=offset).format)
		
		
					
		zoom = Zoomed(root, img, False)
		return CursorPositionInfo(zoom, BiomeInfo(zoom, img, biome_palette, world.transparent, minChunkPos=(min_x, min_z)).format)
			# TODO: put palette in each layer and add to canvas where it scales!

			#if i == 100:
			#	create_palette(img, biome_palette, world.transparent, 255, 0, 0, 255)
			#	img.show("biomes early debug")
		
		
#		img.show("biomes")
#		canvas.create_image(0, 0, image=img, anchor='nw')
#		canvas.img = img

		#return Zoomed(root, img, False)

class ImageLayers:
	def __init__(self, mode: str, size: Tuple[int,int], color = 0):
		self._size = size
		self._mode = mode
		self._color = color
		self._layers = [Image.new(mode, size, color)]

	def __getitem__(self, index: int):
		if index == len(self._layers):
			self._layers.append(Image.new(self._mode, self._size, self._color))
		return self._layers[index]

	def __iter__(self):
		return iter(self._layers)

	def __len__(self):
		return len(self._layers)

class ImageCycler:
	def __init__(self, zoom: MultiImageZoom, images: ImageLayers, coords):
		self._zoom = zoom
		self._images = images
		self._index = 0
		self._rect_id = zoom.add_scaleable_image(images[0], coords)
		zoom.canvas.bind("l", self.change_image)
		#zoom.canvas.itemconfigure(zoom.container, state='hidden') # this hides the rectangle, find a way to hide the image instead

	def change_image(self, *event):
		self._index = (self._index + 1) % len(self._images)
		self._zoom.replace_scaleable_image(self._rect_id, self._images[self._index])

	def current(self):
		return self._images[self._index]

class BiomeInfo3d:
	def __init__(self, frame: MultiImageZoom, image: Image.Image, layers: ImageCycler, biomes, ignore_indices = None, isRawChunkPos = False, **kwargs):
		self._biomes = biomes
		self._image = image
		self._frame = frame
		self._coords = CoordinateFormatter(isRawChunkPos, **kwargs)
		self._ignore = set(ignore_indices) if isinstance(ignore_indices, (set, list, tuple)) else {ignore_indices}
		self._layers = layers
		self._layers_offset = kwargs.get("layers_offset", (0, 0))

	def format(self, position: tuple):
		biome_info: str = ""
		try:
			index: int = self._image.getpixel(position)
			if index not in self._ignore:
				biome_info = "\nBiome: " + self._biomes[index]
		except IndexError:
			pass
		try:
			offset_pos = position[0] - self._layers_offset[0], position[1] - self._layers_offset[1]
			index: int = self._layers.current().getpixel(offset_pos)
			if index not in self._ignore:
				biome_info += "\nUnderground: " + self._biomes[index]
		except IndexError:
			pass
		return self._coords.format(position) + biome_info

class SequencePopper:
	def __init__(self, sequence: list, default_value, overwrite: bool = True):
		self._sequence = sequence
		self._default = default_value
		self._overwrite = overwrite
		self._prev_len = len(sequence)
		if overwrite:
			self._prev_len -= 1

	def __iter__(self):
		for deq in self._sequence:
			if len(deq) == 0:
				yield self._default
			else:
				yield deq.popleft()


		for i in range(len(self._sequence)-1,self._prev_len,-1):
			self._sequence.pop()

		if self._overwrite:
			for i in range(self._prev_len - 1, -1, -1):
				if len(self._sequence[i]) > 0:
					self._prev_len = i + 1
					return
			self._sequence.clear()
		else:
			for i in range(self._prev_len, -1, -1):
				if len(self._sequence[i]) == 0:
					self._sequence.pop()
				else:
					self._prev_len = i
					return
		self._prev_len = 0

	def __bool__(self):
		return self._prev_len > 0


def view_generated_world(root: Tk, path: str, dimension: str = "minecraft:overworld"):

	world = WorldExplorer(path)
	root.title("{} - Cave Biome Fixer".format(world.get_world_name()))

	rectangles, bounds = world.get_chunk_boxes(dimension)
	min_x, min_z = bounds[0], bounds[1]

	color = (128, 0, 255, 255)

	img = Image.new('RGBA', (bounds[2]-min_x, bounds[3]-min_z))
	draw = ImageDraw.Draw(img)

	# Cave biome prediction
	#gen = BiomeGenerator("1.19")
	#gen.apply(world.get_world_seed(), 0)

	points = []
	for entry in rectangles:
		if len(entry) == 2:
			points.append((entry[0] - min_x, entry[1] - min_z))
		else:
			draw.rectangle((entry[0]-min_x, entry[1]-min_z, entry[2]-min_x+1, entry[3]-min_z+1), fill=color)
	draw.point(points, color)

	coordFormat = CoordinateFormatter(True, minChunkPos=(min_x, min_z))
	cursorPosInfo = CursorPositionInfo(Zoomed(root, img, False), coordFormat.format)

	spawn_pos = world.get_world_spawn()
	translated_spawn = (spawn_pos[0] - (min_x * 16)) / 16, (spawn_pos[1] - (min_z * 16)) / 16
	canvas = cursorPosInfo.frame.canvas

	spawn_marker = canvas.create_oval(translated_spawn[0]-1, translated_spawn[1]-1, translated_spawn[0]+2, translated_spawn[1]+2, fill='blue')
	spawn_marker = MapMarker(canvas, spawn_marker, "Spawn Point\nX: {} Z: {}".format(*spawn_pos), translated_spawn[0], translated_spawn[1] - 2)
	
	def generator_params_callback(rectId, coords: Tuple[float, float, float, float]):
		x0, y0, x1, y1 = coords
		x0, y0 = cursorPosInfo.frame.get_pos_on_image(x0, y0, useRawPos=True)
		x1, y1 = cursorPosInfo.frame.get_pos_on_image(x1, y1, useRawPos=True)

		x, z = coordFormat._blockTransformation.transform(((x0 + x1) / 2, (y0 + y1) / 2))

		return MapMarker(canvas, rectId, 'Center: {}, y, {}\nSize: {}x{}'.format(int(x) - 1, int(z) - 1, round((x1 - x0) * 16), round((y1 - y0) * 16)), (coords[0] + coords[2]) / 2, (coords[1] + coords[3]) / 2)

	def create_cave_fixer_callback(copy_source_path):
		cave_world = WorldExplorer(copy_source_path)
		def cave_fixer_callback(rectId, coords: Tuple[float, float, float, float]):
			x0, y0, x1, y1 = coords
			x0, y0 = cursorPosInfo.frame.get_pos_on_image(x0, y0, useRawPos=True)
			x1, y1 = cursorPosInfo.frame.get_pos_on_image(x1, y1, useRawPos=True)

			cx0, cz0 = coordFormat._chunkTransformation.transform((x0, y0))
			cx1, cz1 = coordFormat._chunkTransformation.transform((x1, y1))

			cx0, cz0, cx1, cz1 = floor(cx0), floor(cz0), floor(cx1), floor(cz1)

		#	for cx in range(cx0, cx1):
		#		for cz in range(cz0, cz1):
		#			print('({}, {}): {}'.format(cx, cz, world.get_chunk_biomes_status(cx, cz)))

			def operate():
				translate = lambda entry: (entry[0] - min_x, entry[1] - min_z)
				fixed, good, too_old, bad = world.fix_deepslate_biomes(cave_world, (cx0, cz0, cx1, cz1))
				if len(fixed) > 0:
					draw.point([translate(entry) for entry in fixed], (0, 255, 0, 255))
				if len(good) > 0:
					draw.point([translate(entry) for entry in good], (0, 128, 0, 255))
				if len(too_old):
					draw.point([translate(x) for x in too_old], (234, 192, 0, 255))
				if len(bad) > 0:
					draw.point([translate(entry) for entry in bad], (128, 0, 0, 255))
				cursorPosInfo.frame._update()

			root.after(100, operate)

			marker = MapMarker(canvas, rectId, 'Operation Range\n({}, {}) to ({}, {})'.format(cx0, cz0, cx1, cz1), coords[0], coords[1])

			marker.show_text()

			return marker
		return cave_fixer_callback

	# create_cave_fixer_callback(other_path)


	return cursorPosInfo, spawn_marker, create_cave_fixer_callback

class RectangleAnnotations:
	def __init__(self, frame: Zoomed, callback: Callable[[Any, Tuple[int, int, int, int]], 'MapMarker']):
		self._frame = frame
		self._add_rectangle = ttk.Button(frame.canvas, text='Add Rect', command=self._begin_add)
		self._add_rectangle.place(relx=1, rely=1, anchor='se')
		self._state = 0
		self._new_rect = None
		self._func_ids = {}
		self._callback = callback
		self._markers: List[MapMarker] = []

	def _begin_add(self):
		self._state = 0
		self._func_ids['<Button-3>'] = self._frame.canvas.bind('<Button-3>', self._click)

	def _click(self, event):
		if self._state:
			# Choosing ending corner
			self._unbind_func('<Motion>')
			self._unbind_func('<Enter>')
			self._unbind_func('<Button-3>')
			x0, y0, *_ = self._frame.canvas.coords(self._new_rect)
			self._frame.canvas.delete(self._new_rect); self._new_rect = None
			x1, y1 = self._canvas_transform(event)
			itemid = self._frame.canvas.create_rectangle(x0, y0, x1, y1)
			self._markers.append(self._callback(itemid, self._frame.canvas.coords(itemid)))
			self._state = 0
		else:
			# Choosing starting corner
			self._func_ids['<Motion>'] = self._frame.canvas.bind('<Motion>',self._moved,'+')
			self._func_ids['<Enter>'] = self._frame.canvas.bind('<Enter>',self._moved,'+')
			self._new_rect = self._frame.canvas.create_polygon(self._canvas_transform(event) * 3)
			self._state = 1

	def _unbind_func(self, sequence):
		func_callbacks = self._frame.canvas.tk.call('bind', self._frame.canvas._w, sequence, None).split('\n')
		funcid = self._func_ids.pop(sequence)
		new_callbacks = [l for l in func_callbacks if l[6:6 + len(funcid)] != funcid]
		self._frame.canvas.tk.call('bind', self._frame.canvas._w, sequence, '\n'.join(new_callbacks))
		self._frame.canvas.deletecommand(funcid)

	def _canvas_transform(self, event):
		return self._frame.canvas.canvasx(event.x), self._frame.canvas.canvasy(event.y)

	def _moved(self, event):
		#pos = self._frame.get_pos_on_image(event.x, event.y)
		x0, y0, *_ = self._frame.canvas.coords(self._new_rect)
		x1, y1 = self._canvas_transform(event)
		self._frame.canvas.coords(self._new_rect, x0, y0, x1, y0, x1, y1, x0, y1)

class MapMarker:
	def __init__(self, canvas: Canvas, itemId: int, text: str, xpos: float, ypos: float):
		self._canvas = canvas
		self._text = text
		canvas.tag_bind(itemId, '<Button-1>', self.show_text)
		canvas.tag_bind('all', '<Button-1>', self.hide_text, '+')
		self._textId = canvas.create_text(xpos, ypos, text=text, anchor='s', state='hidden')
		self._hidden = True

	def show_text(self, *args):
		if self._hidden:
			self._canvas.itemconfigure(self._textId, state='normal')
			self._hidden = False

	def hide_text(self, *args):
		if self._hidden:
			return
		self._canvas.itemconfigure(self._textId, state='hidden')
		self._hidden = True

def scale(data, scalar: int):
	if isinstance(data, tuple):
		return tuple(scalar * i for i in data)

def view_generated_world_x16(root: Tk, path: str, dimension: str = "minecraft:overworld"):
	root.title("Chunks generated")

	world = WorldExplorer(path)

	rectangles, bounds = world.get_chunk_boxes(dimension)
	min_x, min_z = bounds[0], bounds[1]

	color = (128, 0, 255, 255)

	img = Image.new('RGBA', scale((bounds[2]-min_x, bounds[3]-min_z), 16))
	draw = ImageDraw.Draw(img)

#	points = []
	for entry in rectangles:
		if len(entry) == 2:
#			points.append(entry)
			draw.rectangle(((entry[0]-min_x) * 16, (entry[1]-min_z) * 16, (entry[0]-min_x) * 16 + 15, (entry[1]-min_z) * 16 + 15), fill=color)
			pass
		else:
			draw.rectangle(((entry[0]-min_x) * 16, (entry[1]-min_z) * 16, (entry[2]-min_x + 1) * 16 - 1, (entry[3]-min_z+ 1) * 16 -1), fill=(128, 0, 200, 255))
#	draw.point(points, color)
	
	#img.show()
	
	return Zoomed(root, img, False)

		#fill(canvas.img, rgb_to_pixel((255, 255, 0)), height=8)

def rgb_to_pixel(color: tuple) -> str:
	"""Converts a tuple (r, g, b) into a string tkinter can put in a image"""
	r,g,b = color
	hexcode: str = "#%02x%02x%02x" % (r,g,b)
	return hexcode


def fast(g: "BiomeGenerator", t_range: Range, dy=1, scale=1):
	# (startX, startZ, sizeX, sizeZ, startY), sizeY=1, scale=16
	# previously flip(generate_range(***).swapaxes(1, 2), 0)
	b: ndarray = g.generate_range(t_range, dy, scale)
	print(unique(b))
	c = squeeze(b)
	print(c)
	return c # ndarray 'c' is accurate 2d data: test 3d data before optimizing further

def show_generated(flat: ndarray):
	img = Image.new('P', flat.shape)
	img.putdata(flat.ravel())
	img.putpalette(cubiomes_palette, rawmode='RGB')
	img.show()

class BiomeGenerator:
	pass

def slow_exact(g: "BiomeGenerator", t_range: Range, dy: int=1, scale: int=1):
	print(g.seed, g.dim, g.mc)
	shape = (t_range[2], t_range[3], dy)
	arr = empty(shape, dtype=int32)
	for index in ndindex(shape):
		value = g.generate_at(t_range[1] + index[0], t_range[4] + index[2], t_range[0] + index[1], scale)
		arr[index] = value
	return arr

deep_dark_range: Range = (-3181, 1487, 32, 16, -51)
spawn_range: Range = (0, -16, 48, 16, -64)
verify_range: Range = (-68 * 16, -328 * 16, 16, 16, -64)
test_range: Range = (-5520, 1280, 16, 16, 48)

if spawn_range != create_chunk_range(0, -1, 2, -1, -64):
	print(create_chunk_range(0, -1, 2, -1, -64))
#check_range(spawn_range, 64, 1)



if __name__ == "__main__":

	root = Tk()
	root.option_add('*tearOff', False)
	win = root #Toplevel(root)

	canvas, spawn_marker, annotations = None, None, None

	menubar = Menu(win)
	menu_file = Menu(menubar)
	#menu_edit = Menu(menubar)

	def choose_world_folder():
		dirname = filedialog.askdirectory(mustexist=True, title='Open world folder')
		print(dirname)
		cursorPosInfo, spawn_marker, create_cave_fixer_callback = view_generated_world(root, dirname)
		menu_file.entryconfigure(0, state='disabled')
		menu_file.entryconfigure(2, state='normal', command=lambda: cursorPosInfo.frame._image.show())

		def choose_biome_source_folder():
			dir_name = filedialog.askdirectory(mustexist=True, title='Open reference world folder')
			annotations = RectangleAnnotations(cursorPosInfo.frame, create_cave_fixer_callback(dir_name))
			menu_file.entryconfigure(1, state='disabled')

		menu_file.entryconfigure(1, command=choose_biome_source_folder, state='normal')


	menubar.add_cascade(menu=menu_file, label='World')
	menu_file.add_command(label='Open...', command=choose_world_folder)
	menu_file.add_command(label='Open biome reference...', state='disabled')
	menu_file.add_command(label='Save Image...', state='disabled')
	#menubar.add_cascade(menu=menu_edit, label='Edit')
	#visual_style = StringVar(value=1)
	#menu_style = Menu(menu_edit)
	#menu_edit.add_cascade(menu=menu_style, label='Quick Style')
	#menu_style.add_radiobutton(label='cubiomes', variable=visual_style, value=1)
	#menu_style.add_radiobutton(label='chunkbase', variable=visual_style, value=2)
	#print("Max depth:", add_item(option, 0))
	win['menu'] = menubar
	save_image = None

	
	root.title("Long-Term World Analysis MC")
		
	root.mainloop()