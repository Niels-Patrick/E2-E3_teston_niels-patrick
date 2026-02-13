import pickle
import torch
from src.brain import Brain, load_params
from src.genetic_algorithm import GeneticTrainer


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {DEVICE}")


def main():
    trainer = GeneticTrainer(
        population_size=64,
        games_per_eval=60,
        mutation_rate=0.05,
        mutation_std=0.15
    )

    print("Initializing population and starting evolution")
    best_genome = trainer.run(generations=200)

    # Save best model
    model = Brain().to(DEVICE)
    load_params(model, best_genome)
    torch.save(model.state_dict(), "best_ttt_model.pt")

    with open("best_genome.pkl", "wb") as f:
        pickle.dump(best_genome.cpu(), f)

    print("Training complete. Model saved as best_ttt_model.pt")


if __name__ == "__main__":
    main()
