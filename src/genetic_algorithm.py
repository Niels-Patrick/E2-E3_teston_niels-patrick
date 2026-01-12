"""
The genetic algorithm to train and mutate an agent.
"""

from typing import List
import numpy as np
import random
from src.brain import Brain
from src.game_env import TicTacToe
from tqdm import tqdm
import torch
from src.brain import load_params
from src.player_wrappers import find_threat_squares, model_player, \
    random_player


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {DEVICE}")


class GeneticTrainer:
    """Genetic algorithm to train agents"""

    def __init__(self,
                 population_size: int = 64,
                 games_per_eval: int = 50,
                 mutation_rate: float = 0.05,
                 mutation_std: float = 0.1,
                 elite_fraction: float = 0.05,
                 tournament_k: int = 3,
                 seed: int = 42
                 ) -> None:
        """
        Initializes the GeneticTrainer.

        Parameters:
            population_size (int): Number of agents in each generation.
            elite_fraction (float): Proportion of top agents copied unchanged
                                    into the next gen (elitism).
            mutation_rate (float): Per-agent probability of applying a
                                   mutation.
            mutation_std (float): Standard deviation for Gaussian noise used
                                  in mutation.
            tournament_k (int): Number of individuals sampled in tournament
                                selection.
            games_per_eval (int): How many TicTacToe games an agent plays when
                                  being evaluated.
            play_second_probability (int): Probability the agent plays second
                                           (helps avoid bias).
            opponent (str): Which opponent function to use when evaluating
                            ('random' or 'heuristic').
            seed: Optional random seed for reproducibility.
        """
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)

        self.population_size = population_size
        self.games_per_eval = games_per_eval
        self.mutation_rate = mutation_rate
        self.mutation_std = mutation_std
        self.elite_fraction = elite_fraction
        self.tournament_k = tournament_k

        # Building example model to get genome size
        self.model = Brain().to(DEVICE)
        self.genome_size = sum(p.numel() for p in self.model.parameters())

    def init_population(self) -> List[torch.Tensor]:
        return [
            torch.randn(self.genome_size, device=DEVICE) * 0.5
            for _ in range(self.population_size)
        ]

    def evaluate_genome(self, genome: torch.Tensor) -> float:
        """
        Returns fitness scalar. Evaluate by having model play games vs
        opponent(s).
        """
        # Creating model and loading genome
        model = self.model.model
        load_params(model, genome)

        score = 0.0
        env = TicTacToe()

        for _ in range(self.games_per_eval):
            env.reset()
            first = random.choice([True, False])
            mark = 1 if first else -1

            while True:
                # First player
                threats = find_threat_squares(env.board, -mark)
                move = model_player(model, env.board, mark, DEVICE)
                env.board[move] = mark
                if threats and move not in threats:
                    score -= 0.2
                result = env.check_winner()
                if result is not None:
                    break

                # Second player
                opp_move = random_player(env.board, -mark)
                env.board[opp_move] = -mark
                result = env.check_winner()
                if result is not None:
                    break

                # Continuing loop

            # Evaluating result from the perspective of the genome player
            if result == mark:
                score += 1.0
            elif result == 0:
                score += 0.5
            else:
                score -= 1.0

        return score / self.games_per_eval

    def tournament(self, pop, fitness):
        indexes = np.random.choice(len(pop), self.tournament_k, replace=False)
        best = max(indexes, key=lambda i: fitness[i])

        return pop[best].clone()

    def crossover(self, a, b):
        """
        Single point crossover on genome arrays.
        """
        point = random.randint(1, self.genome_size - 1)

        return (
            torch.cat([a[:point], b[point:]]),
            torch.cat([b[:point], a[point:]])
        )

    def mutate(self, genome):
        """
        Gaussian mutation applied per-gene with self.mutation_rate probability.
        """
        mask = torch.rand(self.genome_size, device=DEVICE) < self.mutation_rate
        genome[mask] += torch.randn(
            mask.sum(), device=DEVICE
            ) * self.mutation_std

        return genome

    def run(self, generations=50):
        population = self.init_population()

        for gen in tqdm(range(1, generations + 1)):
            fitness = [self.evaluate_genome(g) for g in population]
            # Record best
            best_index = int(np.argmax(fitness))
            print(f"Gen {gen} | Best fitness: {fitness[best_index]:.3f}")

            # Create next generation
            new_pop = []
            # Elitism
            elite_n = max(1, int(self.elite_fraction * self.population_size))
            elite_index = np.argsort(fitness)[-elite_n:]

            for index in elite_index:
                new_pop.append(population[index].clone())

            # Fill rest
            while len(new_pop) < self.population_size:
                parent1 = self.tournament(population, fitness)
                parent2 = self.tournament(population, fitness)
                child1, child2 = self.crossover(parent1, parent2)
                new_pop.append(self.mutate(child1))
                if len(new_pop) < self.population_size:
                    new_pop.append(self.mutate(child2))

            population = new_pop

        best_genome = population[int(np.argmax(fitness))]
        return best_genome
