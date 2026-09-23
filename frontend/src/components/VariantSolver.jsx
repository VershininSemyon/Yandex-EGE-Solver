
import { useState } from 'react';
import { Input, Button, Card } from './ui';

const VariantSolver = () => {
    const [variantId, setVariantId] = useState('');
    const [variantData, setVariantData] = useState(null);
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setVariantData(null);

        setIsLoading(true);
        try {
            const response = await fetch(`/api/variants/${variantId}`);
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
            <h2>Поиск и решение варианта</h2>
            <p className="text-muted">Вставьте ссылку на вариант, чтобы получить готовые ответы на все задания.</p>
            
            <form onSubmit={handleSubmit} className="form">
                <Input
                    id="variant-id"
                    label="ID варианта (UUID)"
                    type="text"
                    placeholder="123e4567-e89b-12d3-a456-426614174000"
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
                    <h3 className="variant-title">{variantData.title || 'Без названия'}</h3>
                    <div className="tasks-grid">
                        {variantData.tasks.map((task) => (
                            <div key={task.number} className="task-card">
                                <div className="task-header">
                                    <span className="task-number">№ {task.number}</span>
                                </div>
                                <div className="task-answers">
                                    {task.answers.length > 0 ? (
                                        task.answers.map((ans, idx) => (
                                            <span key={idx} className="answer-badge">
                                                {ans}
                                            </span>
                                        ))
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

export default VariantSolver;
