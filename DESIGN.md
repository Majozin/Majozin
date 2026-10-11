# Identidade do perfil — Cyberpunk

Direção aprovada: cyberpunk, conteúdo centralizado e linguagem visual de cartões em todas as seções. Fundo azul quase preto, ciano luminoso, magenta pontual, cantos chanfrados e trilhas de circuito. Texto claro e legível, sem animações ou indicadores fictícios de atividade.

Fonte canônica dos tokens e primitivas SVG: scripts/profile_theme.py. Paleta: BG #090D18; SURFACE #101828; BORDER #2A3D56; TEXT #EAF4FF; MUTED #A9BCD3; CYAN #59F3F2; PINK #FC77C8. DejaVu Sans Mono para títulos utilitários e métricas; DejaVu Sans/Arial para leitura.

Cabeçalho 780 × 190; apresentação 520 × 181; métricas 250 × 150; tecnologias e catálogo 250 × 170. Cartões em grupos centralizados de até três por linha: seis métricas formam duas linhas, duas métricas ficam centralizadas. Sem espaços vazios artificiais. Telas estreitas permitem quebra de linha. SVGs possuem títulos e imagens do README têm texto alternativo completo. Fundos opacos mantêm contraste nos temas claro e escuro do GitHub.

Retrato original preservado em assets/avatar.png. Nome público: Majozin. Apresentação preserva o texto escolhido pelo usuário. Nenhum nome completo no perfil.

Dados: somente nomes e indicadores agregados autorizados. **Prioridade para `PROJECT_STATUS.json` validado**, com percentual de entregas integradas/homologadas; se `estimated=false`, mostrar **0%** e situação pública. Para projetos legados não migrados, o cálculo de issues concluídas continua sendo uma métrica provisória, **não conclusão do produto**; sem métrica de issues, o catálogo legado permanece sem barra. Não publicar campos privados. Falha de coleta/schemas preserva o painel. O espelho gerenciado por issue com permissão mínima está descrito em `docs/PROJECT_STATUS_INTEGRATION.md`.

Geradores: python3 scripts/render_profile.py para ativos estáticos; scripts/render_projects.py para projetos; scripts/update_private_projects.py para coleta. O workflow existente versiona README e assets/projects juntos. Ao alterar a identidade, regenerar ambos os conjuntos de ativos. Não incluir dependências externas de imagens, JavaScript, animações, títulos de issues nem detalhes internos.
