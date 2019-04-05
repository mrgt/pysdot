from pysdot.radial_funcs import RadialFuncInBall
from pysdot import OptimalTransport

from scipy.sparse.linalg import spsolve
from scipy.sparse import csr_matrix
from scipy.linalg import eigvals
import numpy as np
import scipy
import sys

import matplotlib.pyplot as plt

class FluidSystem:
    def __init__(self, domain, positions, velocities, masses, base_filename):
        self.ot = OptimalTransport(domain, RadialFuncInBall())
        self.ot.set_positions(np.array(positions))
        self.ot.set_weights(np.array(masses)/np.pi)
        self.ot.set_masses(np.array(masses))

        self.base_filename = base_filename
        self.cpt_display = 0

        self.ot.update_weights()
        self.centroids = self.ot.get_centroids()
        self.velocities = np.array(velocities)

    def display(self):
        fn = "{}{}.vtk".format(self.base_filename, self.cpt_display)
        self.ot.display_vtk(fn, points=True)
        self.cpt_display += 1

    def make_step(self, dt=1.0):
        # target centroid positions + initial guess for the dirac positions
        adv = dt * self.velocities
        target_centroids = self.centroids + adv
        self.ot.set_positions(self.ot.get_positions() + adv)

        # stuff to extract centroids, masses, ...
        d = self.ot.dim()
        n = self.ot.nb_diracs()
        rd = np.arange(d * n, dtype=np.int)
        b0 = (d + 1) * np.floor_divide(rd, d)
        l0 = b0 + rd % d
        l1 = (d + 1) * np.arange(n, dtype=np.int) + d

        # find weights and positions to fit the target centroid positions
        for _ in range(1):
            # search dir
            mvs = self.ot.pd.der_centroids_and_integrals_wrt_weight_and_positions()
            if mvs.error:
                sys.exit(1)

            M = csr_matrix((mvs.m_values, mvs.m_columns, mvs.m_offsets))
            # print("m",np.min(np.real(eigvals(M.todense()))))

            V = mvs.v_values
            V[l0] -= target_centroids.flatten()
            V[l1] -= self.ot.get_masses()

            X = spsolve(M, V)

            v = []
            for l in np.linspace(0,2,100):
                v.append(np.sum(self.ot.get_centroids()-target_centroids))

            self.ot.set_positions(self.ot.get_positions() - X[l0].reshape((-1,d)))
            self.ot.set_weights(self.ot.get_weights() - X[l1])
            e = np.linalg.norm(X)
            if e < 1e-5:
                break



# def obj(cx, ot, bh, dt):
#     pc = cx.reshape((-1, 2))
#     ot.set_positions(pc)
#     ot.update_weights()

#     bm = np.array(bh[-2].flat)
#     b0 = np.array(bh[-1].flat)
#     bc = np.array(ot.get_centroids().flat)
#     bt = 2 * b0 - bm

#     dlt = bc - bt
#     dlp = cx - bt
#     return 0.5 * np.sum(dlt**2) \
#         + 0.5 * 1e-4 * np.sum(dlp**2)


# def jac(cx, ot, bh, dt):
#     nb_diracs = ot.nb_diracs()
#     dim = ot.dim()

#     # get G

#     rd = np.arange(dim * nb_diracs, dtype=np.int)
#     b0 = (dim + 1) * np.floor_divide(rd, dim)
#     l0 = b0 + rd % dim
#     C = m[l0, :][:, l0]

#     # centroids
#     pc = cx.reshape((-1, 2))
#     ot.set_positions(pc)

#     bm = np.array(bh[-2].flat)
#     b0 = np.array(bh[-1].flat)
#     bc = np.array(ot.get_centroids().flat)
#     bt = 2 * b0 - bm

#     dlt = bc - bt
#     # dlp = cx - bt
#     return C.transpose() * dlt  # + 1e-2 * bt


# def get_new_positions_for_centroids(ot, bh, dt):
#     ropt = scipy.optimize.minimize(
#         obj,
#         ot.get_positions().flatten(),
#         (ot, bh, dt),
#         jac=jac,
#         tol=1e-6,
#         method='CG',
#         # options={'disp': True}
#     )
#     # print(ropt.njev)

#     positions = ropt.x.reshape((-1, 2))
#     ot.set_positions(positions)


# def run(n, base_filename, l=0.5):
#     # domain
#     domain = ConvexPolyhedraAssembly()
#     domain.add_box([0, 0], [1, 1])

#     # initial positions, weights and masses
#     positions = []
#     if n == 1:
#         radius = 0.3
#         mass = 3.14159 * radius**2
#         positions.append([0.5, radius])
#     else:
#         radius = l / (2 * (n - 1))
#         mass = l**2 / n**2
#         for y in np.linspace(radius, l - radius, n):
#             for x in np.linspace(0.5 - l / 2 + radius, 0.5 + l / 2 - radius, n):
#                 nx = x + 0.5 * radius * (np.random.rand() - 0.5)
#                 ny = y + radius + 0.5 * radius * (np.random.rand() - 0.5)
#                 positions.append([nx, ny])
#     positions = np.array(positions)
#     nb_diracs = positions.shape[0]

#     # OptimalTransport
#     ot = OptimalTransport(domain, RadialFuncInBall())
#     ot.set_weights(np.ones(nb_diracs) * radius**2)
#     ot.set_masses(np.ones(nb_diracs) * mass)
#     ot.set_positions(positions)
#     ot.update_weights()

#     ot.display_vtk(base_filename + "0.vtk", points=True)

#     # history of centroids
#     ce = ot.get_centroids()
#     ce[:, 1] += radius / 10
#     bh = [ce]

#     dt = 1.0
#     for num_iter in range(500):
#         print("num_iter", num_iter)

#         bh.append(ot.get_centroids())
#         get_new_positions_for_centroids(ot, bh, dt)
#         ot.update_weights()

#         # display
#         n1 = int(num_iter / 1) + 1
#         ot.display_vtk(base_filename + "{}.vtk".format(n1), points=True)
