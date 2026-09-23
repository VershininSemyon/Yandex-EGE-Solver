
import { useState } from 'react';
import VariantSolver from './components/VariantSolver';
import TasksDownloader from './components/TasksDownloader';
import './App.css';

function App() {
    const [activeTab, setActiveTab] = useState('variant');

    return (
        <div className="app-container">
            <header className="app-header">
                <h1 className="app-title">
                    <span className="icon">🎓</span> Yandex EGE Solver
                </h1>
                <p className="app-subtitle">Авторешение вариантов Yandex EGE и загрузка банка задач по номеру в JSON файл</p>
            </header>

            <nav className="tabs">
                <button 
                    className={`tab ${activeTab === 'variant' ? 'active' : ''}`}
                    onClick={() => setActiveTab('variant')}
                >
                    Решение варианта
                </button>
                <button 
                    className={`tab ${activeTab === 'tasks' ? 'active' : ''}`}
                    onClick={() => setActiveTab('tasks')}
                >
                    База заданий
                </button>
            </nav>

            <main className="content">
                {activeTab === 'variant' ? <VariantSolver /> : <TasksDownloader />}
            </main>
            
            <footer className="app-footer">
                <p>© {new Date().getFullYear()} Yandex EGE Solver. Все права защищены.</p>
            </footer>
        </div>
    );
}

export default App;
