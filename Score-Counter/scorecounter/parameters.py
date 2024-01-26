"""Score counter parameters.

This module is divided into user-defined constants and derived constants.
"""

import os
import math
from cq_gears import RingGear, SpurGear

'''User-defined constants'''

DIR_EXPORT = os.path.join(
    os.path.dirname(__file__),
    '..',
    'models')
os.makedirs(DIR_EXPORT, exist_ok=True)

# Printer specific tolerances.
TOL_MOVING = 0.13  # Tolerance for moving components.
TOL_TIGHT_FIT = 0.075  # Tolerance for a snug fit.
ANGLE_OVERHANG = math.radians(25)  # Printer overhang angle.
T_WALL_MIN = 0.8  # Minimum thickness of any walls.
T_FLOOR_MIN = 0.8  # Minimum thickness of any floors.
R_PRINTER_FILLET = 0.8  # Fillet with no overhang.

# General.
ANGLE_VIEWING = math.radians(90 - 38)

# Digit wheel.
DIGITS = [str(i) for i in range(10)]  # Digits shown on the wheel.
R_DIGIT_WHEEL_OUTER = 38 / 2  # Radius of the digit wheel.
T_DIGIT_WHEEL_RIM = 1.75  # Wall thickness from digit ring gear dedendum.
W_DIGIT_WHEEL_GEAR = 3  # Width of ring gear(s) in a digit wheel.
W_DIGIT_CHARACTER = 7.5  # Width allotted to a digit character.
W_DIGIT_SPACING = 2.25  # Width between digit characters (from allotted space).
W_DIGIT_WHEEL_BUMP = 12  # Width of the tactile bumps.
T_BUMP = 1.25  # Thickness of bump.
RATIO_BUMP = 0.7  # Ratio of bumps on circumference.
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

# Spring.
T_SPRING = 0.8  # Thickness of spring (controls stiffness).
T_SPRING_BUMP = 0.9  # How much does the spring need to be displaced.
T_SPRING_SLOT = 1.75  # Depth of spring slot.

# Case.
W_CASE_INTERFACE = 2  # Thickness of walls joining the case.
T_CASE_CORE_WALL = 1.2  # Wall supporting the core.
R_LOCK_HEAD = 15 / 2  # Lock bolt head radius.
R_LOCK_BODY = 10 / 2  # Lock bolt body radius.
T_LOCK_SLOT = 1.8  # Lock slot thickness.
# Minimum overlap between cases between lock begins.
T_CASE_LOCK_WALL_MIN = 1.2
T_LOCK_BOLT = 2  # Thickness of lock bolt.
H_LOCK_BOLT = 1.5  # Height of lock bolt.
ANGLE_LOCK_BOLT = math.radians(30)  # Angle of lock bolt.

# Cover.
T_COVER_WALL = 1


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
R_BUMP_OUTER = R_DIGIT_WHEEL_OUTER + T_BUMP
ANGLE_BUMP_ALL = math.radians(360 / len(DIGITS))
ANGLE_BUMP = RATIO_BUMP * ANGLE_BUMP_ALL

T_FONT = min(T_WALL_MIN,
             R_DIGIT_WHEEL_OUTER - R_DIGIT_WHEEL_INNER - T_WALL_MIN)
W_WHEEL_ONES = W_DIGIT_CHARACTER + W_DIGIT_SPACING + W_DIGIT_WHEEL_BUMP
W_WHEEL_TENS = (2 * W_DIGIT_CHARACTER + W_DIGIT_SPACING
                + max(T_WALL_MIN, W_DIGIT_SPACING / 2))
W_WHEEL_ONES_MIRROR = W_DIGIT_CHARACTER + W_DIGIT_SPACING

# Core configuration.
R_CORE_OUTER = R_DIGIT_WHEEL_INNER - TOL_MOVING
R_CORE_INNER = RG_DIGIT.ra - T_WALL_MIN - TOL_MOVING
R_PEG_CARRY = SG_CARRY.rd - T_WALL_MIN - TOL_MOVING
R_PEG_CARRY_SUPPORT = min(R_PEG_CARRY + T_WALL_MIN + TOL_TIGHT_FIT,
                          SG_CARRY.rd)
