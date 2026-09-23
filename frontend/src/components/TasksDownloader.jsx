
import { useState } from 'react';
import { Input, Button, Card, Alert } from './ui';

const TasksDownloader = () => {
    const [taskId, setTaskId] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');

        setIsLoading(true);
        try {
            const response = await fetch(`/api/tasks/${taskId}`);
            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.detail || 'Не удалось загрузить задания');
            }

            // Скачивание файла через Blob
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `tasks_${taskId}.json`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
            
            setSuccess(`Файл tasks_${taskId}.json успешно скачан!`);
            setTaskId('');
            setTimeout(() => setSuccess(''), 5000);
        } catch (err) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Card className="fade-in">
            <h2>Скачивание базы заданий</h2>
            <p className="text-muted">
                Загрузите все доступные задачи для конкретного номера в формате JSON.
            </p>

            <form onSubmit={handleSubmit} className="form">
                <Input
                    id="task-id"
                    label="Номер задания (1 - 27)"
                    type="number"
                    min="1"
                    max="27"
                    placeholder="Например: 5"
                    value={taskId}
                    onChange={(e) => setTaskId(e.target.value)}
                    error={error}
                />
                <Button type="submit" isLoading={isLoading}>
                    Скачать файл JSON
                </Button>
            </form>

            {success && <Alert type="success">{success}</Alert>}
        </Card>
    );
};

export default TasksDownloader;
