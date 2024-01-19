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


cg = make_carry_gear(W_CARRY_GEAR)
