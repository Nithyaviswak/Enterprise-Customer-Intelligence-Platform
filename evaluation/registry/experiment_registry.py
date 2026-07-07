"""
Experiment Registry - Persistent storage for experiment metadata and results.
"""

import json
import sqlite3
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

from ..types import EvaluationResult

logger = logging.getLogger(__name__)


class ExperimentRegistry:
    """SQLite-backed experiment registry for persistence and querying."""

    def __init__(self, db_path: str = "evaluation_output/registry.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        cursor = self._conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS experiments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT UNIQUE,
                model_name TEXT NOT NULL,
                model_version TEXT NOT NULL,
                dataset TEXT,
                timestamp TEXT,
                git_commit TEXT,
                config TEXT,
                status TEXT DEFAULT 'completed',
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id INTEGER NOT NULL,
                precision REAL,
                recall REAL,
                f1_score REAL,
                mAP50 REAL,
                mAP50_95 REAL,
                fps REAL,
                latency_ms REAL,
                latency_p99_ms REAL,
                gpu_memory_mb REAL,
                model_size_mb REAL,
                inference_cost REAL,
                total_images INTEGER,
                total_detections INTEGER,
                total_ground_truths INTEGER,
                FOREIGN KEY (experiment_id) REFERENCES experiments(id)
            );

            CREATE TABLE IF NOT EXISTS class_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id INTEGER NOT NULL,
                class_name TEXT NOT NULL,
                class_id INTEGER,
                precision REAL,
                recall REAL,
                f1_score REAL,
                ap50 REAL,
                support INTEGER,
                tp INTEGER,
                fp INTEGER,
                fn INTEGER,
                FOREIGN KEY (experiment_id) REFERENCES experiments(id)
            );

            CREATE TABLE IF NOT EXISTS artifacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                path TEXT NOT NULL,
                type TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (experiment_id) REFERENCES experiments(id)
            );

            CREATE INDEX IF NOT EXISTS idx_experiments_model
                ON experiments(model_name, model_version);
            CREATE INDEX IF NOT EXISTS idx_experiments_timestamp
                ON experiments(timestamp);
        """)
        self._conn.commit()

    def register_experiment(self, result: EvaluationResult) -> int:
        """Register an evaluation result in the registry."""
        cursor = self._conn.cursor()
        cursor.execute("""
            INSERT INTO experiments (run_id, model_name, model_version, dataset,
                                     timestamp, git_commit, config)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            result.run_id,
            result.model_name,
            result.model_version,
            result.dataset,
            result.timestamp.isoformat(),
            result.git_commit,
            json.dumps(result.config or {}, default=str),
        ))
        experiment_id = cursor.lastrowid

        m = result.metrics
        cursor.execute("""
            INSERT INTO metrics (experiment_id, precision, recall, f1_score,
                                 mAP50, mAP50_95, fps, latency_ms, latency_p99_ms,
                                 gpu_memory_mb, model_size_mb, inference_cost,
                                 total_images, total_detections, total_ground_truths)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            experiment_id, m.precision, m.recall, m.f1_score,
            m.mAP50, m.mAP50_95, m.fps, m.latency_ms, m.latency_p99_ms,
            m.gpu_memory_mb, m.model_size_mb, m.inference_cost_per_image,
            m.total_images, m.total_detections, m.total_ground_truths,
        ))

        for class_name, cm in m.per_class_metrics.items():
            cursor.execute("""
                INSERT INTO class_metrics (experiment_id, class_name, class_id,
                                           precision, recall, f1_score, ap50,
                                           support, tp, fp, fn)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                experiment_id, class_name, cm.class_id,
                cm.precision, cm.recall, cm.f1_score, cm.ap50,
                cm.support, cm.tp, cm.fp, cm.fn,
            ))

        self._conn.commit()
        logger.info(f"Registered experiment {experiment_id}: {result.model_name} v{result.model_version}")
        return experiment_id

    def query_experiments(
        self,
        model_name: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict]:
        """Query experiments with optional filtering."""
        cursor = self._conn.cursor()
        if model_name:
            cursor.execute("""
                SELECT e.*, m.* FROM experiments e
                JOIN metrics m ON e.id = m.experiment_id
                WHERE e.model_name = ?
                ORDER BY e.timestamp DESC LIMIT ? OFFSET ?
            """, (model_name, limit, offset))
        else:
            cursor.execute("""
                SELECT e.*, m.* FROM experiments e
                JOIN metrics m ON e.id = m.experiment_id
                ORDER BY e.timestamp DESC LIMIT ? OFFSET ?
            """, (limit, offset))
        return [dict(row) for row in cursor.fetchall()]

    def get_best_version(self, model_name: str, metric: str = "mAP50") -> Optional[Dict]:
        """Get best model version by specified metric."""
        allowed = {"mAP50", "mAP50_95", "precision", "recall", "f1_score", "fps"}
        if metric not in allowed:
            raise ValueError(f"Invalid metric. Choose from {allowed}")
        cursor = self._conn.cursor()
        cursor.execute(f"""
            SELECT e.*, m.* FROM experiments e
            JOIN metrics m ON e.id = m.experiment_id
            WHERE e.model_name = ?
            ORDER BY m.{metric} DESC LIMIT 1
        """, (model_name,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_class_trend(
        self, model_name: str, class_name: str, metric: str = "ap50"
    ) -> List[Dict]:
        """Get metric trend for a specific class across versions."""
        allowed = {"precision", "recall", "f1_score", "ap50"}
        if metric not in allowed:
            raise ValueError(f"Invalid metric. Choose from {allowed}")
        cursor = self._conn.cursor()
        cursor.execute(f"""
            SELECT e.model_version, e.timestamp, cm.{metric}
            FROM experiments e
            JOIN class_metrics cm ON e.id = cm.experiment_id
            WHERE e.model_name = ? AND cm.class_name = ?
            ORDER BY e.timestamp ASC
        """, (model_name, class_name))
        return [dict(row) for row in cursor.fetchall()]

    def get_version_count(self, model_name: str) -> int:
        """Get number of registered versions for a model."""
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM experiments WHERE model_name = ?",
            (model_name,),
        )
        return cursor.fetchone()[0]

    def close(self):
        self._conn.close()
