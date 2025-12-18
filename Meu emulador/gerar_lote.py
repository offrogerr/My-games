import os
import re

TEMPLATE = "template_jogo.html"
INDEX = "index.html"
ROMS = "roms"
THUMBS = "thumbs"

DEFAULTS = ["default.png", "default.jpg"]

CORES = {
    ".smc": "snes",
    ".sfc": "snes",
    ".nes": "nes",
    ".gba": "gba",
    ".gb": "gb",
    ".gbc": "gbc"
}

def titulo_amigavel(nome):
    nome = os.path.splitext(nome)[0]
    nome = re.sub(r"\(.*?\)", "", nome)
    nome = re.sub(r"-USA|-EUR|-JPN", "", nome, flags=re.I)
    nome = nome.replace("-", " ").replace("_", " ")
    return nome.strip()

def encontrar_thumb(base):
    if os.path.exists(f"{THUMBS}/{base}.png"):
        return f"{base}.png"
    if os.path.exists(f"{THUMBS}/{base}.jpg"):
        return f"{base}.jpg"
    for d in DEFAULTS:
        if os.path.exists(f"{THUMBS}/{d}"):
            return d
    return ""

# Carrega index e template
with open(INDEX, "r", encoding="utf-8") as f:
    index = f.read()

with open(TEMPLATE, "r", encoding="utf-8") as f:
    template = f.read()

for rom in os.listdir(ROMS):
    ext = os.path.splitext(rom)[1].lower()
    if ext not in CORES:
        continue

    base = os.path.splitext(rom)[0]
    html = f"{base}.html"
    titulo = titulo_amigavel(rom)
    core = CORES[ext]
    thumb = encontrar_thumb(base)

    # 1) HTML — cria apenas se não existir
    if not os.path.exists(html):
        conteudo = (
            template.replace("{{TITULO}}", titulo)
                    .replace("{{ROM}}", rom)
                    .replace("{{CORE}}", core)
        )
        with open(html, "w", encoding="utf-8") as f:
            f.write(conteudo)

    # 2) INDEX — âncora única = href
    href_token = f'href="{html}"'

    if href_token in index:
        # Card já existe → só troca imagem se for default
        img_regex = re.compile(
            rf'({href_token}[\s\S]*?<img src="thumbs/)([^"]+)(")',
            re.IGNORECASE
        )

        match = img_regex.search(index)
        if match:
            atual = match.group(2)
            if atual in DEFAULTS and thumb and atual != thumb:
                index = (
                    index[:match.start(2)] +
                    thumb +
                    index[match.end(2):]
                )
    else:
        # Card NÃO existe → cria (imagem + texto clicáveis)
        card = f"""
  <div class="card">
    <a href="{html}" class="card-link">
      <img src="thumbs/{thumb}" alt="{titulo}">
      <div class="title">{titulo}</div>
    </a>
  </div>
"""
        index = index.replace(
            "<!-- JOGOS_AQUI -->",
            card + "\n  <!-- JOGOS_AQUI -->"
        )

# Salva index uma única vez
with open(INDEX, "w", encoding="utf-8") as f:
    f.write(index)

print("=== LOTE EXECUTADO (IMAGEM E TEXTO CLICÁVEIS) ===")
