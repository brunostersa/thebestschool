# LP Aula Perspectiva Única

Aula exclusiva de Márcio Spagnolo. Usa a identidade visual e o formulário do
HubSpot da LP The Best School, e pode ser publicada de dois jeitos: por **FTP**, como pasta própria em
profissionaissa.com.br/aula-perspectiva-unica/, ou como **widget HTML do Elementor**.

```
embed.html     fonte: página inteira (CSS, HTML e JS), presa ao #psa-pu
montar.py      confere as opções com o HubSpot e gera a dist/
dist/          gerada, não versionada
  ftp/                   página completa para subir por FTP
  embed-elementor.html   o que se cola no Elementor
  imagens/pu-*.webp      o que se sobe na Biblioteca de Mídia
  preview.html           prévia local, com envio interceptado
```

## Gerar

```bash
python3 aula-perspectiva-unica/montar.py
```

O script para se algum `value` de resposta divergir do HubSpot. Para a prévia,
com o servidor da LP rodando (`python3 -m http.server 4173` na raiz), abra
http://localhost:4173/aula-perspectiva-unica/dist/preview.html.

A prévia simula o CSS do tema e **não envia nada ao HubSpot**: o envio é
interceptado e devolve um redirect falso (`#video-liberado`). O que iria para o
HubSpot fica em `window.__puEnvios` e a conversão em `window.dataLayer`.

## Prévia online

```bash
./publicar-previa.sh
```

Publica no GitHub Pages, no branch `gh-pages`, as duas LPs lado a lado, sem GTM
e com o envio interceptado:

- https://brunostersa.github.io/thebestschool/thebestschool/
- https://brunostersa.github.io/thebestschool/aula-perspectiva-unica/

O `gh-pages` é gerado e cada publicação substitui a anterior. A `main` e o que
vai para o FTP não mudam.

## Publicar por FTP

`montar.py` gera `dist/ftp/`, com a página completa: GTM, tracking do HubSpot,
meta tags, imagem de compartilhamento, favicon, `.htaccess` e `sitemap.xml`,
as mesmas coisas da LP The Best School. As imagens ficam na própria pasta, então
não é preciso subir nada na Biblioteca de Mídia.

Envie o **conteúdo** de `dist/ftp/` para `public_html/aula-perspectiva-unica/`:

```
public_html/
└── aula-perspectiva-unica/     ← o conteúdo de dist/ftp/ vai aqui
    ├── index.html              a LP
    ├── conteudo-liberado/      a página do vídeo, depois do envio
    ├── .htaccess               ← arquivo oculto: confira se o FTP enviou
    ├── sitemap.xml
    └── assets/
```

O `.htaccess` desliga a listagem de diretório (a pasta vazia no servidor hoje
mostra "Index of") e garante a barra final: sem ela, as imagens em
`assets/` dariam 404. Divulgue sempre com a barra:
`https://profissionaissa.com.br/aula-perspectiva-unica/`.

Não crie uma página no WordPress com o slug `aula-perspectiva-unica`: a pasta
física ganha, e a página ficaria inacessível sem explicação aparente.

Para indexar, adicione ao `robots.txt` da raiz do domínio:

```
Sitemap: https://profissionaissa.com.br/aula-perspectiva-unica/sitemap.xml
```

## Publicar no WordPress

1. **Imagens.** Suba os dois arquivos de `dist/imagens/` em *Mídia > Adicionar*.
   O embed espera `https://profissionaissa.com.br/wp-content/uploads/2026/09/`.
   O WordPress guarda por mês de envio: subindo em outro mês, troque esse
   caminho no `embed.html` (e na constante `URL_UPLOADS` do `montar.py`) e
   gere de novo. O prefixo `pu-` evita colisão com arquivos existentes, que o
   WordPress renomearia para `-1.webp`, quebrando a URL.
2. **Página.** Nova página, template **Elementor Canvas** (sem header e footer
   do tema: a LP tem os seus). Um container com largura **total**, largura de
   conteúdo total e padding 0.
