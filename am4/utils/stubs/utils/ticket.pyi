from __future__ import annotations
import am4.utils.game
__all__ = ['CargoTicket', 'PaxTicket', 'VIPTicket']
class CargoTicket:
    @staticmethod
    def from_optimal(distance: float, game_mode: am4.utils.game.User.GameMode = am4.utils.game.User.GameMode.EASY) -> PaxTicket:
        ...
    def __repr__(self) -> str:
        ...
    def to_dict(self) -> dict:
        ...
    @property
    def h(self) -> float:
        ...
    @property
    def l(self) -> float:
        ...
class PaxTicket:
    @staticmethod
    def from_optimal(distance: float, game_mode: am4.utils.game.User.GameMode = am4.utils.game.User.GameMode.EASY) -> PaxTicket:
        ...
    def __repr__(self) -> str:
        ...
    def to_dict(self) -> dict:
        ...
    @property
    def f(self) -> int:
        ...
    @property
    def j(self) -> int:
        ...
    @property
    def y(self) -> int:
        ...
class VIPTicket:
    @staticmethod
    def from_optimal(distance: float) -> VIPTicket:
        ...
    def __repr__(self) -> str:
        ...
    def to_dict(self) -> dict:
        ...
    @property
    def f(self) -> int:
        ...
    @property
    def j(self) -> int:
        ...
    @property
    def y(self) -> int:
        ...
