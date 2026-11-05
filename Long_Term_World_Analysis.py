import amulet
from amulet.api.errors import ChunkDoesNotExist, ChunkLoadError, FormatError
from amulet.level.formats.leveldb_world.interface.chunk.base_leveldb_interface import BaseLevelDBInterface
from collections import deque

from numpy import ndarray, full, empty, ubyte, concatenate
from numpy.typing import NDArray
import numpy as np
import struct
from typing import *
from numpy.typing import NDArray
from biomes import Biome

cave_biomes = {Biome.LUSH_CAVES, Biome.DRIPSTONE_CAVES, Biome.DEEP_DARK}
cave_biome_ids = {187, 188, 190}

Dimension = Literal['minecraft:overworld','minecraft:the_nether','minecraft:the_end']
ChunkBiomeStatus = Literal['DOES_NOT_EXIST','NO_DEEPSLATE_LAYER']

	

#def full_resolution_3d_biomes(*args):
#	if len(args) == 3 and isinstance(args[0], BaseLevelDBInterface):
#		args = args[1:3]
#	heightmap, data = (
#		np.frombuffer(args[0][:512], "<i2").reshape((16,16)),
#		args[0][512:]
#	)
#	biomes: Dict[int, NDArray[np.uint32]] = {}
#	cy: int = args[1]
#	while data:
#		data, bits_per_value, arr = BaseLevelDBInterface._decode_packed_array(data)
#		if bits_per_value == 0:
#			value, data = struct.unpack(f"<I", data[:4])[0], data[4:]
#			biomes[cy] = np.full((16,16,16), value, dtype=np.uint32)
#		elif bits_per_value > 0:
#			palette_len, data = struct.unpack("<I", data[:4])[0], data[4:]
#			biomes[cy] = np.frombuffer(data, "<i4", palette_len)[arr].astype(np.uint32)
#			data = data[4 * palette_len :]
#		cy += 1
#	return heightmap, biomes

## Temporary fix for amulet-core 1.8.0 until natively support full array
#BaseLevelDBInterface._decode_height_3d_biomes = full_resolution_3d_biomes

class WorldExplorer:
	def __init__(self, path: str):
		level = amulet.load_level(path)
		if isinstance(level, amulet.api.level.World):
			self._world: amulet.api.level.World = level
		else:
			raise FormatError("path does not open a world level")
#		self._world = attempt_injection(path)

		self.transparent: int = len(Biome.__members__)
		self.error = self.transparent + 1

	def get_chunk_boxes(self, dimension: Dimension = "minecraft:overworld"):
		'''
		Returns a list of rectangles to include all saved chunks
		'''
		return create_rectangles(self._world.all_chunk_coords(dimension))

	def get_3d_chunk_positions(self, dimension: Dimension = "minecraft:overworld"):
		'''
		Returns a list of rectangles where every chunk included has 3d biomes saved
		'''
		all_chunks = self._world.all_chunk_coords(dimension)
		return create_rectangles({(x, z) for x, z in all_chunks if x < 0 if z > -38 if self._world.get_chunk(x, z, dimension).biomes.dimension == 3})

	def get_world_spawn(self):
		root_tag = self._world.level_wrapper.root_tag
		return int(root_tag.get("SpawnX")), int(root_tag.get("SpawnZ"))

	def get_world_seed(self):
		root_tag = self._world.level_wrapper.root_tag
		return int(root_tag.get("RandomSeed"))

	def get_world_name(self):
		root_tag = self._world.level_wrapper.root_tag
		return root_tag.get("LevelName")

	def get_biome_palette(self):
		return self._world.biome_palette

	def _index_biome(self, biome: Biome) -> int:
		return self._world.biome_palette.get_add_biome(biome.universal_id)

	def get_chunk_biomes(self, cx: int, cz: int, dimension: Dimension = "minecraft:overworld", include_underground: bool = False) -> Tuple[NDArray[np.uint32], Union[bool,ndarray]]:
		try:
			chunk = self._world.get_chunk(cx, cz, dimension)
		except ChunkDoesNotExist:
			print("Chunk does not exist")
		except ChunkLoadError:
			print("Chunk load error")
		else:
			biomeArrDim = chunk.biomes.dimension
#			if biomeArrDim == 2:
#				biomes: ndarray = chunk.biomes._2d
#			elif biomeArrDim == 3:
#				biomes = chunk.biomes._3d

