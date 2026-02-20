from pvzemu2.enums import PlantType, PlantReanimName

PEA_OFFSETS_GATLING_PEA = [
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (37.6, 48.7),
    (38.0, 47.0), (38.3, 45.5), (38.6, 43.8), (39.1, 43.5), (39.6, 43.1),
    (40.0, 42.8), (41.1, 43.1), (42.1, 43.5), (43.2, 43.8), (44.6, 44.6),
    (46.0, 45.5), (47.4, 46.3), (46.0, 45.5), (44.6, 44.6), (43.2, 43.8),
    (42.1, 43.5), (41.1, 43.1), (40.0, 42.8), (39.6, 43.1), (39.1, 43.5),
    (38.6, 43.8), (38.3, 45.5), (38.0, 47.0), (37.6, 48.7), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0)
]

PEA_OFFSETS_PEA_SHOOTER = [
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (37.6, 48.7),
    (38.0, 47.0), (38.3, 45.5), (38.6, 43.8), (39.1, 43.5), (39.6, 43.1),
    (40.0, 42.8), (41.1, 43.1), (42.1, 43.5), (43.2, 43.8), (44.6, 44.6),
    (46.0, 45.5), (47.4, 46.3), (46.0, 45.5), (44.6, 44.6), (43.2, 43.8),
    (42.1, 43.5), (41.1, 43.1), (40.0, 42.8), (39.6, 43.1), (39.1, 43.5),
    (38.6, 43.8), (38.3, 45.5), (38.0, 47.0), (37.6, 48.7), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (38.5, 47.0), (39.3, 45.3), (40.1, 43.5), (41.1, 43.0), (42.1, 42.6),
    (43.0, 42.1), (45.1, 41.8), (47.1, 41.5), (49.2, 41.1), (52.0, 42.2),
    (54.8, 43.4), (57.6, 44.5), (55.0, 43.3), (52.4, 42.0), (49.8, 40.8),
    (47.6, 40.0), (45.5, 39.3), (43.4, 38.5), (42.2, 39.0), (41.0, 39.5),
    (39.9, 39.9), (39.2, 42.9), (38.5, 45.8), (37.9, 48.7)
]

PEA_OFFSETS_REPEATER = [
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (37.6, 48.7),
    (38.0, 47.0), (38.3, 45.5), (38.6, 43.8), (39.1, 43.5), (39.6, 43.1),
    (40.0, 42.8), (41.1, 43.1), (42.1, 43.5), (43.2, 43.8), (44.6, 44.6),
    (46.0, 45.5), (47.4, 46.3), (46.0, 45.5), (44.6, 44.6), (43.2, 43.8),
    (42.1, 43.5), (41.1, 43.1), (40.0, 42.8), (39.6, 43.1), (39.1, 43.5),
    (38.6, 43.8), (38.3, 45.5), (38.0, 47.0), (37.6, 48.7), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (38.0, 47.0), (38.3, 45.5), (38.6, 43.8), (39.1, 43.5), (39.6, 43.1),
    (40.0, 42.8), (41.1, 43.1), (42.1, 43.5), (43.2, 43.8), (44.6, 44.6),
    (46.0, 45.5), (47.4, 46.3), (46.0, 45.5), (44.6, 44.6), (43.2, 43.8),
    (42.1, 43.5), (41.1, 43.1), (40.0, 42.8), (39.6, 43.1), (39.1, 43.5),
    (38.6, 43.8), (38.3, 45.5), (38.0, 47.0), (37.6, 48.7)
]

