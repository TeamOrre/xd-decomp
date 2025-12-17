#include <game/pxdvs/app/hero/hero.hpp>
#include <game/pxdvs/app/memcard/savedata.hpp>

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
//void Hero::setBattleResumeFloorIndex(u8) {}

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
//void Hero::setBattleResumeFloorID(uint) {}

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
//void Hero::getHeroObjID(long, long) {}

/*
 * --INFO--
 * Address:	8015027C
 * Size:	000088
 */
//void Hero::setHeroStyle(u8, bool) {}

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
//void Hero::getLegendPokemonSize() const {}

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
  gsVec->param1 = restertPosGSvecParam1;
  gsVec->param2 = restertPosGSvecParam2;
  gsVec->param3 = restertPosGSvecParam3;
  unkShortAddr = restertPosUnknownHalfWord;
  return;
}

/*
 * --INFO--
 * Address:	80150658
 * Size:	00006C
 */
//void Hero::setRestertPos() {}

/*
 * --INFO--
 * Address:	801506C4
 * Size:	000050
 */
//void Hero::deletePokemon(long) {}

/*
 * --INFO--
 * Address:	80150714
 * Size:	000080
 */
//void Hero::setPokemon(const Pokemon *, long) {}

/*
 * --INFO--
 * Address:	80150794
 * Size:	000094
 */
//void Hero::addPokemon(const Pokemon *) {}

/*
 * --INFO--
 * Address:	80150828
 * Size:	0000A4
 */
//void Hero::getPokemon(long, bool &) {}

/*
 * --INFO--
 * Address:	801508CC
 * Size:	00002C
 */
const Pokemon *Hero::getPokemon(long partyIndex) const {
  if (partyIndex < 0 || partyIndex >= 6) {
    return nullptr;
  }

  return &partyPokemon[partyIndex];
}

/*
 * --INFO--
 * Address:	801508F8
 * Size:	00002C
 */
Pokemon *Hero::getPokemon(long partyIndex) {
  if (partyIndex < 0 || partyIndex >= 6) {
    return nullptr;
  }

  return &partyPokemon[partyIndex];
}

/*
 * --INFO--
 * Address:	80150924
 * Size:	000008
 */
void Hero::setMeetDarkPokemonCount(u8 darkPokemonCount) {
  meetDarkPokemonCount = darkPokemonCount;
}

/*
 * --INFO--
 * Address:	8015092C
 * Size:	000008
 */
u8 Hero::getMeetDarkPokemonCount() const { return meetDarkPokemonCount; }

/*
 * --INFO--
 * Address:	80150934
 * Size:	000008
 */
Item **Hero::getDisk() { return disk; }

/*
 * --INFO--
 * Address:	8015093C
 * Size:	000020
 */
void Hero::addFootStep(u32 footstepsToAdd) {
  u32 newFootStepAmount;
  u32 sum;

  newFootStepAmount = -1;
  sum = footStep + footstepsToAdd;
  if (footStep <= sum) {
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
