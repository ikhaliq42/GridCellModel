#
#   place_cells.py
#
#   Place cell simulation class.
#
#       Copyright (C) 2012  Lukas Solanka <l.solanka@sms.ed.ac.uk>
#
#       This program is free software: you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation, either version 3 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import numpy as np


__all__ = ['PlaceCells', 'UniformBoxPlaceCells']



class PlaceCells(object):
    '''
    A class to simulate place cells. This base class simply takes as an argument
    the number of place cells and the distribution of preferred positions and
    widths of the fields. The fields are then simulated as Gaussian functions of
    a position of the animal. The output is an "instantaneous" firing rate of
    each place cell, given a position.
    '''

    def __init__(self, N, maxRates, centers, widths):
        '''
        '''
        self.N          = N
        self.maxRates   = np.array(maxRates)
        self.centers    = np.array(centers)
        if isinstance(widths, int):
            self.widths = widths
        else:
            self.widths     = np.array(widths)

        #print self.centers.shape

        if (self.centers.shape != (self.N, 2)):
            raise Exception('centers must be an array with dimensions (N, 2)')


    def getFiringRates(self, pos):
        '''
        Return a vector of firing rates for each place cell, given position
        'pos'
        '''
        return self.maxRates * \
                np.exp(- ((pos[0] - self.centers[:, 0])**2 + (pos[1] - self.centers[:, 1])**2) /\
                (2.0*self.widths**2))


    def getFiringField(self, positions, neuronN):
        '''
        Return a firing field for a list of positions of a cell with id 'neuronN'

        neuronN     An integer ID of the neuron
        positions   A tuple of position arrays (X, Y)
        '''
        if isinstance(self.widths, int):
            width = self.widths
        else:
            width = self.widths[neuronN]

        return self.maxRates * \
                np.exp(- ((positions[0] - self.centers[neuronN, 0])**2 +
                    (positions[1] - self.centers[neuronN, 1])**2) /\
                    (2.0*width**2))


    def remap(self, envN):
        '''
        Remap the centers and possibly firing rates to the environment number
        envN
        '''
        raise NotImplementedError


class UniformBoxPlaceCells(PlaceCells):
    '''
    Generate a uniform distribution of place cells in a 2D environment of a
    rectangular shape.
    '''

    def __init__(self, boxSize, N, maxRates, widths, random = False):
        '''
        N        A tuple containing number of place cells in each dimension (X, Y)
        maxRates An array of size Nx*Ny specifying max. firing rate in the place
                    field.
        widths   An array of widths of place fields (they are circular)
        random   Uniform, but from a random distribution?
        '''
        self.boxSize = boxSize

        if (boxSize[0] <= 0 or boxSize[1] <= 0):
            raise Exception('boxSize dimenstions must be positive!')

        if not random:
            # Uniform grid
            if N[0] == 1:
                cx			 = np.array([0.0])
            else:
                cx           = np.linspace(-self.boxSize[0]/2.0, self.boxSize[0]/2.0, N[0])
            if N[1] == 1:
                cy			 = np.array([0.0])
            else:
                cy           = np.linspace(-self.boxSize[1]/2.0, self.boxSize[1]/2.0, N[1])
            ctr_x, ctr_y = np.meshgrid(cx, cy)
            centers = np.vstack((ctr_x.flatten(), ctr_y.flatten())).T
        else:
            # Draw from a random distribution
            centers = np.random.rand(N[0]*N[1], 2) - 0.5
            centers[:, 0] *= self.boxSize[0]
            centers[:, 1] *= self.boxSize[1]

        PlaceCells.__init__(self, N[0]*N[1], maxRates, centers, widths)



    def getFiringFields(self, Ns, dx):
        '''
        Get firing fields of neurons specified in Ns.
        if Ns is None, return firing fields for all neurons

        dx      Spacing of positions in the box
        '''
        if Ns is None:
            Narr = np.arange(self.N)
        else:
            Narr = Ns

        posX = np.arange(-self.boxSize[0]/2.0, self.boxSize[0]/2.0, dx)
        posY = np.arange(-self.boxSize[1]/2.0, self.boxSize[1]/2.0, dx)

        fields = np.ndarray((len(Narr), len(posY), len(posX)))
        for posX_it in xrange(len(posX)):
            for posY_it in xrange(len(posY)):
                fields[:, posY_it, posX_it] = self.getFiringRates((posX[posX_it], posY[posY_it]))

        return fields, (posX, posY)


    def getSingleCellFiringField(self, neuronN, dx):
        '''
        Return a firing field of a single place cell.

        dx      Spacing of positions in the box
        '''
        posX = np.arange(-self.boxSize[0]/2.0, self.boxSize[0]/2.0, dx)
        posY = np.arange(-self.boxSize[1]/2.0, self.boxSize[1]/2.0, dx)

        positions = np.meshgrid(posX, posY)
        field = self.getFiringField(positions, neuronN)

        return (field, positions)

