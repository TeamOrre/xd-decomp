#include "GSAPI/GSsysdolphin_baselib/baselib/random.h"

static u32 __hsd_rand_seed_default = 1;
u32* __hsd_rand_seed_hold = &__hsd_rand_seed_default;

u16 HSD_Rand(void)
{
    *__hsd_rand_seed_hold = *__hsd_rand_seed_hold * 214013 + 2531011;
    return *__hsd_rand_seed_hold >> 0x10;
}

f32 HSD_Randf(void)
{
    *__hsd_rand_seed_hold = *__hsd_rand_seed_hold * 214013 + 2531011;
    return (f32) (*__hsd_rand_seed_hold >> 0x10) / (1 << 16);
}

s32 HSD_Randi(s32 max_val)
{
    return max_val * HSD_Rand() / (1 << 16);
}

void _HSD_RandForgetMemory(void* low, void* high)
{
    if (low <= (void*) __hsd_rand_seed_hold && (void*) __hsd_rand_seed_hold < high) {
        __hsd_rand_seed_hold = &__hsd_rand_seed_default;
    }
}
