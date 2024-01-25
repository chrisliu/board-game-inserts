from typing import Tuple
import cadquery as cq
import math
from scorecounter.parameters import (
    W_SPRING, R_SPRING, R_SPRING_BUMP, R_BUMP_OUTER, T_SPRING,
    H_SPRING_SLOT, T_SPRING_SLOT, ANGLE_OVERHANG,
    X_SPRING_BUMP_CENTER, Y_SPRING_BUMP_CENTER,
    X_SPRING_BUMP_TANGENT, Y_SPRING_BUMP_TANGENT, X_SPRING_SLOT, Y_SPRING_SLOT,
    X_SPRING_OUTER, H_CASE_HALF, R_CASE_CORE_BUMP, W_CASE_INNER,
    T_CASE_BUMP_WALL,
    T_CASE_CORE_WALL, T_CASE, T_CASE_DIGIT_WALL, W_DIGIT_WHEEL_BUMP,
    TOL_MOVING, TOL_TIGHT_FIT, T_WALL_MIN, T_CASE_FLOOR,
    X_PEG_CORE_CENTER, Y_PEG_CORE_CENTER, R_PEG, W_PEG,
    W_CASE_INTERFACE, H_COVER_INTERFACE, W_COVER_INTERFACE_WALL,
    T_CASE_INTERFACE_MALE, R_PRINTER_FILLET, R_CASE_CORE_DIGIT,
    T_COVER_WALL, ANGLE_VIEWING, W_DIGIT_CHARACTER, W_DIGIT_SPACING, DIGITS,
    W_WHEEL_ONES_MIRROR, W_WHEEL_TENS, W_WHEEL_ONES
)


def make_spring() -> cq.Workplane:
    spring = (cq.Workplane()
              # Make spring bumps.
              .moveTo(X_SPRING_BUMP_CENTER, Y_SPRING_BUMP_CENTER)
              .circle(R_SPRING_BUMP)
              .mirrorX()
              .extrude(W_SPRING)
              # Make spring.
              .moveTo(X_SPRING_BUMP_TANGENT, Y_SPRING_BUMP_TANGENT)
              .radiusArc((X_SPRING_OUTER, 0), R_SPRING)
              .lineTo(X_SPRING_OUTER + T_SPRING, 0)
              .radiusArc(
                  (X_SPRING_BUMP_TANGENT + T_SPRING, Y_SPRING_BUMP_TANGENT),
                  -R_SPRING)
              .close()
              .mirrorX()
              .extrude(W_SPRING)
              # Make slot.
              .moveTo(X_SPRING_SLOT, Y_SPRING_SLOT)
              .radiusArc((X_SPRING_SLOT, -Y_SPRING_SLOT), -R_SPRING)
              .lineTo(X_SPRING_SLOT - T_SPRING_SLOT, -Y_SPRING_SLOT)
              .lineTo(X_SPRING_SLOT - T_SPRING_SLOT, Y_SPRING_SLOT)
              .close()
              .extrude(W_SPRING)
              # Make printer-friendly support.
              .faces('<X')
              .workplane()
              .moveTo(0, W_SPRING)
              .lineTo(H_SPRING_SLOT / 2,
                      W_SPRING - (H_SPRING_SLOT / 2) * math.tan(ANGLE_OVERHANG))
              .lineTo(H_SPRING_SLOT / 2, W_SPRING)
              .close()
              .extrude(-T_SPRING_SLOT, combine='cut')
              # Note: mirroring and cutting is resulting in incorrect geometry.
              .moveTo(0, W_SPRING)
              .lineTo(-H_SPRING_SLOT / 2,
                      W_SPRING - (H_SPRING_SLOT / 2) * math.tan(ANGLE_OVERHANG))
              .lineTo(-H_SPRING_SLOT / 2, W_SPRING)
              .close()
              .extrude(-T_SPRING_SLOT, combine='cut')
              )
    return spring


