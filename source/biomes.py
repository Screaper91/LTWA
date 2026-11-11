from enum import Enum, auto
from numpy import integer
from typing import Literal, Optional, Tuple, Union, Dict, List, Type

class Biome(Enum):
	OCEAN = auto()
	PLAINS = auto()
	DESERT = auto()
	MOUNTAINS = auto()
	FOREST = auto()
	TAIGA = auto()
	SWAMP = auto()
	RIVER = auto()
	NETHER_WASTES = auto()
	THE_END = auto()
	FROZEN_OCEAN = auto()
	FROZEN_RIVER = auto()
	SNOWY_TUNDRA = auto()
	SNOWY_MOUNTAINS = auto()
	MUSHROOM_FIELDS = auto()
	MUSHROOM_FIELD_SHORE = auto()
	BEACH = auto()
	DESERT_HILLS = auto()
	WOODED_HILLS = auto()
	TAIGA_HILLS = auto()
	MOUNTAIN_EDGE = auto()
	JUNGLE = auto()
	JUNGLE_HILLS = auto()
	JUNGLE_EDGE = auto()
	DEEP_OCEAN = auto()
	STONE_SHORE = auto()
	SNOWY_BEACH = auto()
	BIRCH_FOREST = auto()
	BIRCH_FOREST_HILLS = auto()
	DARK_FOREST = auto()
	SNOWY_TAIGA = auto()
	SNOWY_TAIGA_HILLS = auto()
	GIANT_TREE_TAIGA = auto()
	GIANT_TREE_TAIGA_HILLS = auto()
	WOODED_MOUNTAINS = auto()
	SAVANNA = auto()
	SAVANNA_PLATEAU = auto()
	BADLANDS = auto()
	WOODED_BADLANDS_PLATEAU = auto()
	BADLANDS_PLATEAU = auto()
	SMALL_END_ISLANDS = auto()
	END_MIDLANDS = auto()
	END_HIGHLANDS = auto()
	END_BARRENS = auto()
	WARM_OCEAN = auto()
	LUKEWARM_OCEAN = auto()
	COLD_OCEAN = auto()
	DEEP_WARM_OCEAN = auto()
	DEEP_LUKEWARM_OCEAN = auto()
	DEEP_COLD_OCEAN = auto()
	DEEP_FROZEN_OCEAN = auto()
	THE_VOID = auto()
	SUNFLOWER_PLAINS = auto()
	DESERT_LAKES = auto()
	GRAVELLY_MOUNTAINS = auto()
	FLOWER_FOREST = auto()
	TAIGA_MOUNTAINS = auto()
	SWAMP_HILLS = auto()
	ICE_SPIKES = auto()
	MODIFIED_JUNGLE = auto()
	MODIFIED_JUNGLE_EDGE = auto()
	TALL_BIRCH_FOREST = auto()
	TALL_BIRCH_HILLS = auto()
	DARK_FOREST_HILLS = auto()
	SNOWY_TAIGA_MOUNTAINS = auto()
	GIANT_SPRUCE_TAIGA = auto()
	GIANT_SPRUCE_TAIGA_HILLS = auto()
	MODIFIED_GRAVELLY_MOUNTAINS = auto()
	SHATTERED_SAVANNA = auto()
	SHATTERED_SAVANNA_PLATEAU = auto()
	ERODED_BADLANDS = auto()
	MODIFIED_WOODED_BADLANDS_PLATEAU = auto()
	MODIFIED_BADLANDS_PLATEAU = auto()
	BAMBOO_JUNGLE = auto()
	BAMBOO_JUNGLE_HILLS = auto()
	SOUL_SAND_VALLEY = auto()
	CRIMSON_FOREST = auto()
	WARPED_FOREST = auto()
	BASALT_DELTAS = auto()
	DRIPSTONE_CAVES = auto()
	LUSH_CAVES = auto()
	MEADOW = auto()
	GROVE = auto()
	SNOWY_SLOPES = auto()
	STONY_PEAKS = auto()
	JAGGED_PEAKS = auto()
	FROZEN_PEAKS = auto()
	DEEP_DARK = auto()
	MANGROVE_SWAMP = auto()
	CHERRY_GROVE = auto()
	PALE_GARDEN = auto()
	SULFUR_CAVES = auto()
	DAPPLED_FOREST = auto()
	ICE_CAVES = auto()

	LEGACY_FROZEN_OCEAN = auto()

	@staticmethod
	def parse(value: Union[str, int], context: Union[Literal['universal'],Literal['bedrock'],Literal['cubiomes'],Type[None]] = None):
		if isinstance(value, str) and ((not context) or context == "universal"):
			return from_universal_name[value]
		elif isinstance(value, (int, integer)):
			if ((not context) or context == "bedrock"):
				return integer_ids_latest[value]
			elif context == "cubiomes":
				return cubiomes_enum[value]

	@property
	def universal_id(self) -> str:
		return to_universal_name[self]
	
	@property
	def amidst_color(self) -> Tuple[int, int, int]:
		return amidstColors[self]

	def __repr__(self):
		return '<%s.%s>' % (self.__class__.__name__, self.name)