R_PEG_CORE = R_PEG + T_WALL_MIN + TOL_TIGHT_FIT
W_CORE_ONES = W_WHEEL_ONES - W_DIGIT_WHEEL_GEAR + 2 * TOL_MOVING
W_CORE_TENS = W_WHEEL_TENS + W_DIGIT_WHEEL_GEAR + 2 * TOL_MOVING
W_CORE_ONES_MIRROR = W_WHEEL_ONES_MIRROR + 2 * TOL_MOVING


# Compute center of peg s.t. its edge intersects with the inner wall
# and is x_mid distance from the center in the x direction.
__XMIN_CARRY = RG_DIGIT.r0 - SG_CARRY.r0 - SG_CARRY.ra
__XMAX_SHAFT = -(RG_DIGIT.r0 - SG_SHAFT.r0 - SG_SHAFT.ra)
assert __XMIN_CARRY >= __XMAX_SHAFT and "Carry and shaft gears intersect."
X_PEG_CORE_CENTER = (__XMIN_CARRY + __XMAX_SHAFT) / 2
THETA_PEG_CORE_CENTER = math.acos(
    X_PEG_CORE_CENTER / (R_CORE_INNER - R_PEG_CORE))
Y_PEG_CORE_CENTER = X_PEG_CORE_CENTER * math.tan(THETA_PEG_CORE_CENTER)

# Shaft gear.
R_SHAFT = SG_SHAFT.rd - T_WALL_MIN - TOL_MOVING
W_SHAFT_SQUARE = 2 * R_SHAFT / math.sqrt(2) - 2 * TOL_TIGHT_FIT
W_SHAFT = W_CORE_ONES + W_CORE_TENS + W_CORE_ONES_MIRROR

# Spring.
W_SPRING = min(0.9 * W_DIGIT_WHEEL_BUMP,
               W_DIGIT_WHEEL_BUMP - 2 * TOL_MOVING)
R_SPRING = 1.1 * R_BUMP_OUTER
ANGLE_SPRING = math.pi + ANGLE_BUMP_ALL

# Radius of spring's bump is defined by compute the chord (T_BUMP_CORNER) and
# the given spring displacement (T_SPRING_BUMP).
# Compute distance between the closest corners of two bumps.
__X_BUMP_CORNER = R_BUMP_OUTER * math.cos(ANGLE_BUMP_ALL - ANGLE_BUMP)
__Y_BUMP_CORNER = R_BUMP_OUTER * math.sin(ANGLE_BUMP_ALL - ANGLE_BUMP)
T_BUMP_CORNER = math.sqrt((__X_BUMP_CORNER - R_BUMP_OUTER) ** 2
                          + __Y_BUMP_CORNER ** 2)
R_SPRING_BUMP = ((T_SPRING_BUMP ** 2 + T_BUMP_CORNER ** 2 / 4)
                 / (2 * T_SPRING_BUMP))
H_SPRING_SLOT = T_BUMP_CORNER  # Size of spring slot.

__ANGLE_BUMP_SPACE = ANGLE_BUMP_ALL - ANGLE_BUMP
__X_BUMP_CORNER_1 = (R_BUMP_OUTER
                     * math.cos(ANGLE_SPRING - (__ANGLE_BUMP_SPACE / 2)))
__Y_BUMP_CORNER_1 = (R_BUMP_OUTER
                     * math.sin(ANGLE_SPRING - (__ANGLE_BUMP_SPACE / 2)))
__X_BUMP_CORNER_2 = (R_BUMP_OUTER
                     * math.cos(ANGLE_SPRING + (__ANGLE_BUMP_SPACE / 2)))
__Y_BUMP_CORNER_2 = (R_BUMP_OUTER
                     * math.sin(ANGLE_SPRING + (__ANGLE_BUMP_SPACE / 2)))
__X_BUMP_MIDPT = (__X_BUMP_CORNER_1 + __X_BUMP_CORNER_2) / 2
__Y_BUMP_MIDPT = (__Y_BUMP_CORNER_1 + __Y_BUMP_CORNER_2) / 2
__T_SPRING_BUMP_SAGITTA = R_SPRING_BUMP - T_SPRING_BUMP
X_SPRING_BUMP_CENTER = (__X_BUMP_MIDPT
                        + __T_SPRING_BUMP_SAGITTA * math.cos(ANGLE_SPRING))
