import cadquery as cq
from cadquery import exporters
from cq_gears import RingGear, SpurGear

tol_gear = 0.12
T_wall_min = 0.8
T_wall_housing = 0.9
T_floor = 0.6

T_gear = 5

R_peg = 7.8 / 2

rg = RingGear(module=2, teeth_number=20, width=T_gear,
              rim_width=2)
sg = SpurGear(module=2, teeth_number=8, width=T_gear)

print('RG rr', rg.r0)
print('RG rdd', rg.rd)
print('RG rdd', rg.rd)
print('RG rrim', rg.rim_r)

R_peg_actual = min(R_peg, sg.rb - T_wall_min - tol_gear)
R_peg_outer = R_peg_actual + tol_gear
X_peg = rg.r0 - sg.r0

ring_gear = (cq.Workplane()
             .gear(rg)
             )
spur_gear = (cq.Workplane()
             .gear(sg)
             .circle(R_peg_outer)
             .cutThruAll()
             .translate((X_peg, 0, 0))
             )
housing = (cq.Workplane()
           .circle(rg.rim_r + tol_gear + T_wall_housing)
           .extrude(max(T_gear / 2, T_gear - 2.5))
           .faces('<Z')
           .wires()
           .toPending()
           .extrude(-T_floor)
           .circle(rg.rim_r + tol_gear)
           .extrude(max(T_gear / 2, T_gear - 2.5), combine='cut')
           .moveTo(X_peg, 0)
           .circle(R_peg)
           .extrude(T_gear)
           )

exporters.export(ring_gear, 'ring_gear.stl')
exporters.export(spur_gear, 'spur_gear.stl')
exporters.export(housing, 'housing.stl')