def _make_wheel_bump() -> cq.Workplane:
    from scorecounter.parameters import (
        W_DIGIT_WHEEL_BUMP, T_BUMP, ANGLE_BUMP_ALL, ANGLE_BUMP,
        R_DIGIT_WHEEL_OUTER, R_DIGIT_WHEEL_INNER, DIGITS
    )
    W_BUMP_WHEEL = W_DIGIT_WHEEL_BUMP
    bump_wheel = (cq.Workplane()
                  .circle(R_DIGIT_WHEEL_OUTER)
                  .circle(R_DIGIT_WHEEL_INNER)
                  .extrude(W_BUMP_WHEEL)
                  )
    angle_unit = ANGLE_BUMP_ALL
    angle_bump = ANGLE_BUMP
    bump = (cq.Workplane()
            .moveTo(R_DIGIT_WHEEL_OUTER * math.cos(angle_bump / 2),
                    R_DIGIT_WHEEL_OUTER * math.sin(angle_bump / 2))
            .radiusArc((R_DIGIT_WHEEL_OUTER * math.cos(-angle_bump / 2),
                        R_DIGIT_WHEEL_OUTER * math.sin(-angle_bump / 2)),
                       R_DIGIT_WHEEL_OUTER)
            .lineTo(R_BUMP_OUTER * math.cos(-angle_bump / 2),
                    R_BUMP_OUTER * math.sin(-angle_bump / 2))
            .radiusArc((R_BUMP_OUTER * math.cos(angle_bump / 2),
                        R_BUMP_OUTER * math.sin(angle_bump / 2)),
                       -R_BUMP_OUTER)
            .close()
            .extrude(W_BUMP_WHEEL)
            )

    for i in range(len(DIGITS)):
        angle = angle_unit / 2 + angle_unit * i
        bump_wheel = (bump_wheel
                      .union(bump
                             .rotate((0, 0, 0), (0, 0, 1),
                                     math.degrees(angle)))
                      )
    return bump_wheel


def __compute_side_interface() -> Tuple[int | float,
                                        int | float,
                                        int | float,
                                        int | float]:
    W = T_CASE_INTERFACE_MALE
    y_center = T_CASE / 2 - T_CASE_BUMP_WALL + W / 2
    x_top = -(H_COVER_INTERFACE + T_WALL_MIN)
    x_bot = -(H_CASE_HALF - T_CASE_FLOOR + W + TOL_TIGHT_FIT)
    x_center = (x_top + x_bot) / 2
    H = (x_top - x_bot) - 2 * TOL_TIGHT_FIT
    return x_center, y_center, H, W


def __compute_floor_interface() -> Tuple[int | float,
                                         int | float,
                                         int | float,
                                         int | float]:
    H = T_CASE_INTERFACE_MALE
    x_center = -(H_CASE_HALF - T_CASE_FLOOR + H / 2)
    y_center = 0
    y_left = T_CASE / 2 - T_CASE_BUMP_WALL + T_CASE_INTERFACE_MALE
    W = 2 * (y_left - y_center)
    return x_center, y_center, H, W


