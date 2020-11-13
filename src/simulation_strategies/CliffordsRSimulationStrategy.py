__author__ = 'Tomasz Rybotycki'

# One should note, that R is required to use this module, as original Clifford's program is written in R.
# On my Windows 10, I am using anaconda and I had to add R_HOME env variable and R_path\bin, R_path\bin\x64 to the path.
# https://cran.r-project.org/web/packages/BosonSampling/index.html


from numpy import ndarray, array, arange
from rpy2.robjects import packages

from src.Boson_Sampling_Utilities import particle_state_to_modes_state
from src.rpy2_utilities import numpy_array_to_r_matrix
from src.simulation_strategies.SimulationStrategy import SimulationStrategy


class CliffordsRSimulationStrategy(SimulationStrategy):
    def __init__(self, number_of_bosons: int, interferometer_matrix: ndarray) -> None:
        self.interferometer_matrix = interferometer_matrix
        self.number_of_bosons = number_of_bosons

        required_packages = ('BosonSampling', 'Rcpp', 'RcppArmadillo')

        # Check if required R packages are installed. And note if not.
        if all(packages.isinstalled(package) for package in required_packages):
            print('All R packages are installed!')
        else:
            print('Some packages are missing! Missing packages:')
            for package in required_packages:
                if not packages.isinstalled(package):
                    print(package)

        boson_sampling_package = packages.importr('BosonSampling')
        self.cliffords_r_sampler = boson_sampling_package.bosonSampler
        first_n_columns_of_given_matrix = interferometer_matrix[:, arange(number_of_bosons)]
        self.boson_sampler_input_matrix = numpy_array_to_r_matrix(first_n_columns_of_given_matrix)

    def simulate(self, initial_state: ndarray) -> ndarray:  # Initial state is only added for interface compatibility.
        result, permanent, probability_mass_function = \
            self.cliffords_r_sampler(self.boson_sampler_input_matrix, sampleSize=1, perm=False)
        python_result = array([result[i] - 1 for i in range(self.number_of_bosons)])  # -1 here is to fix R indexation.

        return particle_state_to_modes_state(python_result, len(self.interferometer_matrix))