import csv

class TableBuilder():
  def __init__(self, loops: int, date_time: str, filepath: str):
    self.total_properties = 0
    self.loops = loops
    self.date_time = date_time
    self.filepath = filepath
    self.table_line = 0
  
  def set_total_properties(self, total_properties: int):
    self.total_properties = total_properties

  def part_1(self):
    content  = "\\subsection{Testdurchführung " + self.date_time + "}\n"
    content += "\\begin{table}[ht]\n"
    content += "  \\centering\n"
    content += "  \\begin{tabular}{l | r r r | c c c c}\n"
    content += "    \\multicolumn{4}{c}{} & \multicolumn{4}{|c|}{\cellcolor{highlightListing}Kriterien}\\\\\n"
    content += "    \\Xhline{3\\arrayrulewidth}\n"
    content += "    \\rowcolor{headerTable}\n"
    content += "    \\multicolumn{1}{c|}{\\textbf{Dateiname}} & \\multicolumn{1}{C{1.5cm}}{\\textbf{Eing. Tokens}} & \\multicolumn{1}{C{1.5cm}}{\\textbf{Ausg. Tokens}} & \\multicolumn{1}{C{1.5cm}|}{\\textbf{Zeit \\hspace{.2cm} (sek.)}} & \\textbf{exe} & \\textbf{rnd} & \\textbf{crv} & \\textbf{cfn}\\\\\n"
    content += "    \\Xhline{2\\arrayrulewidth}\n"
    with open(self.filepath + "table.tex", "a") as f:
      f.write(content)

  def part_2(self, filename: str, etok: int, atok: int, sec: float, resamplings: int):
    if self.table_line % 2 == 0:
      content  =  "    \\rowcolor{bodyTable1}\n"
    else:
      content  =  "    \\rowcolor{bodyTable2}\n"
    content += f"    {filename} & {etok} & {atok} & {sec:.3f} & exe & rnd & crv & cfn\\\\\n"
    if ((self.table_line+1) % self.loops == 0) and not (self.table_line == (self.total_properties * self.loops) - 1) and not (self.table_line == 0 and self.loops != 1):
      content += "    \\Xhline{2\\arrayrulewidth}\n"
    elif self.table_line == (self.total_properties * self.loops) - 1:
      content += "    \\Xhline{3\\arrayrulewidth}\n"
      content += "    \\multicolumn{2}{l}{Resamplings = " + str(resamplings) + "} & \\multicolumn{2}{r|}{\\textbf{Summe}} & sum & sum & sum & sum"
      content += "  \\end{tabular}\n"
      content += "  \\caption{Bewertung des Testdurchlaufs von " + self.date_time + "}\n"
      content += "  \\label{tab:eva" + self.date_time.replace(" ", "").replace(":", "") + "}\n"
      content += "\\end{table}\n"
    self.table_line += 1
    with open(self.filepath + "table.tex", "a") as f:
      f.write(content)
  
  def part_3(self, model: str, loaded_in: str, batch_size: int, temperature: float, top_k: int, top_p: float):
    content  = "\\begin{landscape}\n"
    content += "  \\begin{table}\n"
    content += "    \\centering\n"
    content += "    \\resizebox{\\linewidth}{!}{\n"
    content += "    \\begin{tabular}{C{2cm} C{2cm} C{2.5cm} C{1.5cm} C{1.5cm} C{1.4cm} C{1cm} C{1cm} c C{2cm} c C{2.2cm} c c}\n"
    content += "      \\multicolumn{3}{c}{} & \\multicolumn{6}{|c|}{\\cellcolor{highlightListing}Konfiguration des Modells}\\\\\n"
    content += "      \\Xhline{3\\arrayrulewidth}\n"
    content += "      \\rowcolor{headerTable}\n"
    content += "      \\textbf{Prompt Version} & \\textbf{OAS Version} & \\textbf{Datum \\& Uhrzeit} & \\textbf{Modell} & \\textbf{loaded in} & \\textbf{Batch-Size} & \\textbf{Top k} & \\textbf{Top p} & \\textbf{Temp.} & \\textbf{Methoden} & \\textbf{Prop.} & \\textbf{Score} & \\textbf{Ref.} \\\\\n"
    content += "      \\Xhline{2\\arrayrulewidth}\n"
    content += "      \\rowcolor{bodyTable1}\n"
    content += "      V? & V? & " + self.date_time + " & " + model + " & " + loaded_in + " & " + str(batch_size) + " & " + str(top_k) + " & " + str(top_p) + " & " + str(temperature) + " & unknown & " + str(self.total_properties) + " & na & T\\ref{tab:eva" + self.date_time.replace(" ", "").replace(":", "") + "}\\\\\n"
    content += "      \\Xhline{2\\arrayrulewidth}\n"
    content += "      \\rowcolor{bodyTable1}\n"
    content += "      \\multicolumn{13}{c}{-- Zwischenergebnis --}\\\\\n"
    content += "      \\Xhline{3\\arrayrulewidth}\n"
    content += "    \\end{tabular}}\n"
    content += "    \\caption{Zusammenfassung aller Bewertungen Teil 1}\n"
    content += "    \\label{tab:prompt-technics}\n"
    content += "  \\end{table}\n"
    content += "\\end{landscape}\n\n\n"
    with open(self.filepath + "table.tex", "a") as f:
      f.write(content)
    
  def write_csv_meta_data(self, data: dict):
    with open(self.filepath + "meta.csv", "w") as f:
      for key in data:
        if key == "eos":
          f.write(f"{key},")
          eos_string = ""
          for eos in data[key]:
            eos_string += f"'{eos}';"
          f.write(f"{eos_string[:-1]}\n")
          continue
        f.write(f"{key},{data[key]}\n")

  def write_csv_data(self, data: dict):
    with open(self.filepath + "data.csv", "w") as f:
      f.write(f"filename,input-tokens,output-tokens,time-in-sec\n")
      for idx, _ in enumerate(data['filename']):
        f.write(f"{data['filename'][idx]},{data['input-tokens'][idx]},{data['output-tokens'][idx]},{data['time-in-sec'][idx]}\n")

def make_table_builder(loops: int, date_time: str, filepath: str):
  return TableBuilder(
    loops=loops,
    date_time=date_time,
    filepath=filepath
  )