#ifndef POKEMON_H
#define POKEMON_H

#include <global.h>
#include <game/pxdvs/app/pokemon/darkPokemon.hpp>

class Hero;

struct Pokemon {
  s16 dataID; // 0x0
  s8 unk[194]; // temporary until Pokemon struct is figured out
  u16 getPokemonDataId() const;
  s32 * getAttest();
  bool isFuseiFlag() const;
  bool isHatena() const;
  Pokemon * getPokemon(Hero *, s32);
  DarkPokemon * getDarkPokemon();
  bool checkValid() const;
  void clear();
  bool isLegend() const;
  void initCondition();
};

extern "C" void pokemonSetDp(u32, f32);

extern "C" void pokemonSetTokuseiFlag(Pokemon* , u32);
extern "C" void pokemonInitAry(u32, u16);
extern "C" void pokemonInit(u32);
extern "C" void pokemonInitDarkPokemon(u32);
extern "C" void pokemonInitJoutai(Pokemon*);
extern "C" void pokemonWazaInitAry(Pokemon* ,u32);
extern "C" void pokemonWazaInit(Pokemon* ,u32);
extern "C" u32 pokemonCheckRare(Pokemon*);
extern "C" void pokemonGrowBasisStatus(Pokemon*);
extern "C" void pokemonResetBasisStatus(Pokemon*);
extern "C" void pokemonSetStatus(Pokemon*, u32, u16, u32, u32);
extern "C" u16 pokemonGetStatus(Pokemon*, u32, u16, u32);
extern "C" u32 pokemonAdjustValueBySeikaku(u32, u16, u32);
static u8 _pokemonGetSeikaku(Pokemon*);
extern "C" u8 pokemonGetSeikakuAsRnd(u32);
static u8 _pokemonGetHinsi(Pokemon*);
static void _pokemonSetLevelBasisStatus(Pokemon*, u8);
static u16 _pokemonGetLevelOneStatus(Pokemon*, u8, u16, u16, u16, u16, long);
extern "C" u16 pokemonCreateBasisStatus(u16, u8, u16, u8, s32);
static u8 _pokemonGetNowExpToLevel(Pokemon*);
extern "C" u8 pokemonGetExpToLevel(u8, u32);
static int _pokemonGetLevelToExp(u8, u8);
extern "C" int pokemonCheckRareRnd(unsigned long, unsigned long);
static int _pokemonCheckRare(unsigned long, unsigned long);

#endif
