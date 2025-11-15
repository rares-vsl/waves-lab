import asyncio
import logging

from simulation.HistoricalSimulation import HistoricalSimulation

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    asyncio.run(HistoricalSimulation().start())