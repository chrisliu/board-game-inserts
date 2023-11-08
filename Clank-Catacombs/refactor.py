import abc
import cadquery as cq
import enum
import itertools
from dataclasses import dataclass
from typing import List, Optional, Type, Self

from cadquery.selectors import abstractmethod

'''
Constants
'''


class CuboidSpec:
    width: float = 0
    height: float = 0
    thickness: float = 0

    @classmethod
    @property
    def W(cls: Type[Self]) -> float:
        return cls.width

    @classmethod
    @property
    def H(cls: Type[Self]) -> float:
        return cls.height

    @classmethod
    @property
    def T(cls: Type[Self]) -> float:
        return cls.thickness


class StandardCard(CuboidSpec):
    width: float = 63
    height: float = 88
    thickness: float = 0.6


class DragonShieldSleeve(CuboidSpec):
    width: float = 66.4
    height: float = 92.2
    thickness: float = 0.6


class SquareMapTile(CuboidSpec):
    width: float = 100
    height: float = 100
    thickness: float = 1.6


class StartingMapTile(CuboidSpec):
    width: float = 100
    height: float = 200
    thickness: float = 1.6


class GameBoxInner(CuboidSpec):
    width: float = 291
    height: float = 291
    thickness: float = 78.5


class PlayerToken(CuboidSpec):
    width: float = 18
    height: float = 18
    thickness: float = 10.3


class ClankCube(CuboidSpec):
    width: float = 8.2
    height: float = 8.2
    thickness: float = 8.2


'''
Gridfinity Interface
'''


def rounded_rectangle(W: float, H: float, R: float) -> cq.Sketch:
    return cq.Sketch().rect(W, H).vertices().fillet(R)


@dataclass
class GridfinityProfile:
    T_top: float
    T_middle: float
    T_bottom: float
    R_top: float
    R_middle: float
    R_bottom: float

    @property
    def T_all(self: Self) -> float:
        return self.T_top + self.T_middle + self.T_bottom

    @property
    def T_wall(self: Self) -> float:
        return self.T_top + self.T_bottom


class Gridfinity:
    @classmethod
    def define_module_profile(cls: Type[Self],
                              T_top: float = 2.15,
                              T_middle: float = 1.8,
                              T_bottom: float = 0.8,
                              R_top: float = 7.5,
                              R_middle: float = 3.2,
                              R_bottom: float = 1.6,
                              ) -> GridfinityProfile:
        return GridfinityProfile(
            T_top=T_top, T_middle=T_middle, T_bottom=T_bottom,
            R_top=R_top, R_middle=R_middle, R_bottom=R_bottom)

    @classmethod
    def define_stacking_lip_profile(cls: Type[Self],
                                    T_top: float = 1.9,
                                    T_middle: float = 1.8,
                                    T_bottom: float = 0.7,
                                    R_top: float = 7.5,
                                    R_middle: float = 3.2,
                                    R_bottom: float = 1.6,
                                    ) -> GridfinityProfile:
        return GridfinityProfile(
            T_top=T_top, T_middle=T_middle, T_bottom=T_bottom,
            R_top=R_top, R_middle=R_middle, R_bottom=R_bottom)

    @classmethod
    def define_baseplate_profile(cls: Type[Self],
                                 T_top: float = 2.15,
                                 T_middle: float = 1.8,
                                 T_bottom: float = 0.7,
                                 R_top: float = 7.75,  # estimated
                                 R_middle: float = 3.45,  # estimated
                                 R_bottom: float = 1.85,  # estimated
                                 ) -> GridfinityProfile:
        return GridfinityProfile(
            T_top=T_top, T_middle=T_middle, T_bottom=T_bottom,
            R_top=R_top, R_middle=R_middle, R_bottom=R_bottom)

    @classmethod
    def make_positive(cls: Type[Self], profile: GridfinityProfile,
                      W_top: float, H_top: float
                      ) -> cq.Workplane:
        W_middle = W_top - 2 * profile.T_top
        W_bottom = W_top - 2 * profile.T_wall
        H_middle = H_top - 2 * profile.T_top
        H_bottom = H_top - 2 * profile.T_wall

        bottom_profile = rounded_rectangle(
            W_bottom, H_bottom, profile.R_bottom)
        middle_profile = rounded_rectangle(
            W_middle, H_middle, profile.R_middle)
        top_profile = rounded_rectangle(
            W_top, H_top, profile.R_top)
        bot_middle_loc = cq.Location(cq.Vector(0, 0, profile.T_bottom))
        middle_middle_loc = cq.Location(cq.Vector(0, 0, profile.T_middle))
        middle_top_loc = cq.Location(cq.Vector(0, 0, profile.T_top))

        positive_tool = (cq.Workplane()
                         .placeSketch(bottom_profile,
                                      middle_profile.moved(bot_middle_loc))
                         .loft()
                         .faces('>Z')
                         .workplane()
                         .placeSketch(middle_profile,
                                      middle_profile.moved(middle_middle_loc))
                         .loft()
                         .faces('>Z')
                         .workplane()
                         .placeSketch(middle_profile,
                                      top_profile.moved(middle_top_loc))
                         .loft()
                         )

        return positive_tool


