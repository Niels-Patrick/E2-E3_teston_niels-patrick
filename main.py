import pickle
import torch
from src.brain import load_params
from src.genetic_algorithm import GeneticTrainer


def main():
    trainer = GeneticTrainer(
        population_size=64,
        games_per_eval=60,
        mutation_rate=0.05,
        mutation_std=0.15
    )

    print("Initializing population and starting evolution")
    best_genome = trainer.run(generations=40)

    # Save best model
    model = trainer.model.model
    load_params(model, best_genome)
    torch.save(model.state_dict(), "best_ttt_model.pt")

    with open("best_genome.pkl", "wb") as f:
        pickle.dump(best_genome.cpu(), f)

    print("Training complete. Model saved as best_ttt_model.pt")


if __name__ == "__main__":
    main()