3. **Widget HTML.** Arraste um widget *HTML* para o container e cole o conteúdo
   inteiro de `dist/embed-elementor.html`.
4. **Cache.** Publique e limpe o cache do LiteSpeed (*LiteSpeed Cache > Purgar
   tudo*). O script já vem com `data-no-optimize="1"`, que impede o LiteSpeed
   de adiá-lo até o primeiro toque na tela; a foto do topo vem com
   `data-no-lazy="1"`, porque é o primeiro conteúdo visível.
5. **Teste real.** Envie o formulário uma vez com um e-mail seu e confira o
   contato no HubSpot com as quatro respostas preenchidas.

Não coloque o GTM no embed: o site já carrega o `GTM-W8F8SBJ6`, e repetir
contaria cada conversão duas vezes.

## Formulário

Mesmo formulário da LP The Best School — portal `49656171`, form `634374b1-…`.

**Redirecionamento.** Depois do envio, a LP vai para `conteudo-liberado/`
(`PU_CONFIG.redirectUrl`), a página com o vídeo da aula
(YouTube `Y8hzAleMXyY`, sem cookies de rastreio do YouTube até o play). Ela
cumprimenta pelo primeiro nome, que a LP guarda no `sessionStorage`, e não
indexa, para não virar atalho para o vídeo sem o formulário. A fonte é
`conteudo-liberado.html`, que usa o mesmo CSS da LP.

O redirect configurado no formulário do HubSpot é ignorado: o formulário é o
mesmo da The Best School e hoje aponta para `the-best-weekend/inscricao-confirmada/`.
Com `redirectUrl` vazio, a LP passa a usar o do HubSpot e, sem nenhum, mostra a
confirmação no próprio formulário.

Na versão do Elementor o caminho é relativo à página: ela precisa ter uma
subpágina `conteudo-liberado/` com o vídeo, ou `redirectUrl` precisa do
endereço completo.

Como os dois LPs usam o mesmo formulário, os leads chegam juntos. Para separar,
use a página de conversão do contato no HubSpot ou o `lead_origem` no GTM.

**Perguntas ligadas** — as quatro que o formulário tem, todas obrigatórias lá:

| Pergunta | Propriedade |
|---|---|
| Qual a sua atuação hoje? | `qual_a_sua_atuacao_hoje___new_campaign_` |
| Você já atua como palestrante? | `voce_ja_atua_como_palestrante_` |
| O que você está buscando e quanto deseja investir? | `temos_programas_…_o_que_voce_esta_buscando_new` |
| Qual sua urgência…? | `voce_ja_esta_pronto_para_investir_na_sua_carreira_como_palestrante_` |

**Perguntas desligadas** — estão no design, mas o formulário não tem onde
guardá-las: gênero, tempo de palestra, obstáculo e forma de pagamento. Ficam no
HTML com `data-hubspot=""`, o que as esconde e as tira do envio. Para ligar uma:

1. crie a propriedade no HubSpot e inclua no formulário;
2. no `embed.html`, preencha `data-hubspot` com o nome interno e use o mesmo
   nome no `name` de cada radio;
3. troque cada `value` pelo texto exato cadastrado no HubSpot;
4. acrescente a propriedade e os valores ao `OFICIAL` do `montar.py`.

"Há quanto tempo você faz palestras?" só aparece para quem já palestra
(`data-pular-se-*`), como no design.

## Conversão (GTM)

Depois de o HubSpot aceitar o envio, a LP faz o push abaixo e só redireciona
quando o GTM termina de disparar as tags (`eventCallback`), com limite de 2 s:

```js
{
  event: 'lead_perspectiva_unica',
  lead_origem: 'perspectiva-unica',
  diagnostico_atuacao:  '...',
  diagnostico_ja_atua:  '...',
  diagnostico_objetivo: '...',
  diagnostico_urgencia: '...'
}
```

As variáveis `diagnostico_*` têm os mesmos nomes da LP The Best School. No GTM,
crie um acionador de evento personalizado `lead_perspectiva_unica` e ligue nele
as conversões de Ads e Meta. Nome, e-mail e telefone não vão para o dataLayer.
