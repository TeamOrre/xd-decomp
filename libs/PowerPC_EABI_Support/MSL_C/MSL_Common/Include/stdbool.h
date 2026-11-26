#ifndef MSL_STDBOOL_H
#define MSL_STDBOOL_H

#ifdef __cplusplus
extern "C" {
#endif

#ifndef __cplusplus
/// A signed integer used to contain boolean values
/// @todo Maybe some versions of MetroWerks support @c _Bool?
typedef int bool;
#endif

/// #bool true
/// @todo Make this and #false part of an @c enum. Fake usages, such as
/// assigning to a @c u32, will need to be addressed.
#define true 1

/// #bool false
#define false 0

#ifdef __cplusplus
}
#endif
#endif
