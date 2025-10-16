## **🧠 Desafio Técnico – FALCON Vision AI**

Bem-vindo(a)\!  
 Este é um desafio prático para avaliar suas habilidades em **visão computacional, integração de modelos de IA e desenvolvimento de aplicações interativas**. Nosso objetivo é observar como você pensa, estrutura e entrega uma solução funcional — mesmo que simples — com criatividade e boa engenharia.

---

### **🎯 Objetivo Geral**

Desenvolver uma aplicação de **visão computacional em tempo real** que utilize um **modelo pré-treinado de detecção de pessoas** (ex.: YOLO da Ultralytics), capaz de:

1. **Detectar e acompanhar pessoas** em imagens capturadas por uma webcam;

2. **Registrar o horário** em que cada pessoa específica **aparece** e **sai do quadro**;

3. **Coletar e armazenar características visuais** de cada pessoa detectada (ex.: cores predominantes de roupas, presença de objetos, ações simples como “andando”, “parado”, “segurando algo”);

4. **Exibir uma interface interativa (UI)** com:

   * **Visualização em tempo real da câmera** com as detecções;

   * Uma **área de chat** (texto) integrada a alguma **API de LLM** (OpenAI, Gemini, etc.), para o usuário fazer perguntas sobre o que foi registrado pela IA, como:

     * “Quando apareceu a primeira pessoa no vídeo?”

     * “Quantas pessoas foram identificadas?”

     * “Quem estava usando camisa azul?”

---

### **🧩 Requisitos Funcionais**

* A aplicação deve **parar a detecção automaticamente** quando um **QR code específico** for mostrado na câmera (você pode definir o QR code de teste).

* Deve haver um **painel de visualização de dados (dashboard)** com boa aplicação de visualização de dados com **componentes inovadores** (nada de gráfico de pizza 🥴).

* O dashboard deve permitir **consultar, filtrar e visualizar estatísticas** sobre as pessoas detectadas e suas interações.

* Você é **livre para surpreender** com qualquer funcionalidade **inovadora, divertida ou visualmente interessante** — quanto mais criativa, melhor.

---

### **⚙️ Requisitos Técnicos**

* Linguagem: **Python**   
* Frameworks sugeridos:

  * Para IA: `ultralytics`, `opencv`, `mediapipe`, `torch`, `transformers`;

  * Para UI: `Streamlit`, `Gradio`, `FastAPI + React`, ou o que preferir;

* Integração com LLM (qualquer modelo gratuito);

* Armazenamento local (ex.: SQLite, JSON ou CSV) para registrar eventos;

* Código versionado no **GitHub**, com instruções claras para execução.

---

### **🧠 Critérios de Avaliação**

* **Clareza e organização** do código;

* **Lógica e modularização** da aplicação;

* **Criatividade e usabilidade da interface**;

* **Capacidade de integração entre IA, UI e backend**;

* **Documentação e explicação do raciocínio** (README bem escrito conta muito\!);

* **Funcionamento geral da aplicação** — não precisa ser perfeita, mas deve ser coerente e funcional.

---

### **💡 Diferenciais (não obrigatórios)**

* Uso de **técnicas de tracking** (como DeepSORT) para reconhecer a mesma pessoa ao longo do vídeo;

* Implementar uma **API REST ou WebSocket** para consulta dos dados de visão computacional;

* Criar **relatórios automáticos** sobre os eventos registrados (PDF, gráficos dinâmicos, etc.);  
*   
* Aplicar conceitos de **design de experiência do usuário (UX/UI)**;

* Deploy simples (Docker ou app web funcional).

---

### **🕒 Prazo sugerido**

Quinta-feira pela manhã

---

### **📦 Entrega**

* Link para o repositório público (GitHub ou GitLab);

* Instruções de instalação e execução no README;

* (Opcional) Vídeo curto ou GIF demonstrando o funcionamento.

