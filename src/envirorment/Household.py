import random
from datetime import datetime, timedelta

from core.model.NodeStatus import NodeStatus


class Household:
    def __init__(self, repository, switch_interval_minutes=5):
        """
        Initialize the household simulator.

        Args:
            repository: WavesLabRepository instance
            switch_interval_minutes: How many simulated minutes between device switches
        """
        self.repository = repository
        self.switch_interval = timedelta(minutes=switch_interval_minutes)
        self.last_switch_time = None
        self.cycle = 0

        # Day and night device counts
        self.day_devices_to_switch = 5
        self.night_devices_to_switch = 3

        # Time boundaries
        self.day_start_hour = 6
        self.night_start_hour = 21


        self.nodes_to_shutdown = []

    def is_daytime(self, current_timestamp: datetime) -> bool:
        """Check if current time is during daytime (6 AM to 9 PM)."""
        current_hour = current_timestamp.hour
        return self.day_start_hour <= current_hour < self.night_start_hour

    def get_num_devices_to_switch(self, current_timestamp: datetime) -> int:
        """Get the number of devices to switch based on time of day."""
        if self.is_daytime(current_timestamp):
            return self.day_devices_to_switch
        else:
            return self.night_devices_to_switch

    def should_switch_devices(self, current_timestamp: datetime) -> bool:
        """Check if it's time to switch devices based on simulated time."""
        if self.last_switch_time is None:
            self.last_switch_time = current_timestamp
            return True

        time_elapsed = current_timestamp - self.last_switch_time

        if time_elapsed >= self.switch_interval:
            self.last_switch_time = current_timestamp
            return True

        return False

    def switch_random_devices(self, current_timestamp: datetime):
        """Switch a random selection of devices."""
        # Get all nodes from the repository
        all_nodes = self.repository.get_all_nodes()

        if not all_nodes:
            print(f"[{current_timestamp}] Warning: No devices found in repository")
            return

        # Select random devices to switch
        num_to_switch = min(self.get_num_devices_to_switch(current_timestamp), len(all_nodes))
        selected_nodes = random.sample(all_nodes, num_to_switch)


        self.cycle += 1
        print(f"\n[{current_timestamp}] === Cycle {self.cycle} ===")
        print(f"[{current_timestamp}] Switching {num_to_switch} random devices:")

        nodes_to_shutdown = []

        for node in selected_nodes:
            if node.status == NodeStatus.ON:
                copia_nodo = node
                copia_nodo.real_time_consumption = 0
                nodes_to_shutdown.append(copia_nodo)
            try:
                self.repository.switch_node(node.id)
            except Exception as e:
                print(f"[{current_timestamp}] - Failed to switch {node.name}: {e}")

        self.nodes_to_shutdown = nodes_to_shutdown


    def tick(self, current_timestamp: datetime):
        """Called on each simulation tick to check if devices should be switched."""
        if self.should_switch_devices(current_timestamp):
            self.switch_random_devices(current_timestamp)

    def get_nodes_to_shutdown(self):
        nodes_to_shutdown = self.nodes_to_shutdown.copy()

        self.nodes_to_shutdown = []

        return nodes_to_shutdown