amidstColors: Dict[Biome, Tuple[int, int, int]] = {
	Biome.OCEAN: (0, 0, 112),
	Biome.PLAINS: (141, 179, 96),
	Biome.DESERT: (250, 148, 24),
	Biome.MOUNTAINS: (96, 96, 96),
	Biome.FOREST: (5, 102, 33),
	Biome.TAIGA: (11, 106, 95),
	Biome.SWAMP: (7, 249, 178),
	Biome.RIVER: (0, 0, 255),
	Biome.NETHER_WASTES: (87, 37, 38),
	Biome.THE_END: (128, 128, 255),
	Biome.FROZEN_OCEAN: (112, 112, 214),
	Biome.FROZEN_RIVER: (160, 160, 255),
	Biome.SNOWY_TUNDRA: (255, 255, 255),
	Biome.SNOWY_MOUNTAINS: (160, 160, 160),
	Biome.MUSHROOM_FIELDS: (255, 0, 255),
	Biome.MUSHROOM_FIELD_SHORE: (160, 0, 255),
	Biome.BEACH: (250, 222, 85),
	Biome.DESERT_HILLS: (210, 95, 18),
	Biome.WOODED_HILLS: (34, 85, 28),
	Biome.TAIGA_HILLS: (22, 57, 51),
	Biome.MOUNTAIN_EDGE: (114, 120, 154),
	Biome.JUNGLE: (80, 123, 10),
	Biome.JUNGLE_EDGE: (96, 147, 15),
	Biome.JUNGLE_HILLS: (44, 66, 5),
	Biome.DEEP_OCEAN: (0, 0, 48),
	Biome.STONE_SHORE: (162, 162, 132),
	Biome.SNOWY_BEACH: (250, 240, 192),
	Biome.BIRCH_FOREST: (48, 116, 68),
	Biome.BIRCH_FOREST_HILLS: (31, 95, 50),
	Biome.DARK_FOREST: (64, 81, 26),
	Biome.SNOWY_TAIGA: (49, 85, 74),
	Biome.SNOWY_TAIGA_HILLS: (36, 63, 54),
	Biome.GIANT_TREE_TAIGA: (89, 102, 81),
	Biome.GIANT_TREE_TAIGA_HILLS: (69, 79, 62),
	Biome.WOODED_MOUNTAINS: (91, 115, 82),
	Biome.SAVANNA: (189, 178, 95),
	Biome.SAVANNA_PLATEAU: (167, 157, 100),
	Biome.BADLANDS: (217, 69, 21),
	Biome.WOODED_BADLANDS_PLATEAU: (176, 151, 101),
	Biome.BADLANDS_PLATEAU: (202, 140, 101),
	Biome.SMALL_END_ISLANDS: (75, 75, 171),
	Biome.END_MIDLANDS: (201, 201, 89),
	Biome.END_HIGHLANDS: (181, 181, 54),
	Biome.END_BARRENS: (112, 112, 204),
	Biome.WARM_OCEAN: (0, 0, 172),
	Biome.LUKEWARM_OCEAN: (0, 0, 144),
	Biome.COLD_OCEAN: (32, 32, 112),
	Biome.DEEP_WARM_OCEAN: (0, 0, 80),
	Biome.DEEP_LUKEWARM_OCEAN: (0, 0, 64),
	Biome.DEEP_COLD_OCEAN: (32, 32, 56),
	Biome.DEEP_FROZEN_OCEAN: (64, 64, 144),
	Biome.THE_VOID: (0, 0, 0),
	Biome.ICE_SPIKES: (180, 220, 220),
	Biome.BAMBOO_JUNGLE: (132, 149, 0),
	Biome.BAMBOO_JUNGLE_HILLS: (92, 108, 4),
	Biome.SOUL_SAND_VALLEY: (77, 58, 46),
	Biome.CRIMSON_FOREST: (152, 26, 17),
	Biome.WARPED_FOREST: (73, 144, 123),
	Biome.BASALT_DELTAS: (100, 95, 99),
	Biome.DRIPSTONE_CAVES: (78, 48, 18),
	Biome.LUSH_CAVES: (40, 60, 0),
	Biome.MEADOW: (96, 164, 69),
	Biome.GROVE: (71, 114, 108),
	Biome.SNOWY_SLOPES: (196, 196, 196),
	Biome.STONY_PEAKS: (123, 143, 116),
	Biome.JAGGED_PEAKS: (220, 220, 200),
	Biome.FROZEN_PEAKS: (176, 179, 206),
	Biome.DEEP_DARK: (3, 31, 41),
	Biome.MANGROVE_SWAMP: (44, 204, 142),
	Biome.CHERRY_GROVE: (255, 145, 200)
} # Goto: cubiomes/util.c

