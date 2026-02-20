from enum import IntEnum, IntFlag, auto


class PlantReanimName(IntEnum):
    anim_charge = auto()
    anim_unarmed_idle = auto()
    anim_block = auto()
    anim_crumble = auto()
    anim_loop = auto()
    anim_attack = auto()
    anim_shoot = auto()
    anim_idle = auto()
    anim_bigidle = auto()
    anim_scared = auto()
    anim_scaredidle = auto()
    anim_sleep = auto()
    anim_explode = auto()
    anim_grow = auto()
    anim_glow = auto()
    anim_armed = auto()
    anim_land = auto()
    anim_bite = auto()
    anim_chew = auto()
    anim_swallow = auto()
    anim_idlehigh = auto()
    anim_lower = auto()
    anim_rise = auto()
    anim_lookleft = auto()
    anim_lookright = auto()
    anim_jumpup = auto()
    anim_jumpdown = auto()
    anim_splitpea_shooting = auto()
    anim_nonactive_idle2 = auto()
    anim_shooting = auto()
    anim_shootinghigh = auto()


class ZombieReanimName(IntEnum):
    _ground = auto()
    anim_smash = auto()
    anim_dolphinjump = auto()
    anim_ride = auto()
    anim_jumpinpool = auto()
    anim_idle = auto()
    anim_grab = auto()
    anim_ladderwalk = auto()
    anim_laddereat = auto()
    anim_walk_nopaper = auto()
    anim_swim = auto()
    anim_uptoeat = auto()
    anim_drill = auto()
    anim_dizzy = auto()
    anim_walk2 = auto()
    anim_walk = auto()
    anim_dance = auto()
    anim_drop = auto()
    anim_run = auto()
    anim_walkdolphin = auto()
    anim_dig = auto()
    anim_drive = auto()
    anim_pogo = auto()
    anim_moonwalk = auto()
    anim_raise = auto()
    anim_pop = auto()
    anim_gasp = auto()
    anim_eat = auto()
    anim_eat_nopaper = auto()
    anim_point = auto()
    anim_armraise = auto()
    anim_wheelie1 = auto()
    anim_wheelie2 = auto()
    anim_bounce = auto()
    anim_death = auto()
    anim_death2 = auto()
    anim_superlongdeath = auto()
    anim_waterdeath = auto()
    anim_throw = auto()
    anim_jump = auto()
    anim_shoot = auto()
    anim_land = auto()
    anim_landing = auto()
    anim_thrown = auto()
    anim_placeladder = auto()


class SceneType(IntEnum):
    DAY = 0x0
    NIGHT = 0x1
    POOL = 0x2
    FOG = 0x3
    ROOF = 0x4
    MOON_NIGHT = 0x5

    # GARDEN
    MUSHROOM = 0x6
    GREENHOUSE = 0x7
    ZOMBIQUARIUM = 0x8
    TREEOFWISDOM = 0x9


