import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer

# These are the exact features the model will be trained on.
CATEGORICAL_FEATURES = ['action_type', 'privilege_level', 'process_name']
NUMERICAL_FEATURES = ['bytes_transferred', 'hour', 'day_of_week']

def create_preprocessor():
    """Creates a ColumnTransformer object for the defined features."""
    return ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), NUMERICAL_FEATURES),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), CATEGORICAL_FEATURES)
        ], remainder='drop')

def prepare_data_for_model(df):
    """The single source of truth for preparing data. Creates all features and ensures all columns exist."""
    df_prepared = df.copy()
    
    # 1. Time features
    df_prepared['timestamp'] = pd.to_datetime(df_prepared['timestamp'])
    df_prepared['hour'] = df_prepared['timestamp'].dt.hour
    df_prepared['day_of_week'] = df_prepared['timestamp'].dt.dayofweek

    # 2. Ensure all required feature columns exist and fill NaNs
    for col in CATEGORICAL_FEATURES:
        if col not in df_prepared.columns:
            df_prepared[col] = 'none'
        df_prepared[col] = df_prepared[col].fillna('none')
        
    for col in NUMERICAL_FEATURES:
        if col not in df_prepared.columns:
            df_prepared[col] = 0
        df_prepared[col] = df_prepared[col].fillna(0)
        
    return df_prepared