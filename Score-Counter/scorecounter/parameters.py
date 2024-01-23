"""Score counter parameters.

This module is divided into user-defined constants and derived constants.
"""

import math
from cq_gears import RingGear, SpurGear

'''User-defined constants'''

# Printer specific tolerances.
TOL_MOVING = 0.13  # Tolerance for moving components.
TOL_TIGHT_FIT = 0.075  # Tolerance for a snug fit.
ANGLE_OVERHANG = math.radians(25)  # Printer overhang angle.
T_WALL_MIN = 0.8  # Minimum thickness of any walls.

# General.
ANGLE_VIEWING = math.radians(90 - 38)

# Digit wheel.
DIGITS = [str(i) for i in range(10)]  # Digits shown on the wheel.
R_DIGIT_WHEEL_OUTER = 38 / 2  # Radius of the digit wheel.
T_DIGIT_WHEEL_RIM = 1.75  # Wall thickness from digit ring gear dedendum.
W_DIGIT_WHEEL_GEAR = 3  # Width of ring gear(s) in a digit wheel.
W_DIGIT_CHARACTER = 7.5  # Width allotted to a digit character.
W_DIGIT_SPACING = 2.25  # Width between digit characters (from allotted space).
FONT = 'monaco'  # Digit font.

# Core configuration.
T_CORE_WALL = 1.8

# General gear configuration.
N_TEETH_DIGIT = 20  # Should be 2 x len(DIGITS).
N_TEETH_CARRY = 6
N_TEETH_SHAFT = 11

R_PEG = 2.5
W_PEG = 1.5
T_PEG_MIN = 0.6
T_SHAFT_WALL = 1.1

'''Derived constants'''

# General gear configuration.
__D_DIGIT_RING_GEAR_DEDENDUM = (
    2 * R_DIGIT_WHEEL_OUTER) - 2 * T_DIGIT_WHEEL_RIM
GEAR_MODULE = __D_DIGIT_RING_GEAR_DEDENDUM / (N_TEETH_DIGIT + 2 * RingGear.kd)

# Carry gear specification.
W_CARRY_GEAR = 2 * W_DIGIT_WHEEL_GEAR
W_CARRY_GEAR_MUTILATED = W_DIGIT_WHEEL_GEAR / 2  # Width of removed gear teeth.

# Gears for gear-dependent calculations.
__PLACEHOLDER_WIDTH = 1
RG_DIGIT = RingGear(module=GEAR_MODULE,
                    teeth_number=N_TEETH_DIGIT,
                    width=__PLACEHOLDER_WIDTH,
                    rim_width=T_DIGIT_WHEEL_RIM)
SG_CARRY = SpurGear(module=GEAR_MODULE,
                    teeth_number=N_TEETH_CARRY,
                    width=__PLACEHOLDER_WIDTH)
SG_SHAFT = SpurGear(module=GEAR_MODULE,
                    teeth_number=N_TEETH_SHAFT,
                    width=__PLACEHOLDER_WIDTH)

# Digit wheel.
__SGC_TX, __SGC_TY, _ = SG_CARRY.t_tip_pts[0]
# Angle of tip of center tooth (positive)
__ANGLE_SGC_TIP = math.atan(__SGC_TY / __SGC_TX)
# Angle of the closest tip of the first tooth from center (positive)
__ANGLE_SGC_TIP2 = SG_CARRY.tau - __ANGLE_SGC_TIP
__X_SGC_TIP2 = ((RG_DIGIT.r0 - SG_CARRY.r0)
                + (SG_CARRY.ra * math.cos(__ANGLE_SGC_TIP2)))  # Global x
__Y_SGC_TIP2 = SG_CARRY.ra * math.sin(__ANGLE_SGC_TIP2)  # Global y
R_DIGIT_WHEEL_INNER = math.sqrt(__X_SGC_TIP2 ** 2 + __Y_SGC_TIP2 ** 2)

# Core configuration.
R_CORE_OUTER = R_DIGIT_WHEEL_INNER - TOL_MOVING
R_CORE_INNER = RG_DIGIT.ra - T_WALL_MIN - TOL_MOVING
R_PEG_CARRY = SG_CARRY.rd - T_WALL_MIN - TOL_MOVING
R_PEG_CARRY_SUPPORT = min(R_PEG_CARRY + T_WALL_MIN + TOL_TIGHT_FIT,
                          SG_CARRY.rd)
R_PEG_CORE = R_PEG + T_WALL_MIN + TOL_TIGHT_FIT

# Shaft gear.
R_SHAFT = SG_SHAFT.rd - T_WALL_MIN - TOL_MOVING
W_SHAFT_SQUARE = 2 * R_SHAFT / math.sqrt(2) - 2 * TOL_TIGHT_FIT

# Sanity checks.
assert N_TEETH_DIGIT % 2 == 0
assert N_TEETH_CARRY % 2 == 0
assert RG_DIGIT.rim_r == R_DIGIT_WHEEL_OUTER
assert RG_DIGIT.r0 >= (SG_CARRY.ra / 2 + SG_CARRY.r0 / 2
                       + SG_SHAFT.ra / 2 + SG_SHAFT.r0 / 2
                       + TOL_MOVING)
