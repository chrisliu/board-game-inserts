import cadquery as cq
import math
from typing import Literal, Optional, Tuple
from scorecounter.parameters import (
    R_CORE_OUTER, R_CORE_INNER, R_PEG_CARRY, R_PEG, W_PEG, T_PEG_MIN,
    T_WALL_MIN, RG_DIGIT, SG_CARRY, SG_SHAFT, TOL_TIGHT_FIT, ANGLE_OVERHANG,
    R_PEG_CORE, R_SHAFT, R_PEG_CARRY_SUPPORT, W_CORE_ONES, W_CORE_TENS,
    W_CORE_ONES_MIRROR, W_DIGIT_WHEEL_GEAR, TOL_MOVING,
    X_PEG_CORE_CENTER, Y_PEG_CORE_CENTER, THETA_PEG_CORE_CENTER
)


def make_peg_standalone(W_peg) -> cq.Workplane:
    peg = (cq.Workplane()
           .circle(R_PEG)
           .extrude(W_peg)
           )
    return peg


def make_core_ones() -> cq.Workplane:
    # Note: Tens ring extends into the ones.
    W_thinner = W_DIGIT_WHEEL_GEAR + 2 * TOL_MOVING
    W_thicker = W_CORE_ONES - W_thinner
    core_ones = make_core_bottom(W_thicker, W_thinner,
                                 orientation_top='Thinner',
                                 peg_top='Female')
    core_ones = make_core_shaft_gear(core_ones, W_thicker, W_thinner)
    core_ones = make_core_carry_recv(core_ones, W_thicker, W_thinner)
    return core_ones


def make_core_tens() -> cq.Workplane:
    # Goes into the ones ring
    W_thinner = 2 * W_DIGIT_WHEEL_GEAR + 2 * TOL_MOVING
    W_thicker = W_CORE_TENS - W_thinner
    core_tens = make_core_bottom(W_thicker, W_thinner,
                                 orientation_top='Thinner')
    core_tens = make_core_shaft_from_bottom(core_tens, W_thicker + W_thinner)
    core_tens = make_core_carry(core_tens, W_thicker, W_thinner)
    return core_tens


def make_core_ones_mirror() -> cq.Workplane:
    W_thinner = W_DIGIT_WHEEL_GEAR + 2 * TOL_MOVING
    W_thicker = W_CORE_ONES_MIRROR - W_thinner
    core_ones_mirror = make_core_bottom(W_thicker, W_thinner,
                                        orientation_top='Thinner',
                                        peg_top='Female')
    core_ones_mirror = make_core_shaft_gear(core_ones_mirror,
                                            W_thicker, W_thinner)
    return core_ones_mirror