PEA_OFFSETS_SNOW_PEA = [
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (37.6, 48.7),
    (38.0, 47.0), (38.3, 45.5), (38.6, 43.8), (39.1, 43.5), (39.6, 43.1),
    (40.0, 42.8), (41.1, 43.1), (42.1, 43.5), (43.2, 43.8), (44.6, 44.6),
    (46.0, 45.5), (47.4, 46.3), (46.0, 45.5), (44.6, 44.6), (43.2, 43.8),
    (42.1, 43.5), (41.1, 43.1), (40.0, 42.8), (39.6, 43.1), (39.1, 43.5),
    (38.6, 43.8), (38.3, 45.5), (38.0, 47.0), (37.6, 48.7), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (38.0, 47.0), (38.3, 45.5), (38.6, 43.8), (39.1, 43.5), (39.6, 43.1),
    (40.0, 42.8), (41.1, 43.1), (42.1, 43.5), (43.2, 43.8), (44.6, 44.6),
    (46.0, 45.5), (47.4, 46.3), (46.0, 45.5), (44.6, 44.6), (43.2, 43.8),
    (42.1, 43.5), (41.1, 43.1), (40.0, 42.8), (39.6, 43.1), (39.1, 43.5),
    (38.6, 43.8), (38.3, 45.5), (38.0, 47.0), (37.6, 48.7)
]

PEA_OFFSETS_SPLIT_PEA = [
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (37.6, 48.7), (38.0, 47.1), (38.3, 45.5),
    (38.6, 43.8), (39.1, 43.5), (39.6, 43.1), (40.1, 42.8), (41.1, 43.1),
    (42.1, 43.5), (43.2, 43.8), (44.6, 44.6), (46.0, 45.5), (47.4, 46.3),
    (46.0, 45.5), (44.6, 44.6), (43.2, 43.8), (42.1, 43.5), (41.1, 43.1),
    (40.1, 42.8), (39.6, 43.1), (39.1, 43.5), (38.6, 43.8), (38.3, 45.5),
    (38.0, 47.1), (37.6, 48.7), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
    (0.0, 0.0), (0.0, 0.0)
]


def get_plant_reanim_data(plant_type):
    n_frames = 0
    fps = 12.0

    if plant_type == PlantType.BLOVER:
        n_frames = 62
    elif plant_type == PlantType.CABBAGEPULT:
        n_frames = 74
    elif plant_type == PlantType.CACTUS:
        n_frames = 95
    elif plant_type == PlantType.CATTAIL:
        n_frames = 40
    elif plant_type == PlantType.CHERRY_BOMB:
        n_frames = 27
    elif plant_type == PlantType.CHOMPER:
        n_frames = 94
    elif plant_type == PlantType.COB_CANNON:
        n_frames = 100
    elif plant_type == PlantType.COFFEE_BEAN:
        n_frames = 29
    elif plant_type == PlantType.DOOMSHROOM:
        n_frames = 77
    elif plant_type == PlantType.FLOWER_POT:
        n_frames = 39
    elif plant_type == PlantType.FUMESHROOM:
        n_frames = 68
    elif plant_type == PlantType.GARLIC:
        n_frames = 19
    elif plant_type == PlantType.GATLING_PEA:
        n_frames = 93
    elif plant_type == PlantType.GLOOMSHROOM:
        n_frames = 71
    elif plant_type == PlantType.GOLD_MAGNET:
        n_frames = 83
    elif plant_type == PlantType.GRAVE_BUSTER:
        n_frames = 39
    elif plant_type == PlantType.HYPNOSHROOM:
        n_frames = 40
    elif plant_type == PlantType.ICESHROOM:
        n_frames = 38
    elif plant_type == PlantType.IMITATER:
        n_frames = 84
    elif plant_type == PlantType.JALAPENO:
        n_frames = 25
    elif plant_type == PlantType.KERNELPULT:
        n_frames = 77
    elif plant_type == PlantType.LILY_PAD:
        n_frames = 4
    elif plant_type == PlantType.MAGNETSHROOM:
        n_frames = 131
    elif plant_type == PlantType.MARIGOLD:
        n_frames = 30
    elif plant_type == PlantType.MELONPULT:
        n_frames = 74
    elif plant_type == PlantType.PEA_SHOOTER:
        n_frames = 104
    elif plant_type == PlantType.PLANTERN:
        n_frames = 25
    elif plant_type == PlantType.POTATO_MINE:
        n_frames = 37
    elif plant_type == PlantType.PUFFSHROOM:
        n_frames = 51
    elif plant_type == PlantType.PUMPKIN:
        n_frames = 21
    elif plant_type == PlantType.REPEATER:
        n_frames = 104
    elif plant_type == PlantType.SCAREDYSHROOM:
        n_frames = 86
    elif plant_type == PlantType.SEASHROOM:
        n_frames = 93
    elif plant_type == PlantType.SNOW_PEA:
        n_frames = 104
    elif plant_type == PlantType.SPIKEROCK:
        n_frames = 33
    elif plant_type == PlantType.SPIKEWEED:
        n_frames = 35
    elif plant_type == PlantType.SPLIT_PEA:
        n_frames = 132
    elif plant_type == PlantType.SQUASH:
        n_frames = 73
    elif plant_type == PlantType.STARFRUIT:
        n_frames = 39
    elif plant_type == PlantType.SUNFLOWER:
        n_frames = 29
    elif plant_type == PlantType.SUNSHROOM:
        n_frames = 63
    elif plant_type == PlantType.TALLNUT:
        n_frames = 37
    elif plant_type == PlantType.TANGLE_KELP:
        n_frames = 54
    elif plant_type == PlantType.THREEPEATER:
        n_frames = 149
    elif plant_type == PlantType.TORCHWOOD:
        n_frames = 25
    elif plant_type == PlantType.TWIN_SUNFLOWER:
        n_frames = 34
    elif plant_type == PlantType.UMBRELLA_LEAF:
        n_frames = 32
    elif plant_type == PlantType.WALLNUT:
        n_frames = 56
    elif plant_type == PlantType.WINTER_MELON:
        n_frames = 74
    else:
        # Default or error case
        pass

    return n_frames, fps


