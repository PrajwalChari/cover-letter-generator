import random
import matplotlib.pyplot as plt

def simulate_dice_rolls():
    """Simulates rolling a die repeatedly and checks for six consecutive 6s."""

    how_many_sixes = 6
    how_many_die = 1

    roll_histories = [[] for _ in range(how_many_die)]
    count = 0
    money = 0
    money_increment = 1000000

    while True:
        rolls = [random.randint(1, 6) for _ in range(how_many_die)]
        for i in range(how_many_die):
            roll_histories[i].append(rolls[i])

        if count % 18000 == 0:
            money += money_increment

        # Check for six consecutive 6s in any die
        for history in roll_histories:
            if len(history) >= how_many_sixes and all(x == 6 for x in history[-how_many_sixes:]):
                return count + 1, money

        count += 1

def main():
    """Main function to run the simulation multiple times and graph a histogram of averages."""
    num_simulations = 200  # Number of simulations

    total_rolls = []
    total_money = []

    print(f"Running {num_simulations} simulations...")
    for i in range(num_simulations):
        print(f"Starting simulation {i + 1}...")
        rolls, money = simulate_dice_rolls()
        total_rolls.append(rolls)
        total_money.append(money)

    # Plot histogram for average rolls
    plt.figure(figsize=(10, 6))
    plt.hist(total_rolls, bins=30, alpha=0.7, color='blue', edgecolor='black')
    plt.title("Histogram of Rolls to Get Six Consecutive 6s")
    plt.xlabel("Number of Rolls")
    plt.ylabel("Frequency")
    plt.grid(True)

    # Set appropriate x-axis range
    plt.xlim(min(total_rolls) - 1000, max(total_rolls) + 1000)

    plt.show()

if __name__ == "__main__":
    main()