class PlantType(IntEnum):
    NONE = -1
    PEA_SHOOTER = 0x0
    SUNFLOWER = 0x1
    CHERRY_BOMB = 0x2
    WALLNUT = 0x3
    POTATO_MINE = 0x4
    SNOW_PEA = 0x5
    CHOMPER = 0x6
    REPEATER = 0x7
    PUFFSHROOM = 0x8
    SUNSHROOM = 0x9
    FUMESHROOM = 0xA
    GRAVE_BUSTER = 0xB
    HYPNOSHROOM = 0xC
    SCAREDYSHROOM = 0xD
    ICESHROOM = 0xE
    DOOMSHROOM = 0xF
    LILY_PAD = 0x10
    SQUASH = 0x11
    THREEPEATER = 0x12
    TANGLE_KELP = 0x13
    JALAPENO = 0x14
    SPIKEWEED = 0x15
    TORCHWOOD = 0x16
    TALLNUT = 0x17
    SEASHROOM = 0x18
    PLANTERN = 0x19
    CACTUS = 0x1A
    BLOVER = 0x1B
    SPLIT_PEA = 0x1C
    STARFRUIT = 0x1D
    PUMPKIN = 0x1E
    MAGNETSHROOM = 0x1F
    CABBAGEPULT = 0x20
    FLOWER_POT = 0x21
    KERNELPULT = 0x22
    COFFEE_BEAN = 0x23
    GARLIC = 0x24
    UMBRELLA_LEAF = 0x25
    MARIGOLD = 0x26
    MELONPULT = 0x27
    GATLING_PEA = 0x28
    TWIN_SUNFLOWER = 0x29
    GLOOMSHROOM = 0x2A
    CATTAIL = 0x2B
    WINTER_MELON = 0x2C
    GOLD_MAGNET = 0x2D
    SPIKEROCK = 0x2E
    COB_CANNON = 0x2F
    IMITATER = 0x30

    # IZombie
    SEED_ZOMBIE = 0X3C
    SEED_CONE_HEAD = 0x3D
    SEED_POLE_VAULTING = 0x3E
    SEED_BUCKET_HEAD = 0x3F
    SEED_LADDER = 0x40
    SEED_DIGGER = 0x41
    SEED_BUNGEE = 0x42
    SEED_FOOTBALL = 0x43
    SEED_BALLOON = 0x44
    SEED_SCREEN_DOOR = 0x45
    SEED_ZOMBONI = 0x46
    SEED_POGO = 0x47
    SEED_DANCING = 0x48
    SEED_GARGANTUAR = 0x49
    SEED_IMP = 0x4A


class PlantStatus(IntEnum):
    IDLE = 0x0
    WAIT = 0x1
    WORK = 0x2
    SQUASH_LOOK = 0x3
    SQUASH_JUMP_UP = 0x4
    SQUASH_STOP_IN_THE_AIR = 0x5
    SQUASH_JUMP_DOWN = 0x6
    SQUASH_CRUSHED = 0x7
    GRAVE_BUSTER_LAND = 0x8
    GRAVE_BUSTER_IDLE = 0x9
    CHOMPER_BITE_BEGIN = 0xA
    CHOMPER_BITE_SUCCESS = 0xB
    CHOMPER_BITE_FAIL = 0xC
    CHOMPER_CHEW = 0xD
    CHOMPER_SWALLOW = 0xE
    POTATO_SPROUT_OUT = 0xF
    POTATO_ARMED = 0x10
    POTATO_MASHED = 0x11  # TODO
    SPIKE_ATTACK = 0x12
    SPIKEWEED_ATTACK2 = 0x13  # TODO
    SCAREDYSHROOM_SCARED = 0x14
    SCAREDYSHROOM_SCARED_IDLE = 0x15
    SCAREDYSHROOM_GROW = 0x16
    SUNSHROOM_SMALL = 0x17
    SUNSHROOM_GROW = 0x18
    SUNSHROOM_BIG = 0x19
    MAGNETSHROOM_WORKING = 0x1A
    MAGNETSHROOM_INACTIVE_IDLE = 0x1B
    BOWLING_UP = 0x1C  # TODO:?
    BOWLING_DOWN = 0x1D  # TODO:?
    CACTUS_SHORT_IDLE = 0x1E
    CACTUS_GROW_TALL = 0x1F
    CACTUS_TALL_IDLE = 0x20
    CACTUS_GET_SHORT = 0x21
    TANGLE_KELP_GRAB = 0x22
    COB_CANNON_UNARMED_IDLE = 0x23
    COB_CANNON_CHARGE = 0x24
    COB_CANNON_LAUNCH = 0x25
    COB_CANNON_ARMED_IDLE = 0x26
    KERNELPULT_LAUNCH_BUTTER = 0x27
    UMBRELLA_LEAF_BLOCK = 0x28
    UMBRELLA_LEAF_SHRINK = 0x29
    IMITATER_MORPHING = 0x2A
    FLOWER_POT_PLACED = 0x2F
    LILY_PAD_PLACED = 0x30


