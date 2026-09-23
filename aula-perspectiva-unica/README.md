# LP Aula Perspectiva Única

Aula exclusiva de Márcio Spagnolo. Usa a identidade visual da LP The Best School
e o formulário nativo do HubSpot, e pode ser publicada de dois jeitos: por
**FTP**, como pasta própria em profissionaissa.com.br/aula-perspectiva-unica/,
ou como **widget HTML do Elementor**.

```
embed.html              fonte da LP (CSS, HTML e JS), presa ao #psa-pu
conteudo-liberado.html  fonte da página do vídeo
montar.py               gera a dist/
dist/          gerada, não versionada
  ftp/                   página completa para subir por FTP
  embed-elementor.html   o que se cola no Elementor
  imagens/pu-*.webp      o que se sobe na Biblioteca de Mídia
  preview.html           prévia local, com o CSS do tema simulado
```

## Gerar

```bash
python3 aula-perspectiva-unica/montar.py
```

Para a prévia, com o servidor da LP rodando (`python3 -m http.server 4173` na
raiz), abra http://localhost:4173/aula-perspectiva-unica/dist/preview.html.

**Nas prévias o formulário é o nativo do HubSpot: um envio feito nelas é real**
e cria contato. A página de conversão (`pageUri`) mostra de onde veio.

## Prévia online

```bash
./publicar-previa.sh
```

Publica no GitHub Pages, no branch `gh-pages`, as duas LPs lado a lado, sem GTM.
Na The Best School o envio é interceptado; na Perspectiva Única o formulário é o
nativo do HubSpot e envia de verdade:

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

Formulário **nativo do HubSpot**, embutido sem personalização — portal
`49656171`, form `edcd003f-7231-4a3c-8c7b-9bd8b9940c9b`. Campos, opções,
obrigatoriedade e consentimento LGPD são editados no próprio HubSpot; a LP só
emoldura o formulário num cartão.

**Redirecionamento.** Configure no formulário, em *Opções > Após o envio >
Redirecionar para outra página*:
`https://profissionaissa.com.br/aula-perspectiva-unica/conteudo-liberado/`.
Se ele ficar na mensagem de agradecimento, a LP leva para `conteudo-liberado/`
1,5 s depois do envio (`PU_CONFIG.paginaDoVideo`).

**Página do vídeo** (`conteudo-liberado/`): vídeo da aula (YouTube
`Y8hzAleMXyY`, pelo `youtube-nocookie`) e convite para a The Best School. Não
indexa, para não virar atalho para o vídeo sem o formulário.

## Conversão (GTM)

Mesmo desenho da página de obrigado da LP The Best School. Ao ouvir o evento
`hs-form-event:on-submission:success` do HubSpot, a LP grava uma marca
(`pu_lead`) no `sessionStorage`; a página do vídeo, ao encontrá-la, faz o push
e apaga a marca:

```js
{ event: 'lead_perspectiva_unica', lead_origem: 'perspectiva-unica' }
```

Recarregar a página do vídeo, voltar pelo histórico ou abrir o link recebido de
alguém não conta conversão. No GTM, crie um acionador de evento personalizado
`lead_perspectiva_unica` e ligue nele as conversões de Ads e Meta — use o
evento, e não a URL da página, como acionador.

As respostas do formulário não vão para o dataLayer: o formulário nativo roda
num iframe do HubSpot, e a LP não tem acesso a elas. Para segmentar por
qualidade de lead, use as propriedades do contato no HubSpot.
