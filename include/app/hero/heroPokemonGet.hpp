#ifndef HERO_POKEMON_GET_H
#define HERO_POKEMON_GET_H

#include <global.h>

struct HeroPokemonGetParam {
  u8 trainerSexID;         // 0x0
  u8 catchLevel;           // 0x1
  u16 pokemonDataID;       // 0x2
  u16 shadowPokemonDataID; // 0x4
  u16 friendLevel;         // 0x6
  u16 move1;               // 0x8
  u16 move2;               // 0xA
  u16 move3;               // 0xC
  u16 move4;               // 0xE
  u32 trainerRnd;          // 0x10
  char16 *trainerNamePtr;  // 0x14
  char16 *nicknamePtr;     // 0x18
  u32 catchFloorID;        // 0x1C
  u32 exp;                 // 0x20
};

#endif
