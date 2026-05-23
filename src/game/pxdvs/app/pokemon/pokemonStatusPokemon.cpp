#include <game/pxdvs/app/pokemon/pokemon.hpp>
#include <game/pxdvs/app/pokemon/pokemonBios.hpp>
#include <game/pxdvs/app/pokemon/pokemonDB.hpp>

void Pokemon::setConditionTurnNow(u8 data) {
    conditionTurnNow = data;
}
u8 Pokemon::getConditionTurnNow() const {
    return conditionTurnNow;
}
void Pokemon::setConditionTurn(u8 data) {
    conditionTurn = data;
}
u8 Pokemon::getConditionTurn() const {
    return conditionTurn;
}
void Pokemon::setConditionCount(u8 data) {
    conditionCount = data;
}
u8 Pokemon::getConditionCount() const {
    return conditionCount;
}
void Pokemon::setCondition(u8 data) {
    condition = data;
}
u8 Pokemon::getCondition() const {
    return condition;
}
u16 Pokemon::getDarkPokemonDataId() const {
    return darkPokemonDataID;
}
void Pokemon::setPara1Amari(u16 data) {
    para1Amari = data;
}
void Pokemon::setAmari(u16 data) {
    amari = data;
}
void Pokemon::setPcboxMark(u8 data) {
    pcboxMark = data;
}
void Pokemon::setFriendLevel(u16 data) {
    u16 finalData = 0xFF;
    if (data < finalData) {
        finalData = data;
    }
    friendLevel = finalData;
}
void Pokemon::setNimblenessRnd(u16 data) {
    statusRnd.setNimbleness(data);
}
void Pokemon::setSpeDefRnd(u16 data) {
    statusRnd.setSpeDef(data);
}
void Pokemon::setSpeAtkRnd(u16 data) {
    statusRnd.setSpeAtk(data);
}
void Pokemon::setPhyDefRnd(u16 data) {
    statusRnd.setPhyDef(data);
}
void Pokemon::setPhyAtkRnd(u16 data) {
    statusRnd.setPhyAtk(data);
}
void Pokemon::setMaxHpRnd(u16 data) {
    statusRnd.setMaxHp(data);
}
void Pokemon::setNimblenessEffort(u16 data) {
    u16 finalData = 0xFF;
    if (data < finalData) {
        finalData = data;
    }
    nimblenessEffort = finalData;
}
void Pokemon::setSpeDefEffort(u16 data) {
    u16 finalData = 0xFF;
    if (data < finalData) {
        finalData = data;
    }
    speDefEffort = finalData;
}
void Pokemon::setSpeAtkEffort(u16 data) {
    u16 finalData = 0xFF;
    if (data < finalData) {
        finalData = data;
    }
    speAtkEffort = finalData;
}
void Pokemon::setPhyDefEffort(u16 data) {
    u16 finalData = 0xFF;
    if (data < finalData) {
        finalData = data;
    }
    phyDefEffort = finalData;
}
void Pokemon::setPhyAtkEffort(u16 data) {
    u16 finalData = 0xFF;
    if (data < finalData) {
        finalData = data;
    }
    phyAtkEffort = finalData;
}
void Pokemon::setMaxHpEffort(u16 data) {
    u16 finalData = 0xFF;
    if (data < finalData) {
        finalData = data;
    }
    maxHpEffort = finalData;
}
void Pokemon::setNimbleness(u16 data) {
    nimbleness = data;
}
void Pokemon::setSpeDef(u16 data) {
    speDef = data;
}
void Pokemon::setSpeAtk(u16 data) {
    speAtk = data;
}
void Pokemon::setPhyDef(u16 data) {
    phyDef = data;
}
void Pokemon::setPhyAtk(u16 data) {
    phyAtk = data;
}
void Pokemon::setMaxHp(u16 data) {
    maxHp = data;
}
void Pokemon::setHp(u16 data) {
    hp = data;
    u16 hpCap = getMaxHp();
    if (hpCap < hp) {
        hp = hpCap;
    }
}
void Pokemon::setItemDataId(u16 data) {
    itemDataID = data;
}
void Pokemon::setExp(u32 data) {
    exp = data;
}
void Pokemon::setCatchTrainerRnd(u32 data) {
    catchTrainerRnd = data;
}
void Pokemon::setCatchTrainerSex(u8 data) {
    catchTrainerSex = data;
}
void Pokemon::setCatchBallId(u8 data) {
    catchBallId = data;
}
void Pokemon::setCatchLevel(u8 data) {
    catchLevel = data;
}
void Pokemon::setCatchFloorId(u16 data) {
    catchFloorId = data;
}
void Pokemon::setRnd(u32 data) {
    rnd = data;
}
u16 Pokemon::getPara1Amari() const {
    return para1Amari;
}
u16 Pokemon::getAmari() const {
    return amari;
}
bool Pokemon::isFuseiFlag() const {
    return flags.bits.fusei;
}
u8 Pokemon::getPcboxMark() const {
    return pcboxMark;
}
u16 Pokemon::getFriendLevel() const {
    return friendLevel;
}
u16 Pokemon::getItemDataId() const {
    return itemDataID;
}
u8 Pokemon::getLevel() const {
    return level;
}
u16 Pokemon::getHp() const {
    return hp;
}
char* Pokemon::getNicknamePtr() {
    return &nickname[0];
}
u8 Pokemon::getNimblenessRnd() const {
    return statusRnd.getNimbleness();
}
u8 Pokemon::getSpeDefRnd() const {
    return statusRnd.getSpeDef();
}
u8 Pokemon::getSpeAtkRnd() const {
    return statusRnd.getSpeAtk();
}
u8 Pokemon::getPhyDefRnd() const {
    return statusRnd.getPhyDef();
}
u8 Pokemon::getPhyAtkRnd() const {
    return statusRnd.getPhyAtk();
}
u8 Pokemon::getMaxHpRnd() const {
    return statusRnd.getMaxHp();
}
u16 Pokemon::getNimblenessEffort() const {
    return nimblenessEffort;
}
u16 Pokemon::getSpeDefEffort() const {
    return speDefEffort;
}
u16 Pokemon::getSpeAtkEffort() const {
    return speAtkEffort;
}
u16 Pokemon::getPhyDefEffort() const {
    return phyDefEffort;
}
u16 Pokemon::getPhyAtkEffort() const {
    return phyAtkEffort;
}
u16 Pokemon::getMaxHpEffort() const {
    return maxHpEffort;
}
u16 Pokemon::getNimbleness() const {
    return nimbleness;
}
u16 Pokemon::getSpeDef() const {
    return speDef;
}
u16 Pokemon::getSpeAtk() const {
    return speAtk;
}
u16 Pokemon::getPhyDef() const {
    return phyDef;
}
u16 Pokemon::getPhyAtk() const {
    return phyAtk;
}
u16 Pokemon::getMaxHp() const {
    return maxHp;
}
Attest* Pokemon::getAttest() {
    return &attest;
}
u32 Pokemon::getRnd() const {
    return rnd;
}
u16 Pokemon::getPokemonDataId() const {
    return dataID;
}
void Pokemon::initCondition() {
    condition = 0;
    conditionCount = 0;
    conditionTurn = 0;
    conditionTurnNow = 0;
}
void Pokemon::copyCondition(const Pokemon* poke) {
    condition = poke->condition;
    conditionCount = poke->conditionCount;
    conditionTurn = poke->conditionTurn;
    conditionTurnNow = poke->conditionTurnNow;
}

