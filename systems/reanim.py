from pvzemu2.enums import ZombieType, ZombieStatus, ZombieAction, ZombieReanimName
from pvzemu2.objects.base import Reanimate, ReanimateType, ReanimFrameStatus
from pvzemu2.systems.util import is_slowed, is_not_movable


def set_fps(z, fps: float, scene) -> None:
    """内部辅助方法，响应减速状态"""
    z.reanimate.fps = 0.5 * fps if is_slowed(scene, z) else fps


def update_progress(r: Reanimate) -> None:
    if r.n_frames == 0:
        return

    r.prev_progress = r.progress
    # 标准10ms步进
    step = (r.fps * 0.01) / r.n_frames
    r.progress += step

    if r.type == ReanimateType.ONCE:
        if r.progress >= 1.0:
            r.n_repeated = 1
            r.progress = 1.0
        elif r.progress < 0:  # 支持负向播放
            r.n_repeated = 1
            r.progress = 0.0
    else:  # REPEAT
        while r.progress >= 1.0:
            r.n_repeated += 1
            r.progress -= 1.0
        while r.progress < 0:
            r.n_repeated += 1
            r.progress += 1.0


def is_just_finished(r: Reanimate) -> bool:
    """动画是否在当前帧刚刚完成一次循环/播放"""
    return r.n_repeated > 0


def check_hit_frame(r: Reanimate, target_p: float) -> bool:
    """判断是否经过了某个特定比例的帧（用于触发发射子弹等事件）"""
    if r.prev_progress <= r.progress:
        return r.prev_progress <= target_p < r.progress
    else:  # 处理循环回播的情况
        return r.prev_progress <= target_p or target_p < r.progress


def get_frame_status(r: Reanimate) -> ReanimFrameStatus:
    """根据当前 progress 计算具体的帧索引，用于判定特定帧触发事件"""
    current_frame_float = r.progress * (r.n_frames - 1) + r.begin_frame

    frame = int(current_frame_float)
    next_frame = frame + 1

    end_frame = r.begin_frame + r.n_frames - 1
    if frame >= end_frame:
        frame = end_frame
        next_frame = end_frame

    return ReanimFrameStatus(
        frame=frame,
        next_frame=next_frame,
        frame_progress=current_frame_float - frame
    )


def update_dx(z, scene, rng_sys, do_update_fps: bool = True) -> None:
    """核心更新：根据僵尸的 status (如读报加速、撑杆跑) 动态计算真实的 z.dx"""
    if z.status == ZombieStatus.SNORKEL_SWIM:
        z.dx = 0.30000001
    elif z.status == ZombieStatus.DIGGER_WALK_RIGHT:
        z.dx = 0.12
    elif z.status == ZombieStatus.YETI_ESCAPE or z.type == ZombieType.YETI:
        z.dx = 0.40000001
    elif z.type in (ZombieType.DANCING, ZombieType.BACKUP_DANCER, ZombieType.POGO, ZombieType.FLAG):
        z.dx = 0.44999999
    elif z.status in (ZombieStatus.DIGGER_DIG, ZombieStatus.POLE_VALUTING_RUNNING) or \
            z.type in (ZombieType.FOOTBALL, ZombieType.SNORKEL, ZombieType.JACK_IN_THE_BOX):
        z.dx = rng_sys.randfloat(0.66000003, 0.68000001)
    elif z.status == ZombieStatus.LADDER_WALKING:
        z.dx = rng_sys.randfloat(0.79000002, 0.81)
    elif z.status in (
            ZombieStatus.NEWSPAPER_RUNNING, ZombieStatus.DOLPHIN_WALK_WITH_DOLPHIN,
            ZombieStatus.DOLPHIN_WALK_WITHOUT_DOLPHIN):
        z.dx = rng_sys.randfloat(0.88999999, 0.91000003)
    else:
        z.dx = rng_sys.randfloat(0.23, 0.37)
        if z.dx >= 0.3:
            z.garlic_tick.a = 15
        else:
            z.garlic_tick.a = 12

    if do_update_fps:
        update_fps(z, scene)