def make_case_bump_side() -> cq.Workplane:
    W_bump_side_inner = W_DIGIT_WHEEL_BUMP + 2 * TOL_MOVING
    H_spring_f_slot = H_SPRING_SLOT + 2 * TOL_TIGHT_FIT
    W_spring_f_slot = W_SPRING + 2 * TOL_TIGHT_FIT
    T_spring_f_slot = T_SPRING_SLOT + TOL_TIGHT_FIT
    y_spring_f_slot_top = (W_DIGIT_WHEEL_BUMP / 2 + TOL_MOVING
                           + W_spring_f_slot / 2)
    x_side_i_center, y_side_i_center, H_side_i, T_side_i = \
        __compute_side_interface()
    x_floor_i_center, y_floor_i_center, H_floor_i, T_floor_i = \
        __compute_floor_interface()

    case = (cq.Workplane()
            .circle(R_CASE_CORE_BUMP)
            .extrude(T_CASE_CORE_WALL)
            .moveTo(-H_CASE_HALF, 0)
            .rect(H_CASE_HALF, T_CASE, centered=(False, True))
            .extrude(T_CASE_CORE_WALL)
            # Make peg.
            .faces('>Z')
            .workplane()
            .tag('inner')
            .moveTo(X_PEG_CORE_CENTER, Y_PEG_CORE_CENTER)
            .circle(R_PEG)
            .mirrorX()
            .extrude(W_PEG)
            # Make floor.
            .moveTo(-H_CASE_HALF, 0)
            .rect(T_CASE_FLOOR, T_CASE, centered=(False, True))
            .extrude(W_bump_side_inner)
            # Cut spring slot.
            .faces('+X')
            .faces('<X')
            .workplane()
            .moveTo(0, W_DIGIT_WHEEL_BUMP / 2 + TOL_MOVING)
            .rect(H_spring_f_slot, W_spring_f_slot)
            .extrude(-T_spring_f_slot, combine='cut')
            .moveTo(0, y_spring_f_slot_top)
            .lineTo(H_spring_f_slot / 2, y_spring_f_slot_top)
            .lineTo(H_spring_f_slot / 2,
                    y_spring_f_slot_top
                    - H_spring_f_slot / 2 * math.tan(ANGLE_OVERHANG))
            .close()
            .moveTo(0, y_spring_f_slot_top)
            .lineTo(-H_spring_f_slot / 2, y_spring_f_slot_top)
            .lineTo(-H_spring_f_slot / 2,
                    y_spring_f_slot_top
                    - H_spring_f_slot / 2 * math.tan(ANGLE_OVERHANG))
            .close()
            .extrude(-T_spring_f_slot)
            # Reset workplane.
            .workplaneFromTagged('inner')
            # Make side walls.
            .moveTo(-H_CASE_HALF, T_CASE / 2 - T_CASE_BUMP_WALL)
            .rect(H_CASE_HALF, T_CASE_BUMP_WALL, centered=False)
            .mirrorX()
            .extrude(W_bump_side_inner)
            .faces('>Z')
            .workplane()
            # Make side wall interface.
            .moveTo(x_side_i_center, y_side_i_center)
            .rect(H_side_i, T_side_i)
            .mirrorX()
            .extrude(W_CASE_INTERFACE)
            .moveTo(x_floor_i_center, y_floor_i_center)
            .rect(H_floor_i, T_floor_i)
            .extrude(W_CASE_INTERFACE)
            # Fillet.
            .faces('<Z')
            .edges('not(<X)')
            .fillet(R_PRINTER_FILLET)
            )
    return case


def make_case_opposite() -> cq.Workplane:
    W_bump_side_inner = W_DIGIT_WHEEL_BUMP + 2 * TOL_MOVING
    W_inner = W_CASE_INNER - W_bump_side_inner
    x_side_i_center, y_side_i_center, H_side_i, T_side_i = \
        __compute_side_interface()
    x_floor_i_center, y_floor_i_center, H_floor_i, T_floor_i = \
        __compute_floor_interface()

    case = (cq.Workplane()
            .circle(R_CASE_CORE_DIGIT)
            .extrude(T_CASE_CORE_WALL)
            .moveTo(-H_CASE_HALF, 0)
            .rect(H_CASE_HALF, T_CASE, centered=(False, True))
            .extrude(T_CASE_CORE_WALL)
            # Make peg holes.
            .faces('>Z')
            .workplane()
            .tag('inner')
            .moveTo(X_PEG_CORE_CENTER, Y_PEG_CORE_CENTER)
            .circle(R_PEG)
            .mirrorX()
            .extrude(W_PEG)
            # Make floor.
            .moveTo(-H_CASE_HALF, 0)
            .rect(T_CASE_FLOOR, T_CASE, centered=(False, True))
            .extrude(W_inner)
            # Make side walls.
            .moveTo(-H_CASE_HALF, T_CASE / 2 - T_CASE_DIGIT_WALL)
            .rect(H_CASE_HALF, T_CASE_DIGIT_WALL, centered=False)
            .mirrorX()
            .extrude(W_inner)
            # Make side wall interface.
            .faces('>Z')
            .workplane()
            .moveTo(x_side_i_center, y_side_i_center)
            .rect(H_side_i + 2 * TOL_TIGHT_FIT, T_side_i + 2 * TOL_TIGHT_FIT)
            .mirrorX()
            .extrude(-W_CASE_INTERFACE, combine='cut')
            .moveTo(x_floor_i_center, y_floor_i_center)
            .rect(H_floor_i + 2 * TOL_TIGHT_FIT, T_floor_i + 2 * TOL_TIGHT_FIT)
            .extrude(-W_CASE_INTERFACE, combine='cut')
            # Fillet
            .faces('<Z')
            .edges('|X')
            .fillet(R_PRINTER_FILLET)
            )

    T_cover_i = T_WALL_MIN + TOL_TIGHT_FIT
    W_case_all = W_inner + T_CASE_CORE_WALL
    T_cover_i_hook = 2 * T_WALL_MIN + TOL_TIGHT_FIT
    H_cover_i_hook = T_WALL_MIN + 2 * TOL_TIGHT_FIT
    W_cover_i_hook = W_case_all - 2 * W_COVER_INTERFACE_WALL
    cover_tool_l = (cq.Workplane()
                    .moveTo(-H_COVER_INTERFACE / 2,
                            T_CASE / 2 - T_cover_i / 2)
                    .rect(H_COVER_INTERFACE, T_cover_i)
                    .extrude(W_case_all / 2, both=True)
                    .moveTo(-H_COVER_INTERFACE + H_cover_i_hook / 2,
                            T_CASE / 2 - T_cover_i_hook / 2)
                    .rect(H_cover_i_hook, T_cover_i_hook)
                    .extrude(W_cover_i_hook / 2, both=True)
                    .faces('+Z')
                    .faces('not(>Z)')
                    .edges('>X')
                    .chamfer((H_cover_i_hook - 0.1),
                             (H_cover_i_hook - 0.1) * math.tan(ANGLE_OVERHANG))
                    )
    cover_tool_r = (cq.Workplane()
                    .moveTo(-H_COVER_INTERFACE / 2,
                            -(T_CASE / 2 - T_cover_i / 2))
                    .rect(H_COVER_INTERFACE, T_cover_i)
                    .extrude(W_case_all / 2, both=True)
                    .moveTo(-H_COVER_INTERFACE + H_cover_i_hook / 2,
                            -(T_CASE / 2 - T_cover_i_hook / 2))
                    .rect(H_cover_i_hook, T_cover_i_hook)
                    .extrude(W_cover_i_hook / 2, both=True)
                    .faces('+Z')
                    .faces('not(>Z)')
                    .edges('>X')
                    .chamfer((H_cover_i_hook - 0.1) * math.tan(ANGLE_OVERHANG),
                             (H_cover_i_hook - 0.1))
                    )
    case = (case
            .cut(cover_tool_l.translate((0, 0, W_case_all / 2)))
            .cut(cover_tool_r.translate((0, 0, W_case_all / 2)))
            )
    return case


