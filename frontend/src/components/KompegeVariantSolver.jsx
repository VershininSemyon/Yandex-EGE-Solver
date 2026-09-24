
import { useState } from 'react';
import { Input, Button, Card } from './ui';

const KompegeVariantSolver = () => {
    const [variantId, setVariantId] = useState('');
    const [variantData, setVariantData] = useState(null);
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setVariantData(null);

        if (!variantId.trim()) {
            setError('Введите ID варианта');
            return;
        }

        setIsLoading(true);
        try {
            const response = await fetch(`/api/kompege/variants/${encodeURIComponent(variantId.trim())}`);
            
            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                let errorMsg = 'Не удалось получить вариант';
                if (errData.detail) {
                    errorMsg = Array.isArray(errData.detail) 
                        ? errData.detail.map(e => e.msg).join(', ') 
                        : errData.detail;
                }
                throw new Error(errorMsg);
            }

            const data = await response.json();
            setVariantData(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Card className="fade-in">
            <h2>📘 Решение варианта Kompege</h2>
            <p className="text-muted">
                Введите ID варианта с сайта Kompege, чтобы получить готовые ответы на все задания.
            </p>
            
            <form onSubmit={handleSubmit} className="form">
                <Input
                    id="kompege-variant-id"
                    label="ID варианта (например: 2771)"
                    type="text"
                    placeholder="2771"
                    value={variantId}
                    onChange={(e) => setVariantId(e.target.value)}
                    error={error && !variantData ? error : ''}
                />
                <Button type="submit" isLoading={isLoading}>
                    Получить ответы
                </Button>
            </form>

            {variantData && (
                <div className="result-container fade-in">
                    <h3 className="variant-title">
                        {variantData.description || 'Вариант Kompege'}
                    </h3>
                    <div className="tasks-grid">
                        {variantData.tasks.map((task) => (
                            <div key={task.number} className="task-card">
                                <div className="task-header">
                                    <span className="task-number">№ {task.number}</span>
                                </div>
                                <div className="task-answers">
                                    {task.answers ? (
                                        <span className="answer-badge kompege-badge">
                                            {task.answers}
                                        </span>
                                    ) : (
                                        <span className="no-answer">Ответ не найден</span>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </Card>
    );
};

export default KompegeVariantSolver;
