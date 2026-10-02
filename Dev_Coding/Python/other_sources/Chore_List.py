ChorelistJ = ["Clean The Litter","Make Food","Organize Clothes","Clean The Room","Feed Cats","Clean Water"]
Username2 = "Jj"
Name = input("Enter your name: ")


if Name == Username2:
    print(f"Hello Jj, your chores are: ", ChorelistJ)
    if len(ChorelistJ) == 0:
        input("You have completed all your chores, press Any Button to exit")
    while len(ChorelistJ) > 0:
        ChoresDone = input("Which chores have you done?: ")
        ChoresDone = ChoresDone.title()
        ChoresDone = ChoresDone.strip()

        if ChoresDone in ChorelistJ:
            ChorelistJ.remove(ChoresDone)
            if len(ChorelistJ) > 0:
                print(f"Good job Jj, your remaining chores are: ", ChorelistJ)
            if len(ChorelistJ) == 0:
                completed = input("You have completed all your chores, press Enter Button to exit")
                break