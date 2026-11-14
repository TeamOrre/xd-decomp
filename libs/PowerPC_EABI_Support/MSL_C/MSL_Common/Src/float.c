#include "float.h"
#include "global.h"

int __float_nan[] = {0x7FFFFFFF};
int __float_huge[] = {0x7F800000};
int __double_min[] = {0x00100000, 0};
int __double_max[] = {0x7FEFFFFF, 0xFFFFFFFF};
int __double_huge[] = {0x7FF00000, 0};
int __extended_min[] = {0x00100000, 0};
int __extended_max[] = {0x7FEFFFFF, 0xFFFFFFFF};
int __float_min[] = {0x00800000};
int __float_max[] = {0x7F7FFFFF};
int __float_epsilon[] = {0x34000000};
