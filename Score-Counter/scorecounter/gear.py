import math
import cadquery as cq
from typing import Optional
from cq_gears import SpurGear
from scorecounter.parameters import (
    GEAR_MODULE, N_TEETH_CARRY, N_TEETH_SHAFT, W_CARRY_GEAR_MUTILATED,
    W_SHAFT_SQUARE, TOL_TIGHT_FIT, W_SHAFT, R_SHAFT, ANGLE_OVERHANG,
    W_DIGIT_WHEEL_GEAR, R_PEG_CARRY, TOL_MOVING
)


def make_shaft_gear(width: int | float) -> cq.Workplane:
    sg_shaft = SpurGear(module=GEAR_MODULE, teeth_number=N_TEETH_SHAFT,
                        width=width)
    shaft_gear: cq.Workplane = cq.Workplane().gear(sg_shaft)
    shaft_gear = (shaft_gear
                  .moveTo(0, 0)
                  .rect(W_SHAFT_SQUARE + TOL_TIGHT_FIT,
                        W_SHAFT_SQUARE + TOL_TIGHT_FIT)
                  .extrude(width, combine='cut')
                  )
    return shaft_gear


def make_carry_gear(width: int | float,
                    mutilated_width: Optional[int | float] = None
                    ) -> cq.Workplane:
    if mutilated_width is None:
        mutilated_width = W_CARRY_GEAR_MUTILATED
    sg_carry = SpurGear(module=GEAR_MODULE, teeth_number=N_TEETH_CARRY,
                        width=width)
    carry_gear: cq.Workplane = cq.Workplane().gear(sg_carry)

    cut_tool = (cq.Workplane()
                .moveTo(sg_carry.rd * math.cos(sg_carry.tau / 2),
                        sg_carry.rd * math.sin(sg_carry.tau / 2))
                .radiusArc(
                    (sg_carry.rd * math.cos(-sg_carry.tau / 2),
                     sg_carry.rd * math.sin(-sg_carry.tau / 2)),
                    sg_carry.rd)
                .lineTo(sg_carry.ra,
                        sg_carry.ra * math.tan(-sg_carry.tau / 2))
                .lineTo(sg_carry.ra,
                        sg_carry.ra * math.tan(sg_carry.tau / 2))
                .close()
                .extrude(mutilated_width)
                .translate((0, 0, width - mutilated_width))
                )
    for i in range(N_TEETH_CARRY // 2):
        carry_gear = (carry_gear
                      .cut(cut_tool.rotate((0, 0, 0), (0, 0, 1),
                                           2 * i * 360 / N_TEETH_CARRY))
                      )
    carry_gear = (carry_gear
                  .moveTo(0, 0)
                  .circle(R_PEG_CARRY + TOL_MOVING)
                  .extrude(width, combine='cut')
                  )
    return carry_gear


def make_shaft() -> cq.Workplane:
    W_overhang = (R_SHAFT - W_SHAFT_SQUARE / 2) * math.tan(ANGLE_OVERHANG)
    shaft = (cq.Workplane()
             # Create gear square connector.
             .rect(W_SHAFT_SQUARE, W_SHAFT_SQUARE)
             .extrude(W_DIGIT_WHEEL_GEAR)
             # Create printer-friendly loft.
             .faces('>Z')
             .wires()
             .toPending()
             .workplane(offset=W_overhang)
             .circle(R_SHAFT)
             .loft()
             # Create circular shaft.
             .faces('>Z')
             .workplane()
             .circle(R_SHAFT)
             .extrude(W_SHAFT - 2 * (W_DIGIT_WHEEL_GEAR + W_overhang))
             # Create printer-friendly loft (mirrored).
             .faces('>Z')
             .wires()
             .toPending()
             .workplane(offset=W_overhang)
             .rect(W_SHAFT_SQUARE, W_SHAFT_SQUARE)
             .loft()
             # Create gear square connector.
             .faces('>Z')
             .workplane()
             .rect(W_SHAFT_SQUARE, W_SHAFT_SQUARE)
             .extrude(W_DIGIT_WHEEL_GEAR)
             )
    return shaft


if __name__ == '__cq_main__':
    import os
    from scorecounter.parameters import DIR_EXPORT
    from cadquery import exporters

    gear_shaft = make_shaft_gear(W_DIGIT_WHEEL_GEAR)
    exporters.export(gear_shaft, os.path.join(DIR_EXPORT, 'gear_shaft.stl'))

    shaft = make_shaft()
    exporters.export(shaft, os.path.join(DIR_EXPORT, 'shaft.stl'))

    gear_carry = make_carry_gear(2 * W_DIGIT_WHEEL_GEAR)
    exporters.export(gear_carry, os.path.join(DIR_EXPORT, 'gear_carry.stl'))
