from typing import Final, List

from pvzemu2.enums import ZombieType, ZombieReanimName

COMMON_ZOMBIE_GROUND: Final[List[float]] = [
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, -9.8, -8.4, -7.0, -5.6, -4.1, -2.7, -1.3, 0.0, 1.4, 2.8, 4.2, 5.7, 7.1,
    7.9, 8.8, 9.7, 10.5, 10.6, 10.8, 10.9, 11.0, 11.0, 11.0, 11.0, 11.0, 13.4, 15.8,
    18.1, 20.5, 22.8, 25.2, 27.6, 29.9, 31.1, 32.3, 33.5, 34.6, 35.9, 37.0, 38.2, 39.4,
    39.5, 39.6, 39.7, 39.8, 39.9, 40.0, -9.8, -8.5, -7.3, -6.0, -4.7, -3.4, -2.1, -0.9,
    0.3, 1.6, 2.8, 4.1, 5.4, 6.7, 8.0, 9.2, 10.5, 10.6, 10.7, 10.7, 10.8, 10.8,
    10.9, 11.0, 12.8, 14.5, 16.3, 18.1, 19.9, 21.6, 23.4, 25.2, 27.0, 28.8, 30.5, 32.3,
    34.0, 35.9, 37.6, 39.4, 39.5, 39.5, 39.6, 39.8, 39.9, 39.9, 40.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, -9.8, -8.4, -7.0, -5.6, -4.1, -2.7, -1.3, 0.0, 1.4, 2.8,
    4.2, 5.7, 7.1, 7.9, 8.8, 9.7, 10.5, 10.6, 10.8, 10.9, 11.0, 11.0, 11.0, 11.0,
    11.0, 13.4, 15.8, 18.1, 20.5, 22.8, 25.2, 27.6, 29.9, 31.1, 32.3, 33.5, 34.6, 35.9,
    37.0, 38.2, 39.4, 40.0, -28.5, -27.7, -26.9, -26.0, -25.2, -24.4, -23.6, -23.6, -23.6, -23.6,
    -21.4, -19.2, -16.9, -14.5, -12.2, -11.4, -10.7, -5.3, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.9, -1.7, -2.6, -3.5, -3.5, -3.5,
    -3.5, -3.5, -3.5, -3.5, -4.7, -6.0, -7.3, -8.6, -16.1, -23.6, -24.3, -25.1, -25.1, -25.1,
    -26.6, -28.1, -29.6, -31.5, -33.5, -35.4, -35.4, -35.4, -35.4, -35.4, -35.4, -35.4, -35.4, -35.4,
    -35.4, -35.4, -35.4, -35.4, -35.4, -35.4, -35.4, -35.4, -35.4, -35.4, -35.4, -35.4, -35.4, -35.4,
    -35.4, -35.4, -35.4, -35.4, -35.4, -35.4, -35.4, -35.4, -35.4, -35.4, -35.4, -35.4, -35.4, -35.4,
    -35.4, -35.4, -35.4, -35.4, -35.4, -35.4, -35.4, -35.4, -35.4, -35.4, -35.4, -35.4, -35.4, -35.4,
    -35.4, -35.4, -35.4, -35.4, -35.4, -35.4, -35.4, -35.4, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, -9.8, -9.4, -8.9, -8.4, -7.9, -7.5, -7.0, -6.5, -6.1,
    -5.6, -5.1, -4.7, -4.2, -3.7, -3.3, -2.8, -2.3, -1.8, -1.4, -0.9, -0.4, 0.0, 0.3,
    0.8, 1.3, 1.8, 2.2, 2.6, 3.1, 3.6, 4.1, 4.6, 5.0, 5.5, 6.0, 6.5, 6.9,
    7.3, 7.8, 8.3, 8.8, 9.3, 9.7, 10.2, 10.7, 11.1, 11.6, 12.1, 12.6, 13.0
]


