import subprocess
import time
import sys
from pycloudflared import try_cloudflare

print("==================================================", flush=True)
print("Iniciando Monitor YMS SGO2 + Tunel HTTPS Ao Vivo...", flush=True)
print("==================================================", flush=True)

PORT = 8585

# 1. Iniciar o Streamlit em segundo plano na porta 8585
cmd = [
    sys.executable, "-m", "streamlit", "run", 
    r"C:\Users\rogsouza\Desktop\Python_VS\app_sgo2_realtime.py", 
    f"--server.port={PORT}", 
    "--server.address=0.0.0.0",
    "--server.headless=true"
]

proc = subprocess.Popen(cmd)

time.sleep(4)

# 2. Iniciar Túnel Cloudflare para gerar Link HTTPS público
try:
    url = try_cloudflare(port=PORT)
    print("\n" + "="*65, flush=True)
    print("  LINK PUBLICO HTTPS PARA RIO VERDE (SGO2):", flush=True)
    print(f"  --> {url.tunnel} <--", flush=True)
    print("="*65 + "\n", flush=True)
    print("Qualquer computador ou celular em Rio Verde / MELI pode abrir!", flush=True)
    print("Pressione Ctrl+C para encerrar o monitoramento.\n", flush=True)
except Exception as e:
    print(f"Aviso ao iniciar o tunel: {e}", flush=True)

try:
    proc.wait()
except KeyboardInterrupt:
    print("\nEncerrando o Monitor YMS...", flush=True)
    proc.terminate()
