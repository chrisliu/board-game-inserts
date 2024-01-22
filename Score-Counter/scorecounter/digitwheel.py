import functools
import math
import cadquery as cq
from cq_gears import RingGear
from scorecounter.parameters import (
    GEAR_MODULE, N_TEETH_DIGIT, W_DIGIT_WHEEL_GEAR, T_DIGIT_WHEEL_RIM,
    ANGLE_OVERHANG, R_DIGIT_WHEEL_OUTER, R_DIGIT_WHEEL_INNER, RG_DIGIT,
    W_CARRY_GEAR_MUTILATED, DIGITS, FONT, W_DIGIT_CHARACTER
)
from typing import Literal, Optional, Tuple


def make_digit_wheel_rgear(width: Optional[int | float] = None) -> cq.Workplane:
    if width is None:
        width = W_DIGIT_WHEEL_GEAR
    rg_digit = RingGear(module=GEAR_MODULE, teeth_number=N_TEETH_DIGIT,
                        width=width, rim_width=T_DIGIT_WHEEL_RIM)
    digit_gear: cq.Workplane = cq.Workplane().gear(rg_digit)
    return digit_gear


def make_digit_wheel_inner(width: int | float,
                           from_rgear: bool = True,
                           angle_overhang: Optional[int | float] = None
                           ) -> cq.Workplane:
    '''Makes the inner section of the digit wheel.

    If @from_rgear is True, create printer-friendly geometry as if this
    section extends upwards from an existing ring gear.
    '''

    if angle_overhang is None:
        angle_overhang = ANGLE_OVERHANG

    inner = (cq.Workplane()
             .circle(R_DIGIT_WHEEL_OUTER)
             .circle(R_DIGIT_WHEEL_INNER)
             .extrude(width)
             )

    if from_rgear:
        W_overhang = ((RG_DIGIT.rd - R_DIGIT_WHEEL_INNER)
                      * math.tan(angle_overhang))
        assert W_overhang <= width

        # Construct loft for non-teeth regions.
        inner = (inner
                 .moveTo(0, 0)
                 .circle(RG_DIGIT.rd)
                 .workplane(offset=W_overhang)
                 .circle(R_DIGIT_WHEEL_INNER)
                 .loft(combine='cut')
                 )

        # Construct mutilated ring gear teeth.
        mut_rg = (make_digit_wheel_rgear(W_overhang)
                  .moveTo(0, 0)
                  .circle(R_DIGIT_WHEEL_INNER)
                  .cutThruAll()
                  )
        inner = inner.union(mut_rg)

    return inner


def make_digit_wheel_carry(width: Optional[int | float] = None,
                           mulilated_width: Optional[int | float] = None
                           ) -> cq.Workplane:
    if width is None:
        width = W_DIGIT_WHEEL_GEAR

    if mulilated_width is None:
        mulilated_width = W_CARRY_GEAR_MUTILATED

    carry = (make_digit_wheel_inner(width, from_rgear=False)
             .faces('>Z')
             .workplane()
             .moveTo(0, 0)
             .circle(RG_DIGIT.rd)
             .extrude(-mulilated_width, combine='cut')
             .union(__make_two_carry_teeth(width))
             .cut(__make_involute_tool(width))
             )

    return carry


def make_digit_tool(R_width_outer: int | float, T_width_rim: int | float, *,
                    low_to_high: Literal['RotateUp', 'RotateDown']
                    ) -> cq.Workplane:
    '''Makes the number tool for a ring of given width and thickness.

    Resulting tool will be centered on X, Y, and Z axes.

    Numbers will be presented in ascending order when
      a) RotateUp: thumb pushes upwards.
      b) RotateDown: thumb pushes downwards.
    '''
    ring = (cq.Workplane()
            .circle(R_width_outer)
            .circle(R_width_outer - T_width_rim)
            .extrude(W_DIGIT_CHARACTER / 2, both=True)
            )

    digit_tool = cq.Workplane()

    font_size = __get_font_size()
    angle_digit = 360 / len(DIGITS)
    if low_to_high == 'RotateUp':
        angle_digit *= -1
    for i, digit in enumerate(DIGITS):
        dx, dy = __get_digit_center_adj(digit, font_size)
        wp = (cq.Workplane()
              .text(digit, fontsize=font_size, distance=R_width_outer, font=FONT)
              .translate((dx, dy, 0))
              .rotate((0, 0, 0), (0, 1, 0), 90)
              .rotate((0, 0, 0), (0, 0, 1), angle_digit * i)
              )
        digit_tool = digit_tool.union(wp
                                      .intersect(ring))
    return digit_tool


