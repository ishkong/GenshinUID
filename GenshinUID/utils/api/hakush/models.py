from typing import Dict, List, TypedDict


class RoleCombatEvent(TypedDict):
    begin: str
    end: str
    element: List[int]
    invite: List[int]
    buff: List[int]
    live_begin: str
    live_end: str


class BuffAvatar(TypedDict):
    Id: int
    Desc: str


class MonsterPreview(TypedDict):
    Id: int
    Hp: float
    Name: str
    Icon: str


class RoomConfig(TypedDict):
    MonsterLevel: int
    Title: str
    Desc: str
    MonsterPreviewList: List[MonsterPreview]


class DifficultyLevel(TypedDict):
    CanInvitePool: int
    BossMaxRoomNumber: int
    MinimumAvatarLevel: int
    Room: Dict[str, RoomConfig]
    CanInvitePoolAdd: int


class AvatarConfig(TypedDict):
    ElementList: List[int]
    InviteAvatarList: List[int]
    BuffAvatarList: List[BuffAvatar]


class ShopItem(TypedDict):
    Id: int
    Name: str
    Desc: str


class RoleCombatData(TypedDict):
    BeginTime: str
    EndTime: str
    AvatarConfig: AvatarConfig
    DifficultyConfig: Dict[str, DifficultyLevel]
    ShopConfig: List[ShopItem]
