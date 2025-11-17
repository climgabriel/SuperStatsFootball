"""LSTM Model for Sequence-Based Match Outcome Prediction."""

import numpy as np
from typing import Optional, List
import warnings

# Try to import TensorFlow/Keras
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    warnings.warn("TensorFlow not installed. LSTMOutcomeModel will not be available.")


class LSTMOutcomeModel:
    """
    LSTM model for predicting match outcomes from sequences.

    Uses historical match sequences (last N matches) to predict
    win/draw/loss probabilities. Captures temporal patterns and form.

    Best for:
    - Form-based predictions
    - Streak detection
    - Momentum analysis
    - Time-series patterns
    """

    def __init__(
        self,
        sequence_length: int = 10,
        n_features: int = 70,
        lstm_units: int = 64,
        dropout: float = 0.2,
        learning_rate: float = 0.001
    ):
        """
        Initialize LSTM model.

        Args:
            sequence_length: Number of previous matches to use
            n_features: Number of features per match
            lstm_units: Number of LSTM units in each layer
            dropout: Dropout rate for regularization
            learning_rate: Learning rate for optimizer
        """
        if not TF_AVAILABLE:
            raise ImportError(
                "TensorFlow is required for LSTM model. "
                "Install with: pip install tensorflow"
            )

        self.sequence_length = sequence_length
        self.n_features = n_features
        self.lstm_units = lstm_units
        self.dropout = dropout
        self.learning_rate = learning_rate

        self.model = None
        self.is_fitted = False

        self._build_model()

    def _build_model(self):
        """Build LSTM architecture."""
        model = keras.Sequential([
            # Input layer
            layers.Input(shape=(self.sequence_length, self.n_features)),

            # First LSTM layer (returns sequences)
            layers.LSTM(
                self.lstm_units,
                return_sequences=True,
                name='lstm_1'
            ),
            layers.Dropout(self.dropout),

            # Second LSTM layer (returns final state)
            layers.LSTM(
                self.lstm_units // 2,
                return_sequences=False,
                name='lstm_2'
            ),
            layers.Dropout(self.dropout),

            # Dense layers
            layers.Dense(32, activation='relu', name='dense_1'),
            layers.Dropout(self.dropout / 2),

            # Output layer (3 classes: Home/Draw/Away)
            layers.Dense(3, activation='softmax', name='output')
        ])

        # Compile model
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=self.learning_rate),
            loss='categorical_crossentropy',
            metrics=['accuracy', 'categorical_crossentropy']
        )

        self.model = model

    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        validation_split: float = 0.2,
        epochs: int = 50,
        batch_size: int = 32,
        verbose: int = 1
    ) -> 'LSTMOutcomeModel':
        """
        Train LSTM model on sequences.

        Args:
            X: Sequences of shape (n_samples, sequence_length, n_features)
            y: One-hot encoded labels of shape (n_samples, 3)
            validation_split: Fraction of data for validation
            epochs: Number of training epochs
            batch_size: Batch size for training
            verbose: Verbosity mode

        Returns:
            Self for method chaining
        """
        # Add early stopping
        early_stop = keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )

        # Add learning rate reduction
        lr_scheduler = keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-7
        )

        # Train model
        history = self.model.fit(
            X, y,
            validation_split=validation_split,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[early_stop, lr_scheduler],
            verbose=verbose
        )

        self.is_fitted = True
        self.training_history = history.history

        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict outcome probabilities.

        Args:
            X: Sequences of shape (n_samples, sequence_length, n_features)

        Returns:
            Probabilities of shape (n_samples, 3) for [Home, Draw, Away]
        """
        if not self.is_fitted:
            raise ValueError("Model must be trained first")

        return self.model.predict(X, verbose=0)

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class labels.

        Args:
            X: Sequences

        Returns:
            Class labels (0=Home, 1=Draw, 2=Away)
        """
        proba = self.predict_proba(X)
        return np.argmax(proba, axis=1)

    def predict_single_match(
        self,
        sequence: np.ndarray
    ) -> dict:
        """
        Predict outcome for a single match sequence.

        Args:
            sequence: Single sequence of shape (sequence_length, n_features)

        Returns:
            Dictionary with probabilities
        """
        if sequence.shape != (self.sequence_length, self.n_features):
            raise ValueError(
                f"Expected shape {(self.sequence_length, self.n_features)}, "
                f"got {sequence.shape}"
            )

        # Add batch dimension
        X = sequence.reshape(1, self.sequence_length, self.n_features)

        # Get probabilities
        proba = self.predict_proba(X)[0]

        return {
            "probabilities": {
                "home_win": round(float(proba[0]), 4),
                "draw": round(float(proba[1]), 4),
                "away_win": round(float(proba[2]), 4)
            },
            "home_win_prob": round(float(proba[0]), 4),
            "draw_prob": round(float(proba[1]), 4),
            "away_win_prob": round(float(proba[2]), 4),
            "prediction": int(np.argmax(proba)),
            "confidence": round(float(np.max(proba)), 4),
            "model_details": {
                "model": "lstm",
                "sequence_length": self.sequence_length,
                "lstm_units": self.lstm_units
            }
        }

    def save(self, filepath: str):
        """Save model to file."""
        if not self.is_fitted:
            raise ValueError("Cannot save unfitted model")
        self.model.save(filepath)

    @classmethod
    def load(cls, filepath: str, **kwargs) -> 'LSTMOutcomeModel':
        """Load model from file."""
        if not TF_AVAILABLE:
            raise ImportError("TensorFlow required to load LSTM model")

        instance = cls(**kwargs)
        instance.model = keras.models.load_model(filepath)
        instance.is_fitted = True
        return instance

    def get_training_metrics(self) -> dict:
        """Get training history metrics."""
        if not self.is_fitted:
            raise ValueError("Model not trained yet")

        return {
            "final_loss": float(self.training_history['loss'][-1]),
            "final_val_loss": float(self.training_history.get('val_loss', [0])[-1]),
            "final_accuracy": float(self.training_history['accuracy'][-1]),
            "final_val_accuracy": float(self.training_history.get('val_accuracy', [0])[-1]),
            "epochs_trained": len(self.training_history['loss'])
        }


# Global instance
lstm_outcome_model = LSTMOutcomeModel() if TF_AVAILABLE else None