def __make_two_carry_teeth(width: int | float) -> cq.Workplane:
    # Compute angle of the tip of the involute.
    tx, ty, _ = RG_DIGIT.t_lflank_pts[-1]
    angle_tip = math.atan(ty / tx)
    # Angle of the second tooth's closest tip from center
    angle_tip2 = RG_DIGIT.tau - angle_tip

    carry_tool = (cq.Workplane()
                  .moveTo(0, 0)
                  .lineTo(RG_DIGIT.rd * math.cos(angle_tip2),
                          RG_DIGIT.rd * math.sin(angle_tip2))
                  .radiusArc((RG_DIGIT.rd * math.cos(-angle_tip2),
                              RG_DIGIT.rd * math.sin(-angle_tip2)),
                             RG_DIGIT.rd)
                  .close()
                  .extrude(width)
                  )

    two_carry_teeth = (make_digit_wheel_rgear(width)
                       .circle(R_DIGIT_WHEEL_INNER)
                       .cutThruAll()
                       .intersect(carry_tool)
                       )
    return two_carry_teeth


def __make_involute_tool(width: int | float) -> cq.Workplane:
    # Compute angle of root of involute.
    hack = 1.02
    rx, ry, _ = RG_DIGIT.t_root_pts[0]
    angle_root = math.atan(ry / rx)

    involute_tool = (cq.Workplane()
                     .moveTo(0, 0)
                     .lineTo(RG_DIGIT.rd * hack * math.cos(angle_root),
                             RG_DIGIT.rd * hack * math.sin(angle_root))
                     .radiusArc((RG_DIGIT.rd * hack * math.cos(-angle_root),
                                 RG_DIGIT.rd * hack * math.sin(-angle_root)),
                                RG_DIGIT.rd * hack)
                     .close()
                     .extrude(width)
                     .cut(make_digit_wheel_rgear(width))
                     )
    return involute_tool


@functools.cache
def __get_font_size() -> float:
    '''Returns the font size that satisfies the widest character fits in
    W_DIGIT_CHARACTER.
    '''
    def get_x(digit: str, font_size: float) -> float:
        txt = cq.Workplane().text(digit, fontsize=font_size, distance=1,
                                  font=FONT)
        assert len(txt.objects) == 1
        obj = txt.objects[0]
        bb = obj.BoundingBox()
        return bb.xmax - bb.xmin

    fs_min = 5
    fs_max = 10
    fs = list()
    for digit in DIGITS:
        x_min = get_x(digit, fs_min)
        x_max = get_x(digit, fs_max)
        fs_fit = fs_min + ((fs_max - fs_min) / (x_max - x_min)
                           * (W_DIGIT_CHARACTER - x_min))
        fs.append(fs_fit)
    return min(fs)


@functools.cache
def __get_digit_center_adj(digit: str, font_size: int | float
                           ) -> Tuple[float, float]:
    '''Returns the X, Y adjustments required to center a digit.'''

    txt = cq.Workplane().text(digit, fontsize=font_size, distance=1,
                              font=FONT)
    assert len(txt.objects) == 1
    obj = txt.objects[0]
    bb_c = obj.CenterOfBoundBox()
    return -bb_c.x, -bb_c.y


