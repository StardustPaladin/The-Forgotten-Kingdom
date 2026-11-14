

import json
from pathlib import Path

# =====================================================
# THE FORGOTTEN KINGDOM
# A Choose Your Own Adventure Game
# =====================================================

SAVE_FILE = Path("forgotten_kingdom_save.json")


# -----------------------------------------------------
# PLAYER INFORMATION
# -----------------------------------------------------

def new_game():
    """Create a new player and initialize game statistics."""
    name = input("What is your adventurer's name? ").strip()

    if not name:
        name = "Adventurer"

    return {
        "name": name,
        "health": 100,
        "gold": 10,
        "inventory": {
            "Health Potion": 1
        },
        "decisions": 0,
        "discoveries": 0,
        "visited": [],
        "choices": [],
        "rewards_claimed": [],
        "current_scene": "forest"
    }


# -----------------------------------------------------
# INVENTORY SYSTEM
# -----------------------------------------------------

def add_item(item, quantity=1):
    """Add an item to the player's inventory."""
    if quantity <= 0:
        return

    inventory = player["inventory"]
    inventory[item] = inventory.get(item, 0) + quantity

    print(f"\nYou received {quantity} {item}!")


def remove_item(item, quantity=1):
    """Remove an item if the player has enough."""
    inventory = player["inventory"]

    if inventory.get(item, 0) >= quantity:
        inventory[item] -= quantity

        if inventory[item] == 0:
            del inventory[item]

        return True

    return False


def has_item(item):
    """Check whether the player owns an item."""
    return player["inventory"].get(item, 0) > 0


def show_inventory():
    """Display all inventory items and their quantities."""
    while True:
        print("\n========== INVENTORY ==========")

        if not player["inventory"]:
            print("Your inventory is empty.")
        else:
            for item, quantity in player["inventory"].items():
                print(f"{item}: {quantity}")

        print("\n1. Use Health Potion")
        print("2. Return")

        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            use_potion()

        elif choice == "2":
            break

        else:
            print("\nPlease choose a valid option.")


def use_potion():
    """Use a health potion to restore up to 40 health."""
    if not has_item("Health Potion"):
        print("\nYou don't have any Health Potions!")
        return

    if player["health"] >= 100:
        print("\nYour health is already full!")
        return

    old_health = player["health"]

    remove_item("Health Potion")

    player["health"] = min(100, player["health"] + 40)

    restored = player["health"] - old_health

    print("\nYou used a Health Potion!")
    print(f"You restored {restored} health.")
    print(f"Current health: {player['health']}/100")


# -----------------------------------------------------
# PLAYER STATISTICS
# -----------------------------------------------------

def show_stats():
    """Display the player's current statistics."""
    print("\n========== PLAYER STATS ==========")
    print(f"Name: {player['name']}")
    print(f"Health: {player['health']}/100")
    print(f"Gold: {player['gold']}")
    print(f"Decisions Made: {player['decisions']}")
    print(f"Locations Discovered: {player['discoveries']}")
    print(f"Items Owned: {sum(player['inventory'].values())}")
    print("==================================")


def record_choice(choice):
    """Keep track of decisions made by the player."""
    player["decisions"] += 1
    player["choices"].append(choice)


def discover_location(location):
    """Record a location the player visits."""
    if location not in player["visited"]:
        player["visited"].append(location)
        player["discoveries"] += 1


# -----------------------------------------------------
# ONE-TIME REWARD SYSTEM
# -----------------------------------------------------

def reward_claimed(reward):
    """Check whether the player has already collected a reward."""
    return reward in player["rewards_claimed"]


def claim_reward(reward):
    """Mark a reward as collected."""
    if not reward_claimed(reward):
        player["rewards_claimed"].append(reward)
        return True

    return False


# -----------------------------------------------------
# SAVE AND LOAD SYSTEM
# -----------------------------------------------------

def save_game():
    """Save all player information to a JSON file."""
    try:
        with SAVE_FILE.open("w") as file:
            json.dump(player, file, indent=4)

        print("\nGame saved successfully!")

    except (OSError, TypeError) as error:
        print(f"\nCould not save the game: {error}")


