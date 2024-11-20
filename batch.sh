# used for ZIH HPC systems
# srun --nodes=1 --tasks=1 --cpus-per-task=2 --mem-per-cpu=2024 --gres=gpu:1 --time=01:00:00 --pty bash
cd /data/horse/ws/rosc409g-my_python_virtualenv
module load release/23.04 GCC/11.3.0 OpenMPI/4.1.4 CUDAcore/11.5.1 PyTorch/1.12.1
if [ ! -d "my-env" ]; then
  echo "create my-env directory."
  python -m venv --system-site-packages my-env
fi
source my-env/bin/activate
cd fuzzing-web-api-with-llm
pip install -r requirements.txt
python Fuzzer/main.py configs/config-files/default.yml
deactivate