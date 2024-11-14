# Install Cisco AnyConnect

Download Link (etwas weiter runter scrollen): https://tu-dresden.de/zih/dienste/service-katalog/arbeitsumgebung/zugang_datennetz/vpn/ssl_vpn

Anleitung: https://faq.tickets.tu-dresden.de/otrs/public.pl?Action=PublicFAQZoom;ItemID=562;ZoomBackLink=QWN0aW9uPVB1YmxpY0ZBUVNlYXJjaDtTdWJhY3Rpb249U2VhcmNoO0tleXdvcmQ9QW55Q29ubmVj%0AdDtWaWE9VGFnQ2xvdWQ7U29ydEJ5PVRpdGxlO09yZGVyPVVwO1N0YXJ0SGl0PTE%3D%0A

# Install MobaXTerm (Portable reicht)

Anleitung + Download: https://compendium.hpc.tu-dresden.de/access/ssh_mobaxterm/

Anleitung: https://compendium.hpc.tu-dresden.de/access/misc/basic_usage_of_MobaXterm.pdf

>**Caution**: Do not forget to close the session after your jobs are finished. Just type `exit` in the command line and complete with pressing enter.

## Session starten

Anleitung: https://compendium.hpc.tu-dresden.de/quickstart/getting_started/

Es gibt grundsätzlich mehrere Möglichkeiten sich mit den Systemen zu verbinden.
- JupyterHub (nicht empfohlen)
- Terminal wie z.B. MobaXTerm oder Putty
Weiterhin gibt es auch verschiedene Cluster mit denen man sich verbinden kann.
- Alpha (A100 Grafikkarten)
- Barnard (CPU only)
- Romeo
- Vis
- ...

Ich empfehle die Verbindung mit `login1.alpha.hpc.tu-dresden.de` über ein Terminal seiner Wahl. Bei mir scheint MobaXTerm prima zu funktionieren. Auch die hier verlinkte Anleitung ist sehr ausführlich. ([Link](https://compendium.hpc.tu-dresden.de/access/misc/basic_usage_of_MobaXterm.pdf))

Ist man mit dem VPN verbunden und konnte sich erfolgreich mit dem Server über ssh verbinden, kann man folgende 3 Befehle verwenden, um einen Job auszuführen (siehe auch [link](https://compendium.hpc.tu-dresden.de/jobs_and_resources/slurm/)):
- **Run a parallel application** (and, if necessary, allocate resources first).
```
srun --nodes=1 --tasks=1 --cpus-per-task=2 --mem-per-cpu=2024 --gres=gpu:1 --time=01:00:00 --pty bash
```
- **Submit a batch script to Slurm for later execution**.
```
sbatch
```
- **Obtain a Slurm job allocation** (i.e., resources like CPUs, nodes and GPUs) for interactive use. Release the allocation when finished.
```
salloc
```
Ich habe bisher nur mit `srun` gearbeitet. Für die wichtigsten Parameter verweise ich auf die entsprechende [Seite](https://compendium.hpc.tu-dresden.de/jobs_and_resources/slurm/) oder auf die man-pages. Ich versuche das ganze noch in Form eines Batch-Jobs aufzubereiten. Mit `srun` kann man anschließend Jobs ausführen, indem man z.B. einfach das Python-Programm ausführt.

Anschließend kann man auf seinen persönlichen Ordner wechseln. Bei mir wäre dies:
```
cd /data/horse/ws/rosc409g-my_python_virtualenv/
```
dort kann man dann auch das Projekt erstellen:
```
git clone -b rework https://github.com/Neroxeles/fuzzing-web-api-with-llm.git
```

In den folgenden Dateien müssen Pfadangaben noch angepasst werden:
- fuzzing-web-api-with-llm\configs\config-files\default.yml
	- device-map (Zeile 36)
	- template (10)
	- scope-file (8)
	- oas-location (7)
	- output-dir (5)
- fuzzing-web-api-with-llm\batch.sh
	- Zeile 3
	- Zeile 5
	- Zeile 12

Im Projekt selber wurde eine batch.sh Datei angelegt. Diese kann einfach ausgeführt werden. Damit werden auch noch die fehlenden Python Module installiert. Anschließend wird dann auch noch das Programm ausgeführt und die Session wird automatisch beendet, sobald der Job ausgeführt wurde.

### Zusammenfassung:

1. VPN-Verbindung mit Cisco AnyConnect
2. Verbindung über ein Terminal wie Putty oder MobaXTerm
3. `srun --nodes=1 --tasks=1 --cpus-per-task=2 --mem-per-cpu=2024 --gres=gpu:1 --time=01:00:00 --pty bash` in der Konsole ausführen
4. zu `cd /data/horse/ws/<ZIH-Username>-my_python_virtualenv/` navigieren
5. `git clone -b rework https://github.com/Neroxeles/fuzzing-web-api-with-llm.git`
6. Config-Datei & Batch.sh Pfadangaben anpassen
7. `sh fuzzing-web-api-with-llm/batch.sh` ausführen

> **Wenn man Man sich ausloggen möchte:**
> 	1. `deactivate` zum verlassen der Pythonumgebung
> 	2. `exit` um sich von der Node zu trennen
> 	3. `exit` um Terminal zu schließen & sich auszuloggen

# Transfer Data to/from ZIH Systems via Dataport Nodes

Anleitung: https://compendium.hpc.tu-dresden.de/data_transfer/dataport_nodes/

Ich selber habe WinSCP installiert und wie in der Anleitung eingerichtet.