def load_game():
    """Load previously saved player information."""
    try:
        with SAVE_FILE.open("r") as file:
            saved_player = json.load(file)

        # Check that the save contains the required information.
        required = [
            "name", "health", "gold", "inventory",
            "decisions", "discoveries", "visited",
            "choices", "current_scene"
        ]

        if not isinstance(saved_player, dict):
            print("\nThe save file is invalid.")
            return None

        if not all(key in saved_player for key in required):
            print("\nThe save file is incomplete.")
            return None

        # Make sure the inventory and reward tracking exist.
        if not isinstance(saved_player["inventory"], dict):
            print("\nThe inventory in the save file is invalid.")
            return None

        saved_player.setdefault("rewards_claimed", [])

        # Convert the incorrectly named potion from older saves.
        if "??? Potion" in saved_player["inventory"]:
            quantity = saved_player["inventory"].pop("??? Potion")
            saved_player["inventory"]["Health Potion"] = (
                saved_player["inventory"].get("Health Potion", 0)
                + quantity
            )

        # Check that the saved scene is a valid game location.
        valid_scenes = [
            "forest", "cabin", "trail", "mountain",
            "village", "castle", "artifact",
            "power", "hero", "guardian", "lost", "credits"
        ]

        if saved_player["current_scene"] not in valid_scenes:
            print("\nThe saved location is invalid.")
            return None

        print(f"\nWelcome back, {saved_player['name']}!")
        return saved_player

    except FileNotFoundError:
        print("\nNo saved game was found.")
        return None

    except (OSError, json.JSONDecodeError, TypeError):
        print("\nThe save file could not be read.")
        return None


# -----------------------------------------------------
# GENERAL GAME FUNCTIONS
# -----------------------------------------------------

def display_title():
    """Display the game's title screen."""
    print("\n" + "=" * 45)
    print("          THE FORGOTTEN KINGDOM")
    print("          A CHOOSE YOUR OWN ADVENTURE")
    print("=" * 45)


def pause():
    """Pause the story until the player presses Enter."""
    input("\nPress Enter to continue...")


def choose(options):
    """
    Display choices and handle special commands.
    Players can save, view inventory, check stats,
    or quit without leaving their current story location.
    """
    while True:
        print()

        for number, option in enumerate(options, 1):
            print(f"{number}. {option}")

        print("\nCommands: I = Inventory | T = Stats | S = Save | Q = Quit")

        answer = input("\nWhat will you do? ").strip().lower()

        if answer == "i":
            show_inventory()

        elif answer == "t":
            show_stats()

        elif answer == "s":
            save_game()

        elif answer == "q":
            confirm = input(
                "\nAre you sure you want to quit? (y/n): "
            ).strip().lower()

            if confirm == "y":
                print("\nThanks for playing The Forgotten Kingdom!")
                print("Goodbye, adventurer!")
                raise SystemExit

            else:
                print("\nReturning to your adventure...")

        elif answer.isdigit():
            number = int(answer)

            if 1 <= number <= len(options):
                record_choice(options[number - 1])
                return number

            print("\nThat is not a valid option.")

        else:
            print("\nPlease enter a valid option.")


# =====================================================
# STORY LOCATIONS
# Each location is its own reusable function.
# =====================================================


# -----------------------------------------------------
# 1. THE MYSTERIOUS FOREST
# -----------------------------------------------------

def forest():
    discover_location("Mysterious Forest")

    print("\n========== THE MYSTERIOUS FOREST ==========")
    print(f"\nYou wake up in a strange forest, {player['name']}.")
    print("You have no memory of how you arrived here.")
    print("An old map lies beside you, showing a forgotten kingdom.")
    print("Somewhere in the distance, you hear strange noises.")

    print("\nWhat would you like to do?")

    choice = choose([
        "Explore an abandoned cabin.",
        "Follow a trail of glowing footprints.",
        "Travel toward the mountains.",
        "Wander into the mysterious fog."
    ])

    if choice == 1:
        return "cabin"

    elif choice == 2:
        return "trail"

    elif choice == 3:
        return "mountain"

    else:
        return "lost"


# -----------------------------------------------------
# 2. THE ABANDONED CABIN
# -----------------------------------------------------

def cabin():
    discover_location("Abandoned Cabin")

    print("\n========== THE ABANDONED CABIN ==========")
    print("\nYou discover a small cabin hidden between the trees.")
    print("Inside, you find an old chest and a dusty journal.")

    # The rusty key can only be collected once.
    if not reward_claimed("cabin_key"):
        print("\nYou open the chest and discover a rusty key.")
        add_item("Rusty Key")
        claim_reward("cabin_key")

    else:
        print("\nThe chest is empty. You already collected the key.")

    # The journal can only be collected once.
    if not reward_claimed("cabin_journal"):
        print("\nYou discover an old journal.")
        print("It contains information about the forgotten kingdom.")
        add_item("Old Journal")
        claim_reward("cabin_journal")

    else:
        print("\nYou have already collected the old journal.")

    print("\nThe journal mentions a castle hidden beyond an abandoned village.")

    pause()
    return "village"


# -----------------------------------------------------
# 3. THE GLOWING FOOTPRINTS
# -----------------------------------------------------

