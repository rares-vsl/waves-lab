# WavesLab Simulation Environment

**WavesLab** is a simulation environment that models a household equipped with virtual occupants and smart furniture
hookups, called **WaveNodes**.
Each **WaveNode** represents a furniture connection that delivers a single utility (electricity, water, or gas) when
active.

---

### WaveNode

A WaveNode has the following attributes:

* **id** – a slugified version of the name.
* **name** – unique human-readable identifier.
* **node_type** – one of three types: `electricity`, `water`, or `gas`.
* **endpoint_url** – the destination URL where data is transmitted.
* **status** – indicates whether the node is active (`on`) or inactive (`off`).
* **real_time_consumption** – numeric value representing the amount of utility consumed.

---

### VirtualUser

* **username** – unique name for a simulated occupant.

---

### Command Line Interface (CLI)

The simulation entities are controlled via a CLI. It supports starting and stopping WaveNodes, as well as associating
them with users.

**Base Usage:**
`waveslab [COMMAND] [ARGS]...`

#### **Node Control Commands**

* **`waveslab start <node_id> [--user <user_name>]`**
* Starts a specific WaveNode.
* **Options:** `--user` or `-u` to associate a virtual user's token for outgoing requests.
* **Errors:** Exits with a non-zero status if the node is not found or fails to start.
* **Success:** Prints the success message and exits with status `0`.

* **`waveslab stop <node_id>`**
* Shuts down a running WaveNode.
* **Errors:** Exits with a non-zero status if the node is not found or fails to stop.
* **Success:** Prints the success message and exits with status `0`.


* **`waveslab switch <node_id>`**
* Toggles the current status of a WaveNode (On to Off, or vice-versa).
* Useful for quick manual overrides of simulation states.

#### **Monitoring & Status Commands**

* **`waveslab status`**
* Displays a simplified list of all registered nodes, showing their ID, current status (on/off), and friendly name.


* **`waveslab info`**
* Provides a detailed view of **all** nodes.
* **Output Format:** `[Endpoint] [Type - Consumption] [ID] [Status] - [Name]`


* **`waveslab info --active`**
* The same detailed view as `info`, but filtered to show only nodes that are currently **running**.
* 
### Server & API

The environment includes a server that exposes a simple REST API:

* **GET** `/api/wave-nodes`: retrieve all nodes.
* **GET** `/api/wave-nodes/{slug}`: retrieve details of a specific node.
* **PATCH** `/api/wave-nodes/{slug}`: assign or update the endpoint of a node.

---

### Node Behavior

* Every **5 seconds**, each active node automatically sends an HTTP `POST` request to its `endpoint_url`.
* The request payload includes:
    * the node’s `real_time_consumption`, and
    * the associated user’s `username` (if one is assigned).
* For simplicity, the system uses a **single loop** to trigger these requests across all active nodes.

---

### Scope & Simplifications

* Node and user management (creation, deletion) is out of scope.
* Only status toggling, endpoint assignment, and user association are supported.
* For data storage JSON file are used. 