const Ribbon* Pokemon::getRibbon() const {
    return &ribbon;
}
PokemonWaza* Pokemon::getPokemonWaza(u16 wazaNum) {
    if (wazaNum < MAX_WAZA)
    {
        return &wazas[wazaNum];
    }
    return nullptr;
}
u32 Pokemon::getCatchTrainerRnd() const {
    return catchTrainerRnd;
}
void Pokemon::clear() {
    memset(this, 0, sizeof(Pokemon));
}


void PokemonStatusRnd::setNimbleness(u8 data) {
    u16 finalData = 0x1f;
    if (data < 0x1f) {
        finalData = data;
    }
    nimbleness = finalData;
}
void PokemonStatusRnd::setSpeDef(u8 data) {
    u16 finalData = 0x1f;
    if (data < 0x1f) {
        finalData = data;
    }
    speDef = finalData;
}
void PokemonStatusRnd::setSpeAtk(u8 data) {
    u16 finalData = 0x1f;
    if (data < 0x1f) {
        finalData = data;
    }
    speAtk = finalData;
}
void PokemonStatusRnd::setPhyDef(u8 data) {
    u16 finalData = 0x1f;
    if (data < 0x1f) {
        finalData = data;
    }
    phyDef = finalData;
}
void PokemonStatusRnd::setPhyAtk(u8 data) {
    u16 finalData = 0x1f;
    if (data < 0x1f) {
        finalData = data;
    }
    phyAtk = finalData;
}
void PokemonStatusRnd::setMaxHp(u8 data) {
    u16 finalData = 0x1f;
    if (data < 0x1f) {
        finalData = data;
    }
    maxHp = finalData;
}

u32 PokemonStatusRnd::getNimbleness() const {
    return nimbleness;
}
u32 PokemonStatusRnd::getSpeDef() const {
    return speDef;
}
u32 PokemonStatusRnd::getSpeAtk() const {
    return speAtk;
}
u32 PokemonStatusRnd::getPhyDef() const {
    return phyDef;
}
u32 PokemonStatusRnd::getPhyAtk() const {
    return phyAtk;
}
u32 PokemonStatusRnd::getMaxHp() const {
    return maxHp;
}
