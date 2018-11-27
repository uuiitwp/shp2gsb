# coding:utf-8
import arcpy
import sys
import struct
import datetime
import collections
from numpy import arange

DB_NE = "DB_东北"
DB_NW = "DB_西北"
DB_SE = "DB_东南"
DB_SW = "DB_西南"
DL_NE = "DL_东北"
DL_NW = "DL_西北"
DL_SE = "DL_东南"
DL_SW = "DL_西南"


NUM_OREC = 11
NUM_SREC = 11
NUM_FILE = 1
GS_TYPE = "SECONDS"
VERSION = "NTv2.0"
SYSTEM_F = "XIAN_80"
SYSTEM_T = "CGCS2000"
MAJOR_F = 6378140.0
MINOR_F = 6356755.288157528
MAJOR_T = 6378137.0
MINOR_T = 6356752.314140356
SUB_NAME = "NONE"
PARENT = "NONE"
CREATED = datetime.datetime.now().strftime("%Y%m%d")
UPDATED = CREATED
S_LAT = None
N_LAT = None
E_LONG = None
W_LONG = None
LAT_INC = None
LONG_INC = None
GS_COUNT = None
END = "END"


_NUM_OREC = "4e554d5f4f524543"
_NUM_SREC = "4e554d5f53524543"
_NUM_FILE = "4e554d5f46494c45"
_GS_TYPE = "47535f5459504520"
_VERSION = "56455253494f4e20"
_SYSTEM_F = "53595354454D5F46"
_SYSTEM_T = "53595354454D5F54"
_MAJOR_F = "4D414A4F525F4620"
_MINOR_F = "4D494E4F525F4620"
_MAJOR_T = "4D414A4F525F5420"
_MINOR_T = "4D494E4F525F5420"
_SUB_NAME = "5355425F4E414D45"
_PARENT = "504152454E542020"
_CREATED = "4352454154454420"
_UPDATED = "5550444154454420"
_S_LAT = "535F4C4154202020"
_N_LAT = "4E5F4C4154202020"
_E_LONG = "455F4C4F4E472020"
_W_LONG = "575F4C4F4E472020"
_LAT_INC = "4C41545F494E4320"
_LONG_INC = "4C4F4E475F494E43"
_GS_COUNT = "47535F434F554E54"
_END = "0000000000000000"


def dbl2bin(double):
    return struct.pack("<d", double)


def flt2bin(flot):
    return struct.pack("<f", flot)


def int2bin(i):
    return struct.pack("<q", i)


def fillstrTo8(s):
    return s[:8].ljust(8, chr(0x20))


class shp:
    def __init__(self, lyrpath):
        dic = collections.OrderedDict()
        self.lyr = arcpy.mapping.Layer(lyrpath)
        with arcpy.da.SearchCursor(
                self.lyr, ["SHAPE@", DB_NE, DB_NW, DB_SE, DB_SW, DL_NE, DL_NW, DL_SE, DL_SW]) as search:
            for row in search:
                shape = row[0]
                ext = shape.extent
                self.w, self.h = ext.width, ext.height
                centroid = shape.centroid
                ne = round(- (centroid.X + ext.width / 2) * 3600,
                           3), round((centroid.Y + ext.height / 2) * 3600, 3)
                negs = gridshift(-row[5], row[1])
                dic[ne] = negs
                nw = -round((centroid.X - ext.width / 2) * 3600,
                            3), round((centroid.Y + ext.height / 2) * 3600, 3)
                nwgs = gridshift(-row[6], row[2])
                dic[nw] = nwgs
                se = - round((centroid.X + ext.width / 2) * 3600,
                             3), round((centroid.Y - ext.height / 2) * 3600, 3)
                segs = gridshift(-row[7], row[3])
                dic[se] = segs
                sw = - round((centroid.X - ext.width / 2) * 3600,
                             3), round((centroid.Y - ext.height / 2) * 3600, 3)
                swgs = gridshift(-row[8], row[4])
                dic[sw] = swgs
        self.dic = dic

    def getExtent(self):
        ext = self.lyr.getExtent()
        xmax = round(-ext.XMin*3600, 3)
        xmin = round(-ext.XMax*3600, 3)
        ymin = round(ext.YMin*3600, 3)
        ymax = round(ext.YMax*3600, 3)
        global S_LAT, N_LAT, E_LONG, W_LONG 
        S_LAT = ymin
        N_LAT = ymax
        E_LONG = xmin
        W_LONG = xmax
        return xmin, xmax, ymin, ymax

    def getgirdshifts(self):
        xmin, xmax, ymin, ymax = self.getExtent()
        dy = round(self.h*3600, 3)
        dx = round(self.w*3600, 3)
        global LAT_INC, LONG_INC 
        LAT_INC = dy
        LONG_INC = dx
        results = []
        for y in arange(ymin, ymax + dy, dy):
            for x in arange(xmin, xmax + dx, dx):
                gs = self.dic.get((x, y), gridshift(0, 0))
                results.append(gs.torow())
        return results