def trail():
    discover_location("Glowing Footprints")

    print("\n========== THE GLOWING TRAIL ==========")
    print("\nYou follow the glowing footprints deeper into the forest.")
    print("Eventually, you discover a mysterious traveler.")

    # The traveler only gives the potion once.
    if not reward_claimed("trail_potion"):
        print('\n"You seek the forgotten kingdom, do you not?"')
        print('"Take this potion. You will need it on your journey."')

        add_item("Health Potion")
        claim_reward("trail_potion")

    else:
        print("\nYou recognize the traveler you met before.")
        print('"I hope the potion I gave you helped on your journey."')

    print("\nThe traveler points toward a nearby village.")

    pause()
    return "village"


# -----------------------------------------------------
# 4. THE MOUNTAINS
# -----------------------------------------------------

def mountain():
    discover_location("Mountain Pass")

    print("\n========== THE MOUNTAIN PASS ==========")
    print("\nYou begin climbing the dangerous mountain path.")
    print("Loose rocks begin falling around you.")

    choice = choose([
        "Climb over the dangerous rocks.",
        "Find a safer path around the mountain."
    ])

    if choice == 1:

        # Only apply the injury once.
        if not reward_claimed("mountain_injury"):
            print("\nYou make it across, but falling rocks injure you.")

            player["health"] = max(0, player["health"] - 25)
            claim_reward("mountain_injury")

            print(f"Health remaining: {player['health']}/100")

        else:
            print("\nYou carefully cross the rocks without getting injured.")

        if player["health"] <= 0:
            return "lost"

        # The Mountain Gem is a one-time reward.
        if not reward_claimed("mountain_gem"):
            print("\nYou discover a valuable Mountain Gem.")
            add_item("Mountain Gem")
            claim_reward("mountain_gem")

        else:
            print("\nYou already collected the Mountain Gem.")

    else:
        print("\nYou discover a safer path leading toward the village.")

    pause()
    return "village"


# -----------------------------------------------------
# 5. THE FORGOTTEN VILLAGE
# -----------------------------------------------------

def village():
    discover_location("Forgotten Village")

    print("\n========== THE FORGOTTEN VILLAGE ==========")
    print("\nYou arrive at an abandoned village.")
    print("The buildings are falling apart, but someone")
    print("appears to have visited recently.")

    choice = choose([
        "Search the abandoned buildings.",
        "Read the strange writing on a stone wall.",
        "Help a mysterious traveler.",
        "Continue toward the castle."
    ])

    # OPTION 1: Search the buildings.
    if choice == 1:

        if reward_claimed("village_search"):
            print("\nYou search the buildings again.")
            print("You already collected everything useful.")

        else:
            print("\nYou search an abandoned house.")
            print("Inside, you discover 15 gold and a health potion.")

            player["gold"] += 15
            add_item("Health Potion")

            claim_reward("village_search")

            print(f"\nYou now have {player['gold']} gold.")

        return "village"

    # OPTION 2: Read the writing.
    elif choice == 2:

        if reward_claimed("village_clue"):
            print("\nYou have already read the writing.")
            print("You remember the warning about the artifact.")

        else:
            print("\nThe writing reveals that the castle")
            print("contains an ancient artifact.")

            print("\nIt warns that the artifact must never")
            print("fall into the wrong hands.")

            add_item("Ancient Clue")
            claim_reward("village_clue")

        return "village"

    # OPTION 3: Help the traveler.
    elif choice == 3:

        if reward_claimed("village_traveler"):
            print("\nThe traveler thanks you again.")
            print('"I have already given you everything I can spare."')

        else:
            print("\nYou help the mysterious traveler.")
            print("He thanks you for your kindness.")

            print('\n"Thank you for helping me."')
            print('"Please accept these 5 gold coins and a health potion."')
            print('"The castle entrance is locked. Find a key or another way inside."')

            player["gold"] += 5
            add_item("Health Potion")

            claim_reward("village_traveler")

            print(f"\nYou now have {player['gold']} gold.")

        return "village"

    # OPTION 4: Continue toward the castle.
    else:
        print("\nYou leave the village and head toward the castle.")
        return "castle"


# -----------------------------------------------------
# 6. THE FORGOTTEN CASTLE
# -----------------------------------------------------

def castle():
    discover_location("Forgotten Castle")

    print("\n========== THE FORGOTTEN CASTLE ==========")
    print("\nAt last, you reach the forgotten kingdom's castle.")
    print("Its enormous gates stand between you and the treasure.")

    if has_item("Rusty Key"):
        print("\nYou use the Rusty Key to unlock the gates.")
        remove_item("Rusty Key")

    else:
        print("\nYou don't have a key. You must force your way through.")
        player["health"] = max(0, player["health"] - 20)
        print(f"Health remaining: {player['health']}/100")

        if player["health"] <= 0:
            return "lost"

    print("\nInside, you discover an enormous chamber.")
    print("At its center floats a mysterious ancient artifact.")

    if has_item("Ancient Clue"):
        print("\nYou remember the warning written on the village wall.")
        print("The artifact is keeping an ancient darkness sealed.")

    pause()
    return "artifact"


