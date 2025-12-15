"""
The genetic algorithm to train and mutate an agent.
"""

import numpy as np
import random
import tensorflow as tf
from src.brain import Brain
from src.game_env import TicTacToe
from src.player_wrappers import heuristic_player, model_player_factory, \
    random_player


class GeneticTrainer:
    """Genetic algorithm to train agents"""

    def __init__(self,
                 population_size: int = 50,
                 elite_fraction: float = 0.05,
                 mutation_rate: float = 0.02,
                 mutation_std: float = 0.1,
                 tournament_k: int = 3,
                 games_per_eval: int = 40,
                 play_second_probability: int = 5,
                 opponent: str = 'random',
                 seed=None
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
        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)
            tf.random.set_seed(seed)
        self.population_size = population_size
        self.elite_fraction = elite_fraction
        self.mutation_rate = mutation_rate
        self.mutation_std = mutation_std
        self.tournament_k = tournament_k
        self.games_per_eval = games_per_eval
        self.play_second_probability = play_second_probability
        self.opponent = opponent  # 'random' or 'heuristic'

        # Building example model to get genome size
        model = Brain()
        self.model_template = model
        weights = model.model.get_weights()
        self.genome_0, self.shapes, self.sizes = model.weights_to_genome(
                                                                weights
                                                                )
        self.genome_length = self.genome_0.size

    def init_population(self):
        # population: list of genomes (numpy arrays)
        pop = []
        # Initializes from Kaiming-like distribution around initial weights
        for i in range(self.population_size):
            g = np.random.normal(
                loc=0.0,
                scale=1.0,
                size=self.genome_length
                ).astype(np.float32)
            g *= 0.5
            pop.append(g)

        return pop

    def evaluate_genome(self, genome, verbose=False):
        """
        Returns fitness scalar. Evaluate by having model play games vs
        opponent(s).
        """
        # Creating model and loading genome
        model = Brain()
        weights = model.genome_to_weights(genome, self.shapes, self.sizes)
        model.model.set_weights(weights)
        player = model_player_factory(model.model)

        if self.opponent == 'random':
            opp_fn = random_player
        else:
            opp_fn = heuristic_player

        wins = 0
        draws = 0
        losses = 0
        games = self.games_per_eval

        env = TicTacToe()

        for g in range(games):
            env.reset()
            # Randomly deciding if genome plays first or second
            if random.random() < self.play_second_probability:
                # Opponent moves first
                first = opp_fn
                second = player
                first_mark = 1  # X
                second_mark = -1  # O
            else:
                first = player
                second = opp_fn
                first_mark = 1
                second_mark = -1

            done = False
            while not done:
                # First player
                if np.any(env.board == 0):
                    move = first(env.board.copy(), first_mark)
                    env.board[move] = first_mark
                    winner = env.check_winner()
                    if winner is not None:
                        done = True
                        break

                # Second player
                if np.any(env.board == 0):
                    move = second(env.board.copy(), second_mark)
                    env.board[move] = second_mark
                    winner = env.check_winner()
                    if winner is not None:
                        done = True
                        break

                # Continuing loop

            # Evaluating result from the perspective of the genome player
            final_winner = env.check_winner()
            if final_winner == 0:
                draws += 1

            if final_winner is None:
                draws += 1  # Shouldn't happen but counts as a draw

            if final_winner == 1 or final_winner == -1:
                # Determining which mark won, and if that was the genome player
                genome_mark = -1
                if first is player:
                    genome_mark = 1

                if first is opp_fn:
                    genome_mark = -1

                if final_winner == genome_mark:
                    wins += 1

                if final_winner != genome_mark:
                    losses += 1

        # fitness: wins*1 + draws*0.5 normalized by games
        fitness = (wins + 0.5 * draws) / games
        if verbose:
            print(f"Eval -> wins: {wins}, draws: {draws}, losses: {losses}, fitness: {fitness:.3f}")  # noqa

        return fitness

    def evaluate_population(self, population, verbose=False):
        fitnesses = np.zeros(len(population), dtype=float)
        for index, genome in enumerate(population):
            fitnesses[index] = self.evaluate_genome(
                                        genome,
                                        verbose=verbose and index == 0
                                        )

        return fitnesses

    def tournament_select(self, population, fitnesses):
        """
        Returns a single parent via tournament selection.
        """
        indexes = np.random.choice(
            len(population),
            size=self.tournament_k,
            replace=False
            )
        best = indexes[0]

        for index in indexes:
            if fitnesses[index] > fitnesses[best]:
                best = index

        return population[best].copy()

    def crossover(self, a, b):
        """
        Single point crossover on genome arrays.
        """
        if self.genome_length <= 1:
            return a.copy(), b.copy()

        point = np.random.randint(1, self.genome_length)
        child1 = np.concatenate([a[:point], b[point:]])
        child2 = np.concatenate([b[:point], a[point:]])
        return child1, child2

    def mutate(self, genome):
        """
        Gaussian mutation applied per-gene with self.mutation_rate probability.
        """
        mask = np.random.rand(self.genome_length) < self.mutation_rate
        noise = np.random.normal(
            loc=0.0,
            scale=self.mutation_std,
            size=self.genome_length
            ).astype(np.float32)
        genome[mask] += noise[mask]
        return genome

    def run(self, generations=50, verbose_every=1, save_best_path=None):
        pop = self.init_population()
        best_history = []

        for gen in range(1, generations + 1):
            fitnesses = self.evaluate_population(
                            pop,
                            verbose=(gen % verbose_every == 0)
                            )
            # Record best
            best_index = int(np.argmax(fitnesses))
            best_fitness = float(fitnesses[best_index])
            best_genome = pop[best_index].copy()
            best_history.append((gen, best_fitness))
            if gen % verbose_every == 0 or gen == 1:
                print(
                    f"Gen {gen}/{generations} Best fitness: {best_fitness:.4f}"
                    )

            # Create next generation
            new_pop = []
            # Elitism
            n_elite = max(1, int(self.elite_fraction * self.population_size))
            elite_indexes = np.argsort(fitnesses)[-n_elite:]
            for index in elite_indexes:
                new_pop.append(pop[int(index)].copy())

            # Fill rest
            while len(new_pop) < self.population_size:
                parent1 = self.tournament_select(pop, fitnesses)
                parent2 = self.tournament_select(pop, fitnesses)
                child1, child2 = self.crossover(parent1, parent2)
                child1 = self.mutate(child1)
                if len(new_pop) < self.population_size:
                    new_pop.append(child1)
                if len(new_pop) < self.population_size:
                    child2 = self.mutate(child2)
                    new_pop.append(child2)

            pop = new_pop

            # Optionally save best
            if save_best_path is not None:
                # Save Keras model weights of current best
                model = Brain()
                weights = model.genome_to_weights(
                                best_genome,
                                self.shapes,
                                self.sizes
                                )
                model.model.set_weights(weights)
                model.model.save(save_best_path, include_optimizer=False)

        return best_genome, best_history
