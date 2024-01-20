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


def make_digit_tool(width_outer: int | float, width_rim: int | float, *,
                    low_to_high: Literal['RotateUp', 'RotateDown']
                    ) -> cq.Workplane:
    '''Makes the number tool for a ring of given width and thickness.

    Resulting tool will be centered on X, Y, and Z axes.

    Numbers will be presented in ascending order when
      a) RotateUp: thumb pushes upwards.
      b) RotateDown: thumb pushes downwards.
    '''
    ring = (cq.Workplane()
            .circle(width_outer)
            .circle(width_outer - width_rim)
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
              .text(digit, fontsize=font_size, distance=width_outer, font=FONT)
              .translate((dx, dy, 0))
              .rotate((0, 0, 0), (0, 1, 0), 90)
              .rotate((0, 0, 0), (0, 0, 1), angle_digit * i)
              )
        digit_tool = digit_tool.union(wp
                                      .intersect(ring))
    return digit_tool
