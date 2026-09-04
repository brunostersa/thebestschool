#!/bin/bash
# ==========================================================================
# Monta a pasta dist/ com exatamente o que deve subir para o FTP.
# Uso:  ./build.sh
# ==========================================================================
set -e
cd "$(dirname "$0")"

rm -rf dist
mkdir -p dist/assets/img

# Página e configuração de servidor
# (sem robots.txt: em subdiretório ele é ignorado — vai na raiz do domínio)
cp index.html      dist/
cp .htaccess       dist/
cp sitemap.xml     dist/

# Somente os assets referenciados pela página
cp assets/logo-white.svg       dist/assets/
cp assets/logo-school-white.svg dist/assets/
cp assets/logo-psa-only-white.svg dist/assets/
cp assets/favicon.svg          dist/assets/
cp assets/apple-touch-icon.png dist/assets/
cp assets/img/*.webp           dist/assets/img/
cp assets/img/og-image.jpg     dist/assets/img/

# Remove metadados do macOS que sujam o FTP
find dist -name '.DS_Store' -delete
find dist -name '._*' -delete

echo ""
echo "dist/ pronta para o FTP:"
find dist -type f | sort | sed 's|^|  |'
echo ""
echo "Peso total: $(du -sh dist | cut -f1)"
