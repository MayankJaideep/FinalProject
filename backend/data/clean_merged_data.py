
import pandas as pd
import sys

def clean_data(input_path, output_path):
    print(f"🧹 Cleaning data from {input_path}...")
    df = pd.read_csv(input_path)
    print(f"   Original shape: {df.shape}")
    print(f"   Original class distribution:\n{df['outcome'].value_counts()}")
    
    # standardize
    df['outcome'] = df['outcome'].str.lower().str.strip()
    
    # filter classes with < 2 examples
    counts = df['outcome'].value_counts()
    valid_classes = counts[counts >= 2].index
    
    df_clean = df[df['outcome'].isin(valid_classes)]
    
    print(f"   Cleaned shape: {df_clean.shape}")
    print(f"   Removed classes: {list(set(counts.index) - set(valid_classes))}")
    print(f"   Cleaned class distribution:\n{df_clean['outcome'].value_counts()}")
    
    if len(df_clean) < 10:
        print("❌ Error: Too few samples remaining after cleaning.")
        sys.exit(1)
        
    df_clean.to_csv(output_path, index=False)
    print(f"✅ Saved cleaned data to {output_path}")

if __name__ == "__main__":
    clean_data('1-Rag/data/merged_training_data.csv', '1-Rag/data/cleaned_training_data.csv')
