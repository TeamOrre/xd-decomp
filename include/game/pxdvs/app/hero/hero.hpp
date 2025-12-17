#ifndef HERO_MEMBER_FUNCTIONS_H
#define HERO_MEMBER_FUNCTIONS_H

#include <game/pxdvs/GSAPI/GSmath/GSvec.hpp>
#include <game/pxdvs/app/hero/heroPokemonGet.hpp>
#include <game/pxdvs/app/pokemon/pokemon.hpp>

class Item;

class Hero {
private:
  char16 heroName[11];              // 0x0
  char16 heroNameCopy[11];          // heroName copy (need to verify), 0x16
  u32 heroRnd;                   // OT ID, 0x2c
  Pokemon partyPokemon[6];       // 0x30
  Item *normalItem[30];          // Items, 0x4c8
  Item *extraItem[43];           // Key Items, 0x540
  Item *itemBall[16];            // Balls, 0x5ec
  Item *itemSkill[64];           // TMs/HMs, 0x62c
  Item *itemSeed[46];            // Berries, 0x72c
  Item *itemKoron[3];            // Cologne, 0x7e4
  Item *disk[60];                // Battle CDs, 0x7f0
  u8 sexDataID;                  // 0x8e0
  u8 homePlace;                  // 0x8e1
  u16 x8e2;                      // 0x8e2
  u32 pokedoru;                  // 0x8e4
  u32 pokecoupons;               // 0x8e8
  u32 pokecouponsAll;            // 0x8ec
  u8 badge01Flag;                // 0x8f0
  u8 badge02Flag;                // 0x8f1
  u8 badge03Flag;                // 0x8f2
  u8 badge04Flag;                // 0x8f3
  u8 badge05Flag;                // 0x8f4
  u8 badge06Flag;                // 0x8f5
  u8 badge07Flag;                // 0x8f6
  u8 badge08Flag;                // 0x8f7
  u8 hizukiFlag;                 // 0x8f8
  u8 x8f9;                       // 0x8f9
  Item *hizukiItems[10];         // 0x8fa
  u8 x922[20];                   // 0x922
  u8 meetDarkPokemonCount;       // 0x938
  u8 followerID;                 // 0x939
  s16 restertPosUnknownHalfWord; // 0x93a
  f32 restertPosGSvecParam1;     // 0x93c
  f32 restertPosGSvecParam2;     // 0x940
  f32 restertPosGSvecParam3;     // 0x944
  u32 footStep;                  // 0x948
  u32 followerResID;             // 0x94c
  u32 followerGrpID;             // 0x950
  u32 followerObjID;             // 0x954
  u8 followerModelLevel;         // 0x958
  u8 heroStyle;                  // 0x959
  u16 battleResumeFloorID;       // 0x95a
  u8 battleResumeFloorIndex;     // 0x95c

public:
  void itemSort(u8);
  void setBattleResumeFloorIndex(u8);
  u8 getBattleResumeFloorIndex() const;
  void setBattleResumeFloorID(uint);
  u16 getBattleResumeFloorID() const;
  void getHeroObjID(long, long);
  void setHeroStyle(u8, bool);
  u8 getHeroStyle() const;
  void pokemonGet(HeroPokemonGetParam *, bool);
  void getLegendPokemonSize() const;
  void itemQuantity(u16);
  Hero *getHeroPtr();
  void getRestertPos(GSvec *, short &) const;
  void setRestertPos();
  void deletePokemon(long);
  void setPokemon(const Pokemon *, long);
  void addPokemon(const Pokemon *);
  void getPokemon(long, bool &);
  const Pokemon *getPokemon(long) const;
  Pokemon *getPokemon(long);
  void setMeetDarkPokemonCount(u8);
  u8 getMeetDarkPokemonCount() const;
  Item **getDisk();
  void addFootStep(u32);
  u32 getFootStep() const;
  u8 getFollowerModelLevel();
  void setFollowerModelLevel(u8);
  u8 getFollowerID();
  void setFollowerID(u8);
  u32 getFollowerGrpID();
  u32 getFollowerResID();
  void setFollowerObjID(u32);
  void setFollowerGrpID(u32);
  void setFollowerResID(u32);
  u32 getHeroRnd() const;
};

#endif