if __name__ == '__cq_main__':
    from scorecounter.parameters import (
        W_DIGIT_SPACING, T_WALL_MIN, ANGLE_VIEWING
    )
    from scorecounter.parameters import (
        R_CORE_INNER, R_CORE_OUTER, T_CORE_WALL, W_CARRY_GEAR, TOL_MOVING,
        T_WALL_MIN, SG_CARRY, SG_SHAFT, RG_DIGIT, R_PEG_CARRY, R_SHAFT,
        T_SHAFT_WALL, T_PEG_MIN, W_PEG
    )
    from cadquery import exporters

    T_digit = min(0.8, R_DIGIT_WHEEL_OUTER - R_DIGIT_WHEEL_INNER - T_WALL_MIN)

    W_wheel_ones = W_DIGIT_CHARACTER + W_DIGIT_SPACING
    W_wheel_ones_inner = W_wheel_ones - 2 * W_DIGIT_WHEEL_GEAR
    '''
    digit_ones = (make_digit_tool(R_DIGIT_WHEEL_OUTER, T_digit,
                                  low_to_high='RotateUp')
                  .rotate((0, 0, 0), (0, 0, 1),
                          -(math.degrees(ANGLE_VIEWING)
                            + (1 - 1/2) * 360 / len(DIGITS)))
                  .translate((0, 0, W_wheel_ones / 2))
                  )

    wheel_ones = (make_digit_wheel_rgear(W_DIGIT_WHEEL_GEAR)
                  .union(
                      make_digit_wheel_inner(W_wheel_ones_inner)
                      .translate((0, 0, W_DIGIT_WHEEL_GEAR)))
                  .union(
                      make_digit_wheel_carry()
                      .translate((0, 0, W_wheel_ones - W_DIGIT_WHEEL_GEAR)))
                  .cut(digit_ones)
                  )
    '''

    W_wheel_tens = (2 * W_DIGIT_CHARACTER + W_DIGIT_SPACING
                    + max(T_WALL_MIN, W_DIGIT_SPACING / 2))
    '''
    digit_tens = (make_digit_tool(R_DIGIT_WHEEL_OUTER, T_digit,
                                  low_to_high='RotateUp')
                  .rotate((0, 0, 0), (0, 0, 1),
                          -(math.degrees(ANGLE_VIEWING)
                            + (1 - 1/2) * 360 / len(DIGITS)))
                  .translate((0, 0, (W_DIGIT_CHARACTER + W_DIGIT_SPACING) / 2))
                  )
    digit_tens_mirror = (make_digit_tool(R_DIGIT_WHEEL_OUTER, T_digit,
                                         low_to_high='RotateDown')
                         .rotate((0, 0, 0), (1, 0, 0), 180)
                         .rotate((0, 0, 0), (0, 0, 1),
                                 (math.degrees(ANGLE_VIEWING)
                                  - (1 - 1/2) * 360 / len(DIGITS)))
                         .translate((0, 0, W_wheel_tens -
                                     (W_DIGIT_CHARACTER + W_DIGIT_SPACING) / 2))
                         )
    wheel_tens = (make_digit_wheel_rgear(W_DIGIT_WHEEL_GEAR)
                  .union(
        make_digit_wheel_inner(W_wheel_tens - W_DIGIT_WHEEL_GEAR)
        .translate((0, 0, W_DIGIT_WHEEL_GEAR)))
        .cut(digit_tens)
        .cut(digit_tens_mirror)
        .translate((0, 0, W_wheel_ones))
    )
    '''

    W_wheel_ones_mirror = W_DIGIT_CHARACTER + W_DIGIT_SPACING
    W_wheel_ones_mirror_inner = W_wheel_ones_mirror - W_DIGIT_WHEEL_GEAR
    '''
    digit_ones_mirror = (make_digit_tool(R_DIGIT_WHEEL_OUTER, T_digit,
                                         low_to_high='RotateDown')
                         .rotate((0, 0, 0), (0, 0, 1),
                                 -(math.degrees(ANGLE_VIEWING)
                                   - (1 - 1/2) * 360 / len(DIGITS)))
                         .translate((0, 0, W_wheel_ones_mirror / 2))
                         )
    wheel_ones_mirror = (make_digit_wheel_rgear(W_DIGIT_WHEEL_GEAR)
                         .union(
        make_digit_wheel_inner(W_wheel_ones_mirror_inner)
        .translate((0, 0, W_DIGIT_WHEEL_GEAR)))
        .cut(digit_ones_mirror)
        .translate((0, 0, -W_wheel_ones_mirror / 2))
        .rotate((0, 0, 0), (1, 0, 0), 180)
        .translate((0, 0,
                    W_wheel_ones + W_wheel_tens
                    + W_wheel_ones_mirror / 2))
    )
    '''

    '''
    show_object(wheel_ones)
    show_object(wheel_tens)
    show_object(wheel_ones_mirror)

    exporters.export(wheel_ones, 'wheel_ones.stl')
    exporters.export(wheel_tens, 'wheel_tens.stl')
    exporters.export(wheel_ones_mirror, 'wheel_ones_mirror.stl')
    '''

    print(W_wheel_tens)

    # core_tens = (cq.Workplane()
    #              .circle(R_CORE_OUTER)
    #              .circle(R_CORE_INNER)
    #              .extrude(W_wheel_tens - W_DIGIT_WHEEL_GEAR)
    #              .tag('base')
    #              .faces('>Z')
    #              .workplane()
    #              .circle(R_CORE_INNER + min(T_CORE_WALL / 2, T_WALL_MIN))
    #              .circle(R_CORE_INNER)
    #              .extrude(W_CARRY_GEAR + 2 * TOL_MOVING)
    #              # Carry gear cutout.
    #              .moveTo(RG_DIGIT.r0 - SG_CARRY.r0, 0)
    #              .circle(SG_CARRY.ra + TOL_MOVING)
    #              .extrude(W_CARRY_GEAR + 2 * TOL_MOVING, combine='cut')
    #              # Peg.
    #              .moveTo(RG_DIGIT.r0 - SG_CARRY.r0, 0)
    #              .circle(R_PEG_CARRY)
    #              .extrude(W_CARRY_GEAR + 2 * TOL_MOVING)
    #              .moveTo(RG_DIGIT.r0 - SG_CARRY.r0, 0)
    #              .circle(R_PEG_CARRY - T_PEG_MIN)
    #              .extrude(W_CARRY_GEAR + 2 * TOL_MOVING + W_PEG)
    #              # Peg support.
    #              .moveTo(RG_DIGIT.r0 - SG_CARRY.r0, SG_CARRY.rd)
    #              .radiusArc((RG_DIGIT.r0 - SG_CARRY.r0, -SG_CARRY.rd),
    #                         -SG_CARRY.rd)
    #              .lineTo(math.sqrt(R_CORE_INNER ** 2 - SG_CARRY.rd ** 2),
    #                      -SG_CARRY.rd)
    #              .radiusArc(
    #                  (math.sqrt(R_CORE_INNER ** 2 - SG_CARRY.rd ** 2),
    #                   SG_CARRY.rd),
    #                  -R_CORE_INNER)
    #              .close()
    #              .extrude(-(W_wheel_tens - W_DIGIT_WHEEL_GEAR))
    #              .edges('|Z')
    #              .edges('not(>X)')
    #              .edges('>X')
    #              .fillet(SG_CARRY.rd / 4)
    #              # Shaft hole.
    #              .workplaneFromTagged('base')
    #              .moveTo(-(RG_DIGIT.r0 - SG_SHAFT.r0), 0)
    #              .circle(R_SHAFT + TOL_MOVING)
    #              .circle(R_SHAFT + T_SHAFT_WALL)
    #              .extrude(W_wheel_tens - W_DIGIT_WHEEL_GEAR
    #                       + W_CARRY_GEAR + 2 * TOL_MOVING)
    #              .moveTo(-(RG_DIGIT.r0 - SG_SHAFT.r0), 0)
    #              .circle(R_SHAFT + TOL_MOVING)
    #              .cutThruAll()
    #              # .moveTo(-(RG_DIGIT.r0 - SG_SHAFT.r0), 0)
    #              # .circle(SG_SHAFT.ra)
    #              # .moveTo(RG_DIGIT.r0 - SG_CARRY.r0, 0)
    #              # .circle(SG_CARRY.ra)
    #              # .extrude(W_wheel_tens - W_DIGIT_WHEEL_GEAR
    #              #          + W_CARRY_GEAR + 2 * TOL_MOVING)
    #              )

    # print(R_PEG_CARRY - T_PEG_MIN)
