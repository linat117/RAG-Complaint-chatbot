import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

def basic_overview(df):
    print("Columns:", df.columns.tolist())
    print("\nShape:", df.shape)
    print("\nMissing values per column:")
    print(df.isnull().sum())

def product_distribution(df, interactive=False):
    # Count complaints per product
    product_counts = df['Product'].value_counts()
    print(product_counts)

    # Static Seaborn plot
    plt.figure(figsize=(10,6))
    sns.barplot(x=product_counts.index, y=product_counts.values)
    plt.xticks(rotation=45)
    plt.title("Complaint Distribution by Product")
    plt.tight_layout()
    plt.show()

    # Optional: Interactive Plotly
    if interactive:
        fig = px.bar(
            x=product_counts.index, 
            y=product_counts.values,
            labels={'x':'Product', 'y':'Count'},
            title="Complaint Distribution by Product"
        )
        fig.show()

def narrative_availability(df):
    total = len(df)
    with_narrative = df['Consumer complaint narrative'].notna().sum()
    without_narrative = total - with_narrative
    print(f"Total complaints: {total}")
    print(f"With narrative: {with_narrative}")
    print(f"Without narrative: {without_narrative}")

def narrative_length_analysis(df):
    # Compute word count
    df = df.copy()
    df['narrative_word_count'] = df['Consumer complaint narrative'].fillna("").apply(lambda x: len(str(x).split()))
    
    print("Narrative word count statistics:")
    print(df['narrative_word_count'].describe())
    
    # Histogram plot
    plt.figure(figsize=(10,6))
    sns.histplot(df['narrative_word_count'], bins=50)
    plt.title("Distribution of Narrative Word Count")
    plt.xlabel("Word count")
    plt.ylabel("Number of complaints")
    plt.show()