class PlantDirection(IntEnum):
    LEFT = 1
    RIGHT = -1


class PlantEdibleStatus(IntEnum):
    VISIBLE_AND_EDIBLE = 0
    INVISIBLE_AND_EDIBLE = 1
    INVISIBLE_AND_NOT_EDIBLE = 2


class AttackFlags(IntFlag):
    GROUND = 0x1
    FLYING_BALLOON = 0x2
    LURKING_SNORKEL = 0x4
    ANIMATING_ZOMBIES = 0x10
    DYING_ZOMBIES = 0x20
    DIGGING_DIGGER = 0x40
    HYPNO_ZOMBIES = 0x80


class DamageFlags(IntFlag):
    BYPASSES_SHIELD = 0x1
    DAMAGE_HITS_SHIELD_AND_BODY = 0x2
    DAMAGE_FREEZE = 0x4
    NO_FLASH = 0x8
    NO_LEAVE_BODY = 0x10
    SPIKE = 0x20


class ZombieType(IntEnum):
    NONE = -1
    ZOMBIE = 0x0
    FLAG = 0x1
    CONE_HEAD = 0x2
    POLE_VAULTING = 0x3
    BUCKET_HEAD = 0x4
    NEWSPAPER = 0x5
    SCREEN_DOOR = 0x6
    FOOTBALL = 0x7
    DANCING = 0x8
    BACKUP_DANCER = 0x9
    DUCKY_TUBE = 0xA
    SNORKEL = 0xB
    ZOMBONI = 0xC
    ZOMBIE_BOBSLED = 0xD  # TODO:雪橇小队
    DOLPHIN_RIDER = 0xE
    JACK_IN_THE_BOX = 0xF
    BALLOON = 0x10
    DIGGER = 0x11
    POGO = 0x12
    YETI = 0x13
    BUNGEE = 0x14
    LADDER = 0x15
    CATAPULT = 0x16
    GARGANTUAR = 0x17
    IMP = 0x18
    ZOMBIE_BOSS = 0x19  # TODO:僵尸博士
    GIGA_GARGANTUAR = 0x20
    ZOMBIE_PEA_HEAD = 0x21  # TODO:植物僵尸-豌豆射手
    ZOMBIE_WALLNUT_HEAD = 0x22  # TODO:植物僵尸-坚果墙
    ZOMBIE_JALAPENO_HEAD = 0x23  # TODO:植物僵尸-火爆辣椒
    ZOMBIE_GATLING_HEAD = 0x24  # TODO:植物僵尸-机枪射手
    ZOMBIE_SQUASH_HEAD = 0x25  # TODO:植物僵尸-倭瓜
    ZOMBIE_TALLNUT_HEAD = 0x26  # TODO:植物僵尸-高坚果