def make_core_bottom(W_thicker: int | float, W_thinner: int | float,
                     orientation_top: Literal['Thinner', 'Thicker'],
                     peg_top: Optional[Literal['Male', 'Female']] = 'Male'
                     ) -> cq.Workplane:
    '''Make the wheel core with the default support pegs.

    The model consists of a thicker section of size W_thicker and a thinner
    section of W_thinner on top.

    Male & female pegs are placed depending on orientation_top
      a) 'Thinner': male pegs extend from the thinner direction.
      b) 'Thicker': male pegs extend from the thicker direction.

    orientation_top also determines if an overhang-friendly feature
    should be modeled for the main ring.

    Dev-only:
      - named faces: bottom, middle, top
    '''

    W_thicker_actual = W_thicker
    if orientation_top == 'Thicker':
        W_overhang = ((R_CORE_OUTER - (R_CORE_INNER + T_WALL_MIN))
                      * math.tan(ANGLE_OVERHANG))
        W_thicker_actual -= W_overhang

    core_bottom = (cq.Workplane()
                   .tag('bottom')
                   .circle(R_CORE_OUTER)
                   .circle(R_CORE_INNER)
                   .extrude(W_thicker_actual)
                   .faces('>Z')
                   .workplane()
                   )

    if orientation_top == 'Thicker':
        core_bottom = (core_bottom
                       .circle(R_CORE_OUTER)
                       .workplane(offset=W_overhang)
                       .circle(R_CORE_INNER + T_WALL_MIN)
                       .loft()
                       .circle(R_CORE_INNER)
                       .cutThruAll()
                       .faces('>Z')
                       .workplane()
                       )

    core_bottom = (core_bottom
                   .tag('middle')
                   .circle(R_CORE_INNER)
                   .circle(R_CORE_INNER + T_WALL_MIN)
                   .extrude(W_thinner)
                   .faces('>Z')
                   .workplane()
                   .tag('top')
                   )

    # Compute points on inner circle that intersects with the left & right
    # edges of the circle at angle theta.
    x_peg_left = (X_PEG_CORE_CENTER
                  + R_PEG_CORE * math.cos(THETA_PEG_CORE_CENTER + math.pi / 2))
    y_peg_left = (Y_PEG_CORE_CENTER
                  + R_PEG_CORE * math.sin(THETA_PEG_CORE_CENTER + math.pi / 2))
    x_inner_left, y_inner_left = __compute_closest_point_on_circle(
        x_peg_left, y_peg_left, R_CORE_INNER, THETA_PEG_CORE_CENTER)
    x_peg_right = (X_PEG_CORE_CENTER
                   + R_PEG_CORE * math.cos(THETA_PEG_CORE_CENTER - math.pi / 2))
    y_peg_right = (Y_PEG_CORE_CENTER
                   + R_PEG_CORE * math.sin(THETA_PEG_CORE_CENTER - math.pi / 2))
    x_inner_right, y_inner_right = __compute_closest_point_on_circle(
        x_peg_right, y_peg_right, R_CORE_INNER, THETA_PEG_CORE_CENTER)
    W_all = W_thicker + W_thinner
    core_bottom = (core_bottom
                   .workplaneFromTagged('bottom')
                   # Draw peg support.
                   .moveTo(X_PEG_CORE_CENTER, Y_PEG_CORE_CENTER)
                   .circle(R_PEG_CORE)
                   .mirrorX()
                   .extrude(W_all)
                   # Draw peg support wall.
                   .moveTo(x_peg_left, y_peg_left)
                   .lineTo(x_inner_left, y_inner_left)
                   .radiusArc((x_inner_right, y_inner_right), R_CORE_INNER)
                   .lineTo(x_peg_right, y_peg_right)
                   .close()
                   .mirrorX()
                   .extrude(W_all)
                   )

    # Draw (male )& female pegs.
    R_female = R_PEG + TOL_TIGHT_FIT
    W_female = W_PEG + 2 * TOL_TIGHT_FIT
    cone = __make_cone(R_female, ANGLE_OVERHANG)
    if peg_top == 'Male':
        if orientation_top == 'Thinner':
            core_bottom = core_bottom.faces('>Z').workplane()
        elif orientation_top == 'Thicker':
            core_bottom = core_bottom.faces('<Z').workplane()
        core_bottom = (core_bottom
                       .moveTo(X_PEG_CORE_CENTER, Y_PEG_CORE_CENTER)
                       .circle(R_PEG)
                       .mirrorX()
                       .extrude(W_PEG)
                       )
    elif peg_top == 'Female':
        cone_top = cone
        if orientation_top == 'Thinner':
            core_bottom = core_bottom.faces('>Z').workplane()
            Z = W_all - W_female
            cone_top = cone.rotate((0, 0, 0), (0, 1, 0), 180)
        elif orientation_top == 'Thicker':
            core_bottom = core_bottom.faces('<Z').workplane()
            Z = W_female
        core_bottom = (core_bottom
                       .moveTo(X_PEG_CORE_CENTER, Y_PEG_CORE_CENTER)
                       .circle(R_female)
                       .mirrorX()
                       .extrude(-W_female, combine='cut')
                       .cut(cone_top
                            .translate((X_PEG_CORE_CENTER,
                                        Y_PEG_CORE_CENTER,
                                        Z)))
                       .cut(cone_top
                            .translate((X_PEG_CORE_CENTER,
                                        -Y_PEG_CORE_CENTER,
                                        Z)))
                       )

    cone_bot = cone
    if orientation_top == 'Thinner':
        core_bottom = core_bottom.faces('<Z').workplane()
        Z = W_female
    elif orientation_top == 'Thicker':
        core_bottom = core_bottom.faces('>Z').workplane()
        Z = W_all - W_female
        cone_bot = cone.rotate((0, 0, 0), (0, 1, 0), 180)
    core_bottom = (core_bottom
                   .moveTo(X_PEG_CORE_CENTER, Y_PEG_CORE_CENTER)
                   .circle(R_female)
                   .mirrorX()
                   .extrude(-W_female, combine='cut')
                   .cut(cone_bot
                        .translate((X_PEG_CORE_CENTER, Y_PEG_CORE_CENTER, Z)))
                   .cut(cone
                        .translate((X_PEG_CORE_CENTER, -Y_PEG_CORE_CENTER, Z)))
                   )

    return core_bottom


