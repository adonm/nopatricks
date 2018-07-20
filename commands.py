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

    @property
    def lldx( self ):
        return 0 if self.llda != 0b01 else (self.lldi - 15)

    @lldx.setter
    def lldx( self, value ):
        assert value in range( -15, 17 )
        self.llda = 0b01
        self.lldi = value + 15

    @property
    def lldy( self ):
        return 0 if self.llda != 0b10 else (self.lldi - 15)

    @lldy.setter
    def lldy( self, value ):
        assert value in range( -15, 17 )
        self.llda = 0b10
        self.lldi = value + 15

    @property
    def lldz( self ):
        return 0 if self.llda != 0b11 else (self.lldi - 15)

    @lldz.setter
    def lldz( self, value ):
        assert value in range( -15, 17 )
        self.llda = 0b11
        self.lldi = value + 15

    @property
    def repr( self ):
        return 'lld: ({}, {}, {})'.format( self.lldx, self.lldy, self.lldz )


class LMove( mrc.Block ):
    const = mrc.Const( mrc.Bits( 0x00, 0b0000111100000000, size=2 ), 0b1100 )
    sld2a = mrc.Bits( 0x00, 0b1100000000000000, size=2 )
    sld1a = mrc.Bits( 0x00, 0b0011000000000000, size=2 )
    sld2i = mrc.Bits( 0x00, 0b0000000011110000, size=2 )
    sld1i = mrc.Bits( 0x00, 0b0000000000001111, size=2 )

    @property
    def sld2x( self ):
        return 0 if self.sld2a != 0b01 else (self.sld2i - 5)

    @property
    def sld2y( self ):
        return 0 if self.sld2a != 0b10 else (self.sld2i - 5)

    @property
    def sld2z( self ):
        return 0 if self.sld2a != 0b11 else (self.sld2i - 5)

    @property
    def sld1x( self ):
        return 0 if self.sld1a != 0b01 else (self.sld1i - 5)

    @property
    def sld1y( self ):
        return 0 if self.sld1a != 0b10 else (self.sld1i - 5)

    @property
    def sld1z( self ):
        return 0 if self.sld1a != 0b11 else (self.sld1i - 5)

    @property
    def repr( self ):
        return 'sld1: ({}, {}, {}), sld2: ({}, {}, {})'.format( self.sld1x, self.sld1y, self.sld1z, self.sld2x, self.sld2y, self.sld2z )


class NDBase( mrc.Block ):
    @property
    def ndx( self ):
        return self.nd // 9

    @ndx.setter
    def ndx( self, value ):
        assert value in range( -1, 2 )
        self.nd = (value+1)*9 + (self.ndy+1)*3 + (self.ndz+1)

    @property
    def ndy( self ):
        return (self.nd % 9) // 3

    @ndy.setter
    def ndy( self, value ):
        assert value in range( -1, 2 )
        self.nd = (self.ndx+1)*9 + (value+1)*3 + (self.ndz+1)

    @property
    def ndz( self ):
        return ((self.nd % 9) % 3)

    @ndz.setter
    def ndz( self ):
        assert value in range( -1, 2 )
        self.nd = (self.ndx+1)*9 + (self.ndy+1)*3 + (value+1)

    @property
    def repr( self ):
        return 'nd: ({}, {}, {})'.format( self.ndx, self.ndy, self.ndz )


class FusionP( NDBase ):
    const = mrc.Const( mrc.Bits( 0x00, 0b00000111 ), 0b111 )
    nd = mrc.Bits( 0x00, 0b11111000 )

class FusionS( NDBase ):
    const = mrc.Const( mrc.Bits( 0x00, 0b00000111 ), 0b110 )
    nd = mrc.Bits( 0x00, 0b11111000 )

class Fission( NDBase ):
    const = mrc.Const( mrc.Bits( 0x00, 0b00000111, size=1 ), 0b101 )
    nd = mrc.Bits( 0x00, 0b11111000, size=1 )
    m = mrc.UInt8( 0x01 )

class Fill( NDBase ):
    const = mrc.Const( mrc.Bits( 0x00, 0b00000111, size=1 ), 0b011 )
    nd = mrc.Bits( 0x00, 0b11111000, size=1 )




print(SMove(bytes((0b00010100,0b00011011))))
print(SMove(bytes((0b00110100,0b00001011))))
print(LMove(bytes((0b10011100,0b00001000))))
print(LMove(bytes((0b11101100,0b01110011))))


a = LMove()
a.sld2a = 2
print(a.export_data())
