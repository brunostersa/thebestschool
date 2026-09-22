#!/bin/bash
# ==========================================================================
# Publica as prévias no GitHub Pages (branch gh-pages):
#   /thebestschool/            LP The Best School, a mesma da dist/
#   /aula-perspectiva-unica/   LP Perspectiva Única
#
# Nas duas o GTM sai e o envio ao HubSpot é interceptado: a prévia não gera
# lead nem conversão. Também não indexa (noindex).
#
# O gh-pages é gerado: cada publicação substitui a anterior por inteiro.
# Nada aqui mexe na main nem no que vai para o FTP.
# Uso:  ./publicar-previa.sh                publica
#       ./publicar-previa.sh --local DIR    só monta em DIR, sem publicar
# ==========================================================================
set -e
cd "$(dirname "$0")"

./build.sh > /dev/null
python3 aula-perspectiva-unica/montar.py > /dev/null

TMP=$(mktemp -d)
SITE="$TMP/site"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$SITE"

cp -R dist "$SITE/thebestschool"
rm -f "$SITE/thebestschool/.htaccess" "$SITE/thebestschool/sitemap.xml"
cp -R aula-perspectiva-unica/dist/previa "$SITE/aula-perspectiva-unica"
touch "$SITE/.nojekyll"

python3 - "$SITE" <<'PY'
import pathlib, re, sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'aula-perspectiva-unica')
from montar import MOCK, AVISO_PREVIA

site = pathlib.Path(sys.argv[1])
for pagina in (site / 'thebestschool').rglob('*.html'):
    s = pagina.read_text(encoding='utf-8')
    s = re.sub(r'<!-- Google Tag Manager.*?<!-- Fim do Google Tag Manager[^>]*-->\s*', '', s, flags=re.S)
    s = re.sub(r'<meta name="robots"[^>]*>', '', s)
    s = s.replace('<head>', '<head>\n<meta name="robots" content="noindex,nofollow">' + MOCK, 1)
    s = s.replace('</body>', AVISO_PREVIA + '</body>', 1)
    if 'googletagmanager' in s:
        sys.exit(f'GTM ainda presente em {pagina}')
    pagina.write_text(s, encoding='utf-8')

(site / 'index.html').write_text('''<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Prévias · The Best School</title>
<style>
body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;
background:#1A0800;color:#FEF8E8;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;padding:24px;box-sizing:border-box}
main{display:flex;flex-direction:column;gap:12px;width:min(420px,100%)}
h1{font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:#FD6501;margin:0 0 8px}
a{display:block;padding:18px 20px;border-radius:14px;background:#FEF8E8;color:#1A0800;text-decoration:none;font-weight:700}
a span{display:block;font-weight:400;font-size:13px;color:#5b4c42;margin-top:4px}
p{font-size:12px;color:rgba(254,248,232,.6);margin:8px 0 0}
</style></head><body><main>
<h1>Prévias · The Best School</h1>
<a href="thebestschool/">The Best School<span>LP no ar em profissionaissa.com.br/thebestschool/</span></a>
<a href="aula-perspectiva-unica/">Aula Perspectiva Única<span>Embed para o Elementor</span></a>
<p>Nas prévias o formulário não envia nada ao HubSpot.</p>
</main></body></html>
''', encoding='utf-8')
PY

# --local DIR: só monta, para conferir antes de publicar
if [ "$1" = "--local" ]; then
  rm -rf "$2" && cp -R "$SITE" "$2"
  echo "Prévia montada em $2 (nada foi publicado)"
  exit 0
fi

# Commit do site num índice temporário, sem tocar no branch atual
export GIT_INDEX_FILE="$TMP/index"
git --work-tree="$SITE" add -A
TREE=$(git write-tree)
COMMIT=$(git commit-tree "$TREE" -m "Prévias: The Best School e Aula Perspectiva Única

Gerado por publicar-previa.sh a partir de $(git rev-parse --short HEAD).

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>")
unset GIT_INDEX_FILE

git push -f origin "$COMMIT:refs/heads/gh-pages"

echo ""
echo "Prévias publicadas:"
echo "  https://brunostersa.github.io/thebestschool/thebestschool/"
echo "  https://brunostersa.github.io/thebestschool/aula-perspectiva-unica/"
