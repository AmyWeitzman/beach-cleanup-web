# Beach Clean-Up (Web)

Beach clean-up game where the player tries to pick up trash while avoiding the obstacles. Play it live at [amyweitzman.github.io/beach-cleanup-web](https://amyweitzman.github.io/beach-cleanup-web/).

> This is the browser version, rebuilt in vanilla JavaScript/HTML5 Canvas. The original Python/PyGame version is at [BeachHacks](https://github.com/AmyWeitzman/BeachHacks).

![Game Logo - palm tree on beach](imgs/logo.png)

## How to Play

- The game starts by showing you a Settings screen. You can toggle background music and sound effects on/off.

<img src="screenshots/settings.PNG" alt="Settings screen" width="500">

- Once you hit the "Play" button, the game will begin. Pieces of trash and obstacles will be coming towards you. Move around the beach using the **arrow keys**. Your goal is to collect the trash and avoid the obstacles.

  - The pieces of trash are: <br>
    Soda Can: <img src="imgs/trash/can.png" alt="Soda can" width="100">
    Cigarette: <img src="imgs/trash/cigarette.png" alt="Cigarette" width="100">
    Paper Wad: <img src="imgs/trash/paper_wad.png" alt="Paper wad" width="100">
    Water Bottle: <img src="imgs/trash/water_bottle.png" alt="Water bottle" width="100">

  - The obstacles are: <br>
    Crab: <img src="imgs/obstacles/crab.png" alt="Crab" width="100">
    Seagull: <img src="imgs/obstacles/seagull.png" alt="Seagull" width="100">
    Seaweed: <img src="imgs/obstacles/seaweed.png" alt="Seaweed" width="100">

- Each piece of trash collected is worth **20 points**. If you run into an obstacle, the game is over.
- You can also collect seashells for bonus points. Each seashell is worth **100 points**.

<img src="screenshots/game2.PNG" alt="Playing game screenshot" width="500">

## How to Run Locally

Just open `index.html` in any modern browser — no install or build step needed.

## Tech Stack

HTML5 Canvas · Vanilla JavaScript

---

Developed as part of BeachHacks 2021 · Web version 2026
