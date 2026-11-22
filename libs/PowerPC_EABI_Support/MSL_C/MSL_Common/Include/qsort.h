#ifndef _MSL_COMMON_QSORT_H
#define _MSL_COMMON_QSORT_H

#include <stddef.h>

void qsort(void*, size_t, size_t, int (*compar)(const void*,const void*));

#endif