class GridfinityBuilder:
    @classmethod
    def make_module_inner(cls: Type[Self],
                          W_inner: float, H_inner: float, T_inner: float,
                          stackable: bool = True,
                          module_profile: Optional[GridfinityProfile] = None,
                          stacking_lip_profile: Optional[GridfinityProfile] = None,
                          ) -> cq.Workplane:
        if module_profile is None:
            module_profile = Gridfinity.define_module_profile()
        if stacking_lip_profile is None:
            stacking_lip_profile = Gridfinity.define_stacking_lip_profile()
        W = W_inner + 2 * stacking_lip_profile.T_wall
        H = H_inner + 2 * stacking_lip_profile.T_wall
        T = T_inner + module_profile.T_all
        if stackable:
            T += stacking_lip_profile.T_all
        return cls.make_module(W, H, T, stackable, module_profile,
                               stacking_lip_profile)

    @classmethod
    def make_module(cls: Type[Self],
                    W: float, H: float, T: float,
                    stackable: bool = True,
                    module_profile: Optional[GridfinityProfile] = None,
                    stacking_lip_profile: Optional[GridfinityProfile] = None,
                    ) -> cq.Workplane:
        if module_profile is None:
            module_profile = Gridfinity.define_module_profile()
        if stacking_lip_profile is None:
            stacking_lip_profile = Gridfinity.define_stacking_lip_profile()

        module = Gridfinity.make_positive(module_profile, W, H)
        T_no_interface = T - module_profile.T_all
        if T_no_interface > 0:
            module = (module
                      .faces('>Z').wires().toPending()
                      .extrude(T_no_interface))
        if stackable:
            stack_tool = (Gridfinity.make_positive(stacking_lip_profile, W, H)
                          .translate((0, 0, T - stacking_lip_profile.T_all)))
            module = module.cut(stack_tool)

        return module


'''
Component elements.
'''


@dataclass
class BoundingBox:
    width: float
    height: float
    thickness: float = 0

    @property
    def W(self: Self) -> float:
        return self.width

    @property
    def H(self: Self) -> float:
        return self.height

    @property
    def T(self: Self) -> float:
        return self.thickness


class Component(abc.ABC):
    @abc.abstractproperty
    def obj(self: Self) -> Optional[cq.Workplane]:
        ...

    @abc.abstractproperty
    def negative(self: Self) -> Optional[cq.Workplane]:
        ...

    @abc.abstractproperty
    def BB(self: Self) -> BoundingBox:
        ...


class HAlignment(enum.Enum):
    LEFT = enum.auto()
    CENTER = enum.auto()
    RIGHT = enum.auto()


class VAlignment(enum.Enum):
    TOP = enum.auto()
    MIDDLE = enum.auto()
    BOTTOM = enum.auto()


