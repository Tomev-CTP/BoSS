__author__ = 'Tomasz Rybotycki'

from typing import List

from numpy import zeros

from BoSS.Boson_Sampling_Utilities import generate_possible_outputs
from BoSS.BosonSamplingSimulator import BosonSamplingSimulator
from BoSS.LossyBosonSamplingExactDistributionCalculators import BosonSamplingExperimentConfiguration
from BoSS.simulation_strategies.SimulationStrategy import SimulationStrategy


class ApproximateDistributionCalculator:
    def __init__(self, experiment_configuration: BosonSamplingExperimentConfiguration,
                 strategy: SimulationStrategy, outcomes=None) -> None:
        self.configuration = experiment_configuration
        self.strategy = strategy
        self.outcomes = outcomes

    def calculate_approximate_distribution(self, samples_number: int = 5000) -> List[float]:
        """
            Prepares the approximate distribution using boson sampling simulation method described by
            Oszmaniec and Brod. Obviously higher number of samples will generate better approximation.
            :return: Approximate distribution as a list.
        """

        if self.outcomes is not None:
            possible_outcomes = self.outcomes
        else:
            possible_outcomes = generate_possible_outputs(self.configuration.number_of_particles_left,
                                                          self.configuration.number_of_modes)

        simulator = BosonSamplingSimulator(self.strategy)

        outcomes_probabilities = zeros(len(possible_outcomes))

        for i in range(samples_number):
            result = simulator.get_classical_simulation_results(self.configuration.initial_state)

            for j in range(len(possible_outcomes)):
                # Check if obtained result is one of possible outcomes.
                if all(result == possible_outcomes[j]):  # Expect all elements of resultant list to be True.
                    outcomes_probabilities[j] += 1
                    break

        for i in range(len(outcomes_probabilities)):
            outcomes_probabilities[i] /= samples_number

        return outcomes_probabilities