def get_reanim_frame_data(plant_type, name):
    begin_frame = 0
    n_frames = 0

    if plant_type == PlantType.BLOVER:
        if name == PlantReanimName.anim_loop:
            begin_frame = 52
            n_frames = 10
        elif name == PlantReanimName.anim_idle:
            begin_frame = 0
            n_frames = 33

    elif plant_type == PlantType.CABBAGEPULT:
        if name == PlantReanimName.anim_idle:
            begin_frame = 5
            n_frames = 31
        elif name == PlantReanimName.anim_shooting:
            begin_frame = 36
            n_frames = 38

    elif plant_type == PlantType.CACTUS:
        if name == PlantReanimName.anim_idle:
            begin_frame = 5
            n_frames = 15
        elif name == PlantReanimName.anim_idlehigh:
            begin_frame = 53
            n_frames = 15
        elif name == PlantReanimName.anim_lower:
            begin_frame = 82
            n_frames = 13
        elif name == PlantReanimName.anim_rise:
            begin_frame = 38
            n_frames = 15
        elif name == PlantReanimName.anim_shooting:
            begin_frame = 20
            n_frames = 18
        elif name == PlantReanimName.anim_shootinghigh:
            begin_frame = 68
            n_frames = 14

    elif plant_type == PlantType.CATTAIL:
        if name == PlantReanimName.anim_idle:
            begin_frame = 5
            n_frames = 19
        elif name == PlantReanimName.anim_shooting:
            begin_frame = 24
            n_frames = 16

    elif plant_type == PlantType.CHERRY_BOMB:
        if name == PlantReanimName.anim_idle:
            begin_frame = 14
            n_frames = 13
        elif name == PlantReanimName.anim_explode:
            begin_frame = 0
            n_frames = 14

    elif plant_type == PlantType.CHOMPER:
        if name == PlantReanimName.anim_idle:
            begin_frame = 0
            n_frames = 25
        elif name == PlantReanimName.anim_bite:
            begin_frame = 25
            n_frames = 25
        elif name == PlantReanimName.anim_chew:
            begin_frame = 50
            n_frames = 16
        elif name == PlantReanimName.anim_swallow:
            begin_frame = 66
            n_frames = 28

    elif plant_type == PlantType.COB_CANNON:
        if name == PlantReanimName.anim_charge:
            begin_frame = 24
            n_frames = 15
        elif name == PlantReanimName.anim_unarmed_idle:
            begin_frame = 5
            n_frames = 19
        elif name == PlantReanimName.anim_idle:
            begin_frame = 39
            n_frames = 19
        elif name == PlantReanimName.anim_shooting:
            begin_frame = 58
            n_frames = 42

    elif plant_type == PlantType.COFFEE_BEAN:
        if name == PlantReanimName.anim_crumble:
            begin_frame = 14
            n_frames = 15
        elif name == PlantReanimName.anim_idle:
            begin_frame = 0
            n_frames = 9

    elif plant_type == PlantType.DOOMSHROOM:
        if name == PlantReanimName.anim_idle:
            begin_frame = 0
            n_frames = 20
        elif name == PlantReanimName.anim_sleep:
            begin_frame = 52
            n_frames = 25
        elif name == PlantReanimName.anim_explode:
            begin_frame = 19
            n_frames = 33

    elif plant_type == PlantType.FLOWER_POT:
        if name == PlantReanimName.anim_idle:
            begin_frame = 0
            n_frames = 13

    elif plant_type == PlantType.FUMESHROOM:
        if name == PlantReanimName.anim_idle:
            begin_frame = 4
            n_frames = 17
        elif name == PlantReanimName.anim_sleep:
            begin_frame = 51
            n_frames = 17
        elif name == PlantReanimName.anim_shooting:
            begin_frame = 21
            n_frames = 30

    elif plant_type == PlantType.GARLIC:
        if name == PlantReanimName.anim_idle:
            begin_frame = 4
            n_frames = 15

    elif plant_type == PlantType.GATLING_PEA:
        if name == PlantReanimName.anim_idle:
            begin_frame = 4
            n_frames = 25
        elif name == PlantReanimName.anim_shooting:
            begin_frame = 54
            n_frames = 39

    elif plant_type == PlantType.GLOOMSHROOM:
        if name == PlantReanimName.anim_idle:
            begin_frame = 5
            n_frames = 19
        elif name == PlantReanimName.anim_sleep:
            begin_frame = 24
            n_frames = 19
        elif name == PlantReanimName.anim_shooting:
            begin_frame = 43
            n_frames = 28

    elif plant_type == PlantType.GOLD_MAGNET:
        if name == PlantReanimName.anim_idle:
            begin_frame = 5
            n_frames = 47

    elif plant_type == PlantType.GRAVE_BUSTER:
        if name == PlantReanimName.anim_idle:
            begin_frame = 11
            n_frames = 28
        elif name == PlantReanimName.anim_land:
            begin_frame = 0
            n_frames = 7

    elif plant_type == PlantType.HYPNOSHROOM:
        if name == PlantReanimName.anim_idle:
            begin_frame = 0
            n_frames = 20
        elif name == PlantReanimName.anim_sleep:
            begin_frame = 20
            n_frames = 20

    elif plant_type == PlantType.ICESHROOM:
        if name == PlantReanimName.anim_idle:
            begin_frame = 4
            n_frames = 17
        elif name == PlantReanimName.anim_sleep:
            begin_frame = 21
            n_frames = 17

    elif plant_type == PlantType.IMITATER:
        if name == PlantReanimName.anim_idle:
            begin_frame = 3
            n_frames = 50
        elif name == PlantReanimName.anim_explode:
            begin_frame = 53
            n_frames = 31

    elif plant_type == PlantType.JALAPENO:
        if name == PlantReanimName.anim_idle:
            begin_frame = 5
            n_frames = 7
        elif name == PlantReanimName.anim_explode:
            begin_frame = 12
            n_frames = 13

    elif plant_type == PlantType.KERNELPULT:
        if name == PlantReanimName.anim_idle:
            begin_frame = 5
            n_frames = 19
        elif name == PlantReanimName.anim_shooting:
            begin_frame = 24
            n_frames = 34

    elif plant_type == PlantType.LILY_PAD:
        if name == PlantReanimName.anim_idle:
            begin_frame = 0
            n_frames = 1

    elif plant_type == PlantType.MAGNETSHROOM:
        if name == PlantReanimName.anim_idle:
            begin_frame = 4
            n_frames = 29
        elif name == PlantReanimName.anim_sleep:
            begin_frame = 108
            n_frames = 18
        elif name == PlantReanimName.anim_nonactive_idle2:
            begin_frame = 126
            n_frames = 5
        elif name == PlantReanimName.anim_shooting:
            begin_frame = 71
            n_frames = 26

    elif plant_type == PlantType.MARIGOLD:
        if name == PlantReanimName.anim_idle:
            begin_frame = 5
            n_frames = 25

    elif plant_type == PlantType.MELONPULT:
        if name == PlantReanimName.anim_idle:
            begin_frame = 5
            n_frames = 31
        elif name == PlantReanimName.anim_shooting:
            begin_frame = 36
            n_frames = 38

    elif plant_type == PlantType.PEA_SHOOTER:
        if name == PlantReanimName.anim_idle:
            begin_frame = 4
            n_frames = 25
        elif name == PlantReanimName.anim_shooting:
            begin_frame = 54
            n_frames = 25

    elif plant_type == PlantType.PLANTERN:
        if name == PlantReanimName.anim_idle:
            begin_frame = 5
            n_frames = 20

    elif plant_type == PlantType.POTATO_MINE:
        if name == PlantReanimName.anim_idle:
            begin_frame = 0
            n_frames = 1
        elif name == PlantReanimName.anim_glow:
            begin_frame = 20
            n_frames = 1
        elif name == PlantReanimName.anim_armed:
            begin_frame = 20
            n_frames = 11
        elif name == PlantReanimName.anim_rise:
            begin_frame = 1
            n_frames = 19

    elif plant_type == PlantType.PUFFSHROOM:
        if name == PlantReanimName.anim_idle:
            begin_frame = 4
            n_frames = 17
        elif name == PlantReanimName.anim_sleep:
            begin_frame = 34
            n_frames = 17
        elif name == PlantReanimName.anim_shooting:
            begin_frame = 21
            n_frames = 13

    elif plant_type == PlantType.PUMPKIN:
        if name == PlantReanimName.anim_idle:
            begin_frame = 0
            n_frames = 21

    elif plant_type == PlantType.REPEATER:
        if name == PlantReanimName.anim_idle:
            begin_frame = 4
            n_frames = 25
        elif name == PlantReanimName.anim_shooting:
            begin_frame = 54
            n_frames = 25

    elif plant_type == PlantType.SCAREDYSHROOM:
        if name == PlantReanimName.anim_idle:
            begin_frame = 5
            n_frames = 16
        elif name == PlantReanimName.anim_scared:
            begin_frame = 36
            n_frames = 13
        elif name == PlantReanimName.anim_scaredidle:
            begin_frame = 49
            n_frames = 11
        elif name == PlantReanimName.anim_sleep:
            begin_frame = 70
            n_frames = 16
        elif name == PlantReanimName.anim_grow:
            begin_frame = 60
            n_frames = 10
        elif name == PlantReanimName.anim_shooting:
            begin_frame = 21
            n_frames = 15

    elif plant_type == PlantType.SEASHROOM:
        if name == PlantReanimName.anim_idle:
            begin_frame = 4
            n_frames = 25
        elif name == PlantReanimName.anim_sleep:
            begin_frame = 43
            n_frames = 25
        elif name == PlantReanimName.anim_shooting:
            begin_frame = 29
            n_frames = 14

    elif plant_type == PlantType.SNOW_PEA:
        if name == PlantReanimName.anim_idle:
            begin_frame = 4
            n_frames = 25
        elif name == PlantReanimName.anim_shooting:
            begin_frame = 54
            n_frames = 25

    elif plant_type == PlantType.SPIKEROCK:
        if name == PlantReanimName.anim_attack:
            begin_frame = 18
            n_frames = 15
        elif name == PlantReanimName.anim_idle:
            begin_frame = 3
            n_frames = 15

    elif plant_type == PlantType.SPIKEWEED:
        if name == PlantReanimName.anim_attack:
            begin_frame = 25
            n_frames = 10
        elif name == PlantReanimName.anim_idle:
            begin_frame = 4
            n_frames = 21

    elif plant_type == PlantType.SPLIT_PEA:
        if name == PlantReanimName.anim_idle:
            begin_frame = 7
            n_frames = 25
        elif name == PlantReanimName.anim_splitpea_shooting:
            begin_frame = 57
            n_frames = 13
        elif name == PlantReanimName.anim_shooting:
            begin_frame = 107
            n_frames = 25

    elif plant_type == PlantType.SQUASH:
        if name == PlantReanimName.anim_idle:
            begin_frame = 5
            n_frames = 19
        elif name == PlantReanimName.anim_lookleft:
            begin_frame = 24
            n_frames = 6
        elif name == PlantReanimName.anim_lookright:
            begin_frame = 37
            n_frames = 6
        elif name == PlantReanimName.anim_jumpup:
            begin_frame = 50
            n_frames = 15
        elif name == PlantReanimName.anim_jumpdown:
            begin_frame = 65
            n_frames = 8

    elif plant_type == PlantType.STARFRUIT:
        if name == PlantReanimName.anim_shoot:
            begin_frame = 22
            n_frames = 17
        elif name == PlantReanimName.anim_idle:
            begin_frame = 5
            n_frames = 17

    elif plant_type == PlantType.SUNFLOWER:
        if name == PlantReanimName.anim_idle:
            begin_frame = 4
            n_frames = 25

    elif plant_type == PlantType.SUNSHROOM:
        if name == PlantReanimName.anim_idle:
            begin_frame = 5
            n_frames = 12
        elif name == PlantReanimName.anim_bigidle:
            begin_frame = 39
            n_frames = 12
        elif name == PlantReanimName.anim_sleep:
            begin_frame = 17
            n_frames = 10
        elif name == PlantReanimName.anim_grow:
            begin_frame = 27
            n_frames = 12

    elif plant_type == PlantType.TALLNUT:
        if name == PlantReanimName.anim_idle:
            begin_frame = 20
            n_frames = 17

    elif plant_type == PlantType.TANGLE_KELP:
        if name == PlantReanimName.anim_idle:
            begin_frame = 5
            n_frames = 22

    elif plant_type == PlantType.THREEPEATER:
        if name == PlantReanimName.anim_idle:
            begin_frame = 124
            n_frames = 25

    elif plant_type == PlantType.TORCHWOOD:
        if name == PlantReanimName.anim_idle:
            begin_frame = 4
            n_frames = 21

    elif plant_type == PlantType.TWIN_SUNFLOWER:
        if name == PlantReanimName.anim_idle:
            begin_frame = 9
            n_frames = 25

    elif plant_type == PlantType.UMBRELLA_LEAF:
        if name == PlantReanimName.anim_block:
            begin_frame = 19
            n_frames = 13
        elif name == PlantReanimName.anim_idle:
            begin_frame = 4
            n_frames = 15

    elif plant_type == PlantType.WALLNUT:
        if name == PlantReanimName.anim_idle:
            begin_frame = 0
            n_frames = 17

    elif plant_type == PlantType.WINTER_MELON:
        if name == PlantReanimName.anim_idle:
            begin_frame = 5
            n_frames = 31
        elif name == PlantReanimName.anim_shooting:
            begin_frame = 36
            n_frames = 38

    return begin_frame, n_frames