def get_zombie_reanim_data(zombie_type):
    n_frames = 0
    fps = 12.0

    if zombie_type == ZombieType.BACKUP_DANCER:
        n_frames = 100
    elif zombie_type == ZombieType.BALLOON:
        n_frames = 155
    elif zombie_type == ZombieType.BUNGEE:
        n_frames = 67
    elif zombie_type == ZombieType.CATAPULT:
        n_frames = 85
    elif zombie_type == ZombieType.DANCING:
        n_frames = 147
    elif zombie_type == ZombieType.DIGGER:
        n_frames = 200
    elif zombie_type == ZombieType.DOLPHIN_RIDER:
        n_frames = 289
    elif zombie_type == ZombieType.FOOTBALL:
        n_frames = 105
    elif zombie_type in (ZombieType.GARGANTUAR, ZombieType.GIGA_GARGANTUAR):
        n_frames = 197
    elif zombie_type == ZombieType.IMP:
        n_frames = 104
    elif zombie_type == ZombieType.JACK_IN_THE_BOX:
        n_frames = 103
    elif zombie_type == ZombieType.LADDER:
        n_frames = 215
    elif zombie_type == ZombieType.NEWSPAPER:
        n_frames = 216
    elif zombie_type == ZombieType.POGO:
        n_frames = 166
    elif zombie_type == ZombieType.POLE_VAULTING:
        n_frames = 193
    elif zombie_type == ZombieType.SNORKEL:
        n_frames = 249
    elif zombie_type == ZombieType.YETI:
        n_frames = 105
    elif zombie_type in (ZombieType.CONE_HEAD, ZombieType.BUCKET_HEAD, ZombieType.SCREEN_DOOR,
                         ZombieType.FLAG, ZombieType.DUCKY_TUBE, ZombieType.ZOMBIE):
        n_frames = 504
    elif zombie_type == ZombieType.ZOMBONI:
        n_frames = 62
    else:
        # Default or error case
        pass

    return n_frames, fps


