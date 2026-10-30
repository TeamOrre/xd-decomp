#ifndef DARK_POKEMON_H
#define DARK_POKEMON_H

#include <global.h>

enum darkPokemonWhere { place0, place1, place2, place3, place4, place5, place6 };

enum darkPokemonStatus  {
    darkPokemonStatusSnatch = 3L,
    darkPokemonStatusRelive = 4L,
    // 3 bits
};
enum darkPokemonSnatchWho {
    // 2 bits
};

struct DarkPokemon {
    struct {
        u32 status : 3;
        u32 unk : 1;
        u32 snatchInfoLevel : 3;
        u32 snatchWho: 2;
        u32 reversMode: 1;
        u32 update : 1;
        u32 wazaNew : 3;
        u32 where : 3;
        u32 unk2 : 15;
    } bits0x0;

    struct {
        u32 poolExp : 20;
        u32 catchBallID : 4;
        u32 information : 1;
        u32 unk : 7;
    } bits0x4;

    u8 unk0x8[3];
    u8 statusRnd[6]; // 0xb

    u8 placeAux; // 0x11
    u8 unk0x12[1];
    u8 snatchIndex;
    u16 orgTrainer; // 0x14
    u16 catchFloorId; // 0x16
    u16 poolFriendLevel; // 0x18
    u16 pokemonID; // 0x1a
    u32 rnd; // 0x1c
    u32 escapeOrSnatchTime; // 0x20
    s32 darkPoint; // 0x24
    u16 trainerName[11]; // 0x28..0x3c
    u16 darkPokemonID; // 0x3e
    u8 reversPattern; // 0x40
    u8 unk41[3];
    u32 walkCount; // 0x44
    // 0x48 bytes total

    u32 getWalkCount() const;
    void setWalkCount(u32);
    u8 getReversPattern() const;
    void setReversPattern(u8);
    u16 getCatchBallID() const;
    void setCatchBallID(u16);
    u16 getDarkPokemonID() const;
    void setDarkPokemonID(u16);
    u16 getPokemonID() const;
    void setPokemonID(u16);
    bool isSnatch() const;
    bool isRelive() const;
    void setTrainerName(const u16*);
    const u16* getTrainerName() const;
    void setStatusRnd(u8, u8);
    u8 getStatusRnd(u8) const;
    void setInformation(bool);
    bool isInformation() const;
    void setUpdate(bool);
    bool isUpdate() const;
    void setEscapeTime(u32);
    u32 getEscapeTime() const;
    void setSnatchTime(u32);
    u32 getSnatchTime() const;
    void setRnd(u32);
    u32 getRnd() const;
    u16 getCatchFloorId() const;
    void setCatchFloorId(u16);
    u16 getOrgTrainer() const;
    void setOrgTrainer(u16);
    u8 getSnatchIndex() const;
    void setSnatchIndex(u8);
    void getPlace(darkPokemonWhere&, u8&);
    void setPlace(darkPokemonWhere, u8);
    void setWazaNew(u8, bool);
    bool isWazaNew(u8) const;
    u16 getPoolFriendLevel() const;
    void setPoolFriendLevel(u16);
    void setPoolExp(u32);
    u32 getPoolExp() const;
    void setDarkPointDirect(s32);
    s32 getDarkPointDirect() const;
    void setReversMode(bool);
    bool isReversMode() const;
    void setSnatchFromWho(darkPokemonSnatchWho);
    darkPokemonSnatchWho getSnatchFromWho() const;
    void setSnatchInfoLevel(u8);

    darkPokemonStatus getStatus() const;
    void addStatus(darkPokemonStatus);
    void setStatus(darkPokemonStatus);


    void init();
};

#endif
