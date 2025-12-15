"""
The Brain class to build the Agent model.
"""

import numpy as np
from keras import layers, models


class Brain:
    def __init__(self) -> None:
        # Define input and output size
        self.input_size = 9
        self.output_size = 5
        self.mutation_rate = 0.1
        self.std = 0.16

        self.model = models.Sequential([
            layers.Input(shape=(self.input_size,)),
            layers.Dense(27, activation='relu'),
            layers.Dense(27, activation='relu'),
            layers.Dense(9, activation='linear')  # Logits for 9 positions
        ])
        # Initializing weights
        self.model.build((None, self.input_size))

    def weights_to_genome(self, weights: list) -> list:
        """
        Flattens the weights into a 1D genome.

        Parameters:
            weights (list): List of numpy arrays from model.get_weights().

        Returns:
            flat (np.array): The 1D genome.
            shapes (list): The list containing the shapes of weights.
            sizes (list): The list containing the sizes of weights.
        """
        shapes = [weight.shape for weight in weights]
        sizes = [weight.size for weight in weights]
        flat = np.concatenate(
            [weight.reshape(-1) for weight in weights]
            ).astype(np.float32)

        return flat, shapes, sizes

    def genome_to_weights(self, genome, shapes, sizes):
        """
        Reconstructs the list of numpy arrays matching shape from flat genome.

        Parameters:
            flat (np.array): The 1D genome.
            shapes (list): The list containing the shapes of weights.
            sizes (list): The list containing the sizes of weights.

        Returns:
            arrs (list): The list of weights.
        """
        arrs = []
        index = 0
        for shape, size in zip(shapes, sizes):
            chunk = genome[index:index+size]
            arrs.append(chunk.reshape(shape).astype(np.float32))
            index += size

        return arrs