def make_digit_cover() -> cq.Workplane:
    W_bump_side_inner = W_DIGIT_WHEEL_BUMP + 2 * TOL_MOVING
    W_case = W_CASE_INNER - W_bump_side_inner + T_CASE_CORE_WALL
    W_cover = W_case - TOL_TIGHT_FIT

    R_digit_cover_inner = R_CASE_CORE_DIGIT + TOL_TIGHT_FIT
    R_digit_cover_outer = R_digit_cover_inner + T_COVER_WALL
    cover = (cq.Workplane()
             # Create semi-circle.
             .moveTo(0, R_digit_cover_inner)
             .radiusArc((0, -R_digit_cover_inner), R_digit_cover_inner)
             .lineTo(0, -R_digit_cover_outer)
             .radiusArc((0, R_digit_cover_outer), -R_digit_cover_outer)
             .close()
             .extrude(W_cover)
             # Provide tolerance at bottom.
             .moveTo(0, 0)
             .rect(2 * TOL_TIGHT_FIT, 2 * R_digit_cover_outer)
             .extrude(W_cover, combine='cut')
             )

    Z_bump_digit_center = (T_CASE_CORE_WALL + W_WHEEL_ONES_MIRROR
                           + 3 * TOL_MOVING + W_WHEEL_TENS)
    Z_mirror_digit_center = (T_CASE_CORE_WALL + TOL_MOVING +
                             W_WHEEL_ONES_MIRROR)
    W_digit = min(2 * W_DIGIT_CHARACTER + 2 * W_DIGIT_SPACING + 2 * TOL_MOVING,
                  2 * (W_cover - Z_bump_digit_center - T_WALL_MIN))
    angle_digit = math.radians(360 / len(DIGITS))
    digit_tool = (cq.Workplane()
                  .moveTo(0, 0)
                  .lineTo(R_digit_cover_outer * math.cos(angle_digit / 2),
                          R_digit_cover_outer * math.sin(angle_digit / 2))
                  .radiusArc(
                      (R_digit_cover_outer * math.cos(-angle_digit / 2),
                       R_digit_cover_outer * math.sin(-angle_digit / 2)),
                      R_digit_cover_outer)
                  .close()
                  .extrude(W_digit)
                  )
    cover = (cover
             # Cut digit slots.
             .cut(digit_tool
                  .translate((0, 0, Z_bump_digit_center - W_digit / 2))
                  .rotate((0, 0, 0), (0, 0, 1), math.degrees(ANGLE_VIEWING)))
             .cut(digit_tool
                  .translate((0, 0, Z_mirror_digit_center - W_digit / 2))
                  .rotate((0, 0, 0), (0, 0, 1), math.degrees(-ANGLE_VIEWING)))
             )
    # Create interface.
    X_inner = TOL_TIGHT_FIT
    Y_inner = math.sqrt(R_digit_cover_inner ** 2 - X_inner ** 2)
    cover = (cover
             .moveTo(X_inner, Y_inner)
             .rect(T_WALL_MIN, T_CASE / 2 - Y_inner, centered=False)
             .mirrorX()
             .extrude(W_cover)
             .moveTo(X_inner - H_COVER_INTERFACE,
                     T_CASE / 2 - T_WALL_MIN)
             .rect(H_COVER_INTERFACE, T_WALL_MIN, centered=False)
             .mirrorX()
             .extrude(W_cover)
             # Interface peg.
             .moveTo(X_inner - H_COVER_INTERFACE,
                     T_CASE / 2 - 2 * T_WALL_MIN)
             .rect(T_WALL_MIN, T_WALL_MIN, centered=False)
             .mirrorX()
             .extrude(W_cover - W_COVER_INTERFACE_WALL - TOL_TIGHT_FIT)
             .moveTo(X_inner - H_COVER_INTERFACE,
                     T_CASE / 2 - 2 * T_WALL_MIN)
             .rect(T_WALL_MIN, T_WALL_MIN, centered=False)
             .mirrorX()
             .extrude(W_COVER_INTERFACE_WALL + TOL_TIGHT_FIT, combine='cut')
             # Chamfer.
             .faces('+Z')
             .faces('not(>Z)')
             .faces('>Z')
             .edges('>X')
             .chamfer((T_WALL_MIN - 0.1),
                      (T_WALL_MIN - 0.1) * math.tan(ANGLE_OVERHANG))
             .faces('-Z')
             .faces('not(<Z)')
             .faces('<Z')
             .edges('|X')
             .edges('not(>Y or <Y)')
             .chamfer((T_WALL_MIN - 0.1),
                      (T_WALL_MIN - 0.1) * math.tan(ANGLE_OVERHANG))
             )
    return cover