amidstColors[Biome.LEGACY_FROZEN_OCEAN] = amidstColors[Biome.FROZEN_OCEAN]


def mutate(source: Biome, mutant: Biome):
	color = amidstColors[source]
	amidstColors[mutant] = (min(color[0] + 40, 255), min(color[1] + 40, 255), min(color[2] + 40, 255))


for source, mutant in [
	(Biome.PLAINS, Biome.SUNFLOWER_PLAINS), (Biome.DESERT, Biome.DESERT_LAKES), (Biome.MOUNTAINS, Biome.GRAVELLY_MOUNTAINS), (Biome.FOREST, Biome.FLOWER_FOREST), (Biome.TAIGA, Biome.TAIGA_MOUNTAINS), (Biome.SWAMP, Biome.SWAMP_HILLS), (Biome.JUNGLE, Biome.MODIFIED_JUNGLE), (Biome.JUNGLE_EDGE, Biome.MODIFIED_JUNGLE_EDGE), (Biome.BIRCH_FOREST, Biome.TALL_BIRCH_FOREST), (Biome.BIRCH_FOREST_HILLS, Biome.TALL_BIRCH_HILLS),
	(Biome.DARK_FOREST, Biome.DARK_FOREST_HILLS), (Biome.SNOWY_TAIGA, Biome.SNOWY_TAIGA_MOUNTAINS), (Biome.GIANT_TREE_TAIGA, Biome.GIANT_SPRUCE_TAIGA), (Biome.GIANT_TREE_TAIGA_HILLS, Biome.GIANT_SPRUCE_TAIGA_HILLS), (Biome.WOODED_MOUNTAINS, Biome.MODIFIED_GRAVELLY_MOUNTAINS), (Biome.SAVANNA, Biome.SHATTERED_SAVANNA), (Biome.SAVANNA_PLATEAU, Biome.SHATTERED_SAVANNA_PLATEAU), (Biome.BADLANDS, Biome.ERODED_BADLANDS),
    (Biome.WOODED_BADLANDS_PLATEAU, Biome.MODIFIED_WOODED_BADLANDS_PLATEAU), (Biome.BADLANDS_PLATEAU, Biome.MODIFIED_BADLANDS_PLATEAU)
	]:
	mutate(source, mutant)


to_universal_name: Dict[Biome, str] = {}
from_universal_name: Dict[str, Biome] = {}

for b in Biome:
	name = "universal_minecraft:" + b.name.lower()
	to_universal_name[b] = name
	from_universal_name[name] = b

