#ifndef DARK_POKEMON_H
#define DARK_POKEMON_H

#include <global.h>

enum darkPokemonWhere { place0, place1, place2, place3, place4, place5, place6 };

struct DarkPokemon {
    u8 unk0x0[60]; // 0x0, temp until struct figured out
    void setPlace(darkPokemonWhere, u8);
};

#endif
