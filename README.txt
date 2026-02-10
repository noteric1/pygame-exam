NEON DRIFTER: FINAL TACTICAL EDITION
Student Name: Parich Wongpanich
Matriculation Number: 3121277
Course: (G-AMS-12) Advanced Programming
Professor: Navaneeth Shivananjappa

1. Project Overview
Neon Drifter is a physics-based arcade survival shooter developed entirely in Python using Pygame. Unlike traditional shooters, this game utilizes vector-based "drift" physics, requiring players to manage momentum and fuel.

The game features an infinite survival loop, a boss fight, local co-op multiplayer, and a tactical EMP system.

Technical Features:
• Graphics: Procedurally drawn visuals using `pygame.draw`.
• Hybrid Audio: Custom synthetic audio engine for real-time sound effects combined with high-fidelity background music (`music.ogg`).
• Tactical Gameplay: Integrated volume controls and "Neon Trail" performance toggles.

2. Installation & Execution
	1.  Prerequisites: Ensure you have Python 3.x installed.
	2.  Asset: Place your `music.ogg` in the same folder as this script.
	3.  Ensure you have Pygame installed / Install Pygame: pip install pygame
	4.  Run the Game: game.py
  
3. Controls

General
• P / ESC: Pause Game.
• Mouse: Navigate Menus.

Single Player / Player 1 (Cyan Ship)
• W / UP ARROW: Activate Thrusters.
• MOUSE: Aim / Rotate Ship.
• LEFT CLICK: Shoot.
• SPACEBAR: Dash.
• E: EMP Blast (Clears screen).

Player 2 (Orange Ship) - Co-Op Mode
• LEFT / RIGHT ARROWS: Rotate Ship.
• UP ARROW: Thrust.
• RIGHT CTRL / ENTER: Shoot.
• RIGHT SHIFT: Dash.
• NUMPAD 0: EMP Blast.

4. Game Features

Core Mechanics
• Drift Physics: Manage inertia and counter-steering.
• Fuel System: All movement and special abilities consume fuel.
• The Neon Colossus (Boss): Every 2,000 points, a boss appears with unique firing patterns.

5. Implementation Details (Custom Classes)
This project implements Object-Oriented Programming (OOP) with over 10 custom classes:
	1.  `Drifter` (Player): Handles physics and dual-input.
	2.  `Boss` (Enemy): Implements state-machine AI.
	3.  `Hunter` & `Sniper` (AI): Logic for chasing and kiting players.
	4.  `Particle`: Handles visual juice and engine trails.
	5.  `Button`: Reusable UI component with hover/click detection.