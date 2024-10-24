import pandas as pd
import numpy as np
import json
import tensorflow as tf
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split

# Step 1: Load and preprocess the data
with open('manga_data.json', 'r') as f:
    manga_data = json.load(f)

df = pd.DataFrame(manga_data)

# Step 2: Data Preprocessing
# Filling missing values and converting types
df['Synopsis'] = df['Synopsis'].fillna('')
df['Score'] = df['Score'].replace('N/A', np.nan).astype(float)
df['Rank'] = df['Rank'].str.replace('#', '').astype(float)
df['Popularity'] = df['Popularity'].str.replace('#', '').astype(float)
df['Members'] = df['Members'].str.replace(',', '').astype(float)
df['Favourites'] = df['Favourites'].str.replace(',', '').astype(float)

# Step 3: Text Vectorization for Synopsis (TF-IDF)
tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
synopsis_tfidf = tfidf_vectorizer.fit_transform(df['Synopsis'])

# Step 4: One-hot encoding for genres and themes
genres_encoder = OneHotEncoder(sparse_output=False)
genres_one_hot = genres_encoder.fit_transform(df['Genres'].apply(lambda x: ','.join(x) if isinstance(x, list) else '').str.split(',').apply(lambda x: [x]).tolist())

themes_encoder = OneHotEncoder(sparse_output=False)
themes_one_hot = themes_encoder.fit_transform(df['Themes'].apply(lambda x: ','.join(x) if isinstance(x, list) else '').str.split(',').apply(lambda x: [x]).tolist())

# Step 5: Standardize numerical features
scaler = StandardScaler()
numerical_features = df[['Score', 'Rank', 'Popularity', 'Members', 'Favourites']].fillna(0)
numerical_features_scaled = scaler.fit_transform(numerical_features)

# Step 6: Combine all features into one dataset
X = np.hstack((numerical_features_scaled, genres_one_hot, themes_one_hot, synopsis_tfidf.toarray()))

# Step 7: Train-test split
X_train, X_test = train_test_split(X, test_size=0.2, random_state=42)

# Step 8: Building the TensorFlow Model
model = tf.keras.models.Sequential([
    tf.keras.layers.InputLayer(input_shape=(X_train.shape[1],)),
    tf.keras.layers.Dense(256, activation='relu'),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dense(16, activation='relu'),
    tf.keras.layers.Dense(1, activation='linear')
])

model.compile(optimizer='adam', loss='mean_squared_error')

# Step 9: Training the Model
model.fit(X_train, np.ones(X_train.shape[0]), epochs=10, batch_size=32)

# Step 10: Making Recommendations
def recommend_manga(input_title, df=df, X=X, model=model):
    # Find the index of the input manga
    idx = df.index[df['Title'] == input_title].tolist()[0]
    
    # Get the feature vector of the input manga
    input_vector = X[idx].reshape(1, -1)
    
    # Predict similarities with other mangas
    predictions = model.predict(X).flatten()
    
    # Sort the results and get the top recommendations
    recommended_indices = np.argsort(predictions)[::-1]
    
    # Return the recommended manga titles, excluding the input itself
    recommended_indices = [i for i in recommended_indices if i != idx][:5]
    return df['Title'].iloc[recommended_indices]

# Example: Get recommendations for "Berserk"
recommendations = recommend_manga('Berserk')
print(recommendations)
