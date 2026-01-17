import asyncio
import logging

from simulation.RealTimeSimulation import RealTimeSimulation

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    asyncio.run(RealTimeSimulation().start())