#			return biomes, chunk.biome_palette
			if biomeArrDim == 2:
				# Gets the decoded 2d biomes from the amulet library
				return chunk.biomes._2d, False
			elif biomeArrDim == 3:
				if include_underground:
					return self._get_biome_layers(cx, cz, dimension)
				else:
					return self._get_top_biomes_2d(self._get_3d_biomes(cx, cz, dimension)), True
				
			else: # biomeArrDim == 0
				return full((16, 16), self.error, dtype=ubyte), False

	def _get_biome_layers(self, cx:int, cz: int, dimension: Dimension, max_y: Optional[int] = None):
		full_chunk = self._get_3d_biomes(cx, cz, dimension)
		surface_biomes = self._get_top_biomes_2d(full_chunk)
		layers: NDArray = np.empty(surface_biomes.shape, dtype=object)
		for coords, biome in np.ndenumerate(surface_biomes):
			layers[coords] = merged_deque((biome,))

		max_key = max(full_chunk.keys())
		if max_y == None:
			max_y = max_key
		elif max_y // 16 in full_chunk:
			index = max_y // 16
			subchunk = full_chunk[index]
			if isinstance(subchunk, int):
				max_y = index
			else:
				# y_slice should return the appropriate block position and everything below that in the subchunk
				y_slice = slice(max_y % 16)
				columns, inverse = np.unique(subchunk.swapaxes(2,1).reshape((256,16))[:,y_slice,:], axis=0, return_inverse=True)
				deq_cols = np.array([merged_deque((self._index_biome(Biome.parse(y)) for y in col)) for col in columns], dtype=object)
				for coords, col_index in np.ndenumerate(inverse.reshape((16,16))):
					layers[coords].extend(deq_cols[col_index])
				max_y = index - 1
		elif max_y > max_key:
			max_y = max_key
		else:
			return surface_biomes, layers

		for i in range(max_y, min(full_chunk.keys()) - 1, -1):
			# subchunk is entirely one biome
			if isinstance(full_chunk[i], int):
				biome: int = self._index_biome(Biome.parse(full_chunk[i]))
				for deq in layers.flat:
					if deq[-1] != biome:
						deq.append(biome)
			else:
				#unique_biomes: ndarray = np.unique(full_chunk[i])
				#has_cave_biomes = False
				#for biomeId in unique_biomes:
				#	if Biome.parse(biomeId) in cave_biomes:
				#		has_cave_biomes = True
				#		break
				#if has_cave_biomes:
				columns, inverse = np.unique(full_chunk[i].swapaxes(2,1).reshape((256, 16)), axis=0, return_inverse=True)
				deq_cols = np.array([merged_deque((self._index_biome(Biome.parse(y)) for y in col)) for col in columns], dtype=object)
				for coords, col_index in np.ndenumerate(inverse.reshape((16,16))):
					layers[coords].extend(deq_cols[col_index])
		return surface_biomes, layers

	def _get_3d_biomes(self, cx: int, cz: int, dimension: Dimension):
		'''Fetches the specified chunk's raw data and returns a decoded dictionary where values are Bedrock's biome ids'''
		raw_data = self._get_raw_chunk_data(cx, cz, dimension)
		return self._decode_raw_3d_biomes(raw_data[b'+'], -4 if dimension == "minecraft:overworld" else 0)

	def _get_raw_chunk_data(self, cx: int, cz: int, dimension: Dimension) -> Dict[bytes, bytes]:
		return self._world.level_wrapper._get_raw_chunk_data(cx, cz, dimension)

	@staticmethod
	def _decode_packed_array(data: bytes) -> Tuple[bytes, int, Optional[ndarray]]:
		'''Takes a byte sequence and attempts to decode a 16x16x16 ndarray.'''
		bits_per_value, data = struct.unpack("b", data[0:1])[0] >> 1, data[1:]
		if bits_per_value > 0:
			values_per_word = 32 // bits_per_value
			word_count = -(-4096 // values_per_word)
			
			arr = np.packbits(
				np.pad(
					np.unpackbits(
						np.frombuffer(
							bytes(reversed(data[: 4 * word_count])), dtype=np.uint8
						)
					)
					.reshape(-1, 32)[:, -values_per_word * bits_per_value : ]
					.reshape(-1, bits_per_value)[-4096:, :],
					[(0, 0), (16 - bits_per_value, 0)],
					"constant",
				)
			).view(dtype=">i2")[::-1]
			arr = arr.reshape((16, 16, 16)).swapaxes(1, 2)
			data = data[4 * word_count :]
		else:
			arr = None
		return data, bits_per_value, arr

	@staticmethod
	def _encode_packed_array(arr: ndarray, min_bit_size=1) -> bytes:
		bits_per_value = max(int(np.amax(arr)).bit_length(), min_bit_size)
		if bits_per_value == 7:
			bits_per_value = 8
		elif 9 <= bits_per_value <= 15:
			bits_per_value = 16
		header = bytes([(bits_per_value << 1) + 1])

		values_per_word = 32 // bits_per_value
		word_count = -(-4096 // values_per_word)

		arr = arr.swapaxes(1,2).ravel()
		
		packed_arr = bytes(
			reversed(
				np.packbits(
					np.pad(
						np.pad(
							np.unpackbits(np.ascontiguousarray(arr[::-1], dtype=">i").view(dtype='uint8')).reshape(4096, -1)[:, -bits_per_value:],
							[(word_count * values_per_word - 4096, 0), (0, 0)],
							'constant'
						).reshape(-1, values_per_word * bits_per_value),
						[(0, 0), (32 - values_per_word * bits_per_value, 0)],
						'constant'
					)
				).view(dtype='>i4').tobytes()
			)
		)
		return header + packed_arr

	@staticmethod
	def _decode_raw_3d_biomes(data: bytes, floor_cy: int):
		'''Returns a dictionary where keys are subchunk y-positions and values are either:
		a 16x16x16 ndarray of ints, or a single int that represents Bedrock's numerical biome ids'''
		biomes: Dict[int, Union[NDArray[np.uint8],int]] = {}
		cy = floor_cy
		data = data[512:] # dispose of heightmap data
		while data:
			data, bits_per_value, arr = WorldExplorer._decode_packed_array(data)
			if bits_per_value == 0:
				value, data = struct.unpack(f"<I", data[:4])[0], data[4:]
				biomes[cy] = value
			elif bits_per_value > 0:
				palette_len, data = struct.unpack("<I", data[:4])[0], data[4:]
				default_typed = np.frombuffer(data, "<i4", palette_len)[arr]
				biomes[cy] = default_typed.astype(
					np.uint8
				)
				data = data[4 * palette_len :]
			cy += 1
		return biomes

	@staticmethod
	def _encode_height_3d_biomes(height: bytes, biomes: Dict[int, Union[NDArray[np.uint8], int]], floor_cy: int = -4, ceil_cy: int = 8):
		d2d = [height]

		highest = next((cy for cy in range(ceil_cy, floor_cy - 1, -1) if cy in biomes), None)
		if highest is None:
			highest = floor_cy + 24
			print('Warning! highest is None in _encode_height_3d_biomes()')
		else:
			for cy in range(highest - 1, floor_cy - 1, -1):
				if cy not in biomes:
					biomes[cy] = np.repeat(biomes[cy + 1][:, :1, :], 16, 1) if isinstance(biomes[cy + 1], ndarray) else biomes[cy + 1]

		for cy in range(floor_cy, floor_cy + 24):
			if cy in biomes:
				arr = biomes[cy]
				palette, arr_uniq = np.unique(arr, return_inverse=True)
				if len(palette) == 1:
					d2d.append(b'\x01')
				else:
					d2d.append(
						WorldExplorer._encode_packed_array(arr_uniq.reshape(arr.shape))
					)
					d2d.append(struct.pack('<I', len(palette)))
				d2d.append(palette.astype('<i4').tobytes())
			else:
				d2d.append(b'\xFF')

		return b''.join(d2d)

	def _get_top_biomes_2d(self, biomes3d: Dict[int, Union[NDArray[np.uint32],int]]):
		'''Takes a dictionary of a chunk's 3D biomes and returns a 16x16 ndarray of the highest saved position''' 
		top_section = biomes3d[max(biomes3d.keys())]
		top_section = biomes3d[-1] # Testing override
		if isinstance(top_section, int):
			biomes2d = np.full((16, 16), self._index_biome(Biome.parse(top_section)), dtype=np.uint32)
		else:
			biomes2d = np.empty((16,16), dtype=np.uint32)
			biomes2d[:, :] = np.reshape([self._index_biome(Biome.parse(i)) for i in top_section[:,15,:].ravel()], biomes2d.shape)
		return biomes2d
		
	def get_chunk_rect_biomes(self, cx: int, cz: int, dx: int, dz: int, dimension: Dimension = "minecraft:overworld", include_underground: bool = False):
		
		rect_layers: Union[Set[Tuple[int,int]],Dict[Tuple[int,int],ndarray]] = {} if include_underground else set()

		all_xs = []
		for x in range(dx):
			all_zs = []
			for z in range(dz):
				X = x + cx; Z = z + cz
				try:
					chunk = self._world.get_chunk(X, Z, dimension)
				except ChunkDoesNotExist as e:
					raise Exception("Chunk does not exist at (%d, %d)" % (X, Z)) from e
				except ChunkLoadError as e:
					raise Exception("Chunk load error at (%d, %d)" % (X, Z)) from e

				biomeArrDim = chunk.biomes.dimension
				if biomeArrDim == 2:
					biomes2d: ndarray = chunk.biomes._2d
				elif biomeArrDim == 3:
					if include_underground:
						#biomes2d, layers = self._get_biome_layers(X, Z, dimension)
						layers = self._get_3d_biomes(X, Z, dimension); biomes2d = self._get_top_biomes_2d(layers)
						rect_layers[(X, Z)] = layers
					else:
						biomes2d = self._get_top_biomes_2d(self._get_3d_biomes(X, Z, dimension))
						rect_layers.add((X, Z))
				else: # biomeArrDim == 0
					biomes2d = full((16, 16), self.error, dtype=ubyte)
				all_zs.append(biomes2d)

			if len(all_zs) == 1:
				all_xs.append(all_zs[0])
			else:
				all_xs.append(concatenate(all_zs, axis=1, dtype=ubyte, casting='unsafe'))
		
		if len(all_xs) == 1:
			return all_xs[0], rect_layers
		else:
			return concatenate(all_xs, axis=0, dtype=ubyte, casting='unsafe'), rect_layers

#		return layers[0]

	def get_chunk_biomes_status(self, cx: int, cz: int, dimension: Dimension = 'minecraft:overworld') -> ChunkBiomeStatus:
		if not self._world.has_chunk(cx, cz, dimension):
			return 'DOES_NOT_EXIST'

		raw_data = self._get_raw_chunk_data(cx, cz, dimension)
		if b'+' not in raw_data:
			# Deepslate not present at chunk not yet upgraded
			return 'NO_DEEPSLATE_LAYER'
		saved_biomes = self._decode_raw_3d_biomes(raw_data[b'+'],-4 if dimension == 'minecraft:overworld' else 0)
		for cy in range(-4, 0):
			if isinstance(saved_biomes[cy], int):
				if saved_biomes[cy] in cave_biome_ids:
					return 'HAS_CAVE_BIOME'
			elif np.any(np.isin(cave_biome_ids, saved_biomes[cy])):
				return 'HAS_CAVE_BIOME'
		return 'HAS_NO_CAVE_BIOMES'

	def fix_deepslate_biomes(self, generated_caves: 'WorldExplorer', selection_rect):
		DIMENSION = "minecraft:overworld"
		decoding_errors = 0
		encoding_errors = 0
		fixed_chunks = []
		good_chunks = []
		old_chunks = []
		bad_chunks = []

		successful_reencodings = 0
		assertion_errors = 0

		for cx in range(selection_rect[0], selection_rect[2] + 1):
			for cz in range(selection_rect[1], selection_rect[3] + 1):
				if cx == 16 and cz == -7:
					pass

				if not self._world.has_chunk(cx, cz, DIMENSION):
					continue
				if not generated_caves._world.has_chunk(cx, cz, DIMENSION):
					#print('Generated cave biomes not saved at chunk {}, {}'.format(cx, cz))
					continue
				my_raw_data = self._get_raw_chunk_data(cx, cz, DIMENSION)
				if b'+' not in my_raw_data:
					#print('Deepslate not present at chunk not yet upgraded {}, {}'.format(cx, cz))
					old_chunks.append((cx, cz))
					continue
				try:
					heightmap, my_biomes = my_raw_data[b'+'][:512], self._decode_raw_3d_biomes(my_raw_data[b'+'], -4)
					generated_biomes = generated_caves._get_3d_biomes(cx, cz, DIMENSION)
				except Exception as e:
					print('Error decoding biome data at chunk {}, {}\n\t{}'.format(cx, cz, e))
					decoding_errors += 1
					bad_chunks.append((cx, cz))
					continue
				made_changes = False
				for cy in range(-4, 0):
					cave_subchunk = generated_biomes[cy]
					if isinstance(cave_subchunk, int):
						if cave_subchunk in cave_biome_ids:
							my_biomes[cy] = cave_subchunk
							made_changes = True
					else:
						mask = ((186 < cave_subchunk) & (cave_subchunk < 189)) | (cave_subchunk == 190)
						if mask.any():
							my_subchunk = my_biomes[cy]
							if isinstance(my_subchunk, int):
								my_biomes[cy] = np.where(mask, cave_subchunk, my_subchunk)
							else:
								np.putmask(my_subchunk, mask, cave_subchunk)
							made_changes = True
				if made_changes:
					try:
						my_raw_data[b'+'] = self._encode_height_3d_biomes(heightmap, my_biomes)
					except Exception as e:
						print('Error encoding changed biomes at chunk {}, {}\n\t{}'.format(cx, cz, e))
						encoding_errors += 1
						bad_chunks.append((cx, cz))
					else:
						self._world.level_wrapper.put_raw_chunk_data(cx, cz, my_raw_data, DIMENSION)
						fixed_chunks.append((cx, cz))
				else:
					try:
						control_encoding = self._encode_height_3d_biomes(heightmap, my_biomes)
						if control_encoding != my_raw_data[b'+']:
							try:
								assert_decode_encode_3d_biomes(my_raw_data[b'+'][512:])
								successful_reencodings += 1
							except AssertionError as ae:
								assertion_errors += 1
								print('encoding an unmodified biome array does not match the original value')
								print('AsssertionError:\t', ae)
								if len(control_encoding) == len(my_raw_data[b'+']):
									print('\t...there is however no difference in length of {} bytes'.format(len(control_encoding)))
								else:
									print('\tLengths: control={} original={}'.format(len(control_encoding), len(my_raw_data[b'+'])))
								#print('\tHighest adjustment: {} bytes'.format(len(b'\xFF') * (25 - len(my_biomes.keys()))))
								bad_chunks.append((cx, cz))
						else:
							successful_reencodings += 1
					except Exception:
						pass
					good_chunks.append((cx, cz))

		print("Operation Totals:\nDecoding Errors: {}\nEncoding Errors: {}\nFixed Chunks: {}\n".format(decoding_errors, encoding_errors, len(fixed_chunks)))
		print('Successfully Reencoded {} chunk(s)\nAssertion Errors: {}'.format(successful_reencodings, assertion_errors))
		self._world.save()

		return fixed_chunks, good_chunks, old_chunks, bad_chunks

	def destroy(self):
		self._world.close()


def assert_decode_encode_3d_biomes(biome_bytes: bytes):
	'''
	The first 512 bytes of a chunk's [b'+'] value represent the heightmap, which should NOT be passed for assertion
	'''
	_decoding_data = biome_bytes
	tmp_biomes: List[Union[int,NDArray[np.uint8],None]] = []
	encoding_data: List[bytes] = []
	while _decoding_data:
		decoding_data, bits_per_value, arr = WorldExplorer._decode_packed_array(_decoding_data)
		if bits_per_value == 0:
			value: int = struct.unpack(f'<I', decoding_data[:4])[0]
			tmp_biomes.append(value)
			assert (_decoding_data[0] ^ 1) in {0, 1}, "section header should be b'\x00' or b'\x01'"
			assert value.to_bytes(4, 'little') == decoding_data[:4], "value for a single biome subchunk should match exactly"
			encoding_data.extend([_decoding_data[0:1], value.to_bytes(4, 'little')])
			_decoding_data = decoding_data[4:]
		elif bits_per_value > 0:
			_word_count = -(-4096 // (32 // (_decoding_data[0] >> 1)))
			packed_arr = _decoding_data[:(4 * _word_count) + 1]

			palette_len: int = struct.unpack(f'<I', decoding_data[:4])[0]
			assert decoding_data[:4] == struct.pack('<I', palette_len), 'palette_len should match exactly when packed'

			
			
			_palette_arr = np.frombuffer(decoding_data[4:], '<i4', palette_len)
			assert decoding_data[4:(4 * palette_len) + 4] == _palette_arr.astype('<i4').tobytes(), 'using the same palette should encode to the same bytes'
			default_typed = _palette_arr[arr]
			tmp_biomes.append(default_typed.astype(np.uint8))

			new_palette, new_inverse = np.unique(default_typed, return_inverse=True)
			if len(new_palette) == 1:
				'''Extra biomes were saved to the palette which should not happen naturally'''
				tmp_biomes[-1] = new_palette[0] # A single biome subchunk can be compressed
			elif len(new_palette) == palette_len:
				_reencoded_arr = WorldExplorer._encode_packed_array(arr)
				assert (_reencoded_arr[0] ^ packed_arr[0]) in {0, 1}, 'section headers must match exactly, except for the least significant bit'
				assert _reencoded_arr[1:] == packed_arr[1:], 're-packing an array of indexes should match exactly'

				_encoded_arr = WorldExplorer._encode_packed_array(new_inverse.reshape(default_typed.shape))
				assert len(_encoded_arr) == len(packed_arr), 'encoded packed arrays should occupy the same space for the same palette length'
				if new_palette == _palette_arr:
					assert _encoded_arr[1:] == packed_arr[1:], 'encoding an array using the same palette should match exactly'
			
			encoding_data.extend([
				packed_arr, # The original header and following packed array
				struct.pack('<I', palette_len),
				_palette_arr.astype('<i4').tobytes()
			])
			_decoding_data = decoding_data[(4 * palette_len) + 4:]
		else:
			assert _decoding_data[0] == 255, "unsaved sections should be represented as b'\xff'"
			tmp_biomes.append(None)
			encoding_data.append(b'\xff')
			_decoding_data = decoding_data

	assert len(tmp_biomes) == 24, '3d biomes should contain exactly 24 sections, but does not need to save every one. Decoded: {}'.format(len(tmp_biomes))
	assert b''.join(encoding_data) == biome_bytes, 'Assertive safe encoding should match exactly the data being decoded'


class merged_deque(deque):
	def __init__(self, iterable: Iterable = None, maxlen: Union[int,None] = None):
		super().__init__(self._generator_init(iterable), maxlen)
		return

	def appendleft(self, __x):
		if len(self) == 0 or self[0] != __x:
			super().appendleft(__x)

	def append(self, __x):
		if len(self) == 0 or self[-1] != __x:
			super().append(__x)

	def extend(self, __iterable: Iterable):
		if len(self) == 0:
			super().extend(self._generator_init(__iterable))
		else:
			super().extend(self._generator(__iterable,self[-1]))

	def extendleft(self, __iterable: Iterable):
		if len(self) == 0:
			super().extendleft(self._generator_init(__iterable))
		else:
			super().extendleft(self._generator(__iterable,self[0]))

	def reversed(self):
		'''Returns itself after reversing order'''
		self.reverse()
		return self

	@staticmethod
	def _generator(__iterable: Iterable, prior_value):
		for value in __iterable:
			if value != prior_value:
				yield value
				prior_value = value

	@staticmethod
	def _generator_init(__iterable: Iterable):
		iterator = iter(__iterable)
		prior_value = next(iterator)
		yield prior_value
		try:
			while True:
				value = next(iterator)
				if value != prior_value:
					yield value
					prior_value = value
		except StopIteration:
			pass

def get_chunk_boxes(path: str, dimension: Dimension ="minecraft:overworld"):
	return WorldExplorer(path).get_chunk_boxes(dimension)

def create_rectangles(points: Union[Set[Tuple[int, int]],Iterable[Tuple[int,int]]]):
	if not isinstance(points, set):
		points = set(points)
	sorted_points = list(points)

	sorted_points.sort(key = lambda c: c[0])
	min_x = sorted_points[0][0]; max_x = sorted_points[-1][0]
	sorted_points.sort(key = lambda c: c[1])
	min_y = sorted_points[0][1]; max_y = sorted_points[-1][1]

	rectangles: List[Tuple[int,...]] = []
	while sorted_points:
		start_x, start_y = sorted_points.pop(0)
		points.remove((start_x, start_y))
		end_x, end_y = start_x, start_y
		while sorted_points and end_y == sorted_points[0][1] and end_x + 1 == sorted_points[0][0]:
			end_x = sorted_points.pop(0)[0]
			points.remove((end_x, start_y))
		continue_while = True
		while continue_while and (start_x, end_y + 1) in points:
			for x in range(start_x + 1, end_x + 1):
				if (x, end_y + 1) not in points:
					continue_while = False
					break
			if not continue_while:
				break
			end_y += 1
			for x in range(start_x, end_x + 1):
				points.remove((x, end_y))
				sorted_points.remove((x, end_y))
		if (start_x, start_y) == (end_x, end_y):
			rectangles.append((start_x, start_y))
		else:
			rectangles.append((start_x, start_y, end_x, end_y))
			
	def keyfunction(rect):
		'''Key for comparison by size'''
		if len(rect) == 2:
			return 1
		width = rect[2] - rect[0] + 1
		length = rect[3] - rect[1] + 1
		return width * length

	rectangles.sort(key=keyfunction, reverse=True)

	return rectangles, (min_x, min_y, max_x, max_y)