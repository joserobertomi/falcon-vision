FEAT INCREMENTAIS: 
 - Construçao de poligonos para criaçao de ROIs 
 - Registros baseados em mudança de estado (evitar instâncias repetidas)
 - 


Frontend: 
- Pagina 1: CV 
    - Capturar imagem e suportar conexão via websocket para envio de dados para o BE (em streaming) e exibir os dados referentes ao Falcon VISION ---> Alimenta o BE com as rotas do Web Socket 
 - Pagina 2: Analytics 
    - modo 1: Criar dashboards e ferramentas de visualização dos dados presente no banco de dados ---> apresenta os dados por meio de API http ao BE 
    - modo 2: Interação com LLM (ULTIMA ETAPA)


Backend-CV:
 1. Buscar dados para contruir e testar o modelo 
    - Tracking com CV (procurar por modelos ja treinados para a tarefa de identificar pessoas)
        - ikomia? mediapipe? modelo do zero?
    - Criar registros no banco de dados a cada mudança de status detectado pela camera (conferir quais são os dados na tabela do banco de dados)
    - Encerrar operação ao encontrar um qrcode específico
 2. Construção das rotas de websockets de forma assíncrona para o streaming de vídeo
    - abordagem em API pode ser lenta e ter problemas parecidos com o que o Veículo Autonomo teve no PIBICTI
 3. Construção das rotas para obtenção dos dados para construçao do analytics
 4. Construção das rotas da api para construção dos poligonos
 5. 


Backend-LLM: (Ultima etapa)
 1. Apenas faz consultas no banco de dados
 2. Entrada: prompt em busca de uma informação 
 3. Saída: resultado da pergunta após consultar o banco de dados


Banco de Dados: 
Tabela detecçao: 
 - id: automatico gerado por UUID 
 - coor_x: posicionamento do usuário em realacao ao eixo x 
 - cood_y: posicionamento do usuário em realacao ao eixo y
 - cor detectada: indica a cor obtida pelo modelo
 - QR_code identificador nos EPIs? 
 - status: [
    ('andadando', 'parado') + 
    ('segurando_{objeto}', 'maos_livres') + 
    ('epi`s detectados')
 ]
Tabela polígono:
 - id: UUID padrao 
 - pontos: lista dos pontos do poligo definido pelo usuário
Tabela intervalo_detectado: 
 - Cria registros historicos para as detecçoes no poligono 
 - id: UUID 
 - inicio: datetime
 - fim: datetime
 - detecçao: FK 
 - Poligono: Fk 


FLUXO GERAL DA APLICAÇÃO: 
FE-Camera <--> (WebSocket) <--> BE-CV (ML) <--> DB <--> BE(API/LLM) <--> FE-Analytics

FLUXO ESPECÍFICOS
Captura e streaming: FE-Camera -> BE-CV
Inferência e registro: BE-CV -> DB
Consulta e exibição: FE-Analytics <- BE(cv-API/LLM) <- DB
LLM primpts: FE-Analytics <--> BE-LLM