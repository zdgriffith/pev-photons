from icecube import icetray, dataclasses, tableio
import numpy as np
import cPickle as cp

# temporarily called 'python_converters' as this would conflict with boost.python-generated module 'converters'


class PulsesInShowerCS(tableio.I3Converter):

    # this class expects an object of the the type I3RecoPulseSeriesMap
    booked = dataclasses.I3RecoPulseSeriesMap

    def __init__(self, axis, SLC_TCorr_pickle=False):
        tableio.I3Converter.__init__(self)
        self.axis = axis
        self.SLC_TCorr = SLC_TCorr_pickle

    def GetNumberOfRows(self, frame_object):
        return sum([len(o) for o in frame_object.values()])

    def CreateDescription(self, pulses):
        desc = tableio.I3TableRowDescription()
        desc.is_multi_row = True
        desc.add_field('string',       tableio.types.Int32,   '',    'String number')
        desc.add_field('om',           tableio.types.Int32,   '',    'OM number')
        desc.add_field('pmt',          tableio.types.Int32,   '',    'PMT number')
        desc.add_field('x',            tableio.types.Float64, 'm',   'OM x-coordinate in shower coordinate system')
        desc.add_field('y',            tableio.types.Float64, 'm',   'OM y-coordinate in shower coordinate system')
        desc.add_field('z',            tableio.types.Float64, 'm',   'OM z-coordinate in shower coordinate system')
        desc.add_field('vector_index', tableio.types.Int32,   '',    '')
        desc.add_field('time',         tableio.types.Float64, 'ns',  "Signal start time relative to the shower's plane front")
        desc.add_field('charge',       tableio.types.Float64, '',    'Charge in VEM')
        desc.add_field('width',        tableio.types.Float64, '',    '%s useless description'%self.axis)
        desc.add_field('flags',        tableio.types.Int8,    '',    '')
        desc.add_field('phi',          tableio.types.Float64, 'rad', 'Polar angle of the OM position in the shower plane (0 points up-stream)')
        desc.add_field('rho',          tableio.types.Float64, 'm',   'Radial distance from OM to shower axis')
        desc.add_field('X',            tableio.types.Float64, 'm',   'OM x-coordinate in detector coordinate system')
        desc.add_field('Y',            tableio.types.Float64, 'm',   'OM y-coordinate in detector coordinate system')
        desc.add_field('Z',            tableio.types.Float64, 'm',   'OM z-coordinate in detector coordinate system')
        desc.add_field('T',            tableio.types.Float64, 'ns',  'Time of the pulse')
        desc.add_field('N',            tableio.types.Float64, '',    'Number of pulses')
        desc.add_field('total_dt',     tableio.types.Float64, '',    'sum of the time residuals')
        if self.SLC_TCorr:
            desc.add_field('T_corrected',            tableio.types.Float64, '',  'SLC Time After correction')
            desc.add_field('time_corrected',            tableio.types.Float64, '',  'SLC Time After correction w.r.t shower plane front')

        return desc
    def Convert(self, pulses, row, frame):
        from icecube.dataclasses import I3Constants
        from pev_photons.event_selection.llh_ratio_scripts.tools import to_shower_cs, tank_geometry
        import math
        import numpy

        
        if self.axis in frame:
            axis = frame[self.axis]
        else:
            axis = dataclasses.I3Particle()

        if self.SLC_TCorr:
            f=open(self.SLC_TCorr,'r')
            mean_slc_charge = np.array( cp.load(f) )
            median_time_diff = np.array( cp.load(f) )
            variance_time = np.array( cp.load(f) )
            f.close()    

        rotation = to_shower_cs(axis)
        origin = numpy.array([[axis.pos.x], [axis.pos.y], [axis.pos.z]])

        geometry = frame['I3Geometry']
        N = sum([len(o) for o in pulses.values()])
        n_pulses = 0
        #print "rotation",rotation
        total_dt = 0.
	#print pulses
        for k,m in pulses.iteritems():
            for i,pulse in enumerate(m):
                if not k in geometry.omgeo:
                    print "Warning! OM {om} not in geometry!".format(om=k)
                    continue
                
                row.current_row = n_pulses
                # nah!...hp. # We do not use the OM position but the tank position
                # changed... using om position....hp. #The tank position is the middle point between the two DOMs in the station
                position = geometry.omgeo[k].position
                #position = tank_geometry(geometry, k).position
                shower_cs_position = numpy.array([[position.x],
                                                  [position.y],
                                                  [position.z]])
                shower_cs_position = rotation*(shower_cs_position - origin)
                time = pulse.time - float(axis.time - shower_cs_position[2]/ I3Constants.c)
                total_dt += time

                row['string']        = k.string
                row['om']            = k.om
                row['pmt']           = k.pmt
                row['x']             = float(shower_cs_position[0])
                row['y']             = float(shower_cs_position[1])
                row['z']             = float(shower_cs_position[2])
                row['phi']           = math.atan(float(shower_cs_position[1])/float(shower_cs_position[0]))
                row['rho']           = math.sqrt(float(shower_cs_position[0])**2 + float(shower_cs_position[1])**2)
                row['vector_index']  = n_pulses
                row['time']          = time
                row['charge']        = pulse.charge
                row['width']         = pulse.width
                row['flags']         = pulse.flags
                row['X']             = position.x
                row['Y']             = position.y
                row['Z']             = position.z
                row['T']             = pulse.time
                row['N']             = N

                if self.SLC_TCorr:
                    if pulse.charge<=0 or pulse.charge*0!=0:
                        row['T_corrected'] = pulse.time
                        row['time_corrected'] = time
                    else:
                        xx = np.log10(pulse.charge)
                        yy = np.absolute(xx - mean_slc_charge)
                        select = yy==np.amin(yy)
                        correction = np.float(median_time_diff[select])

                        row['T_corrected'] = pulse.time + correction
                        row['time_corrected'] = time + correction

                #print '  OMKey({string},{om},{pmt}): ({X}, {Y}, {Z}) -> ({x}, {y}, {z})'.format(**row)
                n_pulses += 1

        count = 0
        for k,m in pulses.iteritems():
            for i,pulse in enumerate(m):
                if not k in geometry.omgeo:
                    print "Warning! OM {om} not in geometry!".format(om=k)
                    continue
                row.current_row = count
                row['total_dt'] = total_dt
                count += 1

        return n_pulses
