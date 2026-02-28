import pandas as pd
from sklearn.ensemble import IsolationForest
from storage.database import get_connection


class AnomalyModel:
    def __init__(self):
        self.model = None
        self.trained = False
        self.last_trained_row_count = 0

    def get_row_count(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM system_metrics")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def load_recent_data(self):
        conn = get_connection()
        query = """
        SELECT cpu, ram, disk, net_sent, net_recv
        FROM system_metrics
        ORDER BY id DESC
        LIMIT 500
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def should_retrain(self):
        current_rows = self.get_row_count()

        if current_rows - self.last_trained_row_count >= 100:
            return True

        return False

    def train(self):
        df = self.load_recent_data()

        if len(df) < 100:
            return False

        self.model = IsolationForest(
            n_estimators=100,
            contamination=0.05,
            random_state=42
        )

        self.model.fit(df)

        self.trained = True
        self.last_trained_row_count = self.get_row_count()

        return True

    import pandas as pd

    def predict(self, latest_row):
        if not self.trained:
            return None, None

        df = pd.DataFrame(
            [latest_row],
            columns=["cpu", "ram", "disk", "net_sent", "net_recv"]
        )

        prediction = self.model.predict(df)
        score = self.model.decision_function(df)

        return prediction[0], score[0]