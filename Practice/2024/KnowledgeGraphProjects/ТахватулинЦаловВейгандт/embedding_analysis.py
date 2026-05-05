import numpy as np
import pandas as pd
from rdflib import Graph
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.preprocessing import StandardS caler

def load_and_prepare_data():
    """Load data from ontology CSV and prepare for analysis"""
    df = pd.read_csv("ontology.csv")
    print(f"Total rows in ontology: {len(df)}")
    
    # Create embeddings dictionary for champions
    champion_embeddings = {}
    versus_data = {}
    
    # Filter triples related to champions and versus matchups
    champion_triples = df[
        (df['Subject'].str.contains('http://example.org/lol#', na=False)) &
        ~(df['Subject'].str.contains('versus', na=False))
    ]
    versus_triples = df[df['Subject'].str.contains('versus', na=False)]
    
    print(f"Champion triples found: {len(champion_triples)}")
    print(f"Versus triples found: {len(versus_triples)}")
    
    # Get unique champions by filtering subjects that have RDF.type Champion
    champion_type_triples = champion_triples[
        (champion_triples['Predicate'] == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type') &
        (champion_triples['Object'] == 'http://example.org/lol#Champion')
    ]
    
    # Clean champion names by removing URI prefix
    unique_champions = champion_type_triples['Subject'].apply(
        lambda x: x.split('#')[-1]  # Get everything after the last #
    ).unique()
    
    print(f"Unique champions found: {len(unique_champions)}")
    print("Sample champions:", unique_champions[:5])
    
    # Create numerical embeddings based on champion properties
    for champion_name in unique_champions:
        # Get all triples for this champion (need to add URI prefix back for lookup)
        champion_uri = f'http://example.org/lol#{champion_name}'
        champ_data = champion_triples[champion_triples['Subject'] == champion_uri]
        
        # Create embedding vector from champion properties
        embedding = []
        
        # Add winrate value if exists
        winrate = champ_data[champ_data['Predicate'] == 'http://example.org/lol#winrateValue']['Object'].values
        try:
            winrate = [float(w) for w in winrate]
        except (ValueError, TypeError):
            winrate = [0]
        embedding.extend(winrate if len(winrate) > 0 else [0])
        
        # Add pickrate value if exists
        pickrate = champ_data[champ_data['Predicate'] == 'http://example.org/lol#pickrateValue']['Object'].values
        try:
            pickrate = [float(p) for p in pickrate]
        except (ValueError, TypeError):
            pickrate = [0]
        embedding.extend(pickrate if len(pickrate) > 0 else [0])
        
        # Add banrate value if exists
        banrate = champ_data[champ_data['Predicate'] == 'http://example.org/lol#banrateValue']['Object'].values
        try:
            banrate = [float(b) for b in banrate]
        except (ValueError, TypeError):
            banrate = [0]
        embedding.extend(banrate if len(banrate) > 0 else [0])
        
        # Get versus matchup data
        vs_data = versus_triples[
            ((versus_triples['Object'] == champion_uri) | 
             (versus_triples['Subject'].str.contains(champion_name, case=False, na=False))) &
            (versus_triples['Predicate'] == 'http://example.org/lol#winrateValue')
        ]
        
        # Calculate average winrate for each rank
        for rank in ['iron', 'bronze', 'silver', 'gold', 'platinum']:
            rank_vs_data = vs_data[vs_data['Subject'].str.contains(rank, case=False, na=False)]
            try:
                avg_vs_winrate = rank_vs_data['Object'].astype(float).mean()
                embedding.append(avg_vs_winrate if not np.isnan(avg_vs_winrate) else 0)
            except (ValueError, TypeError):
                embedding.append(0)
        
        # Add role information (one-hot encoded)
        roles = champ_data[champ_data['Predicate'] == 'http://example.org/lol#hasRole']['Object'].unique()
        role_features = [1 if any('Support' in str(r) for r in roles) else 0,
                        1 if any('Marksman' in str(r) for r in roles) else 0,
                        1 if any('Mid' in str(r) for r in roles) else 0,
                        1 if any('Jungle' in str(r) for r in roles) else 0,
                        1 if any('Top' in str(r) for r in roles) else 0]
        embedding.extend(role_features)
        
        # Store embedding as numpy array
        embedding_array = np.array(embedding, dtype=float)
        
        # Store data if valid
        if not np.any(np.isnan(embedding_array)):
            champion_embeddings[champion_name] = embedding_array
            versus_data[champion_name] = vs_data

    return df, champion_embeddings, versus_data

def visualize_embeddings(champion_embeddings):
    """Create 2D visualization of champion embeddings"""
    if not champion_embeddings:
        print("No valid embeddings to visualize")
        return
    
    if len(champion_embeddings) < 2:
        print("Need at least 2 champions for visualization")
        return
        
    embeddings_array = np.array(list(champion_embeddings.values()))
    champion_names = list(champion_embeddings.keys())
    
    n_features = embeddings_array.shape[1]
    
    scaler = StandardScaler()
    embeddings_scaled = scaler.fit_transform(embeddings_array)
    
    pca = PCA(n_components=2)
    embeddings_2d = pca.fit_transform(embeddings_scaled)
    
    plot_df = pd.DataFrame({
        'champion': champion_names,
        'x': embeddings_2d[:, 0],
        'y': embeddings_2d[:, 1],
        'winrate': embeddings_array[:, 0],  # First feature is winrate
        'pickrate': embeddings_array[:, 1],  # Second feature is pickrate
        'banrate': embeddings_array[:, 2],   # Third feature is banrate
    })
    
    plt.figure(figsize=(15, 10))
    scatter = sns.scatterplot(
        data=plot_df,
        x='x',
        y='y',
        hue='winrate',
        size='pickrate',
        palette='viridis',
    )
    
    texts = []
    for i, row in plot_df.iterrows():
        texts.append(plt.annotate(
            row['champion'],
            (row['x'], row['y']),
            fontsize=8,
            alpha=0.7,
            xytext=(5, 5),
            textcoords='offset points'
        ))
    
    try:
        from adjustText import adjust_text
        adjust_text(texts, arrowprops=dict(arrowstyle='->', color='gray', alpha=0.5))
    except ImportError:
        print("Install adjustText package for better label positioning")
    
    plt.title('Champion Embeddings Visualization\nColor: Winrate, Size: Pickrate')
    plt.legend(title='Winrate %', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()
    
    print(f"\nExplained variance ratio: {pca.explained_variance_ratio_}")
    
    feature_names = ['Winrate', 'Pickrate', 'Banrate']
    if n_features > 3:
        feature_names.extend([f'VS_{rank}' for rank in ['Iron', 'Bronze', 'Silver', 'Gold', 'Platinum']])
    if n_features > 8:
        feature_names.extend(['Support', 'Marksman', 'Mid', 'Jungle', 'Top'])
    
    feature_names = feature_names[:n_features]
    
    print("\nFeature contributions to principal components:")
    for i, pc in enumerate(pca.components_[:2]):
        print(f"\nPC{i+1} feature importance:")
        importance = pd.DataFrame({
            'Feature': feature_names,
            'Importance': np.abs(pc[:len(feature_names)])
        }).sort_values('Importance', ascending=False)
        print(importance)

def train_classifier(champion_embeddings):
    """Train a classifier using champion embeddings"""
    # Prepare features and labels
    X = np.array(list(champion_embeddings.values()))
    
    if X.shape[1] < 2:
        print("Warning: Not enough features for classification")
        return None
    
    # Create binary labels based on winrate (above/below median)
    winrates = X[:, 0]  # Assuming winrate is first feature
    y = (winrates > np.median(winrates)).astype(int)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train classifier
    clf = XGBClassifier(n_estimators=100, max_depth=3)
    clf.fit(X_train, y_train)
    
    # Make predictions
    y_pred = clf.predict(X_test)
    
    # Print accuracy and classification report
    accuracy = metrics.accuracy_score(y_test, y_pred)
    print(f"Classification accuracy: {accuracy:.2f}")
    print("\nClassification Report:")
    print(metrics.classification_report(y_test, y_pred))
    
    return clf

def analyze_matchups(versus_data):
    """Analyze champion matchup data"""
    print("\nAnalyzing champion matchups...")
    
    # Calculate average winrates for each champion
    matchup_stats = {}
    for champion, data in versus_data.items():
        # Extract champion name from URI
        champ_name = champion.split('#')[-1]
        
        # Get all versus matchups where this champion is either chosen or vs champion
        winrates = []
        for _, row in data.iterrows():
            if row['Predicate'] == 'http://example.org/lol#winrateValue':
                try:
                    winrate = float(row['Object'])
                    winrates.append(winrate)
                except (ValueError, TypeError):
                    continue
        
        # Calculate stats only if we have winrates
        if winrates:
            matchup_stats[champ_name] = {
                'avg_winrate': np.mean(winrates),
                'matchup_count': len(winrates),
                'best_matchup': max(winrates),
                'worst_matchup': min(winrates)
            }
    
    # Convert to dataframe for easy viewing
    stats_df = pd.DataFrame.from_dict(matchup_stats, orient='index')
    
    if not stats_df.empty:
        print("\nTop 5 champions by average winrate:")
        print(stats_df.sort_values('avg_winrate', ascending=False).head())
    else:
        print("\nNo matchup data found. Let's check the versus_triples:")
        print("\nSample of versus_triples data structure:")
        for champion, data in list(versus_data.items())[:1]:
            print(f"\nChampion: {champion}")
            print("Data sample:")
            print(data.head())

def main():
    # Load and prepare data
    print("Loading data...")
    df, champion_embeddings, versus_data = load_and_prepare_data()
    
    # Visualize embeddings
    print("\nCreating visualization...")
    visualize_embeddings(champion_embeddings)
    
    # Train and evaluate classifier
    print("\nTraining classifier...")
    clf = train_classifier(champion_embeddings)
    
    # Analyze matchups
    analyze_matchups(versus_data)

if __name__ == "__main__":
    main() 