def has_reanim(plant_type, name):
    if plant_type == PlantType.BLOVER:
        return name == PlantReanimName.anim_loop or \
            name == PlantReanimName.anim_idle

    elif plant_type == PlantType.CABBAGEPULT:
        return name == PlantReanimName.anim_idle or \
            name == PlantReanimName.anim_shooting

    elif plant_type == PlantType.CACTUS:
        return name == PlantReanimName.anim_idle or \
            name == PlantReanimName.anim_idlehigh or \
            name == PlantReanimName.anim_lower or \
            name == PlantReanimName.anim_rise or \
            name == PlantReanimName.anim_shooting or \
            name == PlantReanimName.anim_shootinghigh

    elif plant_type == PlantType.CATTAIL:
        return name == PlantReanimName.anim_idle or \
            name == PlantReanimName.anim_shooting

    elif plant_type == PlantType.CHERRY_BOMB:
        return name == PlantReanimName.anim_idle or \
            name == PlantReanimName.anim_explode

    elif plant_type == PlantType.CHOMPER:
        return name == PlantReanimName.anim_idle or \
            name == PlantReanimName.anim_bite or \
            name == PlantReanimName.anim_chew or \
            name == PlantReanimName.anim_swallow

    elif plant_type == PlantType.COB_CANNON:
        return name == PlantReanimName.anim_charge or \
            name == PlantReanimName.anim_unarmed_idle or \
            name == PlantReanimName.anim_idle or \
            name == PlantReanimName.anim_shooting

    elif plant_type == PlantType.COFFEE_BEAN:
        return name == PlantReanimName.anim_crumble or \
            name == PlantReanimName.anim_idle

    elif plant_type == PlantType.DOOMSHROOM:
        return name == PlantReanimName.anim_idle or \
            name == PlantReanimName.anim_sleep or \
            name == PlantReanimName.anim_explode

    elif plant_type == PlantType.FLOWER_POT:
        return name == PlantReanimName.anim_idle

    elif plant_type == PlantType.FUMESHROOM:
        return name == PlantReanimName.anim_idle or \
            name == PlantReanimName.anim_sleep or \
            name == PlantReanimName.anim_shooting

    elif plant_type == PlantType.GARLIC:
        return name == PlantReanimName.anim_idle

    elif plant_type == PlantType.GATLING_PEA:
        return name == PlantReanimName.anim_idle or \
            name == PlantReanimName.anim_shooting

    elif plant_type == PlantType.GLOOMSHROOM:
        return name == PlantReanimName.anim_idle or \
            name == PlantReanimName.anim_sleep or \
            name == PlantReanimName.anim_shooting

    elif plant_type == PlantType.GOLD_MAGNET:
        return name == PlantReanimName.anim_idle

    elif plant_type == PlantType.GRAVE_BUSTER:
        return name == PlantReanimName.anim_idle or \
            name == PlantReanimName.anim_land

    elif plant_type == PlantType.HYPNOSHROOM:
        return name == PlantReanimName.anim_idle or \
            name == PlantReanimName.anim_sleep

    elif plant_type == PlantType.ICESHROOM:
        return name == PlantReanimName.anim_idle or \
            name == PlantReanimName.anim_sleep

    elif plant_type == PlantType.IMITATER:
        return name == PlantReanimName.anim_idle or \
            name == PlantReanimName.anim_explode

    elif plant_type == PlantType.JALAPENO:
        return name == PlantReanimName.anim_idle or \
            name == PlantReanimName.anim_explode

    elif plant_type == PlantType.KERNELPULT:
        return name == PlantReanimName.anim_idle or \
            name == PlantReanimName.anim_shooting

    elif plant_type == PlantType.LILY_PAD:
        return name == PlantReanimName.anim_idle

    elif plant_type == PlantType.MAGNETSHROOM:
        return name == PlantReanimName.anim_idle or \
            name == PlantReanimName.anim_sleep or \
            name == PlantReanimName.anim_nonactive_idle2 or \
            name == PlantReanimName.anim_shooting

    elif plant_type == PlantType.MARIGOLD:
        return name == PlantReanimName.anim_idle

    elif plant_type == PlantType.MELONPULT:
        return name == PlantReanimName.anim_idle or \
            name == PlantReanimName.anim_shooting

    elif plant_type == PlantType.PEA_SHOOTER:
        return name == PlantReanimName.anim_idle or \
            name == PlantReanimName.anim_shooting

    elif plant_type == PlantType.PLANTERN:
        return name == PlantReanimName.anim_idle

    elif plant_type == PlantType.POTATO_MINE:
        return name == PlantReanimName.anim_idle or \
            name == PlantReanimName.anim_glow or \
            name == PlantReanimName.anim_armed or \
            name == PlantReanimName.anim_rise

    elif plant_type == PlantType.PUFFSHROOM:
        return name == PlantReanimName.anim_idle or \
            name == PlantReanimName.anim_sleep or \
            name == PlantReanimName.anim_shooting

    elif plant_type == PlantType.PUMPKIN:
        return name == PlantReanimName.anim_idle

    elif plant_type == PlantType.REPEATER:
        return name == PlantReanimName.anim_idle or \
            name == PlantReanimName.anim_shooting

    elif plant_type == PlantType.SCAREDYSHROOM:
        return name == PlantReanimName.anim_idle or \
            name == PlantReanimName.anim_scared or \
            name == PlantReanimName.anim_scaredidle or \
            name == PlantReanimName.anim_sleep or \
            name == PlantReanimName.anim_grow or \
            name == PlantReanimName.anim_shooting

    elif plant_type == PlantType.SEASHROOM:
        return name == PlantReanimName.anim_idle or \
            name == PlantReanimName.anim_sleep or \
            name == PlantReanimName.anim_shooting

    elif plant_type == PlantType.SNOW_PEA:
        return name == PlantReanimName.anim_idle or \
            name == PlantReanimName.anim_shooting

    elif plant_type == PlantType.SPIKEROCK:
        return name == PlantReanimName.anim_attack or \
            name == PlantReanimName.anim_idle

    elif plant_type == PlantType.SPIKEWEED:
        return name == PlantReanimName.anim_attack or \
            name == PlantReanimName.anim_idle

    elif plant_type == PlantType.SPLIT_PEA:
        return name == PlantReanimName.anim_idle or \
            name == PlantReanimName.anim_splitpea_shooting or \
            name == PlantReanimName.anim_shooting

    elif plant_type == PlantType.SQUASH:
        return name == PlantReanimName.anim_idle or \
            name == PlantReanimName.anim_lookleft or \
            name == PlantReanimName.anim_lookright or \
            name == PlantReanimName.anim_jumpup or \
            name == PlantReanimName.anim_jumpdown

    elif plant_type == PlantType.STARFRUIT:
        return name == PlantReanimName.anim_shoot or \
            name == PlantReanimName.anim_idle

    elif plant_type == PlantType.SUNFLOWER:
        return name == PlantReanimName.anim_idle

    elif plant_type == PlantType.SUNSHROOM:
        return name == PlantReanimName.anim_idle or \
            name == PlantReanimName.anim_bigidle or \
            name == PlantReanimName.anim_sleep or \
            name == PlantReanimName.anim_grow

    elif plant_type == PlantType.TALLNUT:
        return name == PlantReanimName.anim_idle

    elif plant_type == PlantType.TANGLE_KELP:
        return name == PlantReanimName.anim_idle

    elif plant_type == PlantType.THREEPEATER:
        return name == PlantReanimName.anim_idle

    elif plant_type == PlantType.TORCHWOOD:
        return name == PlantReanimName.anim_idle

    elif plant_type == PlantType.TWIN_SUNFLOWER:
        return name == PlantReanimName.anim_idle

    elif plant_type == PlantType.UMBRELLA_LEAF:
        return name == PlantReanimName.anim_block or \
            name == PlantReanimName.anim_idle

    elif plant_type == PlantType.WALLNUT:
        return name == PlantReanimName.anim_idle

    elif plant_type == PlantType.WINTER_MELON:
        return name == PlantReanimName.anim_idle or \
            name == PlantReanimName.anim_shooting

    return False
