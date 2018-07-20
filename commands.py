#!/usr/bin/env python3
from mrcrowbar import models as mrc


HALT = b'\xff'
WAIT = b'\xfe'
FLIP = b'\xfd'




class LMove( mrc.Block ):
    const = mrc.Const( mrc.Bits( 0x00, 0b0000111100000000, size=2 ), 0b1100 )
    sld2a = mrc.Bits( 0x00, 0b1100000000000000, size=2 )
    sld1a = mrc.Bits( 0x00, 0b0011000000000000, size=2 )
    sld2i = mrc.Bits( 0x00, 0b0000000011110000, size=2 )
    sld1i = mrc.Bits( 0x00, 0b0000000000001111, size=2 )


a = LMove()
a.sld2a = 2
print(a.export_data())