if __name__ == '__cq_main__':
    import os
    from cadquery import exporters
    from scorecounter.parameters import DIR_EXPORT

    wheel_bump = _make_wheel_bump()

    spring = (make_spring()
              .translate((0, 0, TOL_MOVING + (W_DIGIT_WHEEL_BUMP - W_SPRING) / 2))
              )
    exporters.export(spring, os.path.join(DIR_EXPORT, 'spring.stl'))

    case_bump = (make_case_bump_side()
                 .translate((0, 0, -T_CASE_CORE_WALL))
                 )
    exporters.export(case_bump, os.path.join(DIR_EXPORT, 'case_bump.stl'))

    case_opposite = (make_case_opposite()
                     # .translate((0, 0, -T_CASE_CORE_WALL))
                     .translate((0, 0,
                                 -(W_CASE_INNER
                                   - (W_DIGIT_WHEEL_BUMP + 2 * TOL_MOVING)
                                   + T_CASE_CORE_WALL)))
                     .rotate((0, 0, 0), (1, 0, 0), 180)
                     .translate((0, 0,
                                 W_DIGIT_WHEEL_BUMP + 2 * TOL_MOVING)
                                )
                     )
    exporters.export(case_opposite,
                     os.path.join(DIR_EXPORT, 'case_opposite.stl'))

    digit_cover = (make_digit_cover()
                   .translate((0, 0,
                               -(W_CASE_INNER
                                 - (W_DIGIT_WHEEL_BUMP + 2 * TOL_MOVING)
                                 + T_CASE_CORE_WALL)))
                   .rotate((0, 0, 0), (1, 0, 0), 180)
                   .translate((0, 0,
                               W_DIGIT_WHEEL_BUMP + 2 * TOL_MOVING))
                   )
    exporters.export(digit_cover,
                     os.path.join(DIR_EXPORT, 'digit_cover.stl'))
