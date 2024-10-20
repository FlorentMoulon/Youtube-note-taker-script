transcript = ""
with open("transcript.txt", "r", encoding="utf-8") as f:
    transcript = f.read()

def print_transcript_by_minutes(transcript):
    for i, minute in enumerate(transcript):
        print(f"Minute {i}:")
        print(minute)
        print()

def extract_minute(line):
    return int(line[4:6])
    
def split_transcript_by_minutes(transcript):
    lines = transcript.split("\n")
    transcript_by_minutes = []
    
    for line in lines:
        if not line.startswith("["):
            if transcript_by_minutes:
                transcript_by_minutes[-1] += " " + line  # Append to the last minute's transcript
            continue
        
        minute = extract_minute(line)
        
        # Ensure transcript_by_minutes has enough slots for the current minute
        while len(transcript_by_minutes) <= minute:
            transcript_by_minutes.append("")
        
        transcript_by_minutes[minute] += line[8:]  # Remove the timestamp part and append text

    return transcript_by_minutes




transcript_by_minutes = split_transcript_by_minutes(transcript)



# Embedding Support
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import os

# Data Science
import numpy as np
from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering

# Plotting
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt

# Taking out the warnings
import warnings
from warnings import simplefilter


def mainKmeans():
    embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                cache_folder=os.path.join(os.getcwd(), 'models_cache'),
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )

    # Create cache directory if it doesn't exist
    os.makedirs(os.path.join(os.getcwd(), 'models_cache'), exist_ok=True)

    # Embed the documents
    vectors = embeddings.embed_documents(transcript_by_minutes)
    # Convert vectors to a NumPy array
    vectors = np.array(vectors)  # Ensures that vectors is in the correct format

    # Perform K-means clustering
    num_clusters = 11
    kmeans = KMeans(n_clusters=num_clusters, random_state=42).fit(vectors)
    
    plotKmeans(vectors, kmeans)


def plotKmeans(vectors, kmeans):
    # Filter out FutureWarnings
    simplefilter(action='ignore', category=FutureWarning)

    # Perform t-SNE and reduce to 2 dimensions
    tsne = TSNE(n_components=2, random_state=42)
    reduced_data_tsne = tsne.fit_transform(vectors)

    # Create a color map for the clusters
    cmap = plt.get_cmap('tab10')  # A color palette with more distinguishable colors

    # Plot the reduced data with cluster labels as colors
    plt.figure(figsize=(10, 7))
    scatter = plt.scatter(
        reduced_data_tsne[:, 0], 
        reduced_data_tsne[:, 1], 
        c=kmeans.labels_, 
        cmap=cmap, 
        s=100,  # Make points larger
        alpha=0.7  # Add some transparency
    )
    plt.colorbar(scatter)

    # Add labels (indices of points)
    for i, (x, y) in enumerate(reduced_data_tsne):
        plt.text(x, y, str(i), fontsize=9, ha='right', va='bottom', color='black')

    # Plot labels and title
    plt.xlabel('Dimension 1')
    plt.ylabel('Dimension 2')
    plt.title('Transcript Embeddings Clustered')

    # Show the plot
    plt.show()

    # Optionally save the plot
    print("saving plot")
    plt.savefig("tsne_plot_with_labels.png")  # Save the plot
    
#mainKmeans()





from scipy.cluster.hierarchy import linkage, dendrogram
import matplotlib.pyplot as plt
import numpy as np
import os

def mainHierarchical():
    embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                cache_folder=os.path.join(os.getcwd(), 'models_cache'),
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )

    # Create cache directory if it doesn't exist
    os.makedirs(os.path.join(os.getcwd(), 'models_cache'), exist_ok=True)

    # Embed the documents
    vectors = embeddings.embed_documents(transcript_by_minutes)
    vectors = np.array(vectors)  # Convert vectors to a NumPy array

    # Perform Hierarchical Clustering using linkage from SciPy
    Z = linkage(vectors, method='ward')  # 'ward' minimizes variance between clusters
    
    # Plot the dendrogram
    plot_dendrogram(Z)


def plot_dendrogram(Z):
    # Create a figure for the dendrogram
    plt.figure(figsize=(10, 7))
    
    # Plot the dendrogram
    dendrogram(Z)
    
    # Add title and labels
    plt.title('Dendrogram for Hierarchical Clustering')
    plt.xlabel('Transcript Index')
    plt.ylabel('Distance')

    # Show and save the plot
    plt.show()
    plt.savefig("dendrogram_plot.png")  # Save the plot to verify
    print("Dendrogram saved as 'dendrogram_plot.png'")
    
mainHierarchical()