def get_reanim_frame_data(zombie_type, name):
    begin_frame = 0
    n_frames = 0

    if zombie_type == ZombieType.BACKUP_DANCER:
        if name == ZombieReanimName.anim_walk:
            begin_frame = 0
            n_frames = 21
        elif name == ZombieReanimName.anim_eat:
            begin_frame = 32
            n_frames = 33
        elif name == ZombieReanimName.anim_armraise:
            begin_frame = 21
            n_frames = 11
        elif name == ZombieReanimName.anim_death:
            begin_frame = 65
            n_frames = 35

    elif zombie_type == ZombieType.BALLOON:
        if name == ZombieReanimName.anim_idle:
            begin_frame = 0
            n_frames = 13
        elif name == ZombieReanimName.anim_walk:
            begin_frame = 84
            n_frames = 41
        elif name == ZombieReanimName.anim_pop:
            begin_frame = 31
            n_frames = 28
        elif name == ZombieReanimName.anim_eat:
            begin_frame = 59
            n_frames = 25
        elif name == ZombieReanimName.anim_death:
            begin_frame = 125
            n_frames = 28

    elif zombie_type == ZombieType.BUNGEE:
        if name == ZombieReanimName.anim_idle:
            begin_frame = 0
            n_frames = 20
        elif name == ZombieReanimName.anim_grab:
            begin_frame = 29
            n_frames = 15
        elif name == ZombieReanimName.anim_drop:
            begin_frame = 20
            n_frames = 9
        elif name == ZombieReanimName.anim_raise:
            begin_frame = 54
            n_frames = 13

    elif zombie_type == ZombieType.CATAPULT:
        if name == ZombieReanimName.anim_idle:
            begin_frame = 57
            n_frames = 13
        elif name == ZombieReanimName.anim_walk:
            begin_frame = 0
            n_frames = 25
        elif name == ZombieReanimName.anim_bounce:
            begin_frame = 70
            n_frames = 15
        elif name == ZombieReanimName.anim_shoot:
            begin_frame = 25
            n_frames = 32

    elif zombie_type == ZombieType.DANCING:
        if name == ZombieReanimName.anim_walk:
            begin_frame = 46
            n_frames = 21
        elif name == ZombieReanimName.anim_moonwalk:
            begin_frame = 0
            n_frames = 27
        elif name == ZombieReanimName.anim_eat:
            begin_frame = 78
            n_frames = 34
        elif name == ZombieReanimName.anim_point:
            begin_frame = 27
            n_frames = 10
        elif name == ZombieReanimName.anim_armraise:
            begin_frame = 67
            n_frames = 11
        elif name == ZombieReanimName.anim_death:
            begin_frame = 112
            n_frames = 35

    elif zombie_type == ZombieType.DIGGER:
        if name == ZombieReanimName.anim_idle:
            begin_frame = 0
            n_frames = 18
        elif name == ZombieReanimName.anim_drill:
            begin_frame = 146
            n_frames = 19
        elif name == ZombieReanimName.anim_dizzy:
            begin_frame = 179
            n_frames = 21
        elif name == ZombieReanimName.anim_walk:
            begin_frame = 18
            n_frames = 37
        elif name == ZombieReanimName.anim_dig:
            begin_frame = 128
            n_frames = 18
        elif name == ZombieReanimName.anim_eat:
            begin_frame = 55
            n_frames = 33
        elif name == ZombieReanimName.anim_death:
            begin_frame = 88
            n_frames = 40
        elif name == ZombieReanimName.anim_landing:
            begin_frame = 165
            n_frames = 14

    elif zombie_type == ZombieType.DOLPHIN_RIDER:
        if name == ZombieReanimName.anim_dolphinjump:
            begin_frame = 143
            n_frames = 23
        elif name == ZombieReanimName.anim_ride:
            begin_frame = 138
            n_frames = 5
        elif name == ZombieReanimName.anim_jumpinpool:
            begin_frame = 93
            n_frames = 45
        elif name == ZombieReanimName.anim_idle:
            begin_frame = 0
            n_frames = 15
        elif name == ZombieReanimName.anim_swim:
            begin_frame = 208
            n_frames = 42
        elif name == ZombieReanimName.anim_walk:
            begin_frame = 54
            n_frames = 39
        elif name == ZombieReanimName.anim_walkdolphin:
            begin_frame = 15
            n_frames = 39
        elif name == ZombieReanimName.anim_eat:
            begin_frame = 166
            n_frames = 42
        elif name == ZombieReanimName.anim_death:
            begin_frame = 250
            n_frames = 39

    elif zombie_type == ZombieType.FOOTBALL:
        if name == ZombieReanimName.anim_idle:
            begin_frame = 0
            n_frames = 21
        elif name == ZombieReanimName.anim_walk:
            begin_frame = 21
            n_frames = 30
        elif name == ZombieReanimName.anim_eat:
            begin_frame = 51
            n_frames = 36
        elif name == ZombieReanimName.anim_death:
            begin_frame = 87
            n_frames = 18

    elif zombie_type in (ZombieType.GARGANTUAR, ZombieType.GIGA_GARGANTUAR):
        if name == ZombieReanimName.anim_smash:
            begin_frame = 71
            n_frames = 33
        elif name == ZombieReanimName.anim_idle:
            begin_frame = 0
            n_frames = 22
        elif name == ZombieReanimName.anim_walk:
            begin_frame = 22
            n_frames = 49
        elif name == ZombieReanimName.anim_death:
            begin_frame = 138
            n_frames = 59
        elif name == ZombieReanimName.anim_throw:
            begin_frame = 104
            n_frames = 34

    elif zombie_type == ZombieType.IMP:
        if name == ZombieReanimName.anim_walk:
            begin_frame = 0
            n_frames = 33
        elif name == ZombieReanimName.anim_eat:
            begin_frame = 33
            n_frames = 27
        elif name == ZombieReanimName.anim_death:
            begin_frame = 60
            n_frames = 22
        elif name == ZombieReanimName.anim_land:
            begin_frame = 98
            n_frames = 6
        elif name == ZombieReanimName.anim_thrown:
            begin_frame = 82
            n_frames = 16

    elif zombie_type == ZombieType.JACK_IN_THE_BOX:
        if name == ZombieReanimName.anim_idle:
            begin_frame = 13
            n_frames = 17
        elif name == ZombieReanimName.anim_walk:
            begin_frame = 30
            n_frames = 19
        elif name == ZombieReanimName.anim_pop:
            begin_frame = 64
            n_frames = 16
        elif name == ZombieReanimName.anim_eat:
            begin_frame = 49
            n_frames = 15
        elif name == ZombieReanimName.anim_death:
            begin_frame = 80
            n_frames = 23

    elif zombie_type == ZombieType.LADDER:
        if name == ZombieReanimName.anim_idle:
            begin_frame = 0
            n_frames = 25
        elif name == ZombieReanimName.anim_ladderwalk:
            begin_frame = 25
            n_frames = 47
        elif name == ZombieReanimName.anim_laddereat:
            begin_frame = 72
            n_frames = 24
        elif name == ZombieReanimName.anim_walk:
            begin_frame = 132
            n_frames = 47
        elif name == ZombieReanimName.anim_eat:
            begin_frame = 179
            n_frames = 24
        elif name == ZombieReanimName.anim_death:
            begin_frame = 96
            n_frames = 36
        elif name == ZombieReanimName.anim_placeladder:
            begin_frame = 203
            n_frames = 12

    elif zombie_type == ZombieType.NEWSPAPER:
        if name == ZombieReanimName.anim_idle:
            begin_frame = 0
            n_frames = 25
        elif name == ZombieReanimName.anim_walk_nopaper:
            begin_frame = 145
            n_frames = 47
        elif name == ZombieReanimName.anim_walk:
            begin_frame = 25
            n_frames = 47
        elif name == ZombieReanimName.anim_gasp:
            begin_frame = 132
            n_frames = 13
        elif name == ZombieReanimName.anim_eat:
            begin_frame = 72
            n_frames = 24
        elif name == ZombieReanimName.anim_eat_nopaper:
            begin_frame = 192
            n_frames = 24
        elif name == ZombieReanimName.anim_death:
            begin_frame = 96
            n_frames = 36

    elif zombie_type == ZombieType.POGO:
        if name == ZombieReanimName.anim_idle:
            begin_frame = 0
            n_frames = 29
        elif name == ZombieReanimName.anim_walk:
            begin_frame = 29
            n_frames = 47
        elif name == ZombieReanimName.anim_pogo:
            begin_frame = 155
            n_frames = 11
        elif name == ZombieReanimName.anim_eat:
            begin_frame = 76
            n_frames = 40
        elif name == ZombieReanimName.anim_death:
            begin_frame = 116
            n_frames = 39

    elif zombie_type == ZombieType.POLE_VAULTING:
        if name == ZombieReanimName.anim_idle:
            begin_frame = 0
            n_frames = 13
        elif name == ZombieReanimName.anim_walk:
            begin_frame = 93
            n_frames = 45
        elif name == ZombieReanimName.anim_run:
            begin_frame = 13
            n_frames = 37
        elif name == ZombieReanimName.anim_eat:
            begin_frame = 165
            n_frames = 28
        elif name == ZombieReanimName.anim_death:
            begin_frame = 138
            n_frames = 27
        elif name == ZombieReanimName.anim_jump:
            begin_frame = 50
            n_frames = 43

    elif zombie_type == ZombieType.SNORKEL:
        if name == ZombieReanimName.anim_jumpinpool:
            begin_frame = 59
            n_frames = 19
        elif name == ZombieReanimName.anim_idle:
            begin_frame = 0
            n_frames = 22
        elif name == ZombieReanimName.anim_swim:
            begin_frame = 78
            n_frames = 7
        elif name == ZombieReanimName.anim_uptoeat:
            begin_frame = 85
            n_frames = 12
        elif name == ZombieReanimName.anim_walk:
            begin_frame = 22
            n_frames = 37
        elif name == ZombieReanimName.anim_eat:
            begin_frame = 97
            n_frames = 25
        elif name == ZombieReanimName.anim_death:
            begin_frame = 122
            n_frames = 35

    elif zombie_type == ZombieType.YETI:
        if name == ZombieReanimName.anim_idle:
            begin_frame = 0
            n_frames = 15
        elif name == ZombieReanimName.anim_walk:
            begin_frame = 15
            n_frames = 34
        elif name == ZombieReanimName.anim_eat:
            begin_frame = 49
            n_frames = 29
        elif name == ZombieReanimName.anim_death:
            begin_frame = 78
            n_frames = 27

    elif zombie_type in (ZombieType.ZOMBIE, ZombieType.CONE_HEAD, ZombieType.BUCKET_HEAD,
                         ZombieType.SCREEN_DOOR, ZombieType.FLAG, ZombieType.DUCKY_TUBE):
        if name == ZombieReanimName.anim_idle:
            begin_frame = 0
            n_frames = 29
        elif name == ZombieReanimName.anim_swim:
            begin_frame = 250
            n_frames = 42
        elif name == ZombieReanimName.anim_walk2:
            begin_frame = 91
            n_frames = 47
        elif name == ZombieReanimName.anim_walk:
            begin_frame = 44
            n_frames = 47
        elif name == ZombieReanimName.anim_dance:
            begin_frame = 454
            n_frames = 50
        elif name == ZombieReanimName.anim_eat:
            begin_frame = 138
            n_frames = 40
        elif name == ZombieReanimName.anim_death:
            begin_frame = 178
            n_frames = 39
        elif name == ZombieReanimName.anim_death2:
            begin_frame = 217
            n_frames = 33
        elif name == ZombieReanimName.anim_superlongdeath:
            begin_frame = 292
            n_frames = 137
        elif name == ZombieReanimName.anim_waterdeath:
            begin_frame = 429
            n_frames = 25

    elif zombie_type == ZombieType.ZOMBONI:
        if name == ZombieReanimName.anim_drive:
            begin_frame = 0
            n_frames = 13
        elif name == ZombieReanimName.anim_wheelie1:
            begin_frame = 13
            n_frames = 16
        elif name == ZombieReanimName.anim_wheelie2:
            begin_frame = 29
            n_frames = 33

    return begin_frame, n_frames


