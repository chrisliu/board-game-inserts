import cadquery as cq
import math
from scorecounter.parameters import (
    W_SPRING, R_SPRING, ANGLE_SPRING, R_SPRING_BUMP,
    R_BUMP_OUTER, T_SPRING_BUMP, ANGLE_BUMP, ANGLE_BUMP_ALL, T_SPRING,
    H_SPRING_SLOT, T_SPRING_SLOT, ANGLE_OVERHANG,
    X_SPRING_BUMP_CENTER, Y_SPRING_BUMP_CENTER,
    X_SPRING_BUMP_TANGENT, Y_SPRING_BUMP_TANGENT, X_SPRING_SLOT, Y_SPRING_SLOT,
    X_SPRING_OUTER
)


def make_spring() -> cq.Workplane:
    '''
    # Midpoint between two bump edges.
    angle_space = ANGLE_BUMP_ALL - ANGLE_BUMP
    X_corner1 = R_BUMP_OUTER * math.cos(ANGLE_SPRING - (angle_space / 2))
    Y_corner1 = R_BUMP_OUTER * math.sin(ANGLE_SPRING - (angle_space / 2))
    X_corner2 = R_BUMP_OUTER * math.cos(ANGLE_SPRING + (angle_space / 2))
    Y_corner2 = R_BUMP_OUTER * math.sin(ANGLE_SPRING + (angle_space / 2))
    X_mid = (X_corner1 + X_corner2) / 2
    Y_mid = (Y_corner1 + Y_corner2) / 2
    # Center of spring bump.
    T_sagitta = R_SPRING_BUMP - T_SPRING_BUMP
    X_center = X_mid + T_sagitta * math.cos(ANGLE_SPRING)
    Y_center = Y_mid + T_sagitta * math.sin(ANGLE_SPRING)
    # Furthest point from ANGLE_SPRING (roughly tangent to spring angle)
    X_tangent = X_center + R_SPRING_BUMP * math.cos(ANGLE_SPRING)
    Y_tangent = Y_center + R_SPRING_BUMP * math.sin(ANGLE_SPRING)
    # Compute center of spring.
    X_spring_center = X_tangent + math.sqrt(R_SPRING ** 2 - Y_tangent ** 2)
    X_spring_outer = X_spring_center - R_SPRING
    Y_spring_slot = H_SPRING_SLOT / 2
    X_spring_slot = (X_spring_center
                     - math.sqrt(R_SPRING ** 2 - Y_spring_slot ** 2))
    '''

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
    W_BUMP_WHEEL = W_SPRING
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


if __name__ == '__cq_main__':
    wheel_bump = _make_wheel_bump()

    spring = make_spring()