class Stackable:
    def __init__(self: Self,
                 components: List[Component],
                 ha: HAlignment = HAlignment.CENTER,
                 va: VAlignment = VAlignment.MIDDLE,
                 reversed: bool = False
                 ) -> None:
        self._components = components
        self.__bb: Optional[BoundingBox] = None
        self._ha = ha
        self._va = va
        self._reversed = reversed

    @abc.abstractproperty
    def objs(self: Self) -> List[cq.Workplane]:
        ...

    @abc.abstractproperty
    def negatives(self: Self) -> List[cq.Workplane]:
        ...

    @property
    def BB(self: Self) -> BoundingBox:
        if self.__bb is None:
            self.__bb = self._compute_bb()
        return self.__bb

    @property
    def _prefix_Ts(self: Self) -> List[float]:
        Ts = [c.BB.T for c in self.components]
        cum_Ts = list(itertools.accumulate(Ts))
        if cum_Ts:
            return [0] + cum_Ts[:-1]
        return list()

    @property
    def components(self: Self) -> List[Component]:
        if self._reversed:
            return list(reversed(self._components))
        return self._components

    def insert(self: Self, idx: int, component: Component) -> None:
        self.__invalidate_cache()
        self._components.insert(idx, component)

    def append(self: Self, component: Component) -> None:
        self.__invalidate_cache()
        self._components.append(component)

    def pop(self: Self, idx: int = -1) -> Component:
        self.__invalidate_cache()
        return self._components.pop(idx)

    def __invalidate_cache(self: Self):
        self.__bb = None

    def _compute_bb(self: Self) -> BoundingBox:
        WHTs = list()
        for c in self._components:
            # Want to cache value (if component inefficiently recomputes its
            # bounding box every invokation).
            bb = c.BB
            WHTs.append((bb.W, bb.H, bb.T))
        Ws, Hs, Ts = zip(*WHTs)
        return BoundingBox(max(Ws), max(Hs), sum(Ts))

    def _x_offset(self: Self, component: Component) -> float:
        if self._ha == HAlignment.CENTER:
            return 0
        diff = self.BB.W - component.BB.W
        if self._ha == HAlignment.LEFT:
            return -diff
        elif self._ha == HAlignment.RIGHT:
            return diff
        raise RuntimeError

    def _y_offset(self: Self, component: Component) -> float:
        if self._va == VAlignment.MIDDLE:
            return 0
        diff = self.BB.H - component.BB.H
        if self._va == VAlignment.TOP:
            return diff
        elif self._va == VAlignment.BOTTOM:
            return -diff
        raise RuntimeError


class HStack(Stackable):
    def __init__(self: Self,
                 components: List[Component],
                 va: VAlignment = VAlignment.MIDDLE
                 ) -> None:
        super().__init__(components, va=va)

    @property
    def objs(self: Self) -> List[cq.Workplane]:
        raise NotImplementedError

    @property
    def negatives(self: Self) -> List[cq.Workplane]:
        raise NotImplementedError


class VStack(Stackable):
    def __init__(self: Self,
                 components: List[Component],
                 ha: HAlignment = HAlignment.CENTER
                 ) -> None:
        super().__init__(components, ha=ha)

    @property
    def objs(self: Self) -> List[cq.Workplane]:
        raise NotImplementedError

    @property
    def negatives(self: Self) -> List[cq.Workplane]:
        raise NotImplementedError


class ZStack(Stackable):
    def __init__(self: Self,
                 components: List[Component],
                 ha: HAlignment = HAlignment.CENTER,
                 va: VAlignment = VAlignment.MIDDLE
                 ) -> None:
        super().__init__(components, ha=ha, va=va, reversed=True)

    @property
    def objs(self: Self) -> List[cq.Workplane]:
        objects = list()
        for c, T in zip(self.components, self._prefix_Ts):
            obj = c.obj
            if obj is not None:
                objects.append(obj.translate((self._x_offset(c),
                                              self._y_offset(c),
                                              T)))
        return objects

    @property
    def negatives(self: Self) -> List[cq.Workplane]:
        negs = list()
        for c, T in zip(self.components, self._prefix_Ts):
            neg = c.negative
            if neg is not None:
                negs.append(neg.translate((self._x_offset(c),
                                           self._y_offset(c),
                                           T)))
        return negs


class CardHolder(Component):
    def __init__(self: Self,
                 card: Type[CuboidSpec],
                 T: float,
                 R: float,
                 tol: float = 0.75
                 ) -> None:
        W = card.W + 2 * tol
        H = card.H + 2 * tol
        self._bb = BoundingBox(W, H, T)
        self._R = R

    @property
    def obj(self: Self) -> Optional[cq.Workplane]:
        return None

    @property
    def negative(self: Self) -> Optional[cq.Workplane]:
        profile = (cq.Sketch()
                   .rect(self.BB.W, self.BB.H)
                   .vertices('>Y')
                   .fillet(self._R)
                   )
        return (cq.Workplane()
                .placeSketch(profile)
                .extrude(self.BB.T)
                )

    @property
    def BB(self: Self) -> BoundingBox:
        return self._bb


