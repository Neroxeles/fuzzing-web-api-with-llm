# Installation and Usage Guide

## Install Cisco AnyConnect

- **Download Link**: Visit the following page and scroll down to find the download link: [Cisco AnyConnect Download](https://tu-dresden.de/zih/dienste/service-katalog/arbeitsumgebung/zugang_datennetz/vpn/ssl_vpn)
- **Instructions**: Follow the steps outlined here: [Cisco AnyConnect Setup Guide](https://faq.tickets.tu-dresden.de/otrs/public.pl?Action=PublicFAQZoom;ItemID=562;ZoomBackLink=QWN0aW9uPVB1YmxpY0ZBUVNlYXJjaDtTdWJhY3Rpb249U2VhcmNoO0tleXdvcmQ9QW55Q29ubmVj%0AdDtWaWE9VGFnQ2xvdWQ7U29ydEJ5PVRpdGxlO09yZGVyPVVwO1N0YXJ0SGl0PTE%3D%0A)

---

## Install MobaXTerm (Portable Version is Sufficient)

- **Instructions and Download**: [MobaXTerm Download and Setup](https://compendium.hpc.tu-dresden.de/access/ssh_mobaxterm/)
- **Usage Guide**: [Basic Usage of MobaXTerm (PDF)](https://compendium.hpc.tu-dresden.de/access/misc/basic_usage_of_MobaXterm.pdf)

> **Caution**: Always close your session after completing your tasks. To log out, type `exit` in the command line and press **Enter**.

---

## Start a Session

- **Instructions**: Refer to the [Getting Started Guide](https://compendium.hpc.tu-dresden.de/quickstart/getting_started/).
- **Connection Options**:
  - **JupyterHub** (not recommended)
  - **Terminal Software**: MobaXTerm or PuTTY
- **Cluster Options**:
  - Alpha (A100 GPUs)
  - Barnard (CPU-only)
  - Romeo
  - Vis
  - …

### Recommended Connection
Use the following hostname for connection:
```
login1.alpha.hpc.tu-dresden.de
```
This can be accessed through any terminal of your choice. MobaXTerm works well and is supported by a detailed guide: [MobaXTerm Usage Guide (PDF)](https://compendium.hpc.tu-dresden.de/access/misc/basic_usage_of_MobaXterm.pdf).

---

## Running Jobs

Once connected to the VPN and successfully logged into the server via SSH, use the following commands to manage jobs. For more details, consult the [Slurm Documentation](https://compendium.hpc.tu-dresden.de/jobs_and_resources/slurm/):

1. **Run a parallel application**:
   ```bash
   srun --nodes=1 --tasks=1 --cpus-per-task=2 --mem-per-cpu=2024 --gres=gpu:1 --time=01:00:00 --pty bash
   ```

2. **Submit a batch script** for execution later:
   ```bash
   sbatch
   ```

3. **Allocate resources** interactively (release them after use):
   ```bash
   salloc
   ```

### Example Usage
Navigate to your working directory (replace `<ZIH-Username>` with your own):
```bash
cd /data/horse/ws/<ZIH-Username>-my_python_virtualenv/
```

Clone the project repository:
```bash
git clone https://github.com/Neroxeles/fuzzing-web-api-with-llm.git
```

### Configuration Adjustments
In the cloned project, update the following files with correct paths:

1. **`configs/config-files/default.yml`**:
   - `output-dir` (Line 5)
   - `oas-location` (Line 7)
   - `scope-file` (Line 8)
   - `template` (Line 10)
   - `cache-dir` (Line 30)
   - `device-map` (Line 36)

2. **Add Token**: Add the required secret token to Line 15 (`secret-token`).

3. **`batch.sh`**:
   - Line 3
   - Line 5
   - Line 12

Run the batch script:
```bash
sh fuzzing-web-api-with-llm/batch.sh
```
This script installs the required Python modules, runs the program, and logs you out automatically once the job completes.

---

## Summary of Steps

1. Establish a VPN connection using Cisco AnyConnect.
2. Connect to the server via terminal software (e.g., MobaXTerm).
3. Run the following command in the terminal to start a job:
   ```bash
   srun --nodes=1 --tasks=1 --cpus-per-task=2 --mem-per-cpu=2024 --gres=gpu:1 --time=01:00:00 --pty bash
   ```
4. Navigate to your personal directory:
   ```bash
   cd /data/horse/ws/<ZIH-Username>-my_python_virtualenv/
   ```
5. Clone the project repository:
   ```bash
   git clone https://github.com/Neroxeles/fuzzing-web-api-with-llm.git
   ```
6. Update the configuration file (`default.yml`) and `batch.sh` with your specific paths and add the required token.
7. Execute the batch script:
   ```bash
   sh fuzzing-web-api-with-llm/batch.sh
   ```

### Logging Out (Necessary if the batch file is not executed and the steps are executed manually)
1. Exit the Python environment:
   ```bash
   deactivate
   ```
2. Disconnect from the node:
   ```bash
   exit
   ```
3. Close the terminal and log out completely:
   ```bash
   exit
   ```

---

## Transfer Data to/from ZIH Systems via Dataport Nodes

- **Instructions**: Refer to this guide: [Data Transfer via Dataport Nodes](https://compendium.hpc.tu-dresden.de/data_transfer/dataport_nodes/)

### Example Tool
I recommend **WinSCP** for file transfers. Install and configure it as described in the instructions.
