import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader


class Trainer:
    criterion: nn.Module
    model: nn.Module
    number_of_epochs: int

    def __init__(
        self,
        data: list[np.ndarray],
        criterion: nn.Module,
        model: nn.Module,
        number_of_epochs: int
    ) -> None:
        self.data = data
        self.criterion = criterion
        self.model = model
        self.number_of_epochs = number_of_epochs
        self.split_data()
        self.create_training_entries(sequence_length=50)
        self.create_validation_entries(sequence_length=50)
    
    def split_data(
        self,
        train_ratio: float = 0.7,
        val_ratio: float = 0.15
    ) -> None:
        total_size = len(self.data)
        train_end = int(total_size * train_ratio)
        val_end = train_end + int(total_size * val_ratio)

        self.train_data = self.data[:train_end]
        self.val_data = self.data[train_end:val_end]
        self.test_data = self.data[val_end:]

        self.train_mean = np.mean(self.train_data, axis=0)  # Shape: (90,)
        self.train_std = np.std(self.train_data, axis=0)    # Shape: (90,)
        
        self.train_data_normalized = (self.train_data - self.train_mean) / (self.train_std + 1e-8)
        self.val_data_normalized = (self.val_data - self.train_mean) / (self.train_std + 1e-8)
        self.test_data_normalized = (self.test_data - self.train_mean) / (self.train_std + 1e-8)
        
    def create_training_entries(
        self,
        sequence_length: int
    ) -> None:
        train_data = self.train_data_normalized

        self.training_entries: list[dict[str, np.ndarray]] = []

        for i in range(len(train_data) - (sequence_length + 1)):
            training_sequence = train_data[i:i + sequence_length]
            target = train_data[i + sequence_length]

            entry: dict[str, np.ndarray] = {'input': np.array(training_sequence), 'target': target}
            self.training_entries.append(entry)
    
    def create_validation_entries(
            self,
            sequence_length: int
        ) -> None:
        val_data = self.val_data_normalized

        self.validation_entries: list[dict[str, np.ndarray]] = []

        for i in range(len(val_data) - (sequence_length + 1)):
            val_sequence = val_data[i:i + sequence_length]
            target = val_data[i + sequence_length]

            entry: dict[str, np.ndarray] = {'input': np.array(val_sequence), 'target': target}
            self.validation_entries.append(entry)
    
    def train(
        self,
    ) -> None:
        train_inputs = np.array([entry['input'] for entry in self.training_entries])
        train_targets = np.array([entry['target'] for entry in self.training_entries])
        X_train = torch.FloatTensor(train_inputs)
        y_train = torch.FloatTensor(train_targets)

        val_inputs = np.array([entry['input'] for entry in self.validation_entries])
        val_targets = np.array([entry['target'] for entry in self.validation_entries])
        X_val = torch.FloatTensor(val_inputs)
        y_val = torch.FloatTensor(val_targets)

        # Create dataset and dataloader
        dataset = TensorDataset(X_train, y_train)
        train_loader = DataLoader(dataset, batch_size=32, shuffle=True)

        # Initialize model, loss, optimizer

        optimizer = torch.optim.Adam(self.model.parameters(), lr=0.0001)

        # Training loop

        for epoch in range(self.number_of_epochs):
            _: nn.Module = self.model.train()
            total_loss = 0
            
            for batch_inputs, batch_targets in train_loader:
                # Forward pass
                predictions = self.model(batch_inputs)
                loss = self.criterion(predictions, batch_targets)
                
                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            
            avg_loss = total_loss / len(train_loader)

            # Validation
            _: nn.Module = self.model.eval()
            with torch.no_grad():
                val_preds = self.model(X_val)
                val_loss = self.criterion(val_preds, y_val)
        
            # Print both losses
            print(f'Epoch {epoch+1}/{self.number_of_epochs}, Train Loss: {avg_loss:.6f}, Val Loss: {val_loss.item():.6f}')
    
    def predict(
        self,
        input_sequence: list[np.ndarray],
    ) -> np.ndarray:
        """
        Make a prediction and return it in original scale
        
        Args:
            input_sequence: shape (50, 90) - normalized input
        
        Returns:
            prediction in original scale
        """
        self.model.eval()
        with torch.no_grad():
            # Add batch dimension
            input_tensor = torch.FloatTensor(input_sequence).unsqueeze(0)  # (1, 50, 90)
            
            # Get normalized prediction
            normalized_pred = self.model(input_tensor).numpy()  # (1, 90)
            
            # Denormalize
            actual_prediction = (normalized_pred * self.train_std) + self.train_mean
            
            return actual_prediction.squeeze()  # (90,)

    # def evaluate_test_set(self):
    #     """
    #     Evaluate on test set and show actual vs predicted values
    #     """
    #     test_entries = []
    #     for i in range(len(self.test_data) - 51):
    #         test_sequence = self.test_data[i:i + 50]
    #         test_target = self.test_data[i + 50]
    #         test_entries.append({'input': np.array(test_sequence), 'target': test_target})
        
    #     X_test = torch.FloatTensor([e['input'] for e in test_entries])
    #     y_test_normalized = torch.FloatTensor([e['target'] for e in test_entries])
        
    #     self.model.eval()
    #     with torch.no_grad():
    #         predictions_normalized = self.model(X_test).numpy()
        
    #     # Denormalize both predictions and targets
    #     predictions_actual = (predictions_normalized * self.train_std) + self.train_mean
    #     targets_actual = (y_test_normalized.numpy() * self.train_std) + self.train_mean
        
    #     # Compute MSE in original scale
    #     mse_original = np.mean((predictions_actual - targets_actual) ** 2)
    #     print(f"Test MSE (original scale): {mse_original:.2f}")
        
    #     # Show a few examples
    #     for i in range(min(5, len(predictions_actual))):
    #         print(f"\nExample {i+1}:")
    #         print(f"Predicted (first 5 dims): {predictions_actual[i][:5]}")
    #         print(f"Actual (first 5 dims): {targets_actual[i][:5]}")
        
    #     return predictions_actual, targets_actual

    def evaluate_model_on_test(self) -> float:
        test_data = self.test_data_normalized
    
        test_inputs = np.array([entry['input'] for entry in test_data])
        test_targets = np.array([entry['target'] for entry in test_data])
        X_test = torch.FloatTensor(test_inputs)
        y_test = torch.FloatTensor(test_targets)

        _: nn.Module = self.model.eval()
        with torch.no_grad():
            test_preds: torch.Tensor = self.model(X_test)
            test_loss: float = self.criterion(test_preds, y_test)    

        return test_loss    
