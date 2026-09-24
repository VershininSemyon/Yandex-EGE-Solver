
const TelegramBot = () => {
    return (
        <div className="telegram-bot fade-in">
            <div className="telegram-bot-icon">
                <svg
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                >
                    <path
                        d="M21.5 3.5 18.2 20c-.25 1.16-.9 1.45-1.83.9l-5.05-3.72-2.44 2.35c-.27.27-.5.5-1.02.5l.36-5.14 9.37-8.46c.41-.36-.09-.56-.64-.2L5.36 13.54.36 11.97c-1.09-.34-1.11-1.09.23-1.59L20.12 2.84c.9-.33 1.69.2 1.38.66Z"
                        fill="currentColor"
                    />
                </svg>
            </div>

            <div className="telegram-bot-content">
                <h3>Telegram-бот EGE Solver</h3>
                <p>
                    Решайте варианты Yandex и Kompege и загружайте
                    банк заданий прямо в Telegram.
                </p>
                <span className="telegram-bot-username">
                    @Yandex_EGE_Inf_Solver_Bot
                </span>
            </div>

            <a
                className="telegram-bot-button"
                href="https://t.me/Yandex_EGE_Inf_Solver_Bot"
                target="_blank"
                rel="noopener noreferrer"
            >
                Открыть бота
                <span aria-hidden="true">→</span>
            </a>
        </div>
    );
};

export default TelegramBot;
