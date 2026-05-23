#include <game/pxdvs/app/pokemon/pokemon.hpp>
#include <game/pxdvs/app/pokemon/pokemonBios.hpp>
#include <game/pxdvs/app/pokemon/pokemonDB.hpp>

//TODO this is simply a first pass through this class many things might need changed and or cleaned up even if the function already matches
const f32 zero = 0.0f;
const f32 oneHundred = 100.0f;
const f32 nintyNinePointNine = 99.9f;
const f32 eighty = 80.0f;
const f32 sixty = 60.0f;
const f32 fourty = 40.0f;
const f32 twenty = 20.0f;
const f64 unkDouble = 4503599627370496.0;
const f32 negOne = -1.0f;
const f32 negThree = -3.0f;
const f64 unkDouble2 = 4503601774854144.0;

void pokemonSetTokuseiFlag(Pokemon* param_1, u32 param_2)
{
  u32 uVar1;
  u8 cVar2;
  
  if (param_1 != 0) {
    uVar1 = pokemon_GetPokemonDataId(param_1);
    cVar2 = pokemonDB_GetTokuseiDataId(uVar1,1);
    if (cVar2 == '\0') {
      param_2 = 0;
    }
    pokemon_SetTokuseiFlag(param_1,param_2);
  }
  return;
}

void pokemonInitAry(u32 param_1, u16 param_2)
{  
  if (param_1 != 0) {
    for (u16 uVar1 = 0; uVar1 < param_2; uVar1++) {
      pokemonInit(param_1 + uVar1 * 0xc4);
    }
  }
}

//TODO later needs a decent number of functions defined
//void pokemonInit(u32 param_1){}

//sdata2 mismatch 99.76% match as a result
void pokemonInitDarkPokemon(u32 param_1)
{
	pokemon_SetDarkpokemonDataId(param_1,0);
	pokemonSetDp(param_1, negOne);
	pokemon_SetPoolExp(param_1,0);
	pokemon_SetPoolFriend(param_1,0);
}

void pokemonInitJoutai(Pokemon* param_1)
{
	param_1->initCondition();
}

void pokemonWazaInitAry(Pokemon* param_1, u32 param_2)
{
  u32 uVar1;
  
  if (param_1 != 0) {
    for (uVar1 = 0; (uVar1 & 0xffff) < (param_2 & 0xffff); uVar1 = uVar1 + 1) {
      pokemonWazaInit(param_1,uVar1);
    }
  }
}

void pokemonWazaInit(Pokemon* param_1, u32 param_2)
{
  if (param_1 != 0) {
    pokemon_SetPokemonWazaDataId(param_1,param_2,0);
    pokemon_SetPokemonWazaPp(param_1,param_2,0);
    pokemon_SetPokemonWazaPpCount(param_1,param_2,0);
  }
}

u32 pokemonCheckRare(Pokemon* param_1)
{
  u32 uVar1;
  u32 uVar2;
  
  if (param_1 == 0) {
    uVar1 = 0;
  }
  else {
    uVar1 = pokemon_GetCatchTrainerRnd(param_1);
    uVar2 = pokemon_GetRnd(param_1);
    uVar1 = _pokemonCheckRare(uVar1,uVar2);
  }
  return uVar1;
}

void pokemonGrowBasisStatus(Pokemon* param_1)
{
  if (param_1 != 0) {
    pokemon_SetExp(param_1);
    pokemonResetBasisStatus(param_1);
  }
}

void pokemonResetBasisStatus(Pokemon* param_1)
{
  u8 uVar1;
  
  if (param_1 != 0) {
    uVar1 = pokemon_GetNowExpToLevel(param_1);
    _pokemonSetLevelBasisStatus(param_1, uVar1);
  }
}

//TODO much later needs a ton of functions defined
//void pokemonSetStatus(Pokemon*, u32, u16, u32, u32){}

//TODO much later needs a ton of functions defined
//u16 pokemonGetStatus(Pokemon*, u32, u16, u32){}

u32 pokemonAdjustValueBySeikaku(u32 param1, u16 param2, u32 baseValue)
{
    PokemonSeikakuDataBios* seikakuPtr;
    PokemonSeikakuRateBios* ratePtr;
    u32 rateId;
    s32 result;
    u32 stat;
    u32 kake;
    u32 waru;

    seikakuPtr = pokemonSeikakuDataBiosGetPtr(param1);

    if (seikakuPtr == NULL)
        return baseValue;

    stat = param2;

    switch (stat)
    {
		case 0x88:
			rateId = pokemonSeikakuDataBiosGetPhyAtkRateDataId(seikakuPtr);
			break;
		case 0x89:
			rateId = pokemonSeikakuDataBiosGetPhyDefRateDataId(seikakuPtr);
			break;
		case 0x8A:
			rateId = pokemonSeikakuDataBiosGetSpeAtkRateDataId(seikakuPtr);
			break;
		case 0x8B:
			rateId = pokemonSeikakuDataBiosGetSpeDefRateDataId(seikakuPtr);
			break;
		case 0x8C:
			rateId = pokemonSeikakuDataBiosGetNimblenessRateDataId(seikakuPtr);
			break;
		default:
			return baseValue;
    }

    ratePtr = pokemonSeikakuRateDataBiosGetPtr(rateId);
    if (ratePtr == NULL)
        return 0;

    kake = pokemonSeikakuRateDataBiosGetKake(ratePtr);
    waru = pokemonSeikakuRateDataBiosGetWaru(ratePtr);

    result = baseValue * (u8)kake;

    if ((u8)waru != 0)
        result = result / (u8)waru;

    return result;
}

