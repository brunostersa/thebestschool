#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Confere se as opções dos selects do index.html continuam idênticas às
cadastradas nas propriedades do HubSpot.

Elas divergem do texto exibido de propósito — pontuação, espaços em barras,
acentos e, em dois campos, o texto inteiro. Quando um "value" deixa de bater,
o HubSpot aceita o envio mas descarta aquela resposta em silêncio: o lead
entra e o campo fica vazio. Este script existe para esse erro não passar
despercebido.

Se as opções mudarem no HubSpot, atualize a lista abaixo. Para obtê-la,
carregue o embed do formulário numa página em branco e leia a definição
(o passo a passo está no DEPLOY.md).
"""
import re, sys, html, pathlib

# Valores aceitos pelo HubSpot — portal 49656171, form 634374b1-…
OFICIAL = {
    'ja_atua_como_palestrante': [
        "Sim, já realizo palestras remuneradas.",
        "Sim, mas apenas de forma gratuita.",
        "Não, ainda não atuo como palestrante.",
    ],
    'atuacao_atual': [
        "Palestrante profissional",
        "Executivo (VP/Diretor/C-level)",
        "Acadêmico (Mestre/Doutor)",
        "Empreendedor (Founder/Cofounder)",
        "Coach/Psicologo/RH",
        "Outra",
    ],
    'objetivo_de_carreira': [
        "Apenas conhecer o mercado de palestras de forma gratuita.",
        "Ingressar profissionalmente no mercado (investimento de até 1k)",
        "Consolidar minha carreira de palestrante (investimento de até 5k)",
        "Gerar mais receita com as minhas palestras (investimento de até 15k)",
        "Consolidar como palestrante de alto impacto (investimento de +20k)",
    ],
    'urgencia': [
        "Sim, quero começar o quanto antes!",
        "Sim, estou planejando investir ainda este ano",
        "Não, ainda não estou pronto.",
    ],
}

def main():
    arquivo = pathlib.Path(__file__).parent / 'index.html'
    s = arquivo.read_text(encoding='utf-8')
    problemas = []

    for campo, esperados in OFICIAL.items():
        m = re.search(r'<select[^>]*name="' + campo + r'"[^>]*>(.*?)</select>', s, re.S)
        if not m:
            problemas.append(f'{campo}: select não encontrado no index.html')
            continue
        vals = [html.unescape(v) for v in re.findall(r'<option value="([^"]*)"', m.group(1)) if v]
        for e in esperados:
            if e not in vals:
                problemas.append(f'{campo}: falta a opção {e!r}')
        for v in vals:
            if v not in esperados:
                problemas.append(f'{campo}: {v!r} não existe no HubSpot e seria descartado')

    if problemas:
        print('  opções fora de sincronia com o HubSpot:')
        for p in problemas:
            print(f'    - {p}')
        return 1

    total = sum(len(v) for v in OFICIAL.values())
    print(f'  opções do formulário: {total} conferidas, todas idênticas ao HubSpot')
    return 0

if __name__ == '__main__':
    sys.exit(main())
