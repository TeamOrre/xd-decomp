#ifndef GBA
#define GBA

#include "types.h"

 
#ifdef __cplusplus
extern "C" {
#endif


#define GBA_JSTAT_MASK 0x3A

#define GBA_READY 0
#define GBA_NOT_READY 1
#define GBA_BUSY 2



typedef void (*GBACallback)(s32 chan, s32 ret);

void GBAInit(void);
s32 GBAGetStatus(s32 chan, u8* status);
s32 GBAGetStatusAsync(s32 chan, u8* status, GBACallback callback);
s32 GBAReset(s32 chan, u8* status);
s32 GBAResetAsync(s32 chan, u8* status, GBACallback callback);
s32 GBARead(s32 chan, u8* dst, u8* status);
s32 GBAReadAsync(s32 chan, u8* dst, u8* status, GBACallback callback);
s32 GBAWrite(s32 chan, u8* src, u8* status);
s32 GBAWriteAsync(s32 chan, u8* src, u8* status, GBACallback callback);


#ifdef __cplusplus
}
#endif // extern "C"

#endif // GBA
