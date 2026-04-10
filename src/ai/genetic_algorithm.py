"""
The genetic algorithm to train and mutate an agent.
"""

from typing import List
import numpy as np
import random
from src.ai.brain import Brain
from src.ai.game_env import TicTacToe, check_winner
from tqdm import tqdm
import torch
from src.ai.brain import load_params
from src.ai.player_wrappers import find_threat_squares, heuristic_player, \
    model_player, random_player
import matplotlib.pyplot as plt
import mlflow
import os


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
        self.elite_models = []

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
        model = Brain().to(DEVICE)
        load_params(model, genome)

        score = 0
        losses = 0
        draws = 0
        env = TicTacToe()

        first = True
        first_trainings_count = 0
        for _ in range(self.games_per_eval):
            env.reset()
            current_player = first
            mark = 1 if first else -1

            while True:
                if current_player:
                    # First player
                    threats = find_threat_squares(env.board, -mark)
                    move = model_player(model, env.board, mark, DEVICE)
                    env.board[move] = mark
                    if threats and move not in threats:
                        score -= 0.5
                    result = check_winner(env.board)
                    if result is not None:
                        break
                else:
                    # Second player
                    if self.elite_models != [] and first_trainings_count < 35:
                        elite = random.choice(self.elite_models)
                        opp_move = model_player(
                            elite,
                            env.board,
                            -mark,
                            DEVICE
                            )
                    else:
                        # opp_move = random_player(env.board, -mark)
                        opp_move = heuristic_player(env.board, -mark)
                    env.board[opp_move] = -mark
                    result = check_winner(env.board)
                    if result is not None:
                        break

                current_player = not current_player
                # Continuing loop

            first = -first
            first_trainings_count += 1

            # Evaluating result from the perspective of the genome player
            if result == mark:
                score += 1
            elif result == 0:
                draws += 1
                score += 0.5
            else:
                losses += 1
                score -= 1

            loss_rate = losses / self.games_per_eval
            draw_rate = draws / self.games_per_eval
            fitness = score / self.games_per_eval

        return fitness, loss_rate, draw_rate

    def tournament(self, pop, fitness):
        """
        Mini-tournament between a specific number (tournament_k) of randomly
        selected genomes, to determine which one is the best, then returns it.
        """
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
        mlflow.log_param("population_size", self.population_size)
        mlflow.log_param("mutation_rate", self.mutation_rate)
        mlflow.log_param("elite_fraction", self.elite_fraction)
        mlflow.log_param("generations", generations)

        population = self.init_population()

        fitness_history = []
        loss_rate_history = []
        draw_rate_history = []

        for gen in tqdm(range(1, generations + 1)):
            fitness_scores = []
            generation_losses = []
            generation_draws = []

            for genome in population:
                fitness, loss_rate, draw_rate = self.evaluate_genome(
                    genome
                    )
                fitness_scores.append(fitness)
                generation_losses.append(loss_rate)
                generation_draws.append(draw_rate)

            # Record best
            best_fitness = max(fitness_scores)
            print(f"Gen {gen} | Best fitness: {best_fitness}")

            # Storing metrics for graph
            fitness_history.append(best_fitness)
            loss_rate_history.append(np.mean(generation_losses))
            draw_rate_history.append(np.mean(generation_draws))

            # Create next generation
            new_pop = []
            # Elitism
            elite_n = max(1, int(self.elite_fraction * self.population_size))
            elite_index = np.argsort(fitness_scores)[-elite_n:]

            for index in elite_index:
                new_pop.append(population[index].clone())

            # Fill rest
            while len(new_pop) < self.population_size:
                parent1 = self.tournament(population, fitness_scores)
                parent2 = self.tournament(population, fitness_scores)
                child1, child2 = self.crossover(parent1, parent2)
                new_pop.append(self.mutate(child1))
                if len(new_pop) < self.population_size:
                    new_pop.append(self.mutate(child2))

            population = new_pop

            # Saving elite model
            best_current_genome = population[np.argmax(fitness_scores)]
            model = Brain().to(DEVICE)
            load_params(model, best_current_genome)
            self.elite_models.append(model)

            mlflow.log_metric("best_fitness", best_fitness, step=gen)
            mlflow.log_metric(
                "loss_rate",
                np.mean(generation_losses),
                step=gen
                )
            mlflow.log_metric("draw_rate", np.mean(generation_draws), step=gen)

        # Plot training curves
        generations = range(len(fitness_history))

        plt.figure(figsize=(10, 6))
        plt.plot(generations, fitness_history, label="Best Fitness")
        plt.plot(generations, loss_rate_history, label="Loss Rate")
        plt.plot(generations, draw_rate_history, label="Draw Rate")
        plt.xlabel("Generation")
        plt.ylabel("Metric Value")
        plt.title("Training Evolution")
        plt.legend()
        plt.savefig(os.path.join("training_report", "z_training_evolution.png"))
        mlflow.end_run()

        best_genome = population[np.argmax(fitness_scores)]
        return best_genome
