import math
import cadquery as cq
from scorecounter.parameters import W_CARRY_GEAR
from typing import Optional
from cq_gears import SpurGear
from scorecounter.parameters import (
    GEAR_MODULE, N_TEETH_CARRY, N_TEETH_SHAFT, W_CARRY_GEAR_MUTILATED
)


def make_shaft_gear(width: int | float) -> cq.Workplane:
    sg_shaft = SpurGear(module=GEAR_MODULE, teeth_number=N_TEETH_SHAFT,
                        width=width)
    shaft_gear: cq.Workplane = cq.Workplane().gear(sg_shaft)
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
    return carry_gear


if __name__ == '__cq_main__':
    from scorecounter.parameters import (
        W_DIGIT_WHEEL_GEAR, R_SHAFT, W_DIGIT_CHARACTER, W_DIGIT_SPACING,
        R_PEG_CARRY, TOL_MOVING
    )
    from cadquery import exporters

    '''
    shaft_gear = (make_shaft_gear(W_DIGIT_WHEEL_GEAR)
                  .faces('>Z')
                  .workplane()
                  .moveTo(0, 0)
                  .circle(R_SHAFT)
                  .extrude(W_DIGIT_CHARACTER + W_DIGIT_SPACING - W_DIGIT_WHEEL_GEAR)
                  )
    exporters.export(shaft_gear, 'shaft_gear.stl')
    '''

    carry_gear = (make_carry_gear(2 * W_DIGIT_WHEEL_GEAR)
                  .moveTo(0, 0)
                  .circle(R_PEG_CARRY + TOL_MOVING)
                  .cutThruAll()
                  )
    exporters.export(carry_gear, 'carry_gear.stl')