def update_fps(z, scene) -> None:
    """核心更新：根据僵尸是否被冰冻、是否在吃植物、是否在水下，动态调整动画播放速度"""
    # 修复：确保 prev_fps 不为 0，以便从冰冻恢复时有参照
    if z.reanimate.prev_fps == 0:
        z.reanimate.prev_fps = z.reanimate.fps if z.reanimate.fps != 0 else 12.0

    if z.countdown.freeze > 0 or z.countdown.butter > 0 or (z.has_eaten_garlic and z.time_since_ate_garlic < 170):
        set_fps(z, 0.0, scene)
        return

    if z.status in (
            ZombieStatus.SNORKEL_UP_TO_EAT, ZombieStatus.SNORKEL_FINISHED_EAT) or z.has_death_status() or z.is_dead:
        set_fps(z, z.reanimate.prev_fps, scene)
        return

    if z.is_eating:
        if z.type in (ZombieType.POLE_VAULTING, ZombieType.BALLOON, ZombieType.IMP,
                      ZombieType.DIGGER, ZombieType.JACK_IN_THE_BOX, ZombieType.SNORKEL, ZombieType.YETI):
            set_fps(z, 20.0, scene)
        else:
            set_fps(z, 36.0, scene)
        return

    if is_not_movable(scene, z) or z.type == ZombieType.CATAPULT or \
            z.status == ZombieStatus.DOLPHIN_RIDE or z.status == ZombieStatus.SNORKEL_SWIM:
        set_fps(z, z.reanimate.prev_fps, scene)
        return

    calculated = False
    if z._ground is not None:
        begin_frame = z.reanimate.begin_frame
        n_frames = z.reanimate.n_frames
        if begin_frame + n_frames < len(z._ground):
            d = z._ground[begin_frame + n_frames - 1] - z._ground[begin_frame]
            if d >= 0.000001:
                fps = (n_frames / d) * z.dx * 47.0
                set_fps(z, fps, scene)
                calculated = True

    if not calculated:
        set_fps(z, 12.0, scene)


def set_reanim(z, name, type_, fps: float, scene) -> None:
    """辅助方法"""
    if fps != 0:
        z.reanimate.fps = fps
    z.reanimate.type = type_
    z.reanimate.n_repeated = 0
    z.reanimate.progress = 0.0 if z.reanimate.fps >= 0 else 0.99999988
    z.reanimate.prev_progress = -1
    z.set_reanim_frame(name)

    if z.reanimate.fps == 0:
        update_fps(z, scene)
    else:
        z.reanimate.prev_fps = z.reanimate.fps
        update_fps(z, scene)


def update_status(z, scene, rng_sys) -> None:
    """核心更新：根据场景环境自动为僵尸切换正确的动画序列和状态"""
    update_dx(z, scene, rng_sys, do_update_fps=False)

    if z.status == ZombieStatus.LADDER_WALKING:
        set_reanim(z, ZombieReanimName.anim_ladderwalk, ReanimateType.REPEAT, 0, scene)
    elif z.status == ZombieStatus.NEWSPAPER_RUNNING:
        set_reanim(z, ZombieReanimName.anim_walk_nopaper, ReanimateType.REPEAT, 0, scene)
    elif z.is_in_water and z.action not in (ZombieAction.ENTERING_POOL, ZombieAction.LEAVING_POOL) and z.has_reanim(
            ZombieReanimName.anim_swim):
        set_reanim(z, ZombieReanimName.anim_swim, ReanimateType.REPEAT, 0, scene)
    elif not scene.is_zombie_dance or z.type not in (ZombieType.ZOMBIE, ZombieType.CONE_HEAD, ZombieType.BUCKET_HEAD):
        if (z.type != ZombieType.FLAG and rng_sys.randint(2) != 0) or not z.has_reanim(ZombieReanimName.anim_walk2):
            if z.has_reanim(ZombieReanimName.anim_walk):
                set_reanim(z, ZombieReanimName.anim_walk, ReanimateType.REPEAT, 0, scene)
        else:
            set_reanim(z, ZombieReanimName.anim_walk2, ReanimateType.REPEAT, 0, scene)
    else:
        set_reanim(z, ZombieReanimName.anim_dance, ReanimateType.REPEAT, 0, scene)
