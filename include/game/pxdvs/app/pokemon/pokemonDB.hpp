#ifndef POKEMONDB_H
#define POKEMONDB_H

#include <global.h>
#include <game/pxdvs/app/pokemon/pokemon.hpp>

extern "C" void pokemon_SetPoolFriend(Pokemon*, u16);
extern "C" void pokemon_SetPoolExp(Pokemon*, u32);
extern "C" void pokemon_SetDarkpokemonDataId(Pokemon*, u16);
extern "C" void pokemon_SetTokuseiFlag(Pokemon* , u32);
extern "C" void pokemon_SetMaxHp(Pokemon*, u16);
extern "C" void pokemon_SetHp(Pokemon*, u16);
extern "C" void pokemon_SetPokemonWazaPpCount(Pokemon*, u32, u8);
extern "C" void pokemon_SetPokemonWazaPp(Pokemon*, u32, u8);
extern "C" void pokemon_SetPokemonWazaDataId(Pokemon*, u32, u16);
extern "C" void pokemon_SetLevel(Pokemon*, u8);
extern "C" void pokemon_SetExp(Pokemon*, u32);
extern "C" u8 pokemon_GetNowExpToLevel(Pokemon*);
extern "C" u32 pokemon_GetSeikaku(Pokemon*);
extern "C" u16 pokemon_GetMaxHp(Pokemon*);
extern "C" u16 pokemon_GetHp(Pokemon*);
extern "C" u32 pokemon_GetExp(Pokemon*);
extern "C" u32 pokemon_GetCatchTrainerRnd(Pokemon*);
extern "C" u32 pokemon_GetRnd(Pokemon*);
extern "C" u32 pokemon_GetPokemonDataId(Pokemon*);
extern "C" u32 pokemonDB_GetTokuseiDataId(u32, u32);
extern "C" u8 pokemonDB_GetGrowDataId(u32);
#endif