Y_SPRING_BUMP_CENTER = (__Y_BUMP_MIDPT
                        + __T_SPRING_BUMP_SAGITTA * math.sin(ANGLE_SPRING))
X_SPRING_BUMP_TANGENT = (X_SPRING_BUMP_CENTER
                         + R_SPRING_BUMP * math.cos(ANGLE_SPRING))
Y_SPRING_BUMP_TANGENT = (Y_SPRING_BUMP_CENTER
                         + R_SPRING_BUMP * math.sin(ANGLE_SPRING))
__X_SPRING_CENTER = (X_SPRING_BUMP_TANGENT
                     + math.sqrt(R_SPRING ** 2 - Y_SPRING_BUMP_TANGENT ** 2))
X_SPRING_OUTER = __X_SPRING_CENTER - R_SPRING
Y_SPRING_SLOT = H_SPRING_SLOT / 2
X_SPRING_SLOT = (__X_SPRING_CENTER
                 - math.sqrt(R_SPRING ** 2 - Y_SPRING_SLOT ** 2))

# Case.
# Height of case from the center of core.
H_CASE_HALF = (abs(X_SPRING_SLOT) + T_SPRING_SLOT + T_FLOOR_MIN
               + 2 * TOL_TIGHT_FIT)
R_CASE_CORE_BUMP = RG_DIGIT.rd + TOL_MOVING
R_CASE_CORE_DIGIT = R_DIGIT_WHEEL_OUTER + 2 * TOL_MOVING
W_CASE_INNER = (W_CORE_ONES + W_CORE_TENS + W_CORE_ONES_MIRROR
                + 2 * TOL_TIGHT_FIT)
T_CASE_BUMP_WALL = 2 * (T_WALL_MIN + TOL_TIGHT_FIT)
T_CASE = 2 * (R_DIGIT_WHEEL_OUTER + T_BUMP + 2 * TOL_MOVING + T_CASE_BUMP_WALL)
T_CASE_DIGIT_WALL = T_CASE / 2 - R_CASE_CORE_DIGIT
T_CASE_FLOOR = H_CASE_HALF - abs(X_SPRING_OUTER)

T_CASE_INTERFACE_MALE = T_WALL_MIN

H_LOCK_HEAD = T_CASE_FLOOR - TOL_TIGHT_FIT - T_CASE_INTERFACE_MALE
H_LOCK_BODY = (H_CASE_HALF - R_DIGIT_WHEEL_OUTER - TOL_MOVING) - H_LOCK_HEAD
H_NUT_TOP = min(H_LOCK_BOLT + T_WALL_MIN,
                (H_LOCK_BODY - TOL_TIGHT_FIT) / 2)
H_NUT_BOT = (H_LOCK_BODY - TOL_TIGHT_FIT) - H_NUT_TOP
W_NUT = 2 * (R_LOCK_BODY + TOL_TIGHT_FIT + T_CASE_LOCK_WALL_MIN)
T_NUT = 2 * (R_LOCK_BODY + TOL_TIGHT_FIT + T_CASE_LOCK_WALL_MIN)
H_LOCK_SLOT = H_LOCK_HEAD - T_WALL_MIN
W_LOCK_SLOT = 2 * math.sqrt((R_LOCK_HEAD - 2 * T_WALL_MIN) ** 2
                            - (T_LOCK_SLOT / 2) ** 2)
R_LOCK_BOLT = R_LOCK_BODY + T_LOCK_BOLT

# Overlap between cover and case.
H_COVER_INTERFACE = 2 * T_WALL_MIN + 2 * TOL_TIGHT_FIT
W_COVER_INTERFACE_WALL = T_WALL_MIN

# Sanity checks.
assert N_TEETH_DIGIT % 2 == 0
assert N_TEETH_CARRY % 2 == 0
assert RG_DIGIT.rim_r == R_DIGIT_WHEEL_OUTER
assert RG_DIGIT.r0 >= (SG_CARRY.ra / 2 + SG_CARRY.r0 / 2
                       + SG_SHAFT.ra / 2 + SG_SHAFT.r0 / 2
                       + TOL_MOVING)
assert T_CASE_DIGIT_WALL >= 3 * T_WALL_MIN
