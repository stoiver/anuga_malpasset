"""Validation study of Merimbula lake using Pyvolution.
Example of shallow water wave equation applied to
Malpasset dam break simulation.

   Copyright 2004
   Christopher Zoppou, Stephen Roberts
   Australian National University
   
Specific methods pertaining to the 2D shallow water equation
are imported from shallow_water
for use with the generic finite volume framework

Conserved quantities are h, uh and vh stored as elements 0, 1 and 2 in the
numerical vector named conserved_quantities.

Existence of file 'Malpasset_26000.tsh' is assumed.
"""

###############################
# Setup Path and import modules

import sys
from os import sep, path

#print path
#print sep

import anuga
from anuga.geometry.polygon_function import Polygon_function
from anuga_parallel import distribute, myid, numprocs, finalize, barrier

######################
# Domain
#filename = 'malpasset_26000_merged.tsh'
filename = 'malpasset_46691_mesh.tsh'
yieldstep = 15
finaltime = 3000

if myid == 0:
    print 'Creating domain from', filename
    domain = anuga.Domain(filename, verbose=True, use_cache=True)
    print "Number of triangles = ", len(domain)

    domain.set_flow_algorithm('2_0_limited')
    domain.set_minimum_allowed_height(0.01)
    domain.set_minimum_storable_height(0.1)
    domain.set_name('Malpasset_second_order')

    #------------------
    #Initial conditions
    #------------------
    domain.set_quantity('stage', expression='elevation')
    domain.maximum_quantity('stage',-0.2)

    p0 = [[4701.18,4143.41],[4655.5,4392.10],[3000.,7000.],[0.,7000.],[0.,1000.],[5000.,1000.]]
    domain.maximum_quantity('stage',Polygon_function([(p0,75.0)],default=-100000.0))


    domain.set_quantity('friction', 0.033)

else:
    domain = None

domain = distribute(domain)


#------------------------------
# Boundary Conditions
#------------------------------
Br = anuga.Reflective_boundary(domain)
domain.set_boundary({'external' : Br, 'open' : Br})


elevation = domain.get_quantity('elevation')
stage = domain.get_quantity('stage')

int_elevation_0 = elevation.get_integral()
int_stage_0 = stage.get_integral()

print 'Water Volume ', int_stage_0 - int_elevation_0


######################
#Evolution
import time
t0 = time.time()
for t in domain.evolve(yieldstep = yieldstep, finaltime = finaltime):
    domain.write_time()
    
print 'That took %.2f seconds' %(time.time()-t0)

    
domain.sww_merge()
finalize()
