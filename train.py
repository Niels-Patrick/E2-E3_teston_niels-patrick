import pickle
import mlflow
import torch
import os
import matplotlib.pyplot as plt
from src.ai.brain import Brain, load_params
from src.ai.genetic_algorithm import GeneticTrainer
from src.app.logger_manager import logger_manager
from src.utils.model_evaluation import evaluate
from matplotlib.patches import Wedge


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {DEVICE}")


def main(
        population_size: int = 100,
        games_per_eval: int = 60,
        mutation_rate: float = 0.05,
        mutation_std: float = 0.15,
        generations: int = 200
) -> str:
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment("tic_tac_toe_ga")

    with mlflow.start_run():
        try:
            trainer = GeneticTrainer(
                population_size=population_size,
                games_per_eval=games_per_eval,
                mutation_rate=mutation_rate,
                mutation_std=mutation_std
            )

            logger_manager.info(
                "Initializing population and starting evolution"
                )
            best_genome = trainer.run(generations=generations)

            # Save best model
            model = Brain().to(DEVICE)
            load_params(model, best_genome)

            results = evaluate(model)
            plot_evaluation_gauges(results)
            if results["losses"] / 10 >= 0.75:
                return "Training finished. New model is bad and has been deleted" # noqa
            else:
                torch.save(model.state_dict(), "best_ttt_model.pt")
                mlflow.log_artifact("best_ttt_model.pt")

                with open("best_genome.pkl", "wb") as f:
                    pickle.dump(best_genome.cpu(), f)

                logger_manager.info(
                    "Training finished. Model saved as best_ttt_model.pt"
                    )
                return "Training finished. New model is good."
        except Exception as e:
            logger_manager.error("Training crashed:", e)
            raise


def plot_evaluation_gauges(results: dict, output_dir: str = "training_report"):
    """
    Generate and save gauge plots for win, draw, and loss rates.
    """
    os.makedirs(output_dir, exist_ok=True)
    rates = {
        "Win Rate": results["wins"] / 10,
        "Draw Rate": results["draws"] / 10,
        "Loss Rate": results["losses"] / 10,
    }
    for name, value in rates.items():
        fig, ax = plt.subplots(figsize=(4, 2))
        ax.axis('off')
        # Draw gauge background
        ax.add_patch(Wedge((0.5, 0), 0.4, 0, 180, facecolor="#e0e0e0"))
        # Draw value
        ax.add_patch(
            Wedge(
                (0.5, 0),
                0.4, 0,
                value * 180,
                facecolor="#4caf50" if name == "Win Rate" else (
                    "#ff9800" if name == "Draw Rate" else "#f44336"
                    )
                )
            )
        ax.text(0.5, 0.1, f"{name}", ha="center", va="center", fontsize=12)
        ax.text(
            0.5,
            -0.1,
            f"{value*100:.1f}%",
            ha="center",
            va="center",
            fontsize=16,
            fontweight="bold"
            )
        plt.xlim(0, 1)
        plt.ylim(-0.2, 0.5)
        plt.tight_layout()
        out_path = os.path.join(
            output_dir,
            f"{name.lower().replace(' ', '_')}_gauge.png"
            )
        plt.savefig(out_path)
        plt.close(fig)


if __name__ == "__main__":
    main()
