import gc, sys, timeit

import numpy as np
import h5py
import eagle_IO.eagle_IO as E
import flares



if __name__ == "__main__":

    ii, tag, inp, data_folder, inpfile = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]


    num = str(ii)
    tag = str(tag)
    inp = str(inp)
    data_folder = str(data_folder)
    inpfile = str(inpfile)

    print("Wrting out required properties to hdf5")

    if inp == 'FLARES':
        if len(num) == 1:
            num =  '0'+num
        filename = './{}/FLARES_{}_sp_info.hdf5'.format(data_folder, num)
        sim_type = 'FLARES'


    elif inp == 'REF' or inp == 'AGNdT9':
        filename = F"./{data_folder}/EAGLE_{inp}_sp_info.hdf5"
        sim_type = 'PERIODIC'

    else:
        ValueError("Type of input simulation not recognized")

    fl = flares.flares(fname = filename,sim_type = sim_type)
    fl.create_group(tag)
    if inp == 'FLARES':
        dir = fl.directory
        sim = F"{dir}GEAGLE_{num}/data/"

    elif inp == 'REF':
        sim = fl.ref_directory

    elif inp == 'AGNdT9':
        sim = fl.agn_directory


    with h5py.File(filename, 'r') as hf:
        ok_centrals = np.array(hf[tag+'/Galaxy'].get('Central_Indices'), dtype = np.int64)
        indices = np.array(hf[tag+'/Galaxy'].get('Indices'), dtype = np.int64)
        dindex = np.array(hf[tag+'/Particle'].get('DM_Index'), dtype = np.int64)
        sindex = np.array(hf[tag+'/Particle'].get('S_Index'), dtype = np.int64)
        gindex = np.array(hf[tag+'/Particle'].get('G_Index'), dtype = np.int64)
        bhindex = np.array(hf[tag+'/Particle'].get('BH_Index'), dtype = np.int64)
        bh_mass = np.array(hf[tag+'/Galaxy'].get('BH_Mass'), dtype = np.float64)

    nThreads=8
    a = E.read_header('SUBFIND', sim, tag, 'ExpansionFactor')
    z = E.read_header('SUBFIND', sim, tag, 'Redshift')
    data = np.genfromtxt(inpfile, delimiter=',', dtype='str')
    for ii in range(len(data)):
        name = data[:,0][ii]
        path = data[:,1][ii]
        unit = data[:,3][ii]
        desc = data[:,4][ii]

        if 'PartType' in path:
            tmp = 'PARTDATA'
            location = 'Particle'
            if 'PartType0' in path:
                sel = gindex
            elif 'PartType1' in path:
                sel = dindex
            elif 'PartType4' in path:
                sel = sindex
            else:
                nok = np.where(bh_mass==0)[0]
                sel = bhindex
                location = 'Galaxy'
        else:
            tmp = 'SUBFIND'
            location = 'Galaxy'
            if 'FOF' in path:
                sel = ok_centrals
            else:
                sel = indices

        sel = np.asarray(sel, dtype=np.int64)
        try:
            out = E.read_array(tmp, sim, tag, path, noH=True, physicalUnits=True, numThreads=nThreads)[sel]
        except:
            if 'coordinates' in path.lower():
                out = np.zeros((len(indices),3))
            elif 'velocity' in path.lower():
                out = np.zeros((len(indices),3))
            else:
                out = np.zeros(len(indices))


        if 'age' in name.lower(): out = fl.get_age(out, z, nThreads)
        if 'PartType5' in path:
            if len(out.shape)>1:
                out[nok] = [0.,0.,0.]
            else:
                out[nok] = 0.


        if 'coordinates' in path.lower(): out=out.T/a
        if 'velocity' in path.lower(): out = out.T


        fl.create_dataset(out, name, '{}/{}'.format(tag, location),
            desc = desc.encode('utf-8'), unit = unit.encode('utf-8'))

        del out

    print (F'Completed writing required datasets from {inpfile}')