u8 _pokemonGetSeikaku(Pokemon* a)
{
	return pokemonGetSeikakuAsRnd(pokemon_GetRnd(a));
}

u8 pokemonGetSeikakuAsRnd(u32 a)
{
  return a % 25;
}

u8 _pokemonGetHinsi(Pokemon* a)
{
	return pokemon_GetHp(a) == 0;
}

void _pokemonSetLevelBasisStatus(Pokemon* a , u8 b)
{
	u16 sVar1;
	u32 sVar2;
	u16 sVar3;
	u16 sVar4;
	u16 sVar5;
  
	sVar2 = pokemon_GetPokemonDataId(a);
	sVar3 = pokemon_GetMaxHp(a);
	pokemon_SetLevel(a,b);
	if ((u16)sVar2 == 0x12f) 
	{
		sVar4 = 1;
		pokemon_SetMaxHp(a,1);
	}
	else 
	{
		sVar4 = _pokemonGetLevelOneStatus(a,b,0x87,3,0x93,0x8d,(b & 0xff) + 10);
	}
	_pokemonGetLevelOneStatus(a,b,0x88,4,0x94,0x8e,5);
	_pokemonGetLevelOneStatus(a,b,0x89,5,0x95,0x8f,5);
	_pokemonGetLevelOneStatus(a,b,0x8c,8,0x98,0x92,5);
	_pokemonGetLevelOneStatus(a,b,0x8a,6,0x96,0x90,5);
	_pokemonGetLevelOneStatus(a,b,0x8b,7,0x97,0x91,5);
	sVar5 = pokemon_GetHp(a);
	if ((sVar5 != 0) || (sVar3 == 0)) 
	{
		sVar1 = 1;
		if ((u16)sVar2 != 0x12f) 
		{
			sVar1 = sVar5 + (sVar4 - sVar3);
		}
		pokemon_SetHp(a,sVar1);
	}
}

u16 _pokemonGetLevelOneStatus(Pokemon* a, u8 b, u16 c, u16 d, u16 e, u16 f, long g)
{
	u32 h;
	u32 k;
	u32 i;
	
    h = pokemon_GetPokemonDataId(a);
	i = pokemon_GetSeikaku(a);
	
    h  = pokemonGetStatus(0, h, d, 0);
    k = pokemonGetStatus(a, 0, e, 0);
    u32 l = pokemonGetStatus(a, 0, f, 0);

    h = pokemonCreateBasisStatus(h, k, l, b, g);
    h = pokemonAdjustValueBySeikaku(i, c, h);

    pokemonSetStatus(a, 0, c, 0, h);

    return h;
}

u16 pokemonCreateBasisStatus(u16 a, u8 b, u16 c, u8 d, s32 e)
{
	return e + (s32)((d & 0xff) * ((b & 0xff) + (a & 0xffff) * 2 + (c >> 2 & 0x3fff))) / 100 & 0xffff;
}

u8 _pokemonGetNowExpToLevel(Pokemon* a)
{
  u8 growDataId;
  u32 exp;
  
  growDataId = pokemonDB_GetGrowDataId(pokemon_GetPokemonDataId(a));
  exp = pokemon_GetExp(a);
  return pokemonGetExpToLevel(growDataId,exp);
}

u8 pokemonGetExpToLevel(u8 a, u32 b)
{
    s32 level = 0;
	
    PokemonGrowDataBios* ptr = pokemonGrowDataBiosGetPtr(a);
    if (!ptr)
        return level;

    for (level = 1; level < 101; level++) {
        if (pokemonGrowDataBiosGetExp(ptr, level) > b)
            break;
    }

    return (level - 1);
}

static int _pokemonGetLevelToExp(u8 a, u8 b)
{
	PokemonGrowDataBios* ptr = pokemonGrowDataBiosGetPtr(a);
    if (ptr == 0) {
        return 0;
    }
    return pokemonGrowDataBiosGetExp(ptr, b);
}

int pokemonCheckRareRnd(unsigned long a, unsigned long b)
{
	return _pokemonCheckRare(a, b);
}

static int _pokemonCheckRare(unsigned long a, unsigned long b)
{
	int x = 8 > (a >> 0x10 ^ a & 0xFFFF ^ b >> 0x10 ^ b & 0xFFFF);
	int y = x ? -1 : 0;
	return -y;
}
