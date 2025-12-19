#include <game/pxdvs/app/hero/hero.hpp>
#include <game/pxdvs/app/hero/heroMove.hpp>
#include <game/pxdvs/app/memcard/savedata.hpp>
#include <game/pxdvs/app/gamedata/gamedata.hpp>
#include <game/pxdvs/app/people/people.hpp>
#include <game/pxdvs/app/pokemon/pokemon.hpp>
#include <game/pxdvs/app/pokemon/pokemonBios.hpp>

const f32 unkFloat = 57.29578;

/*
 * --INFO--
 * Address:	801500F0
 * Size:	000064
 */
//void Hero::itemSort(u8) {}

/*
 * --INFO--
 * Address:	80150154
 * Size:	000008
 */
void Hero::setBattleResumeFloorIndex(u8 floorIndex) {
  battleResumeFloorIndex = floorIndex;
}

/*
 * --INFO--
 * Address:	8015015C
 * Size:	000008
 */
u8 Hero::getBattleResumeFloorIndex() const { return battleResumeFloorIndex; }

/*
 * --INFO--
 * Address:	80150164
 * Size:	000008
 */
void Hero::setBattleResumeFloorID(uint floorID) {
  battleResumeFloorID = floorID;
}

/*
 * --INFO--
 * Address:	8015016C
 * Size:	000008
 */
u16 Hero::getBattleResumeFloorID() const { return battleResumeFloorID; }

/*
 * --INFO--
 * Address:	80150174
 * Size:	000108
 */
u32 Hero::getHeroObjID(s32 followerModelLevel, s32 heroStyle) {
  u32 heroObjID = 0x16c90400;

  if (heroStyle < 0) {
    heroStyle = getHeroStyle();
  }
  if (followerModelLevel < 0) {
    followerModelLevel = getFollowerModelLevel();
  }

  if (followerModelLevel == 1) {
    switch (heroStyle) {
      case 0:
        heroObjID = 0x169e0400;
        break;
      case 1:
        heroObjID = 0x1ee20400;
        break;
      case 2:
        heroObjID = 0x16a00400;
        break;
    }
  }
  else {
    switch (heroStyle) {
      case 0:
        heroObjID = 0x16c90400;
        break;
      case 1:
        heroObjID = 0x20250400;
        break;
      case 2:
        heroObjID = 0x169f0400;
        break;
    }
  }

  return heroObjID;
}

/*
 * --INFO--
 * Address:	8015027C
 * Size:	000088
 */
void Hero::setHeroStyle(u8 newHeroStyle, bool unkBool) {
  u32 heroObjID;

  if (heroStyle != newHeroStyle) {
    heroStyle = newHeroStyle;

    if (unkBool) {
      heroObjID = 0x16c90400;

      switch (newHeroStyle) {
        case 0:
          heroObjID = 0x16c90400;
          break;
        case 1:
          heroObjID = 0x20250400;
          break;
        case 2:
          heroObjID = 0x169f0400;
          break;
      }

      peopleReadObject(0, 100, heroObjID);
    }
  }
}

/*
 * --INFO--
 * Address:	80150304
 * Size:	000008
 */
u8 Hero::getHeroStyle() const { return heroStyle; }

/*
 * --INFO--
 * Address:	8015030C
 * Size:	000210
 */
//void Hero::pokemonGet(HeroPokemonGetParam *, bool) {}

/*
 * --INFO--
 * Address:	8015051C
 * Size:	000088
 */
u32 Hero::getLegendPokemonSize() const {
  s32 partySlot = 0;
  u32 legendPokemonSize = 0;
  const Pokemon * pokemonDestAddr;

  do {
    pokemonDestAddr = getPokemon(partySlot);
    if (pokemonDestAddr->checkValid() && pokemonDestAddr->isLegend()) {
      legendPokemonSize++;
    }
    partySlot++;
  }
  while (partySlot < 6);

  return legendPokemonSize;
}

/*
 * --INFO--
 * Address:	801505A4
 * Size:	000068
 */
//void Hero::itemQuantity(u16) {}

/*
 * --INFO--
 * Address:	8015060C
 * Size:	000028
 */
Hero *Hero::getHeroPtr() {
  Hero *heroPtr;

  heroPtr = (Hero *)savedataGetStatus(0, 2);
  return heroPtr;
}

/*
 * --INFO--
 * Address:	80150634
 * Size:	000024
 */
void Hero::getRestertPos(GSvec *gsVec, short &unkShortAddr) const {
  gsVec->param1 = restartPosGSvecParam1;
  gsVec->param2 = restartPosGSvecParam2;
  gsVec->param3 = restartPosGSvecParam3;
  unkShortAddr = restartPosUnknownHalfWord;
  return;
}

/*
 * --INFO--
 * Address:	80150658
 * Size:	00006C
 */
void Hero::setRestertPos() {
  GSvec heroPosVector;
  GSvec heroRotVector;

  heroMoveGetHeroPos(&heroPosVector);
  heroMoveGetHeroRot(&heroRotVector);
  restartPosGSvecParam1 = heroPosVector.param1;
  restartPosGSvecParam2 = heroPosVector.param2;
  restartPosGSvecParam3 = heroPosVector.param3;
  restartPosUnknownHalfWord = unkFloat * heroRotVector.param2;
  return;
}

/*
 * --INFO--
 * Address:	801506C4
 * Size:	000050
 */
bool Hero::deletePokemon(s32 partySlot) {
  Pokemon * pokemonAtSlot;
  bool isPokemonDeleted;

  pokemonAtSlot = getPokemon(partySlot);
  if (!pokemonAtSlot || !pokemonAtSlot->checkValid()) {
    isPokemonDeleted = false;
  }
  else {
    pokemonAtSlot->clear();
    isPokemonDeleted = true;
  }

  return isPokemonDeleted;
}