integer_ids_v1_18 = {
	0: Biome.OCEAN,
	1: Biome.PLAINS,
	2: Biome.DESERT,
	3: Biome.MOUNTAINS,
	4: Biome.FOREST,
	5: Biome.TAIGA,
	6: Biome.SWAMP,
	7: Biome.RIVER,
	8: Biome.NETHER_WASTES,
	9: Biome.THE_END,
	10: Biome.LEGACY_FROZEN_OCEAN,
	11: Biome.FROZEN_RIVER,
	12: Biome.SNOWY_TUNDRA,
	13: Biome.SNOWY_MOUNTAINS,
	14: Biome.MUSHROOM_FIELDS,
	15: Biome.MUSHROOM_FIELD_SHORE,
	16: Biome.BEACH,
	17: Biome.DESERT_HILLS,
	18: Biome.WOODED_HILLS,
	19: Biome.TAIGA_HILLS,
	20: Biome.MOUNTAIN_EDGE,
	21: Biome.JUNGLE,
	22: Biome.JUNGLE_HILLS,
	23: Biome.JUNGLE_EDGE,
	24: Biome.DEEP_OCEAN,
	25: Biome.STONE_SHORE,
	26: Biome.SNOWY_BEACH,
	27: Biome.BIRCH_FOREST,
	28: Biome.BIRCH_FOREST_HILLS,
	29: Biome.DARK_FOREST,
	30: Biome.SNOWY_TAIGA,
	31: Biome.SNOWY_TAIGA_HILLS,
	32: Biome.GIANT_TREE_TAIGA,
	33: Biome.GIANT_TREE_TAIGA_HILLS,
	34: Biome.WOODED_MOUNTAINS,
	35: Biome.SAVANNA,
	36: Biome.SAVANNA_PLATEAU,
	37: Biome.BADLANDS,
	38: Biome.WOODED_BADLANDS_PLATEAU,
	39: Biome.BADLANDS_PLATEAU,
	40: Biome.WARM_OCEAN,
	41: Biome.DEEP_WARM_OCEAN,
	42: Biome.LUKEWARM_OCEAN,
	43: Biome.DEEP_LUKEWARM_OCEAN,
	44: Biome.COLD_OCEAN,
	45: Biome.DEEP_COLD_OCEAN,
	46: Biome.FROZEN_OCEAN,
	47: Biome.DEEP_FROZEN_OCEAN,
	48: Biome.BAMBOO_JUNGLE,
	49: Biome.BAMBOO_JUNGLE_HILLS,
	129: Biome.SUNFLOWER_PLAINS,
	130: Biome.DESERT_LAKES,
	131: Biome.GRAVELLY_MOUNTAINS,
	132: Biome.FLOWER_FOREST,
	133: Biome.TAIGA_MOUNTAINS,
	134: Biome.SWAMP_HILLS,
	140: Biome.ICE_SPIKES,
	149: Biome.MODIFIED_JUNGLE,
	151: Biome.MODIFIED_JUNGLE_EDGE,
	155: Biome.TALL_BIRCH_FOREST,
	156: Biome.TALL_BIRCH_HILLS,
	157: Biome.DARK_FOREST_HILLS,
	158: Biome.SNOWY_TAIGA_MOUNTAINS,
	160: Biome.GIANT_SPRUCE_TAIGA,
	161: Biome.GIANT_SPRUCE_TAIGA_HILLS,
	162: Biome.MODIFIED_GRAVELLY_MOUNTAINS,
	163: Biome.SHATTERED_SAVANNA,
	164: Biome.SHATTERED_SAVANNA_PLATEAU,
	165: Biome.ERODED_BADLANDS,
	166: Biome.MODIFIED_WOODED_BADLANDS_PLATEAU,
	167: Biome.MODIFIED_BADLANDS_PLATEAU,
	178: Biome.SOUL_SAND_VALLEY,
	179: Biome.CRIMSON_FOREST,
	180: Biome.WARPED_FOREST,
	181: Biome.BASALT_DELTAS,
	182: Biome.JAGGED_PEAKS,
	183: Biome.FROZEN_PEAKS,
	184: Biome.SNOWY_SLOPES,
	185: Biome.GROVE,
	186: Biome.MEADOW,
	187: Biome.LUSH_CAVES,
	188: Biome.DRIPSTONE_CAVES,
	189: Biome.STONY_PEAKS
}

integer_ids_latest = integer_ids_v1_18.copy()
# Goto: PyMCTranslate/PyMCTranslate/json/versions/bedrock_1_##_#/__biome_data__.json
integer_ids_latest[190] = Biome.DEEP_DARK
integer_ids_latest[191] = Biome.MANGROVE_SWAMP
integer_ids_latest[192] = Biome.CHERRY_GROVE
integer_ids_latest[193] = Biome.PALE_GARDEN
integer_ids_latest[194] = Biome.SULFUR_CAVES
integer_ids_latest[195] = Biome.DAPPLED_FOREST
integer_ids_latest[196] = Biome.ICE_CAVES

