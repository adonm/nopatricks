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

    def set_lld( self, x, y, z ):
        if (x == y == 0):
            self.lldz = z
        elif (x == z == 0):
            self.lldy = y
        elif (y == z == 0):
            self.lldx = x
        else:
            raise ValueError( 'only one axis allowed' )
        return self

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

    def set_sld1( self, x, y, z ):
        if (x == y == 0):
            self.sld1z = z
        elif (x == z == 0):
            self.sld1y = y
        elif (y == z == 0):
            self.sld1x = x
        else:
            raise ValueError( 'only one axis allowed' )
        return self

    def set_sld2( self, x, y, z ):
        if (x == y == 0):
            self.sld2z = z
        elif (x == z == 0):
            self.sld2y = y
        elif (y == z == 0):
            self.sld2x = x
        else:
            raise ValueError( 'only one axis allowed' )
        return self

    @property
    def sld2x( self ):
        return 0 if self.sld2a != 0b01 else (self.sld2i - 5)

    @sld2x.setter
    def sld2x( self, value ):
        assert value in range( -5, 11 )
        self.sld2a = 0b01
        self.sld2i = value + 5
    
    @property
    def sld2y( self ):
        return 0 if self.sld2a != 0b10 else (self.sld2i - 5)

    @sld2y.setter
    def sld2y( self, value ):
        assert value in range( -5, 11 )
        self.sld2a = 0b10
        self.sld2i = value + 5

    @property
    def sld2z( self ):
        return 0 if self.sld2a != 0b11 else (self.sld2i - 5)

    @sld2z.setter
    def sld2z( self, value ):
        assert value in range( -5, 11 )
        self.sld2a = 0b11
        self.sld2i = value + 5

    @property
    def sld1x( self ):
        return 0 if self.sld1a != 0b01 else (self.sld1i - 5)

    @sld1x.setter
    def sld1x( self, value ):
        assert value in range( -5, 11 )
        self.sld2a = 0b01
        self.sld2i = value + 5

    @property
    def sld1y( self ):
        return 0 if self.sld1a != 0b10 else (self.sld1i - 5)

    @sld1y.setter
    def sld1y( self, value ):
        assert value in range( -5, 11 )
        self.sld2a = 0b10
        self.sld2i = value + 5

    @property
    def sld1z( self ):
        return 0 if self.sld1a != 0b11 else (self.sld1i - 5)

    @sld1z.setter
    def sld1z( self, value ):
        assert value in range( -5, 11 )
        self.sld2a = 0b11
        self.sld2i = value + 5

    @property
    def repr( self ):
        return 'sld1: ({}, {}, {}), sld2: ({}, {}, {})'.format( self.sld1x, self.sld1y, self.sld1z, self.sld2x, self.sld2y, self.sld2z )


class NDBase( mrc.Block ):
    def set_nd( self, x, y, z ):
        self.ndx = x
        self.ndy = y
        self.ndz = z
        return self

    @property
    def ndx( self ):
        return (self.nd // 9)-1

    @ndx.setter
    def ndx( self, value ):
        assert value in range( -1, 2 )
        self.nd = (value+1)*9 + (self.ndy+1)*3 + (self.ndz+1)

    @property
    def ndy( self ):
        return ((self.nd % 9) // 3)-1

    @ndy.setter
    def ndy( self, value ):
        assert value in range( -1, 2 )
        self.nd = (self.ndx+1)*9 + (value+1)*3 + (self.ndz+1)

    @property
    def ndz( self ):
        return ((self.nd % 9) % 3)-1

    @ndz.setter
    def ndz( self, value ):
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

    def set_m( self, m ):
        self.m = m
        return self

    @property
    def repr( self ):
        return 'nd: ({}, {}, {}), m: {}'.format( self.ndx, self.ndy, self.ndz, self.m )
    
class Fill( NDBase ):
    const = mrc.Const( mrc.Bits( 0x00, 0b00000111, size=1 ), 0b011 )
    nd = mrc.Bits( 0x00, 0b11111000, size=1 )


def read_nbt( data ):
    return [x for x in read_nbt_iter( data )]


def read_nbt_iter( data ):
    pointer = 0
    while pointer < len( data ):
        if data[pointer] == 0xff:
            yield Halt()
            pointer += 1
        elif data[pointer] == 0xfe:
            yield Wait()
            pointer += 1
        elif data[pointer] == 0xfd:
            yield Flip()
            pointer += 1
        elif data[pointer] & 0b1111 == 0b0100:
            yield SMove( data[pointer:pointer+2] )
            pointer += 2
        elif data[pointer] & 0b1111 == 0b1100:
            yield LMove( data[pointer:pointer+2] )
            pointer += 2
        elif data[pointer] & 0b111 == 0b111:
            yield FusionP( data[pointer:pointer+1] )
            pointer += 1
        elif data[pointer] & 0b111 == 0b110:
            yield FusionS( data[pointer:pointer+1] )
            pointer += 1
        elif data[pointer] & 0b111 == 0b101:
            yield Fission( data[pointer:pointer+2] )
            pointer += 2
        elif data[pointer] & 0b111 == 0b011:
            yield Fill( data[pointer:pointer+1] )
            pointer += 1
        else:
            raise ValueError( 'wasn\'t expecting a {:02x} at {}'.format( data[pointer], pointer ) )

    return

def export_nbt( commands ):
    result = bytearray()
    for i, c in enumerate(commands):
        if i % 1000 == 0:
            print(i)
        result.extend( c.export_data() )
    return result


