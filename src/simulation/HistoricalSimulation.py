import asyncio
import json
from typing import List

import httpx
import logging

from core.model.WaveNode import WaveNode
from core.storage.WavesLabRepository import repository
from envirorment.Household import Household
from datetime import datetime, timedelta

from influx.influxclient import influxDB

logger = logging.getLogger(__name__)


class HistoricalSimulation:
    def __init__(self):
        self.client = None
        self.running = None
        self.loop = None
        # Start from June 1st, 2024 00:00:00
        self.current_timestamp = datetime(2025, 10, 1, 0, 0, 0)
        self._time_increment = timedelta(seconds=20)

        # Initialize household simulator (switches devices every 15 simulated minutes)
        self.household_simulator = Household(repository, switch_interval_minutes=15)

    async def start(self):
        self.running = True
        self.loop = asyncio.create_task(self._simulation_loop())
        logger.info(f"Simulation loop started at timestamp: {self.current_timestamp}")

        await self.loop

    async def stop(self):
        """Stop the background task manager."""
        print("FINE")
        if not self.running:
            return

        self.running = False

        if self.loop:
            self.loop.cancel()
            try:
                await self.loop
            except asyncio.CancelledError:
                pass

        if self.client:
            await self.client.aclose()
            self.client = None

        logger.info("Simulation loop stopped")

    async def _simulation_loop(self):
        while self.running:
            try:
                now = datetime.now()
                if self.current_timestamp >= now:
                    logger.info(f"Simulation reached current timestamp: {now}. Stopping simulation.")
                    await self.stop()
                    break

                # Check if household devices should be switched
                self.household_simulator.tick(self.current_timestamp)
                print("Ciao")
                active_nodes = repository.get_active_nodes()
                if active_nodes:
                    print(f"Processing {len(active_nodes)} active nodes at timestamp: {self.current_timestamp}")
                    await self._send_requests_for_nodes(active_nodes)
                else:
                    print(f"No active nodes to process at timestamp: {self.current_timestamp}")

                # Update timestamp after processing
                self.current_timestamp += self._time_increment

            except asyncio.CancelledError:
                print("Request loop cancelled")
                break
            except Exception as e:
                print(f"Error in request loop: {e}")
                # Still increment timestamp even on error
                self.current_timestamp += self._time_increment

    async def _send_requests_for_nodes(self, nodes: List[WaveNode]):
        tasks = []

        for node in nodes:
            task = asyncio.create_task(self._send_node_request(node))
            tasks.append(task)

        print("hello")
        if tasks:
            try:
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Log results
                success_count = sum(1 for result in results if result is True)
                error_count = len(results) - success_count

                if success_count > 0:
                    print(f"Successfully sent {success_count} node requests")
                if error_count > 0:
                    print(f"Failed to send {error_count} node requests")
            except Exception as e:
                print(f"Error in request loop: {e}")

    async def _send_node_request(self, node: WaveNode) -> bool:
        try:
            utility = node.node_type.value

            url = node.endpoint  # your URL string

            smart_furniture_hookup_id = url.split('smart_furniture_hookup_id=')[-1]

            real_time_consumption = node.real_time_consumption
            time = self.current_timestamp

            payload = {
                "type": utility,
                "smart_furniture_hookup_id": smart_furniture_hookup_id,
                "real_time_consumption": real_time_consumption,
                "timestamp": time.isoformat() + "Z"
            }

            influxDB.write_node_request(json.dumps(payload))

            print(f"Request sent successfully for node '{node.name}' to {node.endpoint}")
            return True

        except httpx.TimeoutException:
            print(f"Request timeout for node '{node.name}' to {node.endpoint}")
            return False
        except httpx.RequestError as e:
            print(f"Network error for node '{node.name}': {e}")
            return False
        except Exception as e:
            print(f"Unexpected error sending request for node '{node.name}': {e}")
            return False

