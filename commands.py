#!/usr/bin/env python3
from mrcrowbar import models as mrc


class Halt( mrc.Block ):
    const = mrc.Const( mrc.UInt8( 0x00 ), 0xff )

class Wait( mrc.Block ):
    const = mrc.Const( mrc.UInt8( 0x00 ), 0xfe )

class Flip( mrc.Block ):
    const = mrc.Const( mrc.UInt8( 0x00 ), 0xfd )

class SMove( mrc.Block ):
    const = mrc.Const( mrc.Bits( 0x00, 0b1100111111100000, size=2 ), 0b000100000 )
    llda = mrc.Bits( 0x00, 0b0011000000000000, size=2 )
    lldi = mrc.Bits( 0x00, 0b0000000000011111, size=2 )

class LMove( mrc.Block ):
    const = mrc.Const( mrc.Bits( 0x00, 0b0000111100000000, size=2 ), 0b1100 )
    sld2a = mrc.Bits( 0x00, 0b1100000000000000, size=2 )
    sld1a = mrc.Bits( 0x00, 0b0011000000000000, size=2 )
    sld2i = mrc.Bits( 0x00, 0b0000000011110000, size=2 )
    sld1i = mrc.Bits( 0x00, 0b0000000000001111, size=2 )

    @property
    def sld2x( self ):
        return 0 if self.sld2a != 0b01 else (self.sdl2i + 5)

    @property
    def sld2y( self ):
        return 0 if self.sld2a != 0b10 else (self.sdl2i + 5)

    @property
    def sld2z( self ):
        return 0 if self.sld2a != 0b11 else (self.sdl2i + 5)

    @property
    def sld1x( self ):
        return 0 if self.sld1a != 0b01 else (self.sdl1i + 5)

    @property
    def sld1y( self ):
        return 0 if self.sld1a != 0b10 else (self.sdl1i + 5)

    @property
    def sld1z( self ):
        return 0 if self.sld1a != 0b11 else (self.sdl1i + 5)

    @property
    def repr( self ):
        return 'sld1: ({}, {}, {}), sld2: ({}, {}, {})'.format( self.sld1x, self.sld1y, self.sld1z, self.sld2x, self.sld2y, self.sld2z )


class FusionP( mrc.Block ):
    const = mrc.Const( mrc.Bits( 0x00, 0b00000111 ), 0b111 )
    nd = mrc.Bits( 0x00, 0b11111000 )

class FusionS( mrc.Block ):
    const = mrc.Const( mrc.Bits( 0x00, 0b00000111 ), 0b110 )
    nd = mrc.Bits( 0x00, 0b11111000 )

class Fission( mrc.Block ):
    const = mrc.Const( mrc.Bits( 0x00, 0b00000111, size=1 ), 0b101 )
    nd = mrc.Bits( 0x00, 0b11111000, size=1 )
    m = mrc.UInt8( 0x01 )

class Fill( mrc.Block ):
    const = mrc.Const( mrc.Bits( 0x00, 0b00000111, size=1 ), 0b011 )
    nd = mrc.Bits( 0x00, 0b11111000, size=1 )




a = LMove()
a.sld2a = 2
print(a.export_data())
