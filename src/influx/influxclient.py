import json
import os
from datetime import datetime

from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from core.model.NodeType import NodeType


class InfluxDB:
    def __init__(self, url: str, token: str, org: str, bucket: str):
        self.url = url
        self.token = token
        self.org = org
        self.bucket = bucket
        self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

    def write_node_request(self, json_payload: str):
        """
        Writes a node measurement to InfluxDB from a JSON payload.
        Expected JSON format:
        {
            "type": "node_type",
            "smart_furniture_hookup_id": "string",
            "real_time_consumption": float,
            "timestamp": "ISO8601 string"
        }
        """
        try:
            data = json.loads(json_payload)

            point = (
                Point(data["type"])
                .tag("smartFurnitureHookupID", data["smart_furniture_hookup_id"])
                .field("value", float(data["real_time_consumption"]))
                .time(data["timestamp"])
            )

            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            print("✅ Wrote point:", point)

        except json.JSONDecodeError:
            print("❌ Failed to decode JSON payload")
        except KeyError as e:
            print(f"❌ Missing key in payload: {e}")
        except Exception as e:
            print(f"❌ Error writing point: {e}")


load_dotenv()

influxDB =  InfluxDB(
    os.getenv("INFLUX_URL"),
    os.getenv("INFLUX_TOKEN"),
    os.getenv("INFLUX_ORG"),
    os.getenv("INFLUX_BUCKET")
)


if __name__ == "__main__":
    utility = NodeType.ELECTRICITY.value
    url = "http://localhost:3002/api/internal/measurements?smart_furniture_hookup_id=0d2185f0-2c09-4d1f-981a-651735977d01"
    smart_furniture_hookup_id = url.split('smart_furniture_hookup_id=')[-1]
    real_time_consumption = "2.0"
    time = datetime(2025, 11, 14, 6, 0, 0)

    payload = {
        "type": utility,
        "smart_furniture_hookup_id": smart_furniture_hookup_id,
        "real_time_consumption": real_time_consumption,
        "timestamp": time.isoformat() + "Z"
    }

    print(os.getenv("INFLUX_URL"))

    print(json.dumps(payload))

    # influxDB.write_node_request(json.dumps(payload))
