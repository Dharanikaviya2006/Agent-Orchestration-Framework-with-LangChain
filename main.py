from agent import run_basic_chain, run_reasoning_chain, run_agent

def show_menu():
    print("\n=== LangChain Milestone 1 Console ===")
    print("1. Basic Prompt Chain")
    print("2. Reasoning Prompt Chain")
    print("3. Zero-Shot Agent (with Calculator Tool)")
    print("4. Exit")

def main():
    print("LangChain Environment Initialized Successfully ✅")

    while True:
        show_menu()
        choice = input("Select an option: ")

        if choice == "4":
            print("Exiting... Goodbye!")
            break

        user_input = input("\nEnter your query: ")

        if choice == "1":
            response = run_basic_chain(user_input)
        elif choice == "2":
            response = run_reasoning_chain(user_input)
        elif choice == "3":
            response = run_agent(user_input)
        else:
            print("Invalid choice.")
            continue

        print("\n--- Response ---")
        print(response)

if __name__ == "__main__":
    main()
