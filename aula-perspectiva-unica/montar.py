#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monta a LP Perspectiva Única para o Elementor.

Uso:  python3 aula-perspectiva-unica/montar.py

Gera em aula-perspectiva-unica/dist/:
  embed-elementor.html   o que se cola no widget HTML (logos já embutidos)
  imagens/pu-*.webp      o que se sobe na Biblioteca de Mídia do WordPress
  preview.html           prévia local, com um tema "hostil" simulado e o
                         envio ao HubSpot interceptado (não cria lead)

Antes de gerar, confere as opções: o "value" de cada resposta tem de ser o
texto exato cadastrado no HubSpot. Quando não bate, o HubSpot aceita o envio e
descarta a resposta em silêncio. Se algo divergir, o build é interrompido.
"""
import html
import pathlib
import re
import shutil
import sys

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parent
DIST = AQUI / 'dist'
URL_UPLOADS = 'https://profissionaissa.com.br/wp-content/uploads/2026/09/'

# Valores aceitos pelo HubSpot — portal 49656171, form 634374b1-…
# Conferidos contra o formulário publicado em 22/09/2026. Para atualizar,
# leia a definição do formulário (passo a passo no DEPLOY.md da LP).
OFICIAL = {
    'voce_ja_atua_como_palestrante_': [
        "Sim, já realizo palestras remuneradas.",
        "Sim, mas apenas de forma gratuita.",
        "Não, ainda não atuo como palestrante.",
    ],
    'qual_a_sua_atuacao_hoje___new_campaign_': [
        "Palestrante profissional",
        "Executivo (VP/Diretor/C-level)",
        "Acadêmico (Mestre/Doutor)",
        "Empreendedor (Founder/Cofounder)",
        "Coach/Psicologo/RH",
        "Outra",
    ],
    'temos_programas_para_diversos_estagios_da_carreira_de_palestrante_o_que_voce_esta_buscando_new': [
        "Apenas conhecer o mercado de palestras de forma gratuita.",
        "Ingressar profissionalmente no mercado (investimento de até 1k)",
        "Consolidar minha carreira de palestrante (investimento de até 5k)",
        "Gerar mais receita com as minhas palestras (investimento de até 15k)",
        "Consolidar como palestrante de alto impacto (investimento de +20k)",
    ],
    'voce_ja_esta_pronto_para_investir_na_sua_carreira_como_palestrante_': [
        "Sim, quero começar o quanto antes!",
        "Sim, estou planejando investir ainda este ano",
        "Não, ainda não estou pronto.",
    ],
}

# Imagem de origem (LP The Best School) → nome no WordPress.
# O prefixo pu- evita colidir com arquivos que já existem na Biblioteca de
# Mídia: o WordPress renomearia para -1.webp e a URL do embed quebraria.
IMAGENS = {
    'assets/img/marcio-palco.webp':    'pu-hero-marcio.webp',
    'assets/img/marcio-spagnolo.webp': 'pu-marcio-spagnolo.webp',
}


def conferir(fonte):
    problemas = []
    blocos = re.findall(r'<fieldset class="pu-q"([^>]*)>(.*?)</fieldset>', fonte, re.S)
    ligadas = 0
    for attrs, corpo in blocos:
        prop = re.search(r'data-hubspot="([^"]*)"', attrs).group(1)
        if not prop:
            continue
        ligadas += 1
        if prop not in OFICIAL:
            problemas.append(f'{prop}: propriedade sem lista de referência no montar.py')
            continue
        vals = [html.unescape(v) for v in re.findall(r'<input type="radio"[^>]*value="([^"]*)"', corpo)]
        nomes = set(re.findall(r'<input type="radio" name="([^"]*)"', corpo))
        if nomes != {prop}:
            problemas.append(f'{prop}: o name dos radios ({", ".join(sorted(nomes))}) difere do data-hubspot')
        for e in OFICIAL[prop]:
            if e not in vals:
                problemas.append(f'{prop}: falta a opção {e!r}')
        for v in vals:
            if v not in OFICIAL[prop]:
                problemas.append(f'{prop}: {v!r} não existe no HubSpot e seria descartado')
    faltando = set(OFICIAL) - set(re.findall(r'data-hubspot="([^"]+)"', fonte))
    for f in sorted(faltando):
        problemas.append(f'{f}: obrigatória no HubSpot, mas não está ligada na LP — o envio seria recusado')
    return ligadas, problemas


def svg_inline(caminho, classe):
    s = (RAIZ / caminho).read_text(encoding='utf-8')
    s = re.sub(r'<\?xml[^>]*\?>', '', s)
    s = re.sub(r'\s(id|class)="[^"]*"', '', s)
    s = re.sub(r'<defs>\s*</defs>', '', s)
    return s.replace('<svg', f'<svg class="{classe}" aria-hidden="true" focusable="false"', 1).strip()


# Simula o que o tema Hello Elementor aplica em elementos soltos, para a
# prévia mostrar se o #psa-pu segura o layout.
TEMA_HOSTIL = """
body{margin:0;font-family:Georgia,serif;font-size:14px;line-height:2;color:#333;background:#eee;}
h1,h2,h3{font-size:3rem;color:#c36;margin:2rem 0;font-family:Georgia,serif;}
p{margin:1.5rem 0;}
a{color:#c36;text-decoration:underline;}
label{display:inline-block;line-height:1;vertical-align:middle;}
input[type=text],input[type=email],input[type=tel]{width:100%;border:1px solid #666;border-radius:3px;padding:.5rem 1rem;}
button,[type=submit],[type=button]{display:inline-block;color:#c36;background:transparent;border:1px solid #c36;padding:.5rem 1rem;border-radius:3px;font-size:1rem;}
button:hover,[type=submit]:hover{color:#fff;background:#c36;}
fieldset{border:1px solid #666;margin:0 2px;padding:.35em .625em .75em;}
img{height:auto;max-width:100%;border:4px solid red;}
"""

# Na prévia o envio não sai daqui: devolve um redirect falso e registra o
# que iria para o HubSpot e para o dataLayer.
MOCK = """
<script>
window.__puEnvios = [];
window.dataLayer = [];
var fetchOriginal = window.fetch;
window.fetch = function (url, opts) {
  if (String(url).indexOf('hsforms.com') > -1) {
    window.__puEnvios.push(JSON.parse(opts.body));
    console.info('[prévia] envio interceptado', JSON.parse(opts.body));
    return new Promise(function (ok) {
      setTimeout(function () {
        ok(new Response(JSON.stringify({ redirectUri: '#video-liberado' }), { status: 200 }));
      }, 400);
    });
  }
  return fetchOriginal.apply(this, arguments);
};
</script>
"""


AVISO_PREVIA = """
<div style="position:fixed;left:0;top:50%;transform:translateY(-50%);z-index:9999;
writing-mode:vertical-rl;background:#1A0800;color:#FEF8E8;
font:500 10px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.06em;text-transform:uppercase;
padding:12px 5px;border-radius:0 10px 10px 0;box-shadow:0 8px 24px -8px rgba(0,0,0,.6);pointer-events:none">
Prévia · o envio não vai ao HubSpot</div>
"""


def main():
    fonte = (AQUI / 'embed.html').read_text(encoding='utf-8')

    print('Conferindo o formulário:')
    ligadas, problemas = conferir(fonte)
    if problemas:
        print('  opções fora de sincronia com o HubSpot:')
        for p in problemas:
            print(f'    - {p}')
        print('\nBuild interrompido: acerte as opções antes de publicar.')
        return 1
    total = sum(len(v) for v in OFICIAL.values())
    print(f'  {ligadas} perguntas ligadas, {total} opções idênticas ao HubSpot')

    embed = (fonte
             .replace('<!--LOGO_SCHOOL-->', svg_inline('assets/logo-school-white.svg', 'pu-brand__school'))
             .replace('<!--LOGO_PSA-->', svg_inline('assets/logo-psa-only-white.svg', 'pu-brand__psa')))
    if '<!--LOGO_' in embed:
        print('Marcador de logo sem substituição.')
        return 1

    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / 'imagens').mkdir(parents=True)

    (DIST / 'embed-elementor.html').write_text(embed, encoding='utf-8')

    for origem, destino in IMAGENS.items():
        shutil.copy(RAIZ / origem, DIST / 'imagens' / destino)
    usadas = set(re.findall(re.escape(URL_UPLOADS) + r'([\w.-]+)', embed))
    sem_arquivo = usadas - set(IMAGENS.values())
    if sem_arquivo:
        print(f'Imagens usadas no embed sem arquivo de origem: {sorted(sem_arquivo)}')
        return 1

    preview = ('<!DOCTYPE html>\n<html lang="pt-BR">\n<head>\n<meta charset="utf-8">\n'
               '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
               '<title>Prévia · Perspectiva Única</title>\n'
               f'<style>{TEMA_HOSTIL}</style>\n{MOCK}\n</head>\n<body>\n'
               + embed.replace(URL_UPLOADS, 'imagens/') +
               '\n</body>\n</html>\n')
    (DIST / 'preview.html').write_text(preview, encoding='utf-8')

    # Prévia para compartilhar: sem o tema simulado, com o envio interceptado
    # e um aviso de que nada vai ao HubSpot. Não indexa.
    (DIST / 'previa').mkdir()
    shutil.copytree(DIST / 'imagens', DIST / 'previa' / 'imagens')
    previa = ('<!DOCTYPE html>\n<html lang="pt-BR">\n<head>\n<meta charset="utf-8">\n'
              '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
              '<meta name="robots" content="noindex,nofollow">\n'
              '<title>Prévia · Perspectiva Única</title>\n'
              '<style>body{margin:0;background:#FEF8E8;}</style>\n'
              f'{MOCK}\n</head>\n<body>\n'
              + embed.replace(URL_UPLOADS, 'imagens/') + '\n' + AVISO_PREVIA +
              '\n</body>\n</html>\n')
    (DIST / 'previa' / 'index.html').write_text(previa, encoding='utf-8')

    print('\ndist/ pronta:')
    for f in sorted(DIST.rglob('*')):
        if f.is_file():
            print(f'  {f.relative_to(AQUI)}  ({f.stat().st_size / 1024:.1f} KB)')
    print(f'\nSuba as imagens em {URL_UPLOADS}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
