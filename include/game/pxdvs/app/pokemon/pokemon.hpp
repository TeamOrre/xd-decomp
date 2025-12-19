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
};

#endif
