import cadquery as cq
import math
from cadquery import exporters
from cq_gears import RingGear, SpurGear

tol_moving = 0.13  # Tolerance for moving components
tol_tight_fit = 0.1
angle_overhang = math.radians(25)

'''
TODO
1. Number ring.
  a) Digits (0-9).
  b) Carry ring gear (2 teeth).
  c) Carry ring gear (from lower place).
2. Core peg.
  a) Carry ring peg.
  b) Shaft hole.
3. Carry spur gear.
  a) Rotates and locks at 90 deg (since we have 20 teeth).
4. Gear shaft.
  a) Transfers rotation to sister wheel set.
'''

# T_digit =

# Single Digit ring.

digits = list(range(10))  # 0-9

W_digit_ring_all = 10
W_digit_gear = W_digit_ring_all / 3  # Height of gear teeth within this ring.
W_digit_ring_core = W_digit_ring_all - 2 * W_digit_gear
W_carry_gear_catch = W_digit_gear / 2

R_digit_ring_outer = 45 / 2
R_digit_ring_outer = 38 / 2

N_digit_gear_teeth = len(digits) * 2
T_digit_gear_wall = 1.75  # Distance between outer ring wall and gear addendum.
module_digit_gear = ((2 * R_digit_ring_outer - 2 * T_digit_gear_wall)
                     / (N_digit_gear_teeth + 2 * SpurGear.kd))

digit_rg = RingGear(module=module_digit_gear, teeth_number=N_digit_gear_teeth,
                    width=W_digit_gear, rim_width=T_digit_gear_wall)


font = 'Monaco'  # Hardcoded
H_font = W_digit_ring_all / 3 * 5  # Hardcoded for Monaco font
assert font == 'Monaco'

N_carry_teeth = 6
assert N_carry_teeth % 2 == 0
carry_sg = SpurGear(module=module_digit_gear, teeth_number=N_carry_teeth,
                    width=W_digit_gear - tol_moving)
tx, ty, _ = carry_sg.t_tip_pts[0]
angle_tip = math.atan(ty/tx)
angle_2tip = carry_sg.tau - angle_tip
carry_2x = (digit_rg.r0 - carry_sg.r0) + (carry_sg.ra * math.cos(angle_2tip))
carry_2y = carry_sg.ra * math.sin(angle_2tip)

# No tolerance since other components are loose.
R_digit_ring_inner = math.sqrt(carry_2x ** 2 + carry_2y ** 2)

digit_gear: cq.Workplane = cq.Workplane().gear(digit_rg)

# Construct core ring with overhang protection.
W_overhang_loft = (digit_rg.rd - R_digit_ring_inner) * math.tan(angle_overhang)
digit_overhang_rg = RingGear(module=module_digit_gear,
                             teeth_number=N_digit_gear_teeth,
                             width=W_overhang_loft,
                             rim_width=T_digit_gear_wall)
digit_overhang_gear: cq.Workplane = cq.Workplane().gear(digit_overhang_rg)
digit_overhang_gear = (digit_overhang_gear
                       .circle(R_digit_ring_inner)
                       .cutThruAll())
digit_ring = (digit_gear
              .faces('>Z')
              .workplane()
              .circle(R_digit_ring_outer)
              .circle(R_digit_ring_inner)
              .extrude(W_digit_ring_core)
              .circle(digit_rg.rd)
              .workplane(offset=W_overhang_loft)
              .circle(R_digit_ring_inner)
              .loft(combine='cut')
              .union(digit_overhang_gear.translate((0, 0, W_digit_gear)))
              )

# Construct core ring with carry gear.
# assert R_digit_ring_inner >= digit_rg.r0
# assert T_digit_gear_wall > 1  # Hacky magic number.
rx, ry, _ = digit_rg.t_root_pts[0]
angle_root = math.atan(ry/rx)
carry_involute_tool = (cq.Workplane()
                       .moveTo(0, 0)
                       .lineTo(R_digit_ring_outer * math.cos(angle_root),
                               R_digit_ring_outer * math.sin(angle_root))
                       .lineTo(R_digit_ring_outer * math.cos(-angle_root),
                               R_digit_ring_outer * math.sin(-angle_root))
                       .close()
                       .extrude(W_digit_gear)
                       .cut(digit_gear)
                       )