class ZombieStatus(IntEnum):
    WALKING = 0x0
    DYING = 0x1
    DYING_FROM_INSTANT_KILL = 0x2
    DYING_FROM_LAWNMOWER = 0x3

    BUNGEE_TARGET_DROP = 0x4
    BUNGEE_BODY_DROP = 0x5
    BUNGEE_IDLE_AFTER_DROP = 0x6
    BUNGEE_GRAB = 0x7
    BUNGEE_RAISE = 0x8
    BUNGEE_HIT_OUCHY = 0x9  # TODO
    BUNGEE_IDLE = 0xA

    POLE_VALUTING_RUNNING = 0xB
    POLE_VALUTING_JUMPING = 0xC
    POLE_VAULTING_WALKING = 0xD

    RISING_FROM_GROUND = 0xE

    JACKBOX_WALKING = 0xF
    JACKBOX_POP = 0x10

    BOBSLED_SLIDING = 0x11  # TODO:雪橇车僵尸在冰道上滑行
    BOBSLED_BOARDING = 0x12  # TODO:雪橇车僵尸上车（准备滑行）
    BOBSLED_CRASHING = 0x13  # TODO:雪橇车僵尸撞毁（雪橇损坏）

    POGO_WITH_STICK = 0x14
    POGO_IDLE_BEFORE_TARGET = 0x15
    POGO_HIGH_BOUNCE_2 = 0x16  # TODO:跳跳僵尸高跳阶段2
    POGO_HIGH_BOUNCE_3 = 0x17  # TODO:跳跳僵尸高跳阶段3
    POGO_HIGH_BOUNCE_4 = 0x18  # TODO:跳跳僵尸高跳阶段4
    POGO_HIGH_BOUNCE_5 = 0x19  # TODO:跳跳僵尸高跳阶段5
    POGO_HIGH_BOUNCE_6 = 0x1a  # TODO:跳跳僵尸高跳阶段6
    POGO_JUMP_ACROSS = 0x1B
    POGO_FORWARD_ACROSS2 = 0x1C  # TODO:跳跳僵尸向前弹跳（阶段2）

    NEWSPAPER_WALKING = 0x1D
    NEWSPAPER_DESTROYED = 0x1E
    NEWSPAPER_RUNNING = 0x1F

    DIGGER_DIG = 0x20
    DIGGER_DRILL = 0x21
    DIGGER_LOST_DIG = 0x22
    DIGGER_LANDING = 0x23
    DIGGER_DIZZY = 0x24
    DIGGER_WALK_RIGHT = 0x25
    DIGGER_WALK_LEFT = 0x26
    DIGGER_IDLE = 0x27

    DANCING_MOONWALK = 0x28
    DANCING_POINT = 0x29
    DANCING_WAIT_SUMMONING = 0x2A
    DANCING_SUMMONING = 0x2B
    DANCING_WALKING = 0x2C
    DANCING_ARMRISE1 = 0x2D
    DANCING_ARMRISE2 = 0x2E
    DANCING_ARMRISE3 = 0x2F
    DANCING_ARMRISE4 = 0x30
    DANCING_ARMRISE5 = 0x31
    DANCING_DANCER_SPAWNING = 0x32

    DOLPHIN_WALK_WITH_DOLPHIN = 0x33
    DOLPHIN_JUMP_IN_POOL = 0x34
    DOLPHIN_RIDE = 0x35
    DOLPHIN_IN_JUMP = 0x36
    DOLPHIN_WALK_IN_POOL = 0x37
    DOLPHIN_WALK_WITHOUT_DOLPHIN = 0x38

    SNORKEL_WALKING = 0x39
    SNORKEL_JUMP_IN_THE_POOL = 0x3A
    SNORKEL_SWIM = 0x3B
    SNORKEL_UP_TO_EAT = 0x3C
    SNORKEL_EATING_IN_POOL = 0x3D
    SNORKEL_FINISHED_EAT = 0x3E

    ZOMBIE_AQUARIUM_ACCEL = 0x3f  # TODO:水族馆僵尸（迷你游戏）加速
    ZOMBIE_AQUARIUM_DRIFT = 0x40  # TODO:水族馆僵尸漂移
    ZOMBIE_AQUARIUM_BACK_AND_FORTH = 0x41  # TODO:水族馆僵尸来回游动
    ZOMBIE_AQUARIUM_BITE = 0x42  # TODO:水族馆僵尸撕咬

    CATAPULT_SHOOT = 0x43
    CATAPULT_IDLE = 0x44

    GARGANTUAR_THROW = 0x45
    GARGANTUAR_SMASH = 0x46

    IMP_FLYING = 0x47
    IMP_LANDING = 0x48

    BALLOON_FLYING = 0x49
    BALLOON_FALLING = 0x4A
    BALLOON_WALKING = 0x4B

    LADDER_WALKING = 0x4C
    LADDER_PLACING = 0x4D

    BOSS_ENTER = 0x4e  # TODO:僵尸博士入场
    BOSS_IDLE = 0x4f  # TODO:僵尸博士待机
    BOSS_SPAWNING = 0x50  # TODO:僵尸博士召唤僵尸
    BOSS_STOMPING = 0x51  # TODO:僵尸博士跺脚（攻击）
    BOSS_BUNGEES_ENTER = 0x52  # TODO:僵尸博士的蹦极僵尸入场
    BOSS_BUNGEES_DROP = 0x53  # TODO:蹦极僵尸被投下
    BOSS_BUNGEES_LEAVE = 0x54  # TODO:蹦极僵尸撤离
    BOSS_DROP_RV = 0x55  # TODO:僵尸博士投下房车（攻击）
    BOSS_HEAD_ENTER = 0x56  # TODO:博士头颅进入（分离后）
    BOSS_HEAD_IDLE_BEFORE_SPIT = 0x57  # TODO:博士头颅喷火前待机
    BOSS_HEAD_IDLE_AFTER_SPIT = 0x58  # TODO:博士头颅喷火后待机
    BOSS_HEAD_SPIT = 0x59  # TODO:博士头颅喷火
    BOSS_HEAD_LEAVE = 0x5a  # TODO:博士头颅离开

    YETI_ESCAPE = 0x5B

    SQUASH_PRE_LAUNCH = 0x5c  # TODO:僵尸被倭瓜攻击前（准备）
    SQUASH_RISING = 0x5d  # TODO:僵尸被倭瓜压扁中（上升？实际是倭瓜下落？）此处可能指僵尸被压扁的动画
    SQUASH_FALLING = 0x5e  # TODO:僵尸被压扁后下落？通常倭瓜压扁后僵尸消失，可能指压扁过程
    SQUASH_DONE_FALLING = 0x5f  # TODO:压扁完成（僵尸消失）


