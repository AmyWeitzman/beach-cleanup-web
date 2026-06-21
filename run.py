import asyncio
import pygame
from game import Game

async def main():
    game = Game()
    while game.tick():
        await asyncio.sleep(0)

asyncio.run(main())