def make_core_carry_from_bottom(core: cq.Workplane,
                                W_carry: int | float
                                ) -> cq.Workplane:
    x_peg_center = RG_DIGIT.r0 - SG_CARRY.r0
    y_peg_center = 0
    x_peg_left = x_peg_center
    y_peg_left = y_peg_center + R_PEG_CARRY_SUPPORT
    x_inner_left, y_inner_left = __compute_closest_point_on_circle(
        x_peg_center, y_peg_left, R_CORE_INNER, math.pi)
    core = (core
            .workplaneFromTagged('bottom')
            .moveTo(x_peg_center, y_peg_center)
            .circle(R_PEG_CARRY_SUPPORT)
            .extrude(W_carry)
            .moveTo(x_peg_center, y_peg_center)
            .lineTo(x_peg_left, y_peg_left)
            .lineTo(x_inner_left, y_inner_left)
            .radiusArc((R_CORE_INNER, 0), R_CORE_INNER)
            .close()
            .mirrorX()
            .extrude(W_carry)
            )
    return core


def make_core_carry(core: cq.Workplane,
                    W_thicker: int | float,
                    W_thinner: int | float
                    ) -> cq.Workplane:
    x_peg_center = RG_DIGIT.r0 - SG_CARRY.r0
    y_peg_center = 0
    core = (make_core_carry_from_bottom(core, W_thicker)
            .workplaneFromTagged('middle')
            .moveTo(x_peg_center, y_peg_center)
            .circle(SG_CARRY.ra + TOL_MOVING)
            .extrude(W_thinner, combine='cut')
            .moveTo(x_peg_center, y_peg_center)
            .circle(R_PEG_CARRY)
            .extrude(W_thinner + W_PEG)
            )
    return core


def make_core_carry_recv(core: cq.Workplane,
                         W_thicker: int | float,
                         W_thinner: int | float
                         ) -> cq.Workplane:
    '''Assumes peg female will be at the bottom.'''
    W_overhang = (R_PEG_CARRY + TOL_TIGHT_FIT) * math.tan(ANGLE_OVERHANG)
    Z = W_PEG + 2 * TOL_TIGHT_FIT
    W_recv = min(W_thinner + W_thicker,
                 Z + T_WALL_MIN + W_overhang)
    x_peg_center = RG_DIGIT.r0 - SG_CARRY.r0
    y_peg_center = 0
    core = (make_core_carry_from_bottom(core, W_recv)
            .workplaneFromTagged('bottom')
            .moveTo(x_peg_center, y_peg_center)
            .circle(R_PEG_CARRY + TOL_TIGHT_FIT)
            .extrude(Z, combine='cut')
            .cut(__make_cone(R_PEG_CARRY + TOL_TIGHT_FIT, ANGLE_OVERHANG)
                 .translate((x_peg_center, y_peg_center, Z)))
            )
    return core