def has_reanim(zombie_type, name):
    if name == ZombieReanimName._ground:
        return zombie_type != ZombieType.BUNGEE and \
            zombie_type != ZombieType.ZOMBONI and \
            zombie_type != ZombieType.CATAPULT

    if zombie_type == ZombieType.BACKUP_DANCER:
        return name == ZombieReanimName.anim_walk or \
            name == ZombieReanimName.anim_eat or \
            name == ZombieReanimName.anim_armraise or \
            name == ZombieReanimName.anim_death

    elif zombie_type == ZombieType.BALLOON:
        return name == ZombieReanimName.anim_idle or \
            name == ZombieReanimName.anim_walk or \
            name == ZombieReanimName.anim_pop or \
            name == ZombieReanimName.anim_eat or \
            name == ZombieReanimName.anim_death

    elif zombie_type == ZombieType.BUNGEE:
        return name == ZombieReanimName.anim_idle or \
            name == ZombieReanimName.anim_grab or \
            name == ZombieReanimName.anim_drop or \
            name == ZombieReanimName.anim_raise

    elif zombie_type == ZombieType.CATAPULT:
        return name == ZombieReanimName.anim_idle or \
            name == ZombieReanimName.anim_walk or \
            name == ZombieReanimName.anim_bounce or \
            name == ZombieReanimName.anim_shoot

    elif zombie_type == ZombieType.DANCING:
        return name == ZombieReanimName.anim_walk or \
            name == ZombieReanimName.anim_moonwalk or \
            name == ZombieReanimName.anim_eat or \
            name == ZombieReanimName.anim_point or \
            name == ZombieReanimName.anim_armraise or \
            name == ZombieReanimName.anim_death

    elif zombie_type == ZombieType.DIGGER:
        return name == ZombieReanimName.anim_idle or \
            name == ZombieReanimName.anim_drill or \
            name == ZombieReanimName.anim_dizzy or \
            name == ZombieReanimName.anim_walk or \
            name == ZombieReanimName.anim_dig or \
            name == ZombieReanimName.anim_eat or \
            name == ZombieReanimName.anim_death or \
            name == ZombieReanimName.anim_landing

    elif zombie_type == ZombieType.DOLPHIN_RIDER:
        return name == ZombieReanimName.anim_dolphinjump or \
            name == ZombieReanimName.anim_ride or \
            name == ZombieReanimName.anim_jumpinpool or \
            name == ZombieReanimName.anim_idle or \
            name == ZombieReanimName.anim_swim or \
            name == ZombieReanimName.anim_walk or \
            name == ZombieReanimName.anim_walkdolphin or \
            name == ZombieReanimName.anim_eat or \
            name == ZombieReanimName.anim_death

    elif zombie_type == ZombieType.FOOTBALL:
        return name == ZombieReanimName.anim_idle or \
            name == ZombieReanimName.anim_walk or \
            name == ZombieReanimName.anim_eat or \
            name == ZombieReanimName.anim_death

    elif zombie_type in (ZombieType.GARGANTUAR, ZombieType.GIGA_GARGANTUAR):
        return name == ZombieReanimName.anim_smash or \
            name == ZombieReanimName.anim_idle or \
            name == ZombieReanimName.anim_walk or \
            name == ZombieReanimName.anim_death or \
            name == ZombieReanimName.anim_throw

    elif zombie_type == ZombieType.IMP:
        return name == ZombieReanimName.anim_walk or \
            name == ZombieReanimName.anim_eat or \
            name == ZombieReanimName.anim_death or \
            name == ZombieReanimName.anim_land or \
            name == ZombieReanimName.anim_thrown

    elif zombie_type == ZombieType.JACK_IN_THE_BOX:
        return name == ZombieReanimName.anim_idle or \
            name == ZombieReanimName.anim_walk or \
            name == ZombieReanimName.anim_pop or \
            name == ZombieReanimName.anim_eat or \
            name == ZombieReanimName.anim_death

    elif zombie_type == ZombieType.LADDER:
        return name == ZombieReanimName.anim_idle or \
            name == ZombieReanimName.anim_ladderwalk or \
            name == ZombieReanimName.anim_laddereat or \
            name == ZombieReanimName.anim_walk or \
            name == ZombieReanimName.anim_eat or \
            name == ZombieReanimName.anim_death or \
            name == ZombieReanimName.anim_placeladder

    elif zombie_type == ZombieType.NEWSPAPER:
        return name == ZombieReanimName.anim_idle or \
            name == ZombieReanimName.anim_walk_nopaper or \
            name == ZombieReanimName.anim_walk or \
            name == ZombieReanimName.anim_gasp or \
            name == ZombieReanimName.anim_eat or \
            name == ZombieReanimName.anim_eat_nopaper or \
            name == ZombieReanimName.anim_death

    elif zombie_type == ZombieType.POGO:
        return name == ZombieReanimName.anim_idle or \
            name == ZombieReanimName.anim_walk or \
            name == ZombieReanimName.anim_pogo or \
            name == ZombieReanimName.anim_eat or \
            name == ZombieReanimName.anim_death

    elif zombie_type == ZombieType.POLE_VAULTING:
        return name == ZombieReanimName.anim_idle or \
            name == ZombieReanimName.anim_walk or \
            name == ZombieReanimName.anim_run or \
            name == ZombieReanimName.anim_eat or \
            name == ZombieReanimName.anim_death or \
            name == ZombieReanimName.anim_jump

    elif zombie_type == ZombieType.SNORKEL:
        return name == ZombieReanimName.anim_jumpinpool or \
            name == ZombieReanimName.anim_idle or \
            name == ZombieReanimName.anim_swim or \
            name == ZombieReanimName.anim_uptoeat or \
            name == ZombieReanimName.anim_walk or \
            name == ZombieReanimName.anim_eat or \
            name == ZombieReanimName.anim_death

    elif zombie_type == ZombieType.YETI:
        return name == ZombieReanimName.anim_idle or \
            name == ZombieReanimName.anim_walk or \
            name == ZombieReanimName.anim_eat or \
            name == ZombieReanimName.anim_death

    elif zombie_type in (ZombieType.ZOMBIE, ZombieType.CONE_HEAD, ZombieType.BUCKET_HEAD,
                         ZombieType.SCREEN_DOOR, ZombieType.FLAG, ZombieType.DUCKY_TUBE):
        return name == ZombieReanimName.anim_idle or \
            name == ZombieReanimName.anim_swim or \
            name == ZombieReanimName.anim_walk2 or \
            name == ZombieReanimName.anim_walk or \
            name == ZombieReanimName.anim_dance or \
            name == ZombieReanimName.anim_eat or \
            name == ZombieReanimName.anim_death or \
            name == ZombieReanimName.anim_death2 or \
            name == ZombieReanimName.anim_superlongdeath or \
            name == ZombieReanimName.anim_waterdeath

    elif zombie_type == ZombieType.ZOMBONI:
        return name == ZombieReanimName.anim_drive or \
            name == ZombieReanimName.anim_wheelie1 or \
            name == ZombieReanimName.anim_wheelie2

    return False
