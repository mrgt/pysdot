from pysdot.domain_types import ConvexPolyhedraAssembly
from pysdot.radial_funcs import RadialFuncInBall
from pysdot import OptimalTransport
import matplotlib.pyplot as plt
import scipy.optimize
import numpy as np


# objective function
def obj(x, ot, new_barycenters):
    pos = x.reshape((-1, 2))
    # if pos[0, 1] < 0:
    #     d = (0.5-pos[0, 0])**2 + (0.5-pos[0, 1])**2
    #     w = np.array([d])
    #     ot.set_weights(w)
    ot.set_positions(pos)
    ot.update_weights()

    prp = ot.get_centroids()
    dlt = new_barycenters - prp
    dlp = pos - new_barycenters
    return np.sum(dlt**2) \
        + 1e-3 * np.sum(dlp**2) \
        + 1e-3 * np.sum(ot.get_weights()**2)


def run(n, base_filename, l=0.5):
    # domain
    domain = ConvexPolyhedraAssembly()
    domain.add_box([0, 0], [1, 1])

    # initial positions, weights and masses
    positions = []
    radius = l / (2 * (n - 1))
    for y in np.linspace(radius, l - radius, n):
        for x in np.linspace(radius, l - radius, n):
            nx = x + 0.2 * radius * (np.random.rand() - 0.5)
            ny = y + 0.2 * radius * (np.random.rand() - 0.5)
            positions.append([nx, ny])
    positions = np.array(positions)
    nb_diracs = positions.shape[0]

    # OptimalTransport
    ot = OptimalTransport(domain, RadialFuncInBall())
    ot.set_weights(np.ones(nb_diracs) * radius**2)
    ot.set_masses(np.ones(nb_diracs) * l**2 / nb_diracs)
    ot.set_positions(positions)
    ot.update_weights()

    ot.set_positions(ot.get_centroids())
    ot.display_vtk(base_filename + "0.vtk")

    # ys = []
    # values = []
    # new_barycenters = np.array([[radius, 0.2]])
    # for y in np.linspace(-1, 1, 300):
    #     x = np.array([radius, y])
    #     ys.append(y)
    #     values.append(obj(x, ot, new_barycenters))
    # plt.plot(ys, values)
    # plt.show()

    velocity = 0.0 * positions

    for num_iter in range(200):
        print(num_iter)

        # barycenters at the beginning
        ot.update_weights()
        b_o = ot.get_centroids()

        # trial for the new barycenters
        velocity[:, 1] = - 0.05 * radius
        b_n = b_o + velocity

        # optimisation of positions to go to the target barycenters
        ropt = scipy.optimize.minimize(
            obj,
            b_n.flatten(),
            (ot, b_n),
            tol=1e-4,
            method='BFGS',
            options={'eps': 1e-3 * radius}
        )

        positions = ropt.x.reshape((-1, 2))
        ot.set_positions(positions)
        ot.update_weights()

        # new barycenters, corrected (minimize have update the weights)
        b_n = ot.get_centroids()
        velocity = b_n - b_o
        print(positions, velocity)

        # display
        ot.display_vtk(base_filename + "{}.vtk".format(num_iter + 1))


run(10, "results/pd_")
