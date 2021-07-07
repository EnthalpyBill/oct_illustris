import numpy as np

def loadFile(fn, partType, fields=None, mdi=None, float32=True):
    """ Load a subset of fileds for all particles/cells of a given partType
        in one file. """

    # Make sure fields is not a single element
    if isinstance(fields, str):
        fields = [fields]

    # Make sure partType is not a single element
    if isinstance(partType, str):
        partType = [partType]
    
    result = {}
    with h5py.File(fn, "r") as f:
        for p in partType:
            ptNum = partTypeNum(p)
            gName = "PartType%d"%(ptNum)

            numType = f["Header"].attrs["NumPart_ThisFile"][ptNum]
            result[gName]["count"] = numType

            if not numType:
                continue

            # Allocate within return dict
            dtype = f[gName][field].dtype
            shape = f[gName][field].shape
            if dtype == np.float64 and float32: dtype = np.float32
            result[gName][field] = np.zeros(shape, dtype=dtype)

            # Loop over each requested field for this particle type
            for i, field in enumerate(fields):
                # Read data local to the current file
                    result[gName][field] = f[gName][field][:]
                else:
                    result[gName][field] = f[gName][field][:,mdi[i]]

    return result

def partTypeNum(partType):
    """ Mapping between common names and numeric particle types. """
    if str(partType).isdigit():
        return int(partType)
        
    if str(partType).lower() in ["gas","cells"]:
        return 0
    if str(partType).lower() in ["dm","darkmatter"]:
        return 1
    if str(partType).lower() in ["tracer","tracers","tracermc","trmc"]:
        return 3
    if str(partType).lower() in ["star","stars","stellar"]:
        return 4 # only those with GFM_StellarFormationTime>0
    if str(partType).lower() in ["wind"]:
        return 4 # only those with GFM_StellarFormationTime<0
    if str(partType).lower() in ["bh","bhs","blackhole","blackholes"]:
        return 5
    
    raise Exception("Unknown particle type name.")

def snapPath(basePath, snapNum, chunkNum=0):
    """ Return absolute path to a snapshot HDF5 file (modify as needed). """
    snapPath = basePath + "/snapdir_%03d/"%(snapNum)
    filePath = snapPath + "snap_%03d.%d.hdf5"%(snapNum, chunkNum)
    return filePath

def getNumPart(header):
    """ Calculate number of particles of all types given a snapshot header. """
    nTypes = 6

    nPart = np.zeros(nTypes, dtype="i4")
    for j in range(nTypes):
        nPart[j] = (header["NumPart_Total"][j] | 
            (header["NumPart_Total_HighWord"][j] << 32))

    return nPart