class BoxOutlinePlaceCells():
    '''
    Similar to UniformBoxPlaceCells but only the outer perimeter.
    '''

    def __init__(self, boxSize, N, maxRates, widths):
        '''
        N        A tuple containing number of place cells in each dimension (X, Y)
        maxRates An array of size Nx*Ny specifying max. firing rate in the place
                    field.
        widths   An array of widths of place fields (they are circular)
        random   Uniform, but from a random distribution?
        '''
        self.boxSize = boxSize

        if (boxSize[0] <= 0 or boxSize[1] <= 0):
            raise Exception('boxSize dimenstions must be positive!')

        # Uniform box outline
        cx_top    = np.linspace(-self.boxSize[0]/2.0, self.boxSize[0]/2.0, N[0])
        cx_right  = np.linspace( self.boxSize[1]/2.0, self.boxSize[1]/2.0, N[1])		
        cx_bottom = np.linspace( self.boxSize[0]/2.0,-self.boxSize[0]/2.0, N[0])
        cx_left   = np.linspace(-self.boxSize[1]/2.0,-self.boxSize[1]/2.0, N[1])
        ctr_x     = np.hstack((cx_top, cx_right[range(1,N[1]-1)], 
                                    cx_bottom, cx_left[range(1,N[1]-1)]))
        
        cy_top    = np.linspace( self.boxSize[0]/2.0, self.boxSize[0]/2.0, N[0])
        cy_right  = np.linspace( self.boxSize[1]/2.0,-self.boxSize[1]/2.0, N[1])		
        cy_bottom = np.linspace(-self.boxSize[0]/2.0,-self.boxSize[0]/2.0, N[0])
        cy_left   = np.linspace(-self.boxSize[1]/2.0, self.boxSize[1]/2.0, N[1])
        ctr_y     = np.hstack((cy_top, cy_right[range(1,N[1]-1)], 
                                    cy_bottom, cy_left[range(1,N[1]-1)]))
        
        self.centers = np.vstack((ctr_x, ctr_y)).T

class CentredPlaceCells():
    '''
    Place cells which are all located in the centre of the arena.
    '''

    def __init__(self, boxSize, N, maxRates, widths):
        '''
        N        A tuple containing number of place cells in each dimension (X, Y) 
        boxSize  Tuple showing arena dimensions, x then y
        maxRates An array of size Nx*Ny specifying max. firing rate in the place
                    field.
        widths   An array of widths of place fields (they are circular)
        random   Uniform, but from a random distribution?
        '''
        self.boxSize = boxSize

        if (boxSize[0] <= 0 or boxSize[1] <= 0):
            raise Exception('boxSize dimenstions must be positive!')
            
        ctr_x = np.array([0.0] * N[0])
        ctr_y = np.array([0.0] * N[1])
        
        self.centers = np.vstack((ctr_x, ctr_y)).T


if __name__ == '__main__':
    from matplotlib.pyplot import *

    boxSize = (121, 200)
    N = (200, 200)
    totalSz = N[0]*N[1]
    maxRates = 15
    widths = 40

    PC = UniformBoxPlaceCells(boxSize, N, maxRates, widths, random=True)
    print PC.centers

    pos = (0, 0)
    print PC.getFiringRates(pos)

    fields_dx = 2
    #fields, (posX, posY) = PC.getFiringFields(None, fields_dx)
    #X, Y = np.meshgrid(posX, posY)
    #for it in xrange(N[0]*N[1]):
    #    figure()
    #    pcolor(X, Y, fields[it, :, :])

    # Single cell firing field
    neuronN = 0
    field, positions = PC.getSingleCellFiringField(neuronN, fields_dx)
    figure()
    pcolor(positions[0], positions[1], field)
    axis('equal')
    colorbar()


    figure()
    plot(PC.centers[:, 0], PC.centers[:, 1], '.')
    show()



