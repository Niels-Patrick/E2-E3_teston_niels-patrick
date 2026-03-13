import pickle
import mlflow
import torch
from src.ai.brain import Brain, load_params
from src.ai.genetic_algorithm import GeneticTrainer


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {DEVICE}")


def main():
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment("tic_tac_toe_ga")

    with mlflow.start_run():
        try:
            print("Tracking URI:", mlflow.get_tracking_uri())
            trainer = GeneticTrainer(
                population_size=100,
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
            mlflow.log_artifact("best_ttt_model.pt")

            with open("best_genome.pkl", "wb") as f:
                pickle.dump(best_genome.cpu(), f)

            print("Training complete. Model saved as best_ttt_model.pt")
        except Exception as e:
            print("Training crashed:", e)
            raise


if __name__ == "__main__":
    main()