cubiomes_enum = {
	0: Biome.OCEAN,
	1: Biome.PLAINS,
	2: Biome.DESERT,
	3: Biome.MOUNTAINS,
	4: Biome.FOREST,
	5: Biome.TAIGA,
	6: Biome.SWAMP,
	7: Biome.RIVER,
	8: Biome.NETHER_WASTES,
	9: Biome.THE_END,
	10: Biome.FROZEN_OCEAN,
	11: Biome.FROZEN_RIVER,
	12: Biome.SNOWY_TUNDRA,
	13: Biome.SNOWY_MOUNTAINS,
	14: Biome.MUSHROOM_FIELDS,
	15: Biome.MUSHROOM_FIELD_SHORE,
	16: Biome.BEACH,
	17: Biome.DESERT_HILLS,
	18: Biome.WOODED_HILLS,
	19: Biome.TAIGA_HILLS,
	20: Biome.MOUNTAIN_EDGE,
	21: Biome.JUNGLE,
	22: Biome.JUNGLE_HILLS,
	23: Biome.JUNGLE_EDGE,
	24: Biome.DEEP_OCEAN,
	25: Biome.STONE_SHORE,
	26: Biome.SNOWY_BEACH,
	27: Biome.BIRCH_FOREST,
	28: Biome.BIRCH_FOREST_HILLS,
	29: Biome.DARK_FOREST,
	30: Biome.SNOWY_TAIGA,
	31: Biome.SNOWY_TAIGA_HILLS,
	32: Biome.GIANT_TREE_TAIGA,
	33: Biome.GIANT_TREE_TAIGA_HILLS,
	34: Biome.WOODED_MOUNTAINS,
	35: Biome.SAVANNA,
	36: Biome.SAVANNA_PLATEAU,
	37: Biome.BADLANDS,
	38: Biome.WOODED_BADLANDS_PLATEAU,
	39: Biome.BADLANDS_PLATEAU,
	40: Biome.SMALL_END_ISLANDS,
	41: Biome.END_MIDLANDS,
	42: Biome.END_HIGHLANDS,
	43: Biome.END_BARRENS,
	44: Biome.WARM_OCEAN,
	45: Biome.DEEP_WARM_OCEAN,
	46: Biome.LUKEWARM_OCEAN,
	47: Biome.DEEP_LUKEWARM_OCEAN,
	48: Biome.COLD_OCEAN,
	49: Biome.DEEP_COLD_OCEAN,
	50: Biome.DEEP_FROZEN_OCEAN,
	127: Biome.THE_VOID,
	129: Biome.SUNFLOWER_PLAINS,
	130: Biome.DESERT_LAKES,
	131: Biome.GRAVELLY_MOUNTAINS,
	132: Biome.FLOWER_FOREST,
	133: Biome.TAIGA_MOUNTAINS,
	134: Biome.SWAMP_HILLS,
	140: Biome.ICE_SPIKES,
	149: Biome.MODIFIED_JUNGLE,
	151: Biome.MODIFIED_JUNGLE_EDGE,
	155: Biome.TALL_BIRCH_FOREST,
	156: Biome.TALL_BIRCH_HILLS,
	157: Biome.DARK_FOREST_HILLS,
	158: Biome.SNOWY_TAIGA_MOUNTAINS,
	160: Biome.GIANT_SPRUCE_TAIGA,
	161: Biome.GIANT_SPRUCE_TAIGA_HILLS,
	162: Biome.MODIFIED_GRAVELLY_MOUNTAINS,
	163: Biome.SHATTERED_SAVANNA,
	164: Biome.SHATTERED_SAVANNA_PLATEAU,
	165: Biome.ERODED_BADLANDS,
	166: Biome.MODIFIED_WOODED_BADLANDS_PLATEAU,
	167: Biome.MODIFIED_BADLANDS_PLATEAU,
	168: Biome.BAMBOO_JUNGLE,
	169: Biome.BAMBOO_JUNGLE_HILLS,
	170: Biome.SOUL_SAND_VALLEY,
	171: Biome.CRIMSON_FOREST,
	172: Biome.WARPED_FOREST,
	173: Biome.BASALT_DELTAS,
	174: Biome.DRIPSTONE_CAVES,
	175: Biome.LUSH_CAVES,
	177: Biome.MEADOW,
	178: Biome.GROVE,
	179: Biome.SNOWY_SLOPES,
	180: Biome.JAGGED_PEAKS,
	181: Biome.FROZEN_PEAKS,
	182: Biome.STONY_PEAKS,
	183: Biome.DEEP_DARK,
	184: Biome.MANGROVE_SWAMP,
	185: Biome.CHERRY_GROVE
} # Goto: cubiomes/util.c

cubiomes_palette: List[int] = []
for i in range(185):
	if i in cubiomes_enum:
		cubiomes_palette.extend(cubiomes_enum[i].amidst_color)
	else:
		cubiomes_palette.extend((0, 0, 0))