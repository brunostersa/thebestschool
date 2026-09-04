# The Best School — Landing Page

Landing page de captação de leads da PSA, publicada em
**https://profissionaissa.com.br/thebestschool/**

Página estática de arquivo único: HTML, CSS e JavaScript vivem todos em
`index.html`. Sem build, sem dependências, sem `node_modules`.

## Rodar local

```bash
python3 -m http.server 4173
```

Depois abra http://localhost:4173.

## Publicar

```bash
./build.sh
```

Gera `dist/` com apenas os arquivos que vão para o ar (~350 KB). Envie o
**conteúdo** de `dist/` para a pasta `thebestschool` da raiz pública do
servidor, via FTP.

O passo a passo completo — incluindo a configuração do formulário no HubSpot,
o cuidado com a barra final da URL e as pendências de conteúdo — está em
**[DEPLOY.md](DEPLOY.md)**.

## Estrutura

```
index.html                    a página inteira
assets/                       logos, ícones e imagens
  img/*.webp                  imagens otimizadas (desktop + mobile)
  *.png, *.svg                arquivos originais, fonte do build
uploads/                      material de referência do design
LP The Best School.dc.html    design original (Claude Design)
build.sh                      monta a dist/ para o FTP
.htaccess                     gzip, cache e barra final (Apache)
DEPLOY.md                     guia de publicação
```

## Formulário

Os leads vão para o HubSpot pela Forms API, o que permite manter o layout
próprio em vez do formulário embutido. As quatro perguntas do diagnóstico são
obrigatórias no HubSpot — os nomes internos das propriedades estão mapeados no
bloco `CONFIG`, no início do `<script>`. Ver DEPLOY.md antes de alterá-los.