def make_core_shaft_gear(core: cq.Workplane,
                         W_thicker: int | float,
                         W_thinner: int | float
                         ) -> cq.Workplane:
    x_shaft_center = -(RG_DIGIT.r0 - SG_SHAFT.r0)
    y_shaft_center = 0
    core = (core
            .workplaneFromTagged('top')
            .moveTo(x_shaft_center, y_shaft_center)
            .circle(SG_SHAFT.ra + TOL_MOVING)
            .extrude(-W_thinner, combine='cut')
            )
    core = make_core_shaft_from_bottom(core, W_thicker)
    return core


def make_core_shaft_from_bottom(core: cq.Workplane,
                                W_shaft: int | float,
                                ) -> cq.Workplane:
    R_outer = R_SHAFT + TOL_MOVING + T_WALL_MIN
    x_shaft_center = -(RG_DIGIT.r0 - SG_SHAFT.r0)
    y_shaft_center = 0
    x_shaft_left = x_shaft_center
    y_shaft_left = y_shaft_center + R_outer
    x_inner_left, y_inner_left = __compute_closest_point_on_circle(
        x_shaft_left, y_shaft_left, R_CORE_INNER, 0)
    core = (core
            .workplaneFromTagged('bottom')
            .moveTo(x_shaft_center, y_shaft_center)
            .circle(R_outer)
            .extrude(W_shaft)
            .moveTo(x_shaft_center, y_shaft_center)
            .lineTo(x_shaft_left, y_shaft_left)
            .lineTo(x_inner_left, y_inner_left)
            .radiusArc((-R_CORE_INNER, 0), -R_CORE_INNER)
            .close()
            .mirrorX()
            .extrude(W_shaft)
            .moveTo(x_shaft_center, y_shaft_center)
            .circle(R_SHAFT + TOL_MOVING)
            .extrude(W_shaft, combine='cut')
            )
    return core


def __make_cone(R_cone: int | float, angle_cone: int | float) -> cq.Workplane:
    cone = (cq.Workplane('YZ')
            .moveTo(0, 0)
            .lineTo(R_cone, 0)
            .lineTo(0, R_cone * math.tan(angle_cone))
            .close()
            .revolve()
            )
    return cone


def __compute_closest_point_on_circle(
    x_pt: int | float,
    y_pt: int | float,
    r: int | float,
    theta: int | float
) -> Tuple[int | float, int | float]:
    # Line formula: y = Mx + C
    M = math.tan(theta)
    C = y_pt - M * x_pt

    # After plugging in y into the circle formula, we get the following
    # terms for the quadratic formula.
    a = M ** 2 + 1
    b = 2 * M * C
    c = C ** 2 - r ** 2

    # Solve for possible points.
    x1 = (-b + math.sqrt(b ** 2 - 4 * a * c)) / (2 * a)
    y1 = M * x1 + C
    x2 = (-b - math.sqrt(b ** 2 - 4 * a * c)) / (2 * a)
    y2 = M * x2 + C

    d1_sq = (x1 - x_pt) ** 2 + (y1 - y_pt) ** 2
    d2_sq = (x2 - x_pt) ** 2 + (y2 - y_pt) ** 2

    if d1_sq < d2_sq:
        return x1, y1
    return x2, y2


if __name__ == '__cq_main__':
    import os
    from scorecounter.parameters import DIR_EXPORT, W_PEG
    from cadquery import exporters

    core_ones = make_core_ones()
    exporters.export(core_ones, os.path.join(DIR_EXPORT, 'core_ones.stl'))

    core_tens = make_core_tens()
    exporters.export(core_tens, os.path.join(DIR_EXPORT, 'core_tens.stl'))

    core_ones_mirror = make_core_ones_mirror()
    exporters.export(core_ones_mirror,
                     os.path.join(DIR_EXPORT, 'core_ones_mirror.stl'))

    peg_standalone = make_peg_standalone(2 * W_PEG)
    exporters.export(peg_standalone,
                     os.path.join(DIR_EXPORT, 'peg_standalone.stl'))