class gridshift:
    def __init__(self, xshift, yshift):
        self.xshift = xshift
        self.yshift = yshift
        self.x = 0
        self.y = 0

    def torow(self):
        return flt2bin(self.yshift) + flt2bin(self.xshift) + flt2bin(self.y) + flt2bin(self.x)

    def __repr__(self):
        return (self.yshift, self.xshift).__repr__()


def write(lyrpath, outputpath):
    s2g = shp(lyrpath)
    lines = s2g.getgirdshifts()
    f = open(outputpath, 'wb')
    f.write(_NUM_OREC.decode('hex'))
    f.write(int2bin(NUM_OREC))

    f.write(_NUM_SREC.decode('hex'))
    f.write(int2bin(NUM_SREC))

    f.write(_NUM_FILE.decode('hex'))
    f.write(int2bin(NUM_FILE))

    f.write(_GS_TYPE.decode('hex'))
    f.write(fillstrTo8(GS_TYPE))

    f.write(_VERSION.decode('hex'))
    f.write(fillstrTo8(VERSION))

    f.write(_SYSTEM_F.decode('hex'))
    f.write(fillstrTo8(SYSTEM_F))

    f.write(_SYSTEM_T.decode('hex'))
    f.write(fillstrTo8(SYSTEM_T))

    f.write(_MAJOR_F.decode('hex'))
    f.write(dbl2bin(MAJOR_F))

    f.write(_MINOR_F.decode('hex'))
    f.write(dbl2bin(MINOR_F))

    f.write(_MAJOR_T.decode('hex'))
    f.write(dbl2bin(MAJOR_T))

    f.write(_MINOR_T.decode('hex'))
    f.write(dbl2bin(MINOR_T))

    f.write(_SUB_NAME.decode('hex'))
    f.write(fillstrTo8(SUB_NAME))

    f.write(_PARENT.decode('hex'))
    f.write(fillstrTo8(PARENT))

    f.write(_CREATED.decode('hex'))
    f.write(fillstrTo8(CREATED))

    f.write(_UPDATED.decode('hex'))
    f.write(fillstrTo8(UPDATED))

    f.write(_S_LAT.decode('hex'))
    f.write(dbl2bin(S_LAT))

    f.write(_N_LAT.decode('hex'))
    f.write(dbl2bin(N_LAT))

    f.write(_E_LONG.decode('hex'))
    f.write(dbl2bin(E_LONG))

    f.write(_W_LONG.decode('hex'))
    f.write(dbl2bin(W_LONG))

    f.write(_LAT_INC.decode('hex'))
    f.write(dbl2bin(LAT_INC))

    f.write(_LONG_INC.decode('hex'))
    f.write(dbl2bin(LONG_INC))

    GS_COUNT = len(lines)

    f.write(_GS_COUNT.decode('hex'))
    f.write(int2bin(GS_COUNT))

    f.write(''.join(lines))

    
    f.write(fillstrTo8(END))
    f.write(_END.decode('hex'))
    f.close()


if __name__ == "__main__":

    write(sys.argv[1],
          sys.argv[2])
