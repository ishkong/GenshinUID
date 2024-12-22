import re
import json
from typing import List, Union, Optional, TypedDict, cast

import aiofiles
from gsuid_core.utils.api.minigg.models import CharacterTalents
from gsuid_core.utils.api.ambr.request import (
    get_ambr_char_data,
    get_ambr_weapon_data,
)

from .map.grow_curve import GROW_CURVE_LIST, WEAPON_GROW_CURVE
from ..utils.resource.RESOURCE_PATH import CHAR_DATA_PATH, WEAPON_DATA_PATH

PROP_MAP = {
    'FIGHT_PROP_BASE_HP': '基础生命值',
    'FIGHT_PROP_HP': '总生命值',
    'FIGHT_PROP_HP_PERCENT': '生命值',
    'FIGHT_PROP_BASE_ATTACK': '基础攻击力',
    'FIGHT_PROP_ATTACK': '总攻击力',
    'FIGHT_PROP_ATTACK_PERCENT': '攻击力',
    'FIGHT_PROP_BASE_DEFENSE': '基础防御力',
    'FIGHT_PROP_DEFENSE': '总防御力',
    'FIGHT_PROP_DEFENSE_PERCENT': '防御力',
    'FIGHT_PROP_CRITICAL': '暴击率',
    'FIGHT_PROP_ANTI_CRITICAL': '暴击抵抗',
    'FIGHT_PROP_CRITICAL_HURT': '暴击伤害',
    'FIGHT_PROP_CHARGE_EFFICIENCY': '元素充能效率',
    'FIGHT_PROP_HEAL_ADD': '治疗加成',
    'FIGHT_PROP_HEALED_ADD': '受治疗加成',
    'FIGHT_PROP_ELEMENT_MASTERY': '元素精通',
    'FIGHT_PROP_PHYSICAL_ADD_HURT': '物理伤害加成',
    'FIGHT_PROP_FIRE_ADD_HURT': '火元素伤害加成',
    'FIGHT_PROP_ELEC_ADD_HURT': '雷元素伤害加成',
    'FIGHT_PROP_WATER_ADD_HURT': '水元素伤害加成',
    'FIGHT_PROP_GRASS_ADD_HURT': '草元素伤害加成',
    'FIGHT_PROP_WIND_ADD_HURT': '风元素伤害加成',
    'FIGHT_PROP_ROCK_ADD_HURT': '岩元素伤害加成',
    'FIGHT_PROP_ICE_ADD_HURT': '冰元素伤害加成',
    'FIGHT_PROP_FIRE_SUB_HURT': '火元素抗性',
    'FIGHT_PROP_ELEC_SUB_HURT': '雷元素抗性',
    'FIGHT_PROP_WATER_SUB_HURT': '水元素抗性',
    'FIGHT_PROP_GRASS_SUB_HURT': '草元素抗性',
    'FIGHT_PROP_WIND_SUB_HURT': '风元素抗性',
    'FIGHT_PROP_ROCK_SUB_HURT': '岩元素抗性',
    'FIGHT_PROP_ICE_SUB_HURT': '冰元素抗性',
}

ELEMENT_MAP = {
    'Wind': '风',
    'Ice': '冰',
    'Grass': '草',
    'Water': '水',
    'Electric': '雷',
    'Rock': '岩',
    'Fire': '火',
}

TYPE_TO_INT = {
    'GROW_CURVE_HP_S4': 0,
    'GROW_CURVE_ATTACK_S4': 1,
    'GROW_CURVE_HP_S5': 2,
    'GROW_CURVE_ATTACK_S5': 3,
}

WEAPON_TYPE = {
    'WEAPON_SWORD_ONE_HAND': '单手剑',
    'WEAPON_CATALYST': '法器',
    'WEAPON_CLAYMORE': '双手剑',
    'WEAPON_BOW': '弓',
    'WEAPON_POLE': '长柄武器',
}