/*
 * --INFO--
 * Address:	80150714
 * Size:	000080
 */
bool Hero::setPokemon(const Pokemon * pokemonSrcAddr, s32 partySlot) {
  bool isPokemonSet;

  Pokemon * pokemonDestAddr = getPokemon(partySlot);
  if (!pokemonDestAddr || pokemonDestAddr->checkValid()) {
    isPokemonSet = false;
  }
  else {
    pokemonBiosCopy(pokemonDestAddr, pokemonSrcAddr);
    DarkPokemon * darkPokemon = pokemonDestAddr->getDarkPokemon();
    if (darkPokemon) {
      darkPokemon->setPlace(place1, 0);
    }
    isPokemonSet = true;
  }

  return isPokemonSet;
}

/*
 * --INFO--
 * Address:	80150794
 * Size:	000094
 */
// u32 Hero::addPokemon(const Pokemon * pokemon) {
//   u32 partySlot = 0;
//   Pokemon * pokemonAtSlot;

//   for (partySlot = 0; partySlot < 6; partySlot++) {
//     pokemonAtSlot = getPokemon(partySlot);
//     if (!pokemonAtSlot->checkValid()) {
//       setPokemon(pokemon, partySlot);
//       return partySlot;
//     }
//   }

//   return -1;
// }

/*
 * --INFO--
 * Address:	80150828
 * Size:	0000A4
 */
Pokemon * Hero::getPokemon(s32 partySlot, bool &isHatena) {
  Pokemon * pokemon;
  u16 pokemonDataID;
  bool isValidPokemon;

  pokemon = getPokemon(partySlot);
  isHatena = false;

  if (!pokemon) {
    return nullptr;
  }

  pokemonDataID = pokemon->getPokemonDataId();
  if (!pokemonDataID) {
    return nullptr;
  }

  isValidPokemon = gamedataAttestCheckValid(pokemon->getAttest());
  if (!isValidPokemon) {
    return nullptr;
  }

  if (pokemon->isFuseiFlag()) {
    return nullptr;
  }

  isHatena = pokemon->isHatena();
  return pokemon;
}

/*
 * --INFO--
 * Address:	801508CC
 * Size:	00002C
 */
const Pokemon *Hero::getPokemon(s32 partySlot) const {
  if (partySlot < 0 || partySlot >= 6) {
    return nullptr;
  }

  return &partyPokemon[partySlot];
}

/*
 * --INFO--
 * Address:	801508F8
 * Size:	00002C
 */
Pokemon *Hero::getPokemon(s32 partySlot) {
  if (partySlot < 0 || partySlot >= 6) {
    return nullptr;
  }

  return &partyPokemon[partySlot];
}

/*
 * --INFO--
 * Address:	80150924
 * Size:	000008
 */
void Hero::setMeetDarkPokemonCount(u8 shadowPokemonCount) {
  meetShadowPokemonCount = shadowPokemonCount;
}

/*
 * --INFO--
 * Address:	8015092C
 * Size:	000008
 */
u8 Hero::getMeetDarkPokemonCount() const { return meetShadowPokemonCount; }

/*
 * --INFO--
 * Address:	80150934
 * Size:	000008
 */
Item **Hero::getDisk() { return battleCDItems; }

/*
 * --INFO--
 * Address:	8015093C
 * Size:	000020
 */
void Hero::addFootStep(u32 footstepsToAdd) {
  u32 newFootStepAmount;
  u32 currFootStepAmount;
  u32 sum;

  currFootStepAmount = footStep;
  newFootStepAmount = -1;
  sum = currFootStepAmount + footstepsToAdd;
  if (currFootStepAmount <= sum) {
    newFootStepAmount = sum;
  }
  footStep = newFootStepAmount;
}

/*
 * --INFO--
 * Address:	8015095C
 * Size:	000008
 */
u32 Hero::getFootStep() const { return footStep; }

/*
 * --INFO--
 * Address:	80150964
 * Size:	000008
 */
u8 Hero::getFollowerModelLevel() { return followerModelLevel; }

/*
 * --INFO--
 * Address:	8015096C
 * Size:	000008
 */
void Hero::setFollowerModelLevel(u8 followModelLvl) {
  followerModelLevel = followModelLvl;
}

/*
 * --INFO--
 * Address:	80150974
 * Size:	000008
 */
u8 Hero::getFollowerID() { return followerID; }

/*
 * --INFO--
 * Address:	8015097C
 * Size:	000008
 */
void Hero::setFollowerID(u8 followID) { followerID = followID; }

/*
 * --INFO--
 * Address:	80150984
 * Size:	000008
 */
u32 Hero::getFollowerGrpID() { return followerGrpID; }

/*
 * --INFO--
 * Address:	8015098C
 * Size:	000008
 */
u32 Hero::getFollowerResID() { return followerResID; }

/*
 * --INFO--
 * Address:	80150994
 * Size:	000008
 */
void Hero::setFollowerObjID(u32 objID) { followerObjID = objID; }

/*
 * --INFO--
 * Address:	8015099C
 * Size:	000008
 */
void Hero::setFollowerGrpID(u32 grpID) { followerGrpID = grpID; }

/*
 * --INFO--
 * Address:	801509A4
 * Size:	000008
 */
void Hero::setFollowerResID(u32 resID) { followerResID = resID; }

/*
 * --INFO--
 * Address:	801509AC
 * Size:	000008
 */
u32 Hero::getHeroRnd() const { return heroRnd; }
