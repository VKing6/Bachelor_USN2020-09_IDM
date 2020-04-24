#ifndef _BOOLTOBYTE_H
#define _BOOLTOBYTE_H

byte boolToByte(bool bool1) {
    byte ret = 0;
    ret = (bool1) ? ret | B00000001 : ret & B11111110;
    return ret;
}

byte boolToByte(bool bool1, bool bool2) {
    byte ret = 0;
    ret = (bool1) ? ret | B00000001 : ret & B11111110;
    ret = (bool2) ? ret | B00000010 : ret & B11111101;
    return ret;
}

byte boolToByte(bool bool1, bool bool2, bool bool3) {
    byte ret = 0;
    ret = (bool1) ? ret | B00000001 : ret & B11111110;
    ret = (bool2) ? ret | B00000010 : ret & B11111101;
    ret = (bool3) ? ret | B00000100 : ret & B11111011;
    return ret;
}

byte boolToByte(bool bool1, bool bool2, bool bool3, bool bool4) {
    byte ret = 0;
    ret = (bool1) ? ret | B00000001 : ret & B11111110;
    ret = (bool2) ? ret | B00000010 : ret & B11111101;
    ret = (bool3) ? ret | B00000100 : ret & B11111011;
    ret = (bool4) ? ret | B00001000 : ret & B11110111;
    return ret;
}

byte boolToByte(bool bool1, bool bool2, bool bool3, bool bool4, bool bool5) {
    byte ret = 0;
    ret = (bool1) ? ret | B00000001 : ret & B11111110;
    ret = (bool2) ? ret | B00000010 : ret & B11111101;
    ret = (bool3) ? ret | B00000100 : ret & B11111011;
    ret = (bool4) ? ret | B00001000 : ret & B11110111;
    ret = (bool5) ? ret | B00010000 : ret & B11101111;
    return ret;
}

byte boolToByte(bool bool1, bool bool2, bool bool3, bool bool4, bool bool5,
               bool bool6) {
    byte ret = 0;
    ret = (bool1) ? ret | B00000001 : ret & B11111110;
    ret = (bool2) ? ret | B00000010 : ret & B11111101;
    ret = (bool3) ? ret | B00000100 : ret & B11111011;
    ret = (bool4) ? ret | B00001000 : ret & B11110111;
    ret = (bool5) ? ret | B00010000 : ret & B11101111;
    ret = (bool6) ? ret | B00100000 : ret & B11011111;
    return ret;
}

byte boolToByte(bool bool1, bool bool2, bool bool3, bool bool4, bool bool5,
               bool bool6, bool bool7) {
    byte ret = 0;
    ret = (bool1) ? ret | B00000001 : ret & B11111110;
    ret = (bool2) ? ret | B00000010 : ret & B11111101;
    ret = (bool3) ? ret | B00000100 : ret & B11111011;
    ret = (bool4) ? ret | B00001000 : ret & B11110111;
    ret = (bool5) ? ret | B00010000 : ret & B11101111;
    ret = (bool6) ? ret | B00100000 : ret & B11011111;
    ret = (bool7) ? ret | B01000000 : ret & B10111111;
    return ret;
}

byte boolToByte(bool bool1, bool bool2, bool bool3, bool bool4, bool bool5,
               bool bool6, bool bool7, bool bool8) {
    byte ret = 0;
    ret = (bool1) ? ret | B00000001 : ret & B11111110;
    ret = (bool2) ? ret | B00000010 : ret & B11111101;
    ret = (bool3) ? ret | B00000100 : ret & B11111011;
    ret = (bool4) ? ret | B00001000 : ret & B11110111;
    ret = (bool5) ? ret | B00010000 : ret & B11101111;
    ret = (bool6) ? ret | B00100000 : ret & B11011111;
    ret = (bool7) ? ret | B01000000 : ret & B10111111;
    ret = (bool8) ? ret | B10000000 : ret & B01111111;
    return ret;
}

#endif // _BOOLTOBYTE_H
