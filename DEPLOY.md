# LP The Best School — implementação e deploy

Landing page estática, sem build e sem dependências. Todo o CSS e JS estão
dentro de `index.html`.

**Endereço de publicação:** https://profissionaissa.com.br/thebestschool/

A página vive em um **subdiretório** do domínio, não na raiz. Isso já está
refletido no `canonical`, nas tags Open Graph, no `sitemap.xml` e no
`.htaccess`.

## Estrutura

```
index.html                  página inteira (HTML + CSS + JS)
assets/logo-white.svg       logo do header e do rodapé
assets/favicon.svg          ícone da aba
assets/apple-touch-icon.png ícone de atalho no iOS
assets/img/*.webp           imagens otimizadas (desktop + mobile)
assets/img/og-image.jpg     imagem de compartilhamento
.htaccess                   gzip, cache, barra final (Apache)
sitemap.xml                 indexação
build.sh                    monta a pasta dist/ para o FTP
```

Arquivos que **não** vão para o ar (ficam só no projeto):
`LP The Best School.dc.html`, `support.js`, `uploads/`, `.claude/`,
e os PNG/JPG originais em `assets/` (já convertidos para WebP).

## Subir para o FTP

```bash
./build.sh
```

Isso cria `dist/` com os 12 arquivos que vão para o ar. Envie o **conteúdo**
de `dist/` para a pasta `thebestschool` dentro da raiz pública do servidor:

```
public_html/
└── thebestschool/          ← o conteúdo de dist/ vai aqui
    ├── index.html
    ├── .htaccess
    ├── sitemap.xml
    └── assets/
```

Não envie a pasta `dist` em si — envie o que está dentro dela.

Confira que o cliente de FTP está enviando **arquivos ocultos** — o
`.htaccess` começa com ponto e vários clientes o escondem por padrão.
Ele é o que garante a barra final da URL (ver abaixo), além de compressão
e cache.

## Antes de publicar

1. **Barra final da URL.** A página usa caminhos relativos (`assets/img/...`),
   então `profissionaissa.com.br/thebestschool` **sem** a barra faria o
   navegador procurar as imagens em `/assets/` — tudo 404. O `DirectorySlash On`
   do `.htaccess` resolve, redirecionando para a versão com barra. Testado: o
   Apache devolve 301 e a página carrega certo. Ainda assim, divulgue sempre o
   link **com** a barra: `https://profissionaissa.com.br/thebestschool/`.

2. **robots.txt.** Não vai junto: crawlers só leem `robots.txt` na raiz do
   domínio. Se quiser apontar o sitemap, adicione esta linha ao
   `robots.txt` de `profissionaissa.com.br` (que pertence ao site principal):

   ```
   Sitemap: https://profissionaissa.com.br/thebestschool/sitemap.xml
   ```

   O sitemap em si pode ser enviado direto no Google Search Console.

3. **HubSpot — já conectado e testado.** Portal `49656171`, formulário
   `634374b1-…`. Os nomes internos das quatro propriedades foram confirmados
   contra o formulário real e já estão no `fieldMap`:

   | Pergunta na LP | Propriedade no HubSpot |
   |---|---|
   | Você já atua como palestrante? | `voce_ja_atua_como_palestrante_` |
   | Qual a sua atuação hoje? | `qual_a_sua_atuacao_hoje___new_campaign_` |
   | O que você está buscando? | `temos_programas_…_o_que_voce_esta_buscando_new` |
   | Qual sua urgência…? | `voce_ja_esta_pronto_para_investir_na_sua_carreira_como_palestrante_` |
   | Redes sociais (opcional) | `linkedin` |

   As quatro primeiras são **obrigatórias** no formulário, assim como
   `firstname` e `lastname`: faltando qualquer uma, o HubSpot recusa o envio
   inteiro. Por isso o formulário pede nome e sobrenome em campos separados, em
   vez de dividir um "nome completo" no JavaScript — quem digitasse um único
   nome teria o envio rejeitado. O campo de rede social é opcional e só é
   enviado quando preenchido. Não mexa nesses nomes sem conferir no HubSpot.

   Para redescobrir os nomes internos caso o formulário mude, carregue o embed
   oficial numa página em branco e leia os `name` dos campos renderizados — eles
   vêm no formato `0-1/<nome_interno>`:

   ```html
   <script src="https://js.hsforms.net/forms/embed/developer/49656171.js" defer></script>
   <div class="hs-form-html" data-region="na1"
        data-form-id="634374b1-5a70-470e-a975-4a1e2d433b87"
        data-portal-id="49656171"></div>
   ```

4. **Dois pontos de atenção neste formulário:**

   - **O redirect aponta para outra campanha.** O formulário está configurado
     para redirecionar a `profissionaissa.com.br/the-best-weekend/inscricao-confirmada/`.
     A LP ignora esse redirect e mostra a mensagem de sucesso na própria página,
     mas vale revisar no HubSpot — o formulário parece ter sido reaproveitado do
     The Best Weekend. Se você quiser uma página de obrigado própria, preencha
     `CONFIG.redirectUrl` na LP.

   - **A quarta pergunta diverge.** A LP pergunta *"Qual sua urgência em se
     desenvolver como palestrante?"*, mas a propriedade do HubSpot se chama
     *"Você já está pronto para investir na sua carreira como palestrante?"*.
     As respostas da LP foram aceitas pela API, mas confira no CRM se elas
     aparecem como opção válida — ou alinhe a pergunta com a propriedade.

5. **HTTPS e www.** Não configure aqui — quem cuida disso é o `.htaccess` da
   raiz de `profissionaissa.com.br`. Duplicar geraria redirecionamento em
   cadeia.

## Pendências de conteúdo

O design veio com marcações de imagem que ainda não têm foto:

- as três fases (`1º palco`, `imersão`, `palco grande`) na seção Diagnóstico;
- as três capas dos perfis (`INICIANTE`, `IMERSÃO PRESENCIAL`, `PALCO GRANDE`) — 800×500;
- os três vídeos de depoimento e os nomes/atuações reais;
- as sete miniaturas do leque no CTA intermediário;
- a foto da Etapa 03 em "Como funciona".

Os links de redes sociais e a política de privacidade já apontam para os
endereços reais da PSA, copiados do rodapé de profissionaissa.com.br:
Instagram (`psa.talk`), LinkedIn, YouTube e Facebook.

## Navegação

O header muda de comportamento conforme a largura da tela:

- **Desktop (≥768px):** fica fixo o tempo todo. Transparente sobre o hero e com
  fundo escuro a partir de 220px de rolagem. O indicador claro do menu desliza
  entre os itens conforme a seção entra na faixa central da tela.
- **Mobile (<768px):** o menu vira hambúrguer. O header se recolhe enquanto o
  visitante desce e reaparece assim que ele sobe. O painel fecha ao tocar num
  link, no fundo ou com Esc, e esconde o chat do HubSpot enquanto está aberto.

Para mudar o ponto em que o header ganha fundo, ajuste `LIMITE` dentro de
`initHeader()`.

## Onde mexer

- **Cores e tipografia:** bloco `:root` no topo do `<style>`.
- **Ajustes de mobile:** seção `RESPONSIVO` no fim do `<style>`.
- **Formulário e animações:** bloco `<script>` no fim do arquivo, dividido em
  seções numeradas (reveal, stack, fan, navegação, máscara de telefone, envio).
