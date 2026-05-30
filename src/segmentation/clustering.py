"""Customer Segmentation Module - Phase 4"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    silhouette_score,
    davies_bouldin_score,
    calinski_harabasz_score,
)
from typing import Tuple, Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


class CustomerSegmenter:
    """Customer segmentation using clustering algorithms."""

    def __init__(self, df: pd.DataFrame, features: List[str]):
        self.df = df
        self.features = features
        self.scaler = StandardScaler()
        self.scaled_data = None
        self.model = None
        self.segment_labels = None

    def prepare_data(self) -> np.ndarray:
        """Prepare and scale data for clustering."""
        X = self.df[self.features].fillna(0)
        self.scaled_data = self.scaler.fit_transform(X)
        return self.scaled_data

    def kmeans_clustering(self, n_clusters: int = 5) -> np.ndarray:
        """Perform K-Means clustering."""
        if self.scaled_data is None:
            self.prepare_data()

        self.model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.segment_labels = self.model.fit_predict(self.scaled_data)
        self.df["segment_kmeans"] = self.segment_labels

        logger.info(f"K-Means clustering completed with {n_clusters} clusters")
        return self.segment_labels

    def hierarchical_clustering(
        self, n_clusters: int = 5, linkage: str = "ward"
    ) -> np.ndarray:
        """Perform Hierarchical clustering."""
        if self.scaled_data is None:
            self.prepare_data()

        self.model = AgglomerativeClustering(
            n_clusters=n_clusters, linkage=linkage
        )
        self.segment_labels = self.model.fit_predict(self.scaled_data)
        self.df["segment_hierarchical"] = self.segment_labels

        logger.info(f"Hierarchical clustering completed with {n_clusters} clusters")
        return self.segment_labels

    def dbscan_clustering(
        self, eps: float = 0.5, min_samples: int = 5
    ) -> np.ndarray:
        """Perform DBSCAN clustering."""
        if self.scaled_data is None:
            self.prepare_data()

        self.model = DBSCAN(eps=eps, min_samples=min_samples)
        self.segment_labels = self.model.fit_predict(self.scaled_data)
        self.df["segment_dbscan"] = self.segment_labels

        logger.info(f"DBSCAN clustering completed")
        return self.segment_labels

    def evaluate_clustering(self, method: str = "kmeans") -> Dict:
        """Evaluate clustering quality."""
        if self.scaled_data is None or self.segment_labels is None:
            raise ValueError("Run clustering first")

        n_clusters = len(np.unique(self.segment_labels))
        if n_clusters < 2:
            return {"error": "Need at least 2 clusters for evaluation"}

        metrics = {
            "silhouette_score": silhouette_score(
                self.scaled_data, self.segment_labels
            ),
            "davies_bouldin_score": davies_bouldin_score(
                self.scaled_data, self.segment_labels
            ),
            "calinski_harabasz_score": calinski_harabasz_score(
                self.scaled_data, self.segment_labels
            ),
            "n_clusters": n_clusters,
        }

        logger.info(f"Clustering metrics: {metrics}")
        return metrics

    def find_optimal_k(self, k_range: range = range(2, 11)) -> Dict:
        """Find optimal number of clusters using elbow method and silhouette."""
        if self.scaled_data is None:
            self.prepare_data()

        inertias = []
        silhouettes = []

        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(self.scaled_data)

            inertias.append(kmeans.inertia_)
            if len(np.unique(labels)) > 1:
                silhouettes.append(silhouette_score(self.scaled_data, labels))
            else:
                silhouettes.append(0)

        optimal_k = list(k_range)[np.argmax(silhouettes)]

        return {
            "k_values": list(k_range),
            "inertias": inertias,
            "silhouette_scores": silhouettes,
            "optimal_k": optimal_k,
        }

    def assign_personas(self) -> pd.DataFrame:
        """Assign human-readable personas to segments."""
        if "segment_kmeans" not in self.df.columns:
            self.kmeans_clustering()

        segment_stats = self.df.groupby("segment_kmeans")[
            self.features
        ].mean()

        # Define personas based on feature values
        personas = {}
        for segment in segment_stats.index:
            stats = segment_stats.loc[segment]
            persona = []

            # High value
            if "total_revenue" in stats and stats["total_revenue"] > segment_stats["total_revenue"].mean():
                persona.append("High-Value")
            elif "total_revenue" in stats and stats["total_revenue"] < segment_stats["total_revenue"].quantile(0.25):
                persona.append("Low-Value")

            # Recency-based
            if "recency" in stats and stats["recency"] < segment_stats["recency"].quantile(0.25):
                persona.append("Recent")
            elif "recency" in stats and stats["recency"] > segment_stats["recency"].quantile(0.75):
                persona.append("Dormant")

            # Activity
            if "frequency" in stats and stats["frequency"] > segment_stats["frequency"].mean():
                persona.append("Active")
            else:
                persona.append("Inactive")

            personas[segment] = " ".join(persona) if persona else "Standard"

        self.df["persona"] = self.df["segment_kmeans"].map(personas)
        return self.df
