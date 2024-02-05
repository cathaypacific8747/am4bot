from __future__ import annotations
import am4.utils.game
import typing
__all__ = ['Aircraft']
class Aircraft:
    class CargoConfig:
        class Algorithm:
            """
            Members:
            
              AUTO
            
              L
            
              H
            """
            AUTO: typing.ClassVar[Aircraft.CargoConfig.Algorithm]  # value = <Algorithm.AUTO: 0>
            H: typing.ClassVar[Aircraft.CargoConfig.Algorithm]  # value = <Algorithm.H: 2>
            L: typing.ClassVar[Aircraft.CargoConfig.Algorithm]  # value = <Algorithm.L: 1>
            __members__: typing.ClassVar[dict[str, Aircraft.CargoConfig.Algorithm]]  # value = {'AUTO': <Algorithm.AUTO: 0>, 'L': <Algorithm.L: 1>, 'H': <Algorithm.H: 2>}
            def __eq__(self, other: typing.Any) -> bool:
                ...
            def __getstate__(self) -> int:
                ...
            def __hash__(self) -> int:
                ...
            def __index__(self) -> int:
                ...
            def __init__(self, value: int) -> None:
                ...
            def __int__(self) -> int:
                ...
            def __ne__(self, other: typing.Any) -> bool:
                ...
            def __repr__(self) -> str:
                ...
            def __setstate__(self, state: int) -> None:
                ...
            def __str__(self) -> str:
                ...
            @property
            def name(self) -> str:
                ...
            @property
            def value(self) -> int:
                ...
        def __repr__(self) -> str:
            ...
        def to_dict(self) -> dict:
            ...
        @property
        def algorithm(self) -> Aircraft.CargoConfig.Algorithm:
            ...
        @property
        def h(self) -> int:
            ...
        @property
        def l(self) -> int:
            ...
        @property
        def valid(self) -> bool:
            ...
    class ParseResult:
        @property
        def co2_mod(self) -> bool:
            ...
        @property
        def fourx_mod(self) -> bool:
            ...
        @property
        def fuel_mod(self) -> bool:
            ...
        @property
        def priority(self) -> int:
            ...
        @property
        def search_str(self) -> str:
            ...
        @property
        def search_type(self) -> Aircraft.SearchType:
            ...
        @property
        def speed_mod(self) -> bool:
            ...
    class PaxConfig:
        class Algorithm:
            """
            Members:
            
              AUTO
            
              FJY
            
              FYJ
            
              JFY
            
              JYF
            
              YJF
            
              YFJ
            """
            AUTO: typing.ClassVar[Aircraft.PaxConfig.Algorithm]  # value = <Algorithm.AUTO: 0>
            FJY: typing.ClassVar[Aircraft.PaxConfig.Algorithm]  # value = <Algorithm.FJY: 1>
            FYJ: typing.ClassVar[Aircraft.PaxConfig.Algorithm]  # value = <Algorithm.FYJ: 2>
            JFY: typing.ClassVar[Aircraft.PaxConfig.Algorithm]  # value = <Algorithm.JFY: 3>
            JYF: typing.ClassVar[Aircraft.PaxConfig.Algorithm]  # value = <Algorithm.JYF: 4>
            YFJ: typing.ClassVar[Aircraft.PaxConfig.Algorithm]  # value = <Algorithm.YFJ: 6>
            YJF: typing.ClassVar[Aircraft.PaxConfig.Algorithm]  # value = <Algorithm.YJF: 5>
            __members__: typing.ClassVar[dict[str, Aircraft.PaxConfig.Algorithm]]  # value = {'AUTO': <Algorithm.AUTO: 0>, 'FJY': <Algorithm.FJY: 1>, 'FYJ': <Algorithm.FYJ: 2>, 'JFY': <Algorithm.JFY: 3>, 'JYF': <Algorithm.JYF: 4>, 'YJF': <Algorithm.YJF: 5>, 'YFJ': <Algorithm.YFJ: 6>}
            def __eq__(self, other: typing.Any) -> bool:
                ...
            def __getstate__(self) -> int:
                ...
            def __hash__(self) -> int:
                ...
            def __index__(self) -> int:
                ...
            def __init__(self, value: int) -> None:
                ...
            def __int__(self) -> int:
                ...
            def __ne__(self, other: typing.Any) -> bool:
                ...
            def __repr__(self) -> str:
                ...
            def __setstate__(self, state: int) -> None:
                ...
            def __str__(self) -> str:
                ...
            @property
            def name(self) -> str:
                ...
            @property
            def value(self) -> int:
                ...
        def __repr__(self) -> str:
            ...
        def to_dict(self) -> dict:
            ...
        @property
        def algorithm(self) -> Aircraft.PaxConfig.Algorithm:
            ...
        @property
        def f(self) -> int:
            ...
        @property
        def j(self) -> int:
            ...
        @property
        def valid(self) -> bool:
            ...
        @property
        def y(self) -> int:
            ...
    class SearchResult:
        def __init__(self, arg0: Aircraft, arg1: Aircraft.ParseResult) -> None:
            ...
        @property
        def ac(self) -> Aircraft:
            ...
        @property
        def parse_result(self) -> Aircraft.ParseResult:
            ...
    class SearchType:
        """
        Members:
        
          ALL
        
          ID
        
          SHORTNAME
        
          NAME
        """
        ALL: typing.ClassVar[Aircraft.SearchType]  # value = <SearchType.ALL: 0>
        ID: typing.ClassVar[Aircraft.SearchType]  # value = <SearchType.ID: 1>
        NAME: typing.ClassVar[Aircraft.SearchType]  # value = <SearchType.NAME: 3>
        SHORTNAME: typing.ClassVar[Aircraft.SearchType]  # value = <SearchType.SHORTNAME: 2>
        __members__: typing.ClassVar[dict[str, Aircraft.SearchType]]  # value = {'ALL': <SearchType.ALL: 0>, 'ID': <SearchType.ID: 1>, 'SHORTNAME': <SearchType.SHORTNAME: 2>, 'NAME': <SearchType.NAME: 3>}
        def __eq__(self, other: typing.Any) -> bool:
            ...
        def __getstate__(self) -> int:
            ...
        def __hash__(self) -> int:
            ...
        def __index__(self) -> int:
            ...
        def __init__(self, value: int) -> None:
            ...
        def __int__(self) -> int:
            ...
        def __ne__(self, other: typing.Any) -> bool:
            ...
        def __repr__(self) -> str:
            ...
        def __setstate__(self, state: int) -> None:
            ...
        def __str__(self) -> str:
            ...
        @property
        def name(self) -> str:
            ...
        @property
        def value(self) -> int:
            ...
    class Suggestion:
        def __init__(self, arg0: Aircraft, arg1: float) -> None:
            ...
        @property
        def ac(self) -> Aircraft:
            ...
        @property
        def score(self) -> float:
            ...
    class Type:
        """
        Members:
        
          PAX
        
          CARGO
        
          VIP
        """
        CARGO: typing.ClassVar[Aircraft.Type]  # value = <Type.CARGO: 1>
        PAX: typing.ClassVar[Aircraft.Type]  # value = <Type.PAX: 0>
        VIP: typing.ClassVar[Aircraft.Type]  # value = <Type.VIP: 2>
        __members__: typing.ClassVar[dict[str, Aircraft.Type]]  # value = {'PAX': <Type.PAX: 0>, 'CARGO': <Type.CARGO: 1>, 'VIP': <Type.VIP: 2>}
        def __eq__(self, other: typing.Any) -> bool:
            ...
        def __getstate__(self) -> int:
            ...
        def __hash__(self) -> int:
            ...
        def __index__(self) -> int:
            ...
        def __init__(self, value: int) -> None:
            ...
        def __int__(self) -> int:
            ...
        def __ne__(self, other: typing.Any) -> bool:
            ...
        def __repr__(self) -> str:
            ...
        def __setstate__(self, state: int) -> None:
            ...
        def __str__(self) -> str:
            ...
        @property
        def name(self) -> str:
            ...
        @property
        def value(self) -> int:
            ...
    @staticmethod
    def search(s: str, user: am4.utils.game.User = am4.utils.game.User.Default()) -> Aircraft.SearchResult:
        ...
    @staticmethod
    def suggest(s: Aircraft.ParseResult) -> list[Aircraft.Suggestion]:
        ...
    def __repr__(self) -> str:
        ...
    def to_dict(self) -> dict:
        ...
    @property
    def capacity(self) -> int:
        ...
    @property
    def ceil(self) -> int:
        ...
    @property
    def check_cost(self) -> int:
        ...
    @property
    def co2(self) -> float:
        ...
    @property
    def co2_mod(self) -> bool:
        ...
    @property
    def cost(self) -> int:
        ...
    @property
    def crew(self) -> int:
        ...
    @property
    def eid(self) -> int:
        ...
    @property
    def ename(self) -> str:
        ...
    @property
    def engineers(self) -> int:
        ...
    @property
    def fourx_mod(self) -> bool:
        ...
    @property
    def fuel(self) -> float:
        ...
    @property
    def fuel_mod(self) -> bool:
        ...
    @property
    def id(self) -> int:
        ...
    @property
    def img(self) -> str:
        ...
    @property
    def length(self) -> int:
        ...
    @property
    def maint(self) -> int:
        ...
    @property
    def manufacturer(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def pilots(self) -> int:
        ...
    @property
    def priority(self) -> int:
        ...
    @property
    def range(self) -> int:
        ...
    @property
    def rwy(self) -> int:
        ...
    @property
    def shortname(self) -> str:
        ...
    @property
    def speed(self) -> float:
        ...
    @property
    def speed_mod(self) -> bool:
        ...
    @property
    def technicians(self) -> int:
        ...
    @property
    def type(self) -> Aircraft.Type:
        ...
    @property
    def valid(self) -> bool:
        ...
    @property
    def wingspan(self) -> int:
        ...
