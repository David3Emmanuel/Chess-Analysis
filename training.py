import joblib
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.linear_model import Lasso
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score

from data import load_data


def display_linear_regression_coefficients(model, feature_names, model_name="Linear Regression"):
    """Display the coefficients of a linear regression model with feature names."""
    if hasattr(model, 'coef_') and hasattr(model, 'intercept_'):
        print(f"\n{model_name} Coefficients:")
        print(f"Intercept: {model.intercept_:.6f}")
        print("\nFeature Coefficients:")
        print("-" * 50)
        
        coef_pairs = list(zip(model.coef_, feature_names))
        coef_pairs.sort(key=lambda x: abs(x[0]), reverse=True)
        
        for coef, feature in coef_pairs:
            print(f"{feature:30} : {coef:12.6f}")
        
        print("-" * 50)
        print(f"Number of features: {len(feature_names)}")


def evaluate_model(model, X_train, X_test, y_train, y_test, model_name, cv_folds=5):
    """Evaluate a model and print comprehensive results."""
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    train_r2 = r2_score(y_train, y_pred_train)
    test_r2 = r2_score(y_test, y_pred_test)
    train_mse = mean_squared_error(y_train, y_pred_train)
    test_mse = mean_squared_error(y_test, y_pred_test)
    
    cv_scores = cross_val_score(model, X_train, y_train, cv=cv_folds, scoring='r2')
    
    print(f"\n{model_name} Results:")
    print(f"Training R² score: {train_r2:.4f}")
    print(f"Testing R² score: {test_r2:.4f}")
    print(f"Training MSE: {train_mse:.4f}")
    print(f"Testing MSE: {test_mse:.4f}")
    print(f"Cross-validation R² scores: {cv_scores}")
    print(f"Mean CV R² score: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    return test_r2, y_pred_test


def tune_and_evaluate_model(model, param_grid, X_train, X_test, y_train, y_test, model_name, cv_folds=5):
    """Perform hyperparameter tuning and evaluate a model."""
    print(f"\n{model_name}...")
    
    grid_search = GridSearchCV(
        model, 
        param_grid, 
        cv=cv_folds, 
        scoring='neg_mean_squared_error',
        n_jobs=-1,
        verbose=1
    )
    
    grid_search.fit(X_train, y_train)
    best_model = grid_search.best_estimator_
    
    print(f"Best parameters: {grid_search.best_params_}")
    
    test_r2, y_pred_test = evaluate_model(best_model, X_train, X_test, y_train, y_test, model_name, cv_folds)
    
    if "Regression" in model_name and hasattr(best_model, 'coef_'):
        display_linear_regression_coefficients(best_model, feature_names, model_name)
    
    return best_model, test_r2, y_pred_test


X, y, feature_names = load_data()
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"Training set size: {X_train.shape[0]} samples")
print(f"Testing set size: {X_test.shape[0]} samples")

# Define models and their parameter grids
models_to_test = [
    {
        'name': 'RandomForestRegressor',
        'model': RandomForestRegressor(random_state=42),
        'param_grid': {
            'n_estimators': [50, 100, 200],
            'max_depth': [5, 10, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        },
        'cv_folds': 5
    },
    {
        'name': 'Ridge Regression',
        'model': Ridge(random_state=42),
        'param_grid': {
            'alpha': [0.1, 1.0, 10.0, 100.0, 1000.0]
        },
        'cv_folds': 5
    },
    {
        'name': 'Lasso Regression',
        'model': Lasso(random_state=42, max_iter=2000),
        'param_grid': {
            'alpha': [0.001, 0.01, 0.1, 1.0, 10.0]
        },
        'cv_folds': 5
    },
    {
        'name': 'Polynomial RandomForest',
        'model': Pipeline([
            ('poly', PolynomialFeatures(degree=2, include_bias=False)),
            ('rf', RandomForestRegressor(random_state=42))
        ]),
        'param_grid': {
            'poly__degree': [1, 2],
            'rf__n_estimators': [50, 100],
            'rf__max_depth': [5, 10, None]
        },
        'cv_folds': 3
    }
]

# Store results for comparison
model_results = {}
trained_models = {}

# Test models with hyperparameter tuning
for i, model_config in enumerate(models_to_test, 1):
    print(f"\n{i}. Testing {model_config['name']}...")
    
    best_model, test_r2, _ = tune_and_evaluate_model(
        model_config['model'],
        model_config['param_grid'],
        X_train, X_test, y_train, y_test,
        model_config['name'],
        model_config['cv_folds']
    )
    
    model_results[model_config['name']] = test_r2
    trained_models[model_config['name']] = best_model

# Test Linear Regression (no hyperparameters to tune)
print(f"\n{len(models_to_test) + 1}. Testing Linear Regression...")
linear_model = LinearRegression()
linear_model.fit(X_train, y_train)

test_r2, _ = evaluate_model(linear_model, X_train, X_test, y_train, y_test, "Linear Regression")
display_linear_regression_coefficients(linear_model, feature_names, "Linear Regression")
model_results["Linear Regression"] = test_r2
trained_models["Linear Regression"] = linear_model

# Compare all models
print(f"\n{len(models_to_test) + 2}. Model Comparison:")
for model_name, score in model_results.items():
    print(f"{model_name} - Test R²: {score:.4f}")

# Choose the best model
best_model_name = max(model_results.keys(), key=lambda x: model_results[x])
best_score = model_results[best_model_name]
final_model = trained_models[best_model_name]

print(f"\nSelected model: {best_model_name}")
print(f"Final model test R² score: {best_score:.4f}")

joblib.dump(final_model, 'final_model.joblib')