class ConvertWeapon(TypedDict):
    name: str
    weaponText: str
    rarity: str
    baseAtkValue: float
    mainStatText: str
    effectTemplateRaw: str
    effectName: str
    level: int
    ascension: int
    attack: float
    specialized: float
    r1: List[str]
    r2: List[str]
    r3: List[str]
    r4: List[str]
    r5: List[str]


class Image(TypedDict):
    nameicon: str


class ConvertCharacter(TypedDict):
    name: str
    weaponText: str
    rarity: str
    baseatk: float
    substatText: str
    effect: str
    effectname: str
    level: int
    ascension: int
    attack: float
    specialized: float
    title: str
    elementText: str
    images: Image
    hp: float
    defense: float


async def convert_exist_data_to_char(
    char_id: Union[str, int]
) -> ConvertCharacter:
    path = CHAR_DATA_PATH / f'{char_id}.json'
    if path.exists():
        async with aiofiles.open(path, 'r', encoding='utf-8') as f:
            raw_data = json.loads(await f.read())
    else:
        raw_data = await get_ambr_char_data(char_id)
        if raw_data is None:
            raise Exception('[AmbrData] 未找到该角色/数据无法下载!')
        # 保存
        async with aiofiles.open(path, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(raw_data))

    substatText = PROP_MAP[
        list(raw_data['upgrade']['promote'][-1]['addProps'].keys())[-1]
    ]
    sp = raw_data['upgrade']['promote'][-1]['addProps'][
        list(raw_data['upgrade']['promote'][-1]['addProps'].keys())[-1]
    ]

    if substatText == '暴击伤害':
        sp += 0.5
    elif substatText == '暴击率':
        sp += 0.05

    result = {
        'name': raw_data['name'],
        'title': raw_data['fetter']['title'],
        'rarity': raw_data['rank'],
        'weapontype': WEAPON_TYPE[raw_data['weaponType']],
        'elementText': ELEMENT_MAP[raw_data['element']],
        'element': ELEMENT_MAP[raw_data['element']],
        'images': {'namesideicon': raw_data['icon']},  # 暂时适配
        'substatText': substatText,
        'hp': raw_data['upgrade']['prop'][0]['initValue']
        * GROW_CURVE_LIST[89]['curveInfos'][
            TYPE_TO_INT[raw_data['upgrade']['prop'][0]['type']]
        ]['value']
        + raw_data['upgrade']['promote'][-1]['addProps']['FIGHT_PROP_BASE_HP'],
        'attack': raw_data['upgrade']['prop'][1]['initValue']
        * GROW_CURVE_LIST[89]['curveInfos'][
            TYPE_TO_INT[raw_data['upgrade']['prop'][1]['type']]
        ]['value']
        + raw_data['upgrade']['promote'][-1]['addProps'][
            'FIGHT_PROP_BASE_ATTACK'
        ],
        'defense': raw_data['upgrade']['prop'][2]['initValue']
        * GROW_CURVE_LIST[89]['curveInfos'][
            TYPE_TO_INT[raw_data['upgrade']['prop'][2]['type']]
        ]['value']
        + raw_data['upgrade']['promote'][-1]['addProps'][
            'FIGHT_PROP_BASE_DEFENSE'
        ],
        'specialized': sp,
    }
    return cast(ConvertCharacter, result)


