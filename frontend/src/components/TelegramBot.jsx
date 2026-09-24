
import { Card } from './ui';

function TelegramBot() {
    return (
        <Card className="telegram-bot-card fade-in">
            <div className="telegram-bot-header">
                <div className="telegram-bot-icon">
                    <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                    >
                        <path
                            d="M21.5 3.5L18.1 20.2C17.85 21.4 17.2 21.7 16.25 21.15L10.9 17.2L8.32 19.68C8.03 19.97 7.79 20.21 7.2 20.21L7.58 14.75L17.52 5.77C17.95 5.39 17.43 5.18 16.86 5.56L4.57 13.3L-0.71 11.64C-1.86 11.28 -1.88 10.49 -0.47 9.94L20.19 1.97C21.15 1.62 21.99 2.18 21.5 3.5Z"
                            transform="translate(1 0)"
                            fill="currentColor"
                        />
                    </svg>
                </div>

                <div className="telegram-bot-info">
                    <h2>Telegram-бот EGE Solver</h2>

                    <p className="text-muted">
                        Решайте варианты Yandex и Kompege и загружайте банк
                        заданий прямо в Telegram.
                    </p>

                    <div className="telegram-bot-username">
                        @Yandex_EGE_Inf_Solver_Bot
                    </div>
                </div>
            </div>

            <a
                className="telegram-bot-button"
                href="https://t.me/Yandex_EGE_Inf_Solver_Bot"
                target="_blank"
                rel="noopener noreferrer"
            >
                Открыть Telegram-бота
            </a>
        </Card>
    );
}

export default TelegramBot;
