__author__ = 'Tomasz Rybotycki'

# TR TODO: Consider making this file a package along with exact distribution calculator.

import itertools
from typing import List

from numpy import ndarray, zeros
from scipy.special import binom


def calculate_permanent(matrix: ndarray) -> float:
    """
    Returns the permanent of the matrix mat.
    """
    return permanent_recursive_part(matrix, 0, [], 1)


def permanent_recursive_part(mtx: ndarray, column: int, selected: List[int], prod: int) -> float:
    """
    Row expansion for the permanent of matrix mtx.
    The counter column is the current column,
    selected is a list of indices of selected rows,
    and prod accumulates the current product.
    """
    if column == mtx.shape[1]:
        return prod

    result = 0
    for row in range(mtx.shape[0]):
        if row not in selected:
            result = result \
                     + permanent_recursive_part(mtx, column + 1, selected + [row], prod * mtx[row, column])
    return result


def particle_state_to_modes_state(particle_state: ndarray, observed_modes_number: int) -> ndarray:
    modes_state = zeros(observed_modes_number)

    # Adding the particle to it's mode.
    for particle in particle_state:
        modes_state[int(particle)] += 1

    # numbers of particles in each mode
    return modes_state


def modes_state_to_particle_state(mode_state: ndarray, particles_number: int) -> ndarray:
    """
        Return given mode-basis state in particle basis.

        :param mode_state: Input state in mode-basis.
        :param particles_number: Number of particles.
        :return: Given mode-basis state in particle basis.
    """

    number_of_observed_modes = len(mode_state)
    modes = mode_state.copy()
    particles_state = zeros(particles_number)

    i = k = 0
    while i < number_of_observed_modes:

        if modes[i] > 0:
            modes[i] -= 1
            particles_state[k] = int(i)
            k += 1
        else:
            i += 1

    return particles_state


def generate_possible_outputs(number_of_particles: int, number_of_modes: int) -> List[ndarray]:
    outputs = []

    output = zeros(number_of_modes)
    output[0] = number_of_particles
    outputs.append(output)

    while outputs[-1][number_of_modes - 1] < number_of_particles:

        k = number_of_modes - 1
        while outputs[-1][k - 1] == 0:
            k -= 1

        output = outputs[-1].copy()
        output[k - 1] -= 1
        output[k:] = 0
        output[k] = number_of_particles - sum(output)

        outputs.append(output)

    return outputs


def generate_lossy_inputs(initial_state: ndarray, number_of_particles_left: int) -> List[List[int]]:
    """
        From initial state generate all possible input states after losses application.
        :param initial_state: The state we start with.
        :param number_of_particles_left: Number of particles after losses application.
        :return: A list of lists representing initial states after losses.
    """
    x0 = []
    number_of_modes = len(initial_state)
    initial_number_of_particles = sum(initial_state)
    for i in range(number_of_modes):
        x0.extend([i] * int(initial_state[i]))

    lossy_inputs_list = []

    # Symmetrization
    for combination in itertools.combinations(list(range(initial_number_of_particles)), number_of_particles_left):
        lossy_input_in_particle_basis = []
        for el in combination:
            lossy_input_in_particle_basis.append(x0[el])

        lossy_input = particle_state_to_modes_state(lossy_input_in_particle_basis, number_of_modes)

        # Check if calculated lossy input is already in the list. If not, add it.
        if all(list(lossy_input_in_list) != list(lossy_input) for lossy_input_in_list in lossy_inputs_list):
            lossy_inputs_list.append(lossy_input)

    return lossy_inputs_list


def calculate_number_of_possible_n_particle_m_mode_output_states(n: int, m: int) -> int:
    """
        Calculates the number of possible output states with n particles placed around m modes. This is basically
        the same answer as to in how many possible combinations can we put n objects in m bins. It's also a dimension
        of n-particle m-mode bosonic space. Stars-and-bars argument applies here.
    """
    return binom(n + m - 1, n)


class ChinHuhPermanentCalculator:

    def __init__(self, matrix: ndarray, input_state: List[int] = [], output_state: List[int] = []):
        self.__matrix = matrix
        self.__input_state = input_state
        self.__output_state = output_state

    @property
    def matrix(self) -> ndarray:
        return self.__matrix

    @matrix.setter
    def matrix(self, matrix) -> None:
        self.__matrix = matrix

    @property
    def input_state(self) -> List[int]:
        return self.__input_state

    @input_state.setter
    def input_state(self, input_state) -> None:
        self.__input_state = input_state

    @property
    def output_state(self) -> List[int]:
        return self.__output_state

    @output_state.setter
    def output_state(self, output_state) -> None:
        self.__output_state = output_state

    def calculate_permanent_of_effective_scattering_matrix(self) -> float:
        """
            This is the main method of the calculator. Assuming that input state, output state and the matrix are
            defined correctly (that is we've got m x m matrix, and vectors of with length m) this calculates the
            permanent of an effective scattering matrix related to probability of obtaining output state from given
            input state.
            :return: Permanent of effective scattering matrix.
        """
        if not self.__can_calculation_be_performed():
            raise AttributeError

        v_vectors = self.__calculate_v_vectors()
        permanent = 0
        for v_vector in v_vectors:
            v_sum = sum(v_vector)
            addend = pow(-1, v_sum)
            # Binoms calculation
            for i in range(len(v_vector)):
                addend *= binom(self.__input_state[i], v_vector[i])
            # Product calculation
            product = 1
            for i in range(len(self.__input_state)):
                if self.__output_state[i] == 0:  # There's no reason to calculate the sum if t_i = 0
                    continue
                # Otherwise we calculate the sum
                product_part = 0
                for j in range(len(self.__input_state)):
                    product_part += (self.__input_state[j] + v_vector[j]) * self.__matrix[j][i]
                product_part = pow(product_part, self.__output_state[i])
                product *= product_part
            addend *= product
            permanent *= addend
        permanent /= pow(2, sum(self.__input_state))
        return permanent

    def __can_calculation_be_performed(self) -> bool:
        """
            Checks if calculation can be performed. For this to happen sizes of given matrix and states have
            to match.
            :return: Information if the calculation can be performed.
        """
        can_calculation_be_performed = True
        can_calculation_be_performed = \
            can_calculation_be_performed and self.__matrix.shape[0] == self.__matrix.shape[1]
        can_calculation_be_performed = \
            can_calculation_be_performed and len(self.__output_state) == len(self.__input_state)
        can_calculation_be_performed = \
            can_calculation_be_performed and len(self.__output_state) == self.__matrix.shape[0]

        return can_calculation_be_performed

    def __calculate_v_vectors(self):
        v_vectors = []
        for i in range(self.__input_state[len(self.__input_state)] + 1):
            input_vector = self.__input_state.copy()
            input_vector.append(i)

            if len(input_vector) == len(self.__input_state):
                v_vectors.append(input_vector)
            else:
                v_vectors.extend(self.__calculate_v_vectors(input_vector))

        return v_vectors
