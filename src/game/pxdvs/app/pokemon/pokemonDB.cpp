#include <game/pxdvs/app/pokemon/pokemon.hpp>
#include <game/pxdvs/app/pokemon/pokemonBios.hpp>
#include <game/pxdvs/app/pokemon/pokemonDB.hpp>

extern "C" {

void pokemon_SetComboPartnerAll(Pokemon* poke, u8 data) {
    if (poke != nullptr)
    {
        poke->comboPartnerAll = data;
    }
}

void pokemon_SetPoolFriend(Pokemon* poke, u16 data) {
    if (poke != nullptr)
    {
        if (data > 0xFF) {
            data = 0xFF;
        }
        poke->setPoolFriendLevel(data);
    }
}
void pokemon_SetPoolExp(Pokemon* poke, u32 data) {
    if (poke != nullptr)
    {
        poke->setPoolExp(data);
    }
}
void pokemon_SetDarkpokemonDataId(Pokemon* poke, u16 data) {
    if (poke != nullptr)
    {
        poke->darkPokemonDataID = data;
    }
}
void pokemon_SetFightTrainerPokemonDataId(Pokemon* poke, u16 data) {
    if (poke != nullptr)
    {
        poke->fightTrainerPokemonDataId = data;
    }
}
void pokemon_SetAmari(Pokemon* poke, u16 data) {
    pokemonBiosSetAmari(poke, data);
}
void pokemon_SetPara1Amari(Pokemon* poke, u16 data) {
    pokemonBiosSetPara1Amari(poke, data);
}
void pokemon_SetMailId(Pokemon* poke, u8 data) {
    if (poke != nullptr)
    {
        poke->mailId = data;
    }
}
void pokemon_SetPcboxMark(Pokemon* poke, u8 data) {
    if (poke != nullptr)
    {
        poke->pcboxMark = data;
    }
}
void pokemon_SetFlagAmari(Pokemon* poke, u8 data) {
    if (poke != nullptr)
    {
        poke->flagAmari = data;
    }
}
void pokemon_SetFuseiFlag(Pokemon* poke, u8 data) {
    if (poke != nullptr)
    {
        poke->flags.bits.fusei = data;
    }
}
void pokemon_SetTamagoFlag(Pokemon* poke, u8 data) {
    if (poke != nullptr)
    {
        poke->flags.bits.tamago = data;
    }
}
void pokemon_SetPokerus(Pokemon* poke, u8 data) {
    if (poke != nullptr)
    {
        poke->pokerus = data;
    }
}
void pokemon_SetStrongMedal(Pokemon* poke, u8 data) {
    if (poke) {
        ExpandStatus* status = pokemonBiosGetExpandStatusPtr(poke, 1);
        if (status != nullptr) {
            status->strong = data;
        }
    }
}
void pokemon_SetCleverMedal(Pokemon* poke, u8 data) {
    if (poke) {
        ExpandStatus* status = pokemonBiosGetExpandStatusPtr(poke, 1);
        if (status != nullptr) {
            status->clever = data;
        }
    }
}
void pokemon_SetCuteMedal(Pokemon* poke, u8 data) {
    if (poke) {
        ExpandStatus* status = pokemonBiosGetExpandStatusPtr(poke, 1);
        if (status != nullptr) {
            status->cute = data;
        }
    }
}
void pokemon_SetBeautifulMedal(Pokemon* poke, u8 data) {
    if (poke) {
        ExpandStatus* status = pokemonBiosGetExpandStatusPtr(poke, 1);
        if (status != nullptr) {
            status->beautiful = data;
        }
    }
}
void pokemon_SetStyleMedal(Pokemon* poke, u8 data) {
    if (poke) {
        ExpandStatus* status = pokemonBiosGetExpandStatusPtr(poke, 1);
        if (status != nullptr) {
            status->style = data;
        }
    }
}
void pokemon_SetAmariRibbon(Pokemon* poke, u8 data) {
    if (poke) {
        Ribbon* ribbon = pokemonBiosGetRibbonPtr(poke);
        if (ribbon != nullptr) {
            ribbon->bits.amari = data;
        }
    }
}

void pokemon_SetWorldRibbon(Pokemon* poke, u8 data) {
    if (poke) {
        Ribbon* ribbon = pokemonBiosGetRibbonPtr(poke);
        if (ribbon != nullptr) {
            ribbon->bits.world = data;
        }
    }
}

void pokemon_SetEarthRibbon(Pokemon* poke, u8 data) {
    if (poke) {
        Ribbon* ribbon = pokemonBiosGetRibbonPtr(poke);
        if (ribbon != nullptr) {
            ribbon->bits.earth = data;
        }
    }
}

void pokemon_SetNationalRibbon(Pokemon* poke, u8 data) {
    if (poke) {
        Ribbon* ribbon = pokemonBiosGetRibbonPtr(poke);
        if (ribbon != nullptr) {
            ribbon->bits.national = data;
        }
    }
}

void pokemon_SetCountryRibbon(Pokemon* poke, u8 data) {
    if (poke) {
        Ribbon* ribbon = pokemonBiosGetRibbonPtr(poke);
        if (ribbon != nullptr) {
            ribbon->bits.country = data;
        }
    }
}

void pokemon_SetSkyRibbon(Pokemon* poke, u8 data) {
    if (poke) {
        Ribbon* ribbon = pokemonBiosGetRibbonPtr(poke);
        if (ribbon != nullptr) {
            ribbon->bits.sky = data;
        }
    }
}

void pokemon_SetLandRibbon(Pokemon* poke, u8 data) {
    if (poke) {
        Ribbon* ribbon = pokemonBiosGetRibbonPtr(poke);
        if (ribbon != nullptr) {
            ribbon->bits.land = data;
        }
    }
}

void pokemon_SetMarineRibbon(Pokemon* poke, u8 data) {
    if (poke) {
        Ribbon* ribbon = pokemonBiosGetRibbonPtr(poke);
        if (ribbon != nullptr) {
            ribbon->bits.marine = data;
        }
    }
}

void pokemon_SetGanbaRibbon(Pokemon* poke, u8 data) {
    if (poke) {
        Ribbon* ribbon = pokemonBiosGetRibbonPtr(poke);
        if (ribbon != nullptr) {
            ribbon->bits.ganba = data;
        }
    }
}

void pokemon_SetBromideRibbon(Pokemon* poke, u8 data) {
    if (poke) {
        Ribbon* ribbon = pokemonBiosGetRibbonPtr(poke);
        if (ribbon != nullptr) {
            ribbon->bits.bromide = data;
        }
    }
}

void pokemon_SetVictoryRibbon(Pokemon* poke, u8 data) {
    if (poke) {
        Ribbon* ribbon = pokemonBiosGetRibbonPtr(poke);
        if (ribbon != nullptr) {
            ribbon->bits.victory = data;
        }
    }
}

void pokemon_SetWinningRibbon(Pokemon* poke, u8 data) {
    if (poke) {
        Ribbon* ribbon = pokemonBiosGetRibbonPtr(poke);
        if (ribbon != nullptr) {
            ribbon->bits.winning = data;
        }
    }
}

void pokemon_SetChampRibbon(Pokemon* poke, u8 data) {
    if (poke) {
        Ribbon* ribbon = pokemonBiosGetRibbonPtr(poke);
        if (ribbon != nullptr) {
            ribbon->bits.champ = data;
        }
    }
}

void pokemon_SetFur(Pokemon* poke, u8 data) {
    if (poke != nullptr)
    {
        poke->fur = data;
    }
}
void pokemon_SetStrong(Pokemon* poke, u8 data) {
    if (poke) {
        ExpandStatus* status = pokemonBiosGetExpandStatusPtr(poke, 0);
        if (status != nullptr) {
            status->strong = data;
        }
    }
}
void pokemon_SetClever(Pokemon* poke, u8 data) {
    if (poke) {
        ExpandStatus* status = pokemonBiosGetExpandStatusPtr(poke, 0);
        if (status != nullptr) {
            status->clever = data;
        }
    }
}
void pokemon_SetCute(Pokemon* poke, u8 data) {
    if (poke) {
        ExpandStatus* status = pokemonBiosGetExpandStatusPtr(poke, 0);
        if (status != nullptr) {
            status->cute = data;
        }
    }
}
void pokemon_SetBeautiful(Pokemon* poke, u8 data) {
    if (poke) {
        ExpandStatus* status = pokemonBiosGetExpandStatusPtr(poke, 0);
        if (status != nullptr) {
            status->beautiful = data;
        }
    }
}
void pokemon_SetStyle(Pokemon* poke, u8 data) {
    if (poke) {
        ExpandStatus* status = pokemonBiosGetExpandStatusPtr(poke, 0);
        if (status != nullptr) {
            status->style = data;
        }
    }
}
void pokemon_SetFriend(Pokemon* poke, u16 data) {
    if (poke) {
        if (data > 0xFF) {
            data = 0xFF;
        }
        poke->friendLevel = data;
    }
}
void pokemon_SetNimblenessRnd(Pokemon* poke, u16 data) {
    pokemonBiosSetNimblenessRnd(poke, data);
}
void pokemon_SetSpeDefRnd(Pokemon* poke, u16 data) {
    pokemonBiosSetSpeDefRnd(poke, data);
}
void pokemon_SetSpeAtkRnd(Pokemon* poke, u16 data) {
    pokemonBiosSetSpeAtkRnd(poke, data);
}
void pokemon_SetPhyDefRnd(Pokemon* poke, u16 data) {
    pokemonBiosSetPhyDefRnd(poke, data);
}
void pokemon_SetPhyAtkRnd(Pokemon* poke, u16 data) {
    pokemonBiosSetPhyAtkRnd(poke, data);
}
void pokemon_SetMaxHpRnd(Pokemon* poke, u16 data) {
    pokemonBiosSetMaxHpRnd(poke, data);
}
void pokemon_SetNimblenessEffort(Pokemon* poke, u16 data) {
    pokemonBiosSetNimblenessEffort(poke, data);
}
void pokemon_SetSpeDefEffort(Pokemon* poke, u16 data) {
    pokemonBiosSetSpeDefEffort(poke, data);
}
void pokemon_SetSpeAtkEffort(Pokemon* poke, u16 data) {
    pokemonBiosSetSpeAtkEffort(poke, data);
}
void pokemon_SetPhyDefEffort(Pokemon* poke, u16 data) {
    pokemonBiosSetPhyDefEffort(poke, data);
}
void pokemon_SetPhyAtkEffort(Pokemon* poke, u16 data) {
    pokemonBiosSetPhyAtkEffort(poke, data);
}
void pokemon_SetMaxHpEffort(Pokemon* poke, u16 data) {
    pokemonBiosSetMaxHpEffort(poke, data);
}
void pokemon_SetNimbleness(Pokemon* poke, u16 data) {
    pokemonBiosSetNimbleness(poke, data);
}
void pokemon_SetSpeDef(Pokemon* poke, u16 data) {
    pokemonBiosSetSpeDef(poke, data);
}
void pokemon_SetSpeAtk(Pokemon* poke, u16 data) {
    pokemonBiosSetSpeAtk(poke, data);
}
void pokemon_SetPhyDef(Pokemon* poke, u16 data) {
    pokemonBiosSetPhyDef(poke, data);
}
void pokemon_SetPhyAtk(Pokemon* poke, u16 data) {
    pokemonBiosSetPhyAtk(poke, data);
}
void pokemon_SetMaxHp(Pokemon* poke, u16 data) {
    pokemonBiosSetMaxHp(poke, data);
}
void pokemon_SetHp(Pokemon* poke, u16 data) {
    if (poke) {
        poke->hp = data;
        u16 maxHp = pokemonBiosGetMaxHp(poke);
        if (maxHp < poke->hp) {
            poke->hp = maxHp;
        }
    }
}
void pokemon_SetItemDataId(Pokemon* poke, u16 data) {
    if (poke != nullptr)
    {
        poke->itemDataID = data;
    }
}

void pokemon_SetPokemonWazaPp(Pokemon* poke, u32 wazaNum, u8 data) {
    if (poke != nullptr)
    {
        PokemonWaza* waza = pokemonBiosGetPokemonWazaPtr(poke, wazaNum, 0);
        if (waza)
        {
            u8 maxPp = pokemonWazaGetMaxPP(poke, wazaNum);
            if (maxPp < data) {
                data = maxPp;
            }

            waza->pp = data;
        }
    }
}

void pokemon_SetPokemonWazaDataId(Pokemon* poke, u32 wazaNum, u16 data) {
    if (poke != nullptr)
    {
        PokemonWaza* waza = pokemonBiosGetPokemonWazaPtr(poke, wazaNum, 0);
        if (waza)
        {
            waza->dataId = data;
        }
    }
}
void pokemon_SetConditionAmari(Pokemon* poke, u32 data) {
    if (poke != nullptr)
    {
        poke->conditionAmari = data;
    }
}
void pokemon_SetLevel(Pokemon* poke, u8 data) {
    if (poke != nullptr)
    {
        if (data <= 100)
        {
            poke->level = data;
        }
    }
}
void pokemon_SetExp(Pokemon* poke, u32 data) {
    if (poke != nullptr)
    {
        poke->exp = data;
    }
}

void pokemon_SetCatchTrainerSex(Pokemon* poke, u8 data) {
    if (poke != nullptr)
    {
        poke->catchTrainerSex = data;
    }
}
void pokemon_SetCatchBallId(Pokemon* poke, u8 data) {
    if (poke != nullptr)
    {
        poke->catchBallId = data;
    }
}

void pokemon_SetCatchLevel(Pokemon* poke, u8 data) {
    if (poke != nullptr)
    {
        poke->catchLevel = data;
    }
}
void pokemon_SetCatchFloorId(Pokemon* poke, u16 data) {
    if (poke != nullptr)
    {
        poke->catchFloorId = data;
    }
}
void pokemon_SetRnd(Pokemon* poke, u32 data) {
    if (poke != nullptr)
    {
        poke->rnd = data;
    }
}
void pokemon_SetPokemonDataId(Pokemon* poke, u16 data) {
    if (poke != nullptr)
    {
        poke->dataID = data;
    }
}

bool pokemon_GetDarkFlag(Pokemon* poke) {
    if (poke == nullptr) {
        return false;
    }
    return poke->isDarkPokemon();
}
u8 pokemon_GetPoolFriend(Pokemon* poke) {
    if (poke == nullptr) {
        return 0;
    }
    return poke->getPoolFriendLevel();
}
u8 pokemon_GetPoolExp(Pokemon* poke) {
    if (poke == nullptr) {
        return 0;
    }
    return poke->getPoolExp();
}
u16 pokemon_GetDarkpokemonDataId(Pokemon* poke) {
    if (poke == nullptr) {
        return 0;
    }
    return poke->darkPokemonDataID;
}
u16 pokemon_GetFightTrainerPokemonDataId(Pokemon* poke) {
    if (poke == nullptr) {
        return 0;
    }
    return poke->fightTrainerPokemonDataId;
}
bool pokemon_GetFuseiFlag(Pokemon* poke) {
    if (poke == nullptr) {
        return 0;
    }
    return poke->flags.bits.fusei;
}

bool pokemon_GetTamagoFlag(Pokemon* poke) {
    if (poke == nullptr)
    {
        return 0;
    }
    return poke->flags.bits.tamago;
}
u8 pokemon_GetPokerus(Pokemon* poke) {
    if (poke == nullptr)
    {
        return 0;
    }
    return poke->pokerus;
}
u16 pokemon_GetFriend(Pokemon* poke) {
    if (poke == nullptr)
    {
        return 0;
    }
    return poke->friendLevel;
}
u8 pokemon_GetNimblenessRnd(Pokemon* poke) {
    return pokemonBiosGetNimblenessRnd(poke);
}
u8 pokemon_GetSpeDefRnd(Pokemon* poke) {
    return pokemonBiosGetSpeDefRnd(poke);
}
u8 pokemon_GetSpeAtkRnd(Pokemon* poke) {
    return pokemonBiosGetSpeAtkRnd(poke);
}
u8 pokemon_GetPhyDefRnd(Pokemon* poke) {
    return pokemonBiosGetPhyDefRnd(poke);
}
u8 pokemon_GetPhyAtkRnd(Pokemon* poke) {
    return pokemonBiosGetPhyAtkRnd(poke);
}
u8 pokemon_GetMaxHpRnd(Pokemon* poke) {
    return pokemonBiosGetMaxHpRnd(poke);
}
u16 pokemon_GetNimbleness(Pokemon* poke) {
    return pokemonBiosGetNimbleness(poke);
}
u16 pokemon_GetSpeDef(Pokemon* poke) {
    return pokemonBiosGetSpeDef(poke);
}
u16 pokemon_GetSpeAtk(Pokemon* poke) {
    return pokemonBiosGetSpeAtk(poke);
}
u16 pokemon_GetPhyDef(Pokemon* poke) {
    return pokemonBiosGetPhyDef(poke);
}
u16 pokemon_GetPhyAtk(Pokemon* poke) {
    return pokemonBiosGetPhyAtk(poke);
}
u16 pokemon_GetMaxHp(Pokemon* poke) {
    return pokemonBiosGetMaxHp(poke);
}
u16 pokemon_GetHp(Pokemon* poke) {
    if (poke == 0) {
        return 0;
    }
    return poke->hp;
}
u16 pokemon_GetItemDataId(Pokemon* poke) {
    if (poke == 0) {
        return 0;
    }
    return poke->itemDataID;
}
u8 pokemon_GetPokemonWazaPpCount(Pokemon* poke, u32 wazaNum) {
    if (poke == nullptr) {
        return 0;
    }

    PokemonWaza* waza = pokemonBiosGetPokemonWazaPtr(poke, wazaNum, 1);
    if (waza == nullptr) {
        return 0;
    }
    return waza->ppCount;
}
u8 pokemon_GetPokemonWazaPp(Pokemon* poke, u32 wazaNum) {
    if (poke == nullptr) {
        return 0;
    }

    PokemonWaza* waza = pokemonBiosGetPokemonWazaPtr(poke, wazaNum, 1);
    if (waza == nullptr) {
        return 0;
    }
    return waza->pp;
}
u16 pokemon_GetPokemonWazaDataId(Pokemon* poke, u32 wazaNum) {
    if (poke == nullptr) {
        return 0;
    }

    PokemonWaza* waza = pokemonBiosGetPokemonWazaPtr(poke, wazaNum, 1);
    if (waza == nullptr) {
        return 0;
    }
    return waza->dataId;
}
u16 pokemon_GetHinsi(Pokemon* poke) {
    if (poke == nullptr) {
        return 0;
    }
    return pokemon_GetHp(poke) == 0;
}
u8 pokemon_GetLevel(Pokemon* poke) {
    if (poke == nullptr)
    {
        return 0;
    }
    return poke->level;
}
u32 pokemon_GetExp(Pokemon* poke) {
    if (poke == nullptr)
    {
        return 0;
    }
    return poke->exp;
}
char* pokemon_GetNicknamePtr(Pokemon* poke) {
    if (poke == nullptr)
    {
        return nullptr;
    }
    return &poke->nickname[0];
}
u32 pokemon_GetCatchTrainerRnd(Pokemon* poke) {
    if (poke == nullptr)
    {
        return 0;
    }
    return poke->catchTrainerRnd;
}
u8 pokemon_GetCatchBallId(Pokemon* poke) {
    if (poke == nullptr)
    {
        return 0;
    }
    return poke->catchBallId;
}
Attest* pokemon_GetAttest(Pokemon* poke) {
    if (poke == nullptr)
    {
        return nullptr;
    }
    return &poke->attest;
}
u32 pokemon_GetRnd(Pokemon* poke) {
    if (poke == nullptr)
    {
        return 0;
    }
    return poke->rnd;
}
u32 pokemon_GetPokemonDataId(Pokemon* poke) {
    if (poke == nullptr)
    {
        return 0;
    }
    return poke->dataID;
}


}
