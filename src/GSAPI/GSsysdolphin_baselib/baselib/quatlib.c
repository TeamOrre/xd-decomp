#include "GSAPI/GSsysdolphin_baselib/baselib/quatlib.h"

#include <math.h>
#include <GSAPI/GSsysdolphin_baselib/placeholder.h>
#include <GSAPI/GSsysdolphin_baselib/platform.h>

s32 EulerToQuat(Vec3* euler, Quaternion* q)
{
    f32 cx;
    f32 cy;
    f32 cz;
    f32 sx;
    f32 sy;
    f32 sz;
    f32 cc;
    f32 ss;

    cx = cosf(0.5F * euler->x);
    cy = cosf(0.5F * euler->y);
    cz = cosf(0.5F * euler->z);
    sx = sinf(0.5F * euler->x);
    sy = sinf(0.5F * euler->y);
    sz = sinf(0.5F * euler->z);

    ss = sy * sz;
    cc = cy * cz;
    q->w = cx * cc + sx * ss;
    q->x = sx * cc - cx * ss;
    q->y = cz * (cx * sy) + sz * (sx * cy);
    q->z = sz * (cx * cy) - cz * (sx * sy);

    return 1;
}

s32 QuatSlerp(Quaternion* p, Quaternion* q, Quaternion* out, f32 t)
{
    f32 cosom;
    f32 t2;
    f32 theta;
    f32 sinom;
    f32 sp;
    f32 sq;

    cosom = p->x * q->x + p->y * q->y + p->z * q->z + p->w * q->w;

    if ((1.0F + cosom) > EPSILON) {
        if ((1.0F - cosom) > EPSILON) {
            theta = acosf(cosom);
            sinom = sinf(theta);
            sp = sinf((1.0F - t) * theta) / sinom;
            sq = sinf(t * theta) / sinom;
        } else {
            sq = t;
            sp = (f32) (1.0 - (f64) t);
        }
        out->x = sp * p->x + sq * q->x;
        out->y = sp * p->y + sq * q->y;
        out->z = sp * p->z + sq * q->z;
        out->w = sp * p->w + sq * q->w;
    } else {
        out->x = -p->y;
        out->y = p->x;
        out->z = -p->w;
        out->w = p->z;

        if (t < 0.5F) {
            sp = sinf((f32) (M_PI_2 * (1.0F - (2.0F * t))));
            sq = sinf((f32) (M_PI_2 * (2.0F * t)));
            out->x = sp * p->x + sq * q->x;
            out->y = sp * p->y + sq * q->y;
            out->z = sp * p->z + sq * q->z;
            out->w = sp * p->w + sq * q->w;
        } else {
            t -= 0.5F;
            t2 = 2.0F * t;
            sp = sinf((f32) (M_PI_2 * (1.0F - t2)));
            sq = sinf((f32) (M_PI_2 * t2));
            out->x = sp * p->x + sq * q->x;
            out->y = sp * p->y + sq * q->y;
            out->z = sp * p->z + sq * q->z;
            out->w = sp * p->w + sq * q->w;
        }
    }

    return 1;
}