class ZombieAction(IntEnum):
    NONE = 0x0
    ENTERING_POOL = 0x1
    LEAVING_POOL = 0x2
    CAUGHT_BY_KELP = 0x3
    CLIMBING_LADDER = 0x6
    FALLING = 0x7
    FALL_FROM_SKY = 0x9


class ZombieAccessoriesType1(IntEnum):
    NONE = 0x0
    ROADCONE = 0x1
    BUCKET = 0x2
    FOOTBALL_CAP = 0x3
    MINER_HAT = 0x4


class ZombieAccessoriesType2(IntEnum):
    NONE = 0x0
    SCREEN_DOOR = 0x1
    NEWSPAPER = 0x2
    LADDER = 0x3


class GridItemType(IntEnum):
    NONE = 0x0
    GRAVE = 0x1
    CRATER = 0x2
    LADDER = 0x3
    PORTAL_CIRCLE = 0x4  # TODO
    PORTAL_SQUARE = 0x5  # TODO
    BRAIN = 0x6  # TODO
    SCARY_POT = 0x7  # TODO
    SQUIRREL = 0x8  # TODO
    ZEN_TOOL = 0x9  # TODO
    STINKY = 0xA  # TODO
    RAKE = 0xB  # TODO
    I_ZOMBIE_BRAIN = 0xC  # TODO


class GridSquareType(IntEnum):
    NONE = 0x0
    GRASS = 0x1
    DIRT = 0x2
    POOL = 0x3
    HIGH_GROUND = 0x4


class ProjectileType(IntEnum):
    NONE = -1
    PEA = 0x0
    SNOW_PEA = 0x1
    CABBAGE = 0x2
    MELON = 0x3
    PUFF = 0x4
    WINTERMELON = 0x5
    FIRE_PEA = 0x6
    STAR = 0x7
    CACTUS = 0x8
    BASKETBALL = 0x9
    KERNEL = 0xA
    COB_CANNON = 0xB
    BUTTER = 0xC
    ZOMBIE_PEA = 0xD  # TODO


class ProjectileMotionType(IntEnum):
    STRAIGHT = 0
    PARABOLA = 1
    SWITCH_WAY = 2
    PUFF = 5
    LEFT_STRAIGHT = 6
    STARFRUIT = 7
    CATTAIL = 9
