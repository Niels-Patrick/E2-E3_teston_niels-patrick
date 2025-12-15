import pickle
from src.genetic_algorithm import GeneticTrainer


def main():
    trainer = GeneticTrainer(
        population_size=40,
        elite_fraction=0.05,
        mutation_rate=0.05,
        mutation_std=0.2,
        tournament_k=3,
        games_per_eval=60,
        play_second_probability=0.5,
        opponent='random',
        seed=42
    )

    print("Initializing population and starting evolution")
    best_genome, history = trainer.run(
                            generations=30,
                            verbose_every=1,
                            save_best_path="best_ttt_model.keras"
                            )

    # Save genome and metadata so it's possible to reload easily
    with open("best_genome.pkl", "wb") as f:
        pickle.dump({
            'genome': best_genome,
            'shapes': trainer.shapes,
            "sizes": trainer.sizes
        }, f)

    print("Training done. Best fitness history (last 10):")
    for g, fval in history[-10:]:
        print(f"Gen {g}: {fval:.4f}")

    print("Best model saved to './best_ttt_model' and './best_genome.pkl'.")


if __name__ == "__main__":
    main()
