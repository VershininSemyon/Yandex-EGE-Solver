
export const Input = ({ label, error, id, ...props }) => (
    <div className="input-group">
        {label && <label htmlFor={id} className="input-label">{label}</label>}
        <input 
            id={id}
            className={`input-field ${error ? 'input-error' : ''}`} 
            {...props} 
        />
        {error && <span className="error-message">{error}</span>}
    </div>
);

export const Button = ({ children, isLoading, ...props }) => (
    <button 
        className={`btn ${isLoading ? 'btn-loading' : ''}`} 
        disabled={isLoading} 
        {...props}
    >
        {isLoading ? (
            <>
                <span className="spinner"></span>
                Загрузка...
            </>
        ) : (
            children
        )}
    </button>
);

export const Card = ({ children, className = '' }) => (
    <div className={`card ${className}`}>
        {children}
    </div>
);

export const Alert = ({ type = 'error', children }) => (
    <div className={`alert alert-${type}`}>
        {children}
    </div>
);
