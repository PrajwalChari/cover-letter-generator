import random
import time

def simulate_dice_rolls():
    """Simulates rolling 10 dice repeatedly and checks for any die getting six consecutive 6s."""


    how_many_sixes = 10

    how_many_die = 100

    roll_histories = [[] for _ in range(how_many_die)]
    count = 0
    money = 0
    money_increment = 1000000



    while True:
        rolls = [random.randint(1, 6) for _ in range(how_many_die)]
        for i in range(how_many_die):
            roll_histories[i].append(rolls[i])

        if count % 1800 == 0:
            money += money_increment

        print(f"Roll {count + 1}: {rolls}, Total Money: ${money:,}")

        # Check for six consecutive 6s in any die
        for history in roll_histories:
            if len(history) >= how_many_sixes and all(x == 6 for x in history[-how_many_sixes:]):
                return count + 1, money

        count += 1
        time.sleep(0.0000000001)  # Simulate a 1-second interval for rolling

def main():

    """Main function to simulate the dice roll scenario and display the result."""
    print("Starting simulation to find six consecutive 6s on any die...")
    roll_number, total_money = simulate_dice_rolls()
    print(f"Six consecutive 6s found at roll number {roll_number}!")
    print(f"Total money earned: ${total_money:,}")
    print(f"Total time spent: {roll_number*2} seconds")
    print(f"Total time spent: {roll_number*2/60} hours")
    print(f"Total time spent: {round(roll_number*2/60)/10} of 10 hour days")

if __name__ == "__main__":
    main()
