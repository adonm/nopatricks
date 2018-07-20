import unittest

import commands

class TestCommands(unittest.TestCase):
    def test_smove1( self ):
        dat = bytes((0b00010100, 0b00011011))
        s = commands.SMove( dat )
        self.assertEqual( (s.lldx, s.lldy, s.lldz), (12, 0, 0) )
        self.assertEqual( s.export_data(), dat )

    def test_smove2( self ):
        dat = bytes((0b00110100, 0b00001011))
        s = commands.SMove( dat )
        self.assertEqual( (s.lldx, s.lldy, s.lldz), (0, 0, -4) )
        self.assertEqual( s.export_data(), dat )

    def test_lmove1( self ):
        dat = bytes((0b10011100, 0b00001000))
        s = commands.LMove( dat )
        self.assertEqual( (s.sld1x, s.sld1y, s.sld1z), (3, 0, 0) )
        self.assertEqual( (s.sld2x, s.sld2y, s.sld2z), (0, -5, 0) )
        self.assertEqual( s.export_data(), dat )

    def test_lmove2( self ):
        dat = bytes((0b11101100, 0b01110011))
        s = commands.LMove( dat )
        self.assertEqual( (s.sld1x, s.sld1y, s.sld1z), (0, -2, 0) )
        self.assertEqual( (s.sld2x, s.sld2y, s.sld2z), (0, 0, 2) )
        self.assertEqual( s.export_data(), dat )

    def test_fusionp( self ):
        dat = bytes((0b00111111,))
        s = commands.FusionP( dat )
        self.assertEqual( (s.ndx, s.ndy, s.ndz), (-1, 1, 0) )
        self.assertEqual( s.export_data(), dat )

    def test_fusions( self ):
        dat = bytes((0b10011110,))
        s = commands.FusionS( dat )
        self.assertEqual( (s.ndx, s.ndy, s.ndz), (1, -1, 0) )
        self.assertEqual( s.export_data(), dat )

    def test_fission( self ):
        dat = bytes((0b01110101,0b00000101))
        s = commands.Fission( dat )
        self.assertEqual( (s.ndx, s.ndy, s.ndz), (0, 0, 1) )
        self.assertEqual( s.m, 5 )
        self.assertEqual( s.export_data(), dat )

    def test_fill( self ):
        dat = bytes((0b01010011,))
        s = commands.Fill( dat )
        self.assertEqual( (s.ndx, s.ndy, s.ndz), (0, -1, 0) )
        self.assertEqual( s.export_data(), dat )

    def test_roundtrip( self ):
        with open('dfltTracesL/LA095.nbt', 'rb') as f:
            data = f.read()
            cmds = commands.read_nbt_iter( data )
            out = commands.export_nbt( cmds )
            self.assertEqual( data, out )

        
if __name__ == '__main__':
    unittest.main()
