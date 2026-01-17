import asyncio
from typing import List

import httpx
import logging

from core.model.WaveNode import WaveNode
from core.storage.WavesLabRepository import repository
from envirorment.Household import Household

from datetime import datetime

from server.NodeRequest import NodeRequest

logger = logging.getLogger(__name__)

class RealTimeSimulation:
    def __init__(self):
        self.client = None
        self.running = None
        self.loop = None
        self._simulation_interval = 5

        self.household_simulator = Household(repository, switch_interval_minutes=1)

    async def start(self):
        self.client = httpx.AsyncClient(timeout=10.0)
        self.running = True
        self.loop = asyncio.create_task(self._simulation_loop())
        logger.info("Simulation loop started")
        await self.loop

    async def stop(self):
        """Stop the background task manager."""
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

                self.household_simulator.tick(now)

                active_nodes = repository.get_active_nodes()
                shutdown_nodes = self.household_simulator.get_nodes_to_shutdown()

                if active_nodes:
                    logger.info(f"Processing {len(active_nodes)} active nodes")
                    await self._send_requests_for_nodes(active_nodes)
                    logger.info(f"Processing {len(shutdown_nodes)} nodes to shutdown")
                    await self._send_requests_for_nodes(shutdown_nodes)
                else:
                    logger.info("No active nodes to process")

                await asyncio.sleep(self._simulation_interval)

            except asyncio.CancelledError:
                print("Request loop cancelled")
                break
            except Exception as e:
                print(f"Error in request loop: {e}")
                await asyncio.sleep(1)

    async def _send_requests_for_nodes(self, nodes: List[WaveNode]):
        tasks = []

        for node in nodes:
            task = asyncio.create_task(self._send_node_request(node))
            tasks.append(task)

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
            request_data = NodeRequest(
                realTimeConsumption=node.real_time_consumption,
                username=node.assigned_user
            )

            print(node.endpoint)
            response = await self.client.post(
                node.endpoint,
                json=request_data.model_dump(mode='json'),
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 204:
                logger.info(f"Request sent successfully for node '{node.name}' to {node.endpoint}")
                return True
            else:
                print("================")
                print(response)
                logger.info(f"Request failed for node '{node.name}': HTTP {response.status_code}")
                return False

        except httpx.TimeoutException:
            print(f"Request timeout for node '{node.name}' to {node.endpoint}")
            return False
        except httpx.RequestError as e:
            print(f"Network error for node '{node.name}': {e}")
            return False
        except Exception as e:
            print(f"Unexpected error sending request for node '{node.name}': {e}")
            return False

