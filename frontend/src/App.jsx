
import { useState } from 'react';
import YandexVariantSolver from './components/YandexVariantSolver';
import YandexTasksDownloader from './components/YandexTasksDownloader';
import KompegeVariantSolver from './components/KompegeVariantSolver';
import TelegramBot from './components/TelegramBot';
import './App.css';

function App() {
    const [activeTab, setActiveTab] = useState('yandex-variant');

    const renderContent = () => {
        switch (activeTab) {
            case 'yandex-variant':
                return <YandexVariantSolver />;
            case 'kompege-variant':
                return <KompegeVariantSolver />;
            case 'tasks':
                return <YandexTasksDownloader />;
            case 'telegram-bot':
                return <TelegramBot />;
            default:
                return null;
        }
    };

    return (
        <div className="app-container">
            <header className="app-header">
                <h1 className="app-title">
                    EGE Solver
                </h1>
                <p className="app-subtitle">
                    Авторешение вариантов и загрузка банка задач из Yandex и Kompege
                </p>
            </header>

            <nav className="tabs">
                <button
                    className={`tab ${activeTab === 'yandex-variant' ? 'active' : ''}`}
                    onClick={() => setActiveTab('yandex-variant')}
                >
                    Yandex Вариант
                </button>

                <button
                    className={`tab ${activeTab === 'kompege-variant' ? 'active' : ''}`}
                    onClick={() => setActiveTab('kompege-variant')}
                >
                    Kompege Вариант
                </button>

                <button
                    className={`tab ${activeTab === 'tasks' ? 'active' : ''}`}
                    onClick={() => setActiveTab('tasks')}
                >
                    База заданий
                </button>

                <button
                    className={`tab ${activeTab === 'telegram-bot' ? 'active' : ''}`}
                    onClick={() => setActiveTab('telegram-bot')}
                >
                    Telegram-бот
                </button>
            </nav>

            <main className="content">
                {renderContent()}
            </main>

            <footer className="app-footer">
                <p>© {new Date().getFullYear()} EGE Solver By SV_Vershina. Все права защищены.</p>
            </footer>
        </div>
    );
}

export default App;
