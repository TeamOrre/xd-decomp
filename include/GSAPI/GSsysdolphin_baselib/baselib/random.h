#ifndef _random_h_
#define _random_h_

#include <GSAPI/GSsysdolphin_baselib/platform.h>

#ifdef __cplusplus
extern "C" {
#endif

u16 HSD_Rand(void);
f32 HSD_Randf(void);
s32 HSD_Randi(s32 max_val);
void _HSD_RandForgetMemory(void* low, void* high);
extern u32* HSD_RandSeedPtr;

/// #HSD_Randi that accepts an empty range.
static inline int randi(int max_val)
{
    if (max_val != 0) {
        return HSD_Randi(max_val);
    }
    return 0;
}

#ifdef __cplusplus
}
#endif

#endif
