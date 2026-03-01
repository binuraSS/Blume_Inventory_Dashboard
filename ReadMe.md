🛠️ System Architecture
The application is built on a View-Controller-Database pattern:

Frontend (main.py + views/): A modern Material Design UI using CustomTkinter.

Styles (styles.py): A centralized design system for colors, fonts, and button behaviors.

Database Layer (database.py): A wrapper for the gspread API that handles multi-sheet logic and date calculations.

Cloud Database (Google Sheets):

Sheet 1 (Inventory): The "Source of Truth." Contains IDs and the critical "Last Service" date.

Sheet 2 (Active Faults): Current open tickets.

Sheet 3/4 (Archive): Permanent history of every repair.

✨ Key Features & Functionalities
1. The Overview (System Pulse)

Live Metrics: Categorizes the fleet into Healthy (Green), Overdue (Yellow), and Broken (Red).

Health Score: Dynamically calculates a "System Health %" based on active equipment versus maintenance debt.

2. The Unified Life Story (Search & History)

Timeline View: Merges inventory data, active faults, and archived repairs into a single chronological feed for any device ID.

Maintenance Awareness: If a device hasn't been serviced in 180 days, a yellow warning banner appears automatically.

3. The "Quick Inspect" Function

Allows technicians to reset the 180-day maintenance clock with a single click from the search results, instantly updating the cloud database.

🏗️ Technical Implementation: The "Maintenance Clock"
One of the most complex parts of this project was the synchronization between Sheet 4 (Archive) and Sheet 1 (Inventory).

The Logic:

When a ticket is Resolved in the Repair Center, the system:

Moves the ticket data to the Archive.

Immediately finds the device in the Inventory sheet.

Updates Column E (Last Service) with today's date.

The system uses LaTeX-style date comparisons to calculate maintenance debt:

DaysSinceService=CurrentDate−LastServiceDate

If DaysSinceService≥180, the status triggers a Yellow Pulse.

⚠️ Challenges & Debugging (Post-Mortem)
During development, we navigated several critical hurdles:

1. The "Free Variable" Lambda Trap

The Error: NameError: cannot access free variable 'e' inside a Tkinter callback.

The Cause: Attempting to pass an exception object e into a self.after() lambda after the except block had already finished.

The Fix: Used default argument capturing: lambda err=e: self.show_msg(err).

2. The "Stuck UI" Indentation Bug

The Error: The application would open but stay stuck on a single tab; clicking sidebar buttons changed colors but not the view.

The Cause: The frame.grid() command was accidentally placed outside the initialization loop in main.py, meaning only the last frame in the list was ever actually positioned on the screen.

The Fix: Indented the .grid() call into the loop to ensure every frame was stacked correctly in the deck.

3. Circular Imports and __init__.py

The Error: ImportError or NameError: DashboardView is not defined.

The Cause: Moving views into a separate folder requires an __init__.py file to export the classes properly.

The Fix: Standardized the views/__init__.py to explicitly import and expose all View classes.

🚀 Future Roadmap
Failure Heatmaps: Analyzing Archive notes to find which parts (screens, batteries) fail most often.

Bulk Inspections: Allowing technicians to scan multiple Blume IDs at once to reset service clocks.

User Authentication: Adding login tiers for "Technicians" vs "Admins."