# -----------------------------------------------------
# 7. THE FINAL DECISION
# -----------------------------------------------------

def artifact():
    discover_location("Artifact Chamber")

    print("\n========== THE ANCIENT ARTIFACT ==========")
    print("\nA mysterious voice echoes through the chamber.")
    print('"You have traveled far to find me, adventurer."')
    print('"Your final decision will determine the fate of this kingdom."')

    choice = choose([
        "Take the artifact and claim its power.",
        "Destroy the artifact and save the kingdom.",
        "Protect the artifact and become its guardian."
    ])

    if choice == 1:
        return "power"

    elif choice == 2:
        return "hero"

    else:
        return "guardian"


# =====================================================
# ENDINGS
# =====================================================


# -----------------------------------------------------
# ENDING 1: THE POWER-HUNGRY ADVENTURER
# -----------------------------------------------------

def ending_power():
    print("\n========== THE POWER-HUNGRY ADVENTURER ==========")
    print("\nYou reach out and take the ancient artifact.")
    print("An enormous wave of dark energy fills the castle.")
    print("The kingdom is consumed by darkness.")
    print("You have gained incredible power, but at a terrible cost.")

    print("\nENDING: THE POWER-HUNGRY ADVENTURER")

    return "credits"


# -----------------------------------------------------
# ENDING 2: THE HERO
# -----------------------------------------------------

def ending_hero():
    print("\n========== THE HERO ==========")
    print("\nYou raise your weapon and destroy the artifact.")
    print("A blinding light fills the chamber.")
    print("The darkness disappears, and the kingdom is finally free.")
    print("Your journey will be remembered for generations.")

    print("\nENDING: THE HERO")

    return "credits"


# -----------------------------------------------------
# ENDING 3: THE ETERNAL GUARDIAN
# -----------------------------------------------------

def ending_guardian():
    print("\n========== THE ETERNAL GUARDIAN ==========")
    print("\nYou carefully approach the artifact.")
    print("Instead of taking its power, you promise to protect it.")
    print("The ancient voice falls silent.")
    print("You become the guardian of the forgotten kingdom.")

    print("\nENDING: THE ETERNAL GUARDIAN")

    return "credits"


# -----------------------------------------------------
# ENDING 4: LOST FOREVER
# -----------------------------------------------------

def lost():
    print("\n========== LOST FOREVER ==========")
    print("\nYou wander too far into the mysterious forest.")
    print("The fog grows thicker, and the trees begin to look identical.")
    print("No matter which direction you travel, you cannot find your way home.")

    print("\nENDING: LOST FOREVER")

    return "credits"


# -----------------------------------------------------
# GAME CREDITS AND FINAL STATISTICS
# -----------------------------------------------------

def credits():
    print("\n========== ADVENTURE COMPLETE ==========")
    print(f"\nThank you for playing, {player['name']}!")

    show_stats()

    print("\nEvery decision creates a different adventure.")

    return "menu"


# =====================================================
# MAIN GAME LOOP
# =====================================================

def play_game():
    """Run the game using the current story location."""

    scene = player["current_scene"]

    # Connect each scene name to its function.
    scenes = {
        "forest": forest,
        "cabin": cabin,
        "trail": trail,
        "mountain": mountain,
        "village": village,
        "castle": castle,
        "artifact": artifact,
        "power": ending_power,
        "hero": ending_hero,
        "guardian": ending_guardian,
        "lost": lost,
        "credits": credits
    }

    while scene != "menu":

        if scene not in scenes:
            print("\nSomething went wrong with the story.")
            break

        # Remember the current location for saving.
        player["current_scene"] = scene

        # Run the function for the current location.
        next_scene = scenes[scene]()

        # Move to the next part of the adventure.
        scene = next_scene

        player["current_scene"] = scene


# =====================================================
# MAIN MENU
# =====================================================

def main():
    """Display the main menu and start the adventure."""

    global player

    while True:
        display_title()

        print("\n1. Start New Adventure")
        print("2. Load Saved Adventure")
        print("3. Quit Game")

        choice = input("\nSelect an option: ").strip()

        if choice == "1":
            player = new_game()
            play_game()

        elif choice == "2":
            loaded_player = load_game()

            if loaded_player is not None:
                player = loaded_player
                play_game()

        elif choice == "3":
            print("\nThank you for playing The Forgotten Kingdom!")
            print("Goodbye, adventurer!")
            break

        else:
            print("\nPlease select 1, 2, or 3.")


# -----------------------------------------------------
# START THE PROGRAM
# -----------------------------------------------------

if __name__ == "__main__":
    main()
