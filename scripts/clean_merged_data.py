import pandas as pd
import os

def clean_and_merge():
    # Paths
    synthetic_path = "1-Rag/data/training_cases.csv"
    real_path = "1-Rag/data/real_cases_fetched.csv"
    output_path = "1-Rag/data/cleaned_training_data.csv"
    
    dfs = []
    
    # Load Synthetic
    if os.path.exists(synthetic_path):
        df_syn = pd.read_csv(synthetic_path)
        print(f"Loaded {len(df_syn)} synthetic cases.")
        dfs.append(df_syn)
        
    # Load Real
    if os.path.exists(real_path):
        df_real = pd.read_csv(real_path)
        print(f"Loaded {len(df_real)} real cases.")
        # Ensure compatible columns
        common_cols = ['title', 'description', 'court', 'date', 'outcome']
        # Add missing if needed
        for col in common_cols:
            if col not in df_real.columns:
                df_real[col] = ''
        
        # Select and reorder
        df_real = df_real[common_cols]
        # Add dummy for missing cols if synthetic has more (e.g. prompt is not in real)
        if dfs:
            for col in dfs[0].columns:
                if col not in df_real.columns:
                    df_real[col] = ''
            df_real = df_real[dfs[0].columns] # Align columns
            
        dfs.append(df_real)
        
    if not dfs:
        print("No data found!")
        return
        
    # Merge
    full_df = pd.concat(dfs, ignore_index=True)
    
    # Deduplicate by description
    full_df.drop_duplicates(subset=['description'], inplace=True)
    
    # Clean Outcomes
    full_df['outcome'] = full_df['outcome'].str.lower().str.strip()
    valid_outcomes = ['allowed', 'dismissed', 'partly_allowed', 'settlement', 'petitioner_win', 'defendant_win'] # petitioner_win/defendant_win are likely from synthetic
    # Normalize: map synthetic 'petitioner_win' -> 'allowed', 'defendant_win' -> 'dismissed' (rough equivalent for training stability)
    outcome_map = {
        'petitioner_win': 'allowed',
        'defendant_win': 'dismissed',
        'plaintiff_win': 'allowed'
    }
    full_df['outcome'] = full_df['outcome'].replace(outcome_map)
    
    # Filter rare classes (< 2 samples)
    class_counts = full_df['outcome'].value_counts()
    print("\nClass distribution before filtering:")
    print(class_counts)
    
    valid_classes = class_counts[class_counts >= 2].index
    filtered_df = full_df[full_df['outcome'].isin(valid_classes)]
    
    print(f"\nFinal dataset size: {len(filtered_df)}")
    filtered_df.to_csv(output_path, index=False)
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    clean_and_merge()
