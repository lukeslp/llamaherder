# Caminaå: A Mixture-of-Experts (MoE) Architecture

Caminaå is an advanced MoE system designed to coordinate task execution using a team of specialized agents. The system consists of:

- **Caminaå (Coordinator):**  
  - **Model:** `mistral-small:22b`  
  - **Role:** Serves as the central reasoning agent. It parses incoming tasks, consults with the background reasoning agent, and delegates sub-tasks to the specialized agents.

- **Belters (File Manipulation Agents):**  
  - **Model:** `mistral:7b`  
  - **Role:** Handle file operations and tool-based interactions, managing the creation, deletion, and modification of files as needed.

- **Drummers (Information Gathering Agents):**  
  - **Model:** `mistral:7b`  
  - **Role:** Focus on gathering context and information required for the task. They query data sources and extract pertinent details for synthesis.

- **DeepSeek Reasoner (Background Reasoning Agent):**  
  - **Model:** `deepseek-r1:7b`  
  - **Role:** Operates in the background, offering a contemplative layer that reviews and refines the overall process. It provides high-level feedback to Caminaå, ensuring robust task planning and execution.

---

## Repository Structure

```
Caminaa/
├── models/
│   ├── caminaa/                # Model files for Caminaå (mistral-small:22b)
│   ├── belters/                # Model files for Belters (mistral:7b)
│   ├── drummers/               # Model files for Drummers (mistral:7b)
│   └── deepseek/               # Model files for DeepSeek (deepseek-r1:7b)
├── tools/                      # Tools for file manipulation, information retrieval, etc.
│   ├── file_manager.py         # Utilities for file operations (used by Belters)
│   ├── info_gather.py          # Modules for data and context gathering (used by Drummers)
│   └── api_utils.py            # API communication and helper functions
├── servers/                    # Server scripts to host each agent
│   ├── caminaa_server.py       # API server for Caminaå
│   ├── belters_server.py       # API server for Belters
│   ├── drummers_server.py      # API server for Drummers
│   └── deepseek_server.py      # API server for DeepSeek
├── config/                     # Configuration files for models, API endpoints, and system parameters
│   ├── models_config.yaml
│   └── server_config.yaml
├── tests/                      # Unit and integration tests for all modules
├── README.md                   # Project readme file
└── project_plan.md             # Detailed project plan and milestones
```

---

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/your_org/Caminaa.git
   cd Caminaa
   ```

2. **Set Up the Python Environment:**

   Create and activate a virtual environment (Python 3.8+ recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Linux/macOS
   .\venv\Scripts\activate    # On Windows
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Model Files:**

   Place the respective model files for:
   - `mistral-small:22b` into `models/caminaa/`
   - `mistral:7b` into both `models/belters/` and `models/drummers/`
   - `deepseek-r1:7b` into `models/deepseek/`

   Adjust paths and parameters in `config/models_config.yaml` as needed.

---

## Usage

### Running the Servers

Start each agent's server in separate terminal windows or using a process manager:

- **Caminaå (Coordinator):**

   ```bash
   python servers/caminaa_server.py
   ```

- **Belters (File Manipulation):**

   ```bash
   python servers/belters_server.py
   ```

- **Drummers (Information Gathering):**

   ```bash
   python servers/drummers_server.py
   ```

- **DeepSeek Reasoner (Background Agent):**

   ```bash
   python servers/deepseek_server.py
   ```

### Workflow Overview

1. **Task Reception:**
   A user submits a complex task to Caminaå via its API.
2. **Coordination & Reasoning:**
   Caminaå uses its `mistral-small:22b` backbone to interpret the task and consults the DeepSeek Reasoner (`deepseek-r1:7b`) for meta-level insights.
3. **Delegation:**
   Based on the analysis, Caminaå delegates:
    - File-related tasks to Belters.
    - Information gathering tasks to Drummers.
4. **Execution:**
   Belters and Drummers perform their specialized roles, using the tools available in the `tools/` directory.
5. **Synthesis & Output:**
   Results are sent back to Caminaå, which integrates the outputs into a final, coherent response.

---

## Configuration

- **Model Configuration:**
  Update `config/models_config.yaml` to modify model parameters, file paths, and other relevant settings.
  
- **Server Configuration:**
  Adjust API endpoints, ports, and timeouts in `config/server_config.yaml`.

---

## Testing

- **Unit Tests:**
  Run tests for individual components:
  
   ```bash
   pytest tests/unit
   ```

- **Integration Tests:**
  Validate the entire workflow:

   ```bash
   pytest tests/integration
   ```

---

## Contributing

Contributions are welcome! Please read our `CONTRIBUTING.md` for guidelines on how to contribute to the project.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details. 