async def convert_ambr_to_weapon(
    weapon_id: Union[int, str]
) -> Optional[ConvertWeapon]:
    path = WEAPON_DATA_PATH / f'{weapon_id}.json'
    if path.exists():
        async with aiofiles.open(path, 'r', encoding='utf-8') as f:
            raw_data = json.loads(await f.read())
    else:
        raw_data = await get_ambr_weapon_data(weapon_id)
        if raw_data is None:
            raise Exception('[AmbrData] 未找到该武器/数据无法下载!')
        # 保存
        async with aiofiles.open(path, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(raw_data))

    if raw_data['affix'] is None:
        effect = {
            'name': '无特效',
            'upgrade': {
                '0': '无特效',
                '1': '无特效',
                '2': '无特效',
                '3': '无特效',
                '4': '无特效',
            },
        }
    else:
        effect = list(raw_data['affix'].values())[0]
    effect_name = effect['name']
    effect_up = effect['upgrade']
    upgrade = raw_data['upgrade']
    baseatk = upgrade['prop'][0]['initValue']
    basesp = upgrade['prop'][-1]['initValue']
    if 'propType' in upgrade['prop'][1]:
        substat = PROP_MAP[upgrade['prop'][1]['propType']]
    else:
        substat = '无副词条'
    result = {
        'name': raw_data['name'],
        'weaponText': raw_data['type'],
        'rarity': str(raw_data['rank']),
        'baseAtkValue': baseatk,
        'mainStatText': substat,
        'effectName': effect_name,
        'level': 90,
        'ascension': 6,
    }
    index = 0
    for index, affix in enumerate(effect_up):
        effect_desc = re.sub(
            r'</?c[^\u4e00-\u9fa5/d]+>',
            '',
            effect_up[affix],
        )

        result[f'r{index+1}'] = {'description': effect_desc}
    else:
        if index != 0:
            result['effectTemplateRaw'] = result[f'r{index+1}']['description']
    atk_curve_type = upgrade['prop'][0]['type']
    sp_curve_type = upgrade['prop'][1]['type']
    atk_curve = WEAPON_GROW_CURVE['90']['curveInfos'][atk_curve_type]
    sp_curve = WEAPON_GROW_CURVE['90']['curveInfos'][sp_curve_type]
    atk_promoto = upgrade['promote'][-1]['addProps']['FIGHT_PROP_BASE_ATTACK']

    result['attack'] = atk_curve * baseatk + atk_promoto
    result['specialized'] = sp_curve * basesp

    return cast(ConvertWeapon, result)


async def convert_ambr_to_minigg(
    char_id: Union[str, int]
) -> Optional[ConvertCharacter]:
    return await convert_exist_data_to_char(char_id)


async def convert_ambr_to_talent(
    char_id: Union[str, int]
) -> Optional[CharacterTalents]:
    raw_data = await get_ambr_char_data(char_id)
    if raw_data is None:
        return
    talent_data = raw_data['talent']
    result = {}
    if '7' in talent_data:
        num = ['0', '1', '4']
    else:
        num = ['0', '1', '3']
    for index, i in enumerate(num):
        result[f'combat{index+1}'] = {
            'name': talent_data[i]['name'],
            'info': talent_data[i]['description'],
            'attributes': {
                'labels': [],
                'parameters': {},
            },
        }
        label_str = ''
        for label in talent_data[i]['promote']['1']['description']:
            if label:
                label_str += label
                result[f'combat{index+1}']['attributes']['labels'].append(
                    label
                )
        para_list = re.findall(r'{(param[0-9]+):', label_str)

        # 进行排序
        nums = [
            i
            for i in sorted(
                [
                    int(i[-2:]) if i[-2].isdigit() else int(i[-1])
                    for i in para_list
                ]
            )
        ]

        num_temp = 0
        new_nums = []
        for num in nums:
            if num != num_temp + 1:
                new_nums.append(num_temp + 1)
            num_temp = num
            new_nums.append(num)

        new_para_list = [f'param{i}' for i in new_nums]

        for ig, para in enumerate(new_para_list):
            for level in talent_data[i]['promote']:
                if (
                    para
                    not in result[f'combat{index+1}']['attributes'][
                        'parameters'
                    ]
                ):
                    result[f'combat{index+1}']['attributes']['parameters'][
                        para
                    ] = []
                result[f'combat{index+1}']['attributes']['parameters'][
                    para
                ].append(talent_data[i]['promote'][level]['params'][ig])
    return cast(CharacterTalents, result)
    return cast(CharacterTalents, result)