class ClankTray(Component):
    def __init__(self: Self,
                 W_outer: float,
                 H_outer: float,
                 T_all: float,
                 T_expose: float,
                 T_wall: float,
                 T_floor: float,
                 R: float,
                 H_pad: float = 2.5,
                 tol: float = 0.3
                 ) -> None:
        self._W_outer = W_outer
        self._H_outer = H_outer
        self._W_inner = W_outer - 2 * tol
        self._H_inner = H_outer - 2 * tol
        self._T_all = T_all
        self._T_inner = T_all - tol
        self._T_expose = T_expose
        self._T_wall = T_wall
        self._T_floor = T_floor
        self._H_pad = H_pad
        self._R = R
        assert self._T_expose <= self._T_inner

        self._bb = BoundingBox(self._W_outer, self._H_outer, self._T_all)

    @property
    def obj(self: Self) -> Optional[cq.Workplane]:
        W_tray_inner = self._W_inner - 2 * self._T_wall
        H_tray_inner = self._H_inner - 2 * self._T_wall
        T_tray_inner = self._T_inner - self._T_floor
        tray = (cq.Workplane()
                .rect(self._W_inner, self._H_inner)
                .extrude(self._T_inner)
                .faces('>Z')
                .placeSketch(rounded_rectangle(W_tray_inner,
                                               H_tray_inner,
                                               self._R))
                .extrude(-T_tray_inner, combine='cut')
                )

        # Topmost coordinate of cut.
        Y_expose = self._H_inner / 2 - self._H_pad
        T_cut = T_tray_inner - self._T_expose  # Thickenss of cut material.
        spline_coords = [
            (Y_expose, self._T_inner),
            (Y_expose - T_cut * 0.25, self._T_inner - T_cut * 0.1),
            (Y_expose - T_cut * 0.5, self._T_inner - T_cut * 0.5),
            (Y_expose - T_cut * 0.75, self._T_inner - T_cut * 0.9),
            (Y_expose - T_cut, self._T_inner - T_cut),
        ]

        tray = (tray
                .faces('>X')
                .workplane()
                .moveTo(0, self._T_inner)
                .lineTo(Y_expose, self._T_inner)
                .spline(spline_coords)
                .lineTo(0, self._T_inner - T_cut)
                .close()
                .mirrorY()
                .extrude(-self._H_inner, combine='cut')
                .faces('>Y')
                .workplane()
                .center(self._W_inner / 2, 0)
                .moveTo(W_tray_inner / 2, self._T_floor)
                .lineTo(W_tray_inner / 2 - self._T_expose, self._T_floor)
                .radiusArc((W_tray_inner / 2, self._T_floor + self._T_expose),
                           -self._T_expose)
                .close()
                .mirrorY()
                .extrude(-self._H_inner)
                )

        tray = (tray
                .faces('>Y or <Y')
                .edges('|Z')
                .fillet(self._R)
                .faces('+Z')
                .faces('not(>Z or <Z)')
                .edges('|Y')
                .fillet(self._T_wall / 2 * 0.6)
                )

        return tray

    @property
    def negative(self: Self) -> Optional[cq.Workplane]:
        return (cq.Workplane()
                .placeSketch(rounded_rectangle(self._W_outer,
                                               self._H_outer,
                                               self._R))
                .extrude(self._T_all)
                )

    @property
    def BB(self: Self) -> BoundingBox:
        return self._bb


card = DragonShieldSleeve
num_cards = 10
T_cards = (num_cards * card.T) * 1.5
module_profile = Gridfinity.define_module_profile()
stacking_lip_profile = Gridfinity.define_stacking_lip_profile()

T_wall = 0.8
ch = CardHolder(card, T_cards, stacking_lip_profile.R_bottom)
zs = ZStack([
    ClankTray(ch.BB.W + 2 * T_wall, ch.BB.H + T_wall,
              ClankCube.T + 2.5, ClankCube.T, T_wall, 0.8,
              stacking_lip_profile.R_bottom),
    ch,
], va=VAlignment.BOTTOM)

W = zs.BB.W
H = zs.BB.H
T = zs.BB.T
m = GridfinityBuilder.make_module_inner(
    W, H, T,
    module_profile=module_profile,
    stacking_lip_profile=stacking_lip_profile)

inner = (cq.Workplane()
         .placeSketch(rounded_rectangle(
             W, H, stacking_lip_profile.R_bottom))
         .extrude(T)
         )

offset = (0, 0, module_profile.T_all)
m = m.cut(inner.translate(offset))

for negative in zs.negatives:
    inner = inner.cut(negative)
m = m.union(inner.translate(offset))

# for obj in zs.objs:
#     show_object(obj.translate(offset))

T_module_wall = stacking_lip_profile.T_wall
W_pad = 10
m = (m
     .faces('+Z')
     .faces('<Z')
     .moveTo(0, -(H / 2 + T_module_wall) + T_module_wall / 2)
     .rect(W - 2 * W_pad, T_module_wall)
     .cutThruAll()
     )
show_object(m, 'module')
# show_object(inner, 'inner')
