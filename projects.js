// ============================================
//  СПИСОК ПРОЕКТОВ
//  Чтобы добавить новый проект — скопируйте блок
//  { ... }, вставьте в список и поменяйте текст.
//  Название и описание пишутся на каждом языке.
//  Если какого-то языка нет, покажется английский.
// ============================================

const projects = [
  {
    title: {
      ru: "Сайт-портфолио",
      en: "Portfolio website",
      de: "Portfolio-Website",
      es: "Sitio web portfolio",
      fr: "Site portfolio",
      zh: "作品集网站",
    },
    description: {
      ru: "Этот сайт. Мой первый проект: адаптивная мультиязычная страница-визитка на чистом HTML, CSS и JavaScript.",
      en: "This very site. My first project: a responsive multilingual portfolio page built with plain HTML, CSS and JavaScript.",
      de: "Genau diese Seite. Mein erstes Projekt: eine responsive, mehrsprachige Portfolio-Seite mit reinem HTML, CSS und JavaScript.",
      es: "Este mismo sitio. Mi primer proyecto: una página de portfolio adaptable y multilingüe hecha con HTML, CSS y JavaScript puros.",
      fr: "Ce site même. Mon premier projet : une page portfolio responsive et multilingue en HTML, CSS et JavaScript pur.",
      zh: "就是这个网站。我的第一个项目：使用纯 HTML、CSS 和 JavaScript 构建的响应式多语言作品集页面。",
    },
    tags: ["HTML", "CSS", "JavaScript", "i18n"],
    link: "",   // ссылка на работающий проект (если есть)
    code: "https://github.com/nikita-aidev/nikita-aidev.github.io",   // ссылка на код, например на GitHub (если есть)
  },
  {
    title: {
      ru: "Telegram-бот визитка",
      en: "Telegram business-card bot",
      de: "Telegram-Visitenkarten-Bot",
      es: "Bot de Telegram tarjeta de visita",
      fr: "Bot Telegram carte de visite",
      zh: "Telegram 名片机器人",
    },
    description: {
      ru: "Бот со встроенным ИИ-ассистентом на LLM: отвечает на вопросы посетителей обо мне на их языке, помнит контекст разговора и сам предлагает оставить заявку. Заявки сразу приходят мне. Работает в облаке круглосуточно.",
      en: "A bot with a built-in LLM-powered AI assistant: it answers visitors' questions about me in their language, keeps the conversation context and suggests leaving a request. Requests reach me instantly. Runs 24/7 in the cloud.",
      de: "Ein Bot mit integriertem KI-Assistenten auf LLM-Basis: Er beantwortet Fragen der Besucher über mich in ihrer Sprache, behält den Gesprächskontext und schlägt vor, eine Anfrage zu hinterlassen. Anfragen erreichen mich sofort. Läuft rund um die Uhr in der Cloud.",
      es: "Un bot con asistente de IA integrado basado en LLM: responde a las preguntas de los visitantes sobre mí en su idioma, recuerda el contexto de la conversación y propone dejar una solicitud. Las solicitudes me llegan al instante. Funciona 24/7 en la nube.",
      fr: "Un bot avec un assistant IA intégré basé sur un LLM : il répond aux questions des visiteurs à mon sujet dans leur langue, garde le contexte de la conversation et propose de laisser une demande. Les demandes m'arrivent aussitôt. Il tourne 24 h/24 dans le cloud.",
      zh: "内置大语言模型 AI 助手的机器人：用访客的语言回答关于我的问题，记住对话上下文，并主动建议留下需求。需求会立即发送给我。全天候运行在云端。",
    },
    // Тег можно писать просто строкой ("Python") или переводить
    tags: ["Python", "aiogram", "LLM", "Groq", "Webhook", "Render"],
    link: "https://t.me/nikita_aidev_bot",
    code: "https://github.com/nikita-aidev/telegram-bot",
  },
];