tx, ty, _ = digit_rg.t_lflank_pts[-1]
angle_tip = math.atan(ty/tx)
angle_2tip = digit_rg.tau - angle_tip
carry_teeth_tool = (cq.Workplane()
                    .moveTo(0, 0)
                    .lineTo(R_digit_ring_outer,
                            R_digit_ring_outer * math.tan(angle_2tip))
                    .lineTo(R_digit_ring_outer,
                            R_digit_ring_outer * math.tan(-angle_2tip))
                    .close()
                    .extrude(W_digit_gear)
                    )
carry_teeth = digit_gear.intersect(carry_teeth_tool)
digit_ring_carry = (cq.Workplane()
                    .circle(R_digit_ring_outer)
                    .circle(R_digit_ring_inner)
                    .extrude(W_digit_gear)
                    .faces('>Z')
                    # Cut carry catch lip.
                    .workplane()
                    .circle(digit_rg.rd)
                    .extrude(-W_carry_gear_catch, combine='cut')
                    # Add ring gear profile.
                    .union(carry_teeth)
                    .moveTo(0, 0)
                    .circle(R_digit_ring_inner)
                    .cutThruAll()
                    # Cut entire tooth involute.
                    .cut(carry_involute_tool)
                    )

digit_ring = (digit_ring
              .union(digit_ring_carry.translate(
                  (0, 0, W_digit_gear + W_digit_ring_core)))
              )

show_object(digit_ring)
exporters.export(digit_ring, 'digit_ring.stl')


R_peg = min(6.25 / 2, carry_sg.rd - 0.8 - tol_moving)
carry_gear: cq.Workplane = cq.Workplane().gear(carry_sg)
carry_gear = (carry_gear
              .moveTo(0, 0)
              .circle(R_peg + tol_moving)
              .cutThruAll()
              # .translate((digit_rg.r0 - carry_sg.r0, 0, 0))
              )
carry_cut_tool = (cq.Workplane()
                  .moveTo(carry_sg.rd * math.cos(carry_sg.tau / 2),
                          carry_sg.rd * math.sin(carry_sg.tau / 2))
                  .radiusArc(
                      (carry_sg.rd * math.cos(-carry_sg.tau / 2),
                       carry_sg.rd * math.sin(-carry_sg.tau / 2)),
                      carry_sg.rd)
                  .lineTo(carry_sg.ra,
                          -carry_sg.ra * math.tan(carry_sg.tau / 2))
                  .lineTo(carry_sg.ra,
                          carry_sg.ra * math.tan(carry_sg.tau / 2))
                  .close()
                  .extrude(W_carry_gear_catch - tol_moving)
                  .translate(
                      (0, 0,
                       carry_sg.width - (W_carry_gear_catch - tol_moving)))
                  )

for i in range(N_carry_teeth // 2):
    carry_gear = (carry_gear
                  .cut(carry_cut_tool
                       .rotate((0, 0, 0), (0, 0, 1),
                               360 / N_carry_teeth * 2 * i))
                  )
carry_gear = carry_gear.translate((digit_rg.r0 - carry_sg.r0, 0, 0))
show_object(carry_gear)
exporters.export(carry_gear, 'carry_gear.stl')

sample_core = (cq.Workplane()
               .circle(R_digit_ring_outer + tol_moving + 0.8)
               .circle(R_digit_ring_outer + tol_moving)
               .extrude(W_digit_gear)
               .moveTo(digit_rg.r0 - carry_sg.r0)
               .circle(R_peg)
               .extrude(W_digit_gear)
               .moveTo(0, 0)
               .circle(R_digit_ring_outer + tol_moving + 0.8)
               .extrude(-0.3)
               )
show_object(sample_core)
exporters.export(sample_core, 'sample_core.stl')

print(digit_rg.r0 - carry_sg.r0 - carry_sg.ra)
