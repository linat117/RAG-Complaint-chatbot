import re
import pandas as pd

def clean_text(text: str) -> str:
    """
    Basic text cleaning for embeddings:
    - Lowercase
    - Remove special characters except basic punctuation
    - Remove boilerplate phrases
    """
    if pd.isna(text):
        return ""
    
    # Lowercase
    text = text.lower()
    
    # Remove boilerplate phrases
    boilerplate_patterns = [
        r"i am writing to file a complaint",
        r"i am contacting you regarding",
        r"this is to complain about"
    ]
    for pattern in boilerplate_patterns:
        text = re.sub(pattern, '', text)
    
    # Remove special characters (keep letters, numbers, basic punctuation)
    text = re.sub(r"[^a-z0-9\s\.,;!?]", "", text)
    
    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()
    
    return text

def apply_text_cleaning(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply cleaning function to the narrative column.
    """
    df = df.copy()
    df['cleaned_narrative'] = df['Consumer complaint narrative'].apply(clean_text)
    print("Text cleaning applied.")
    return df
