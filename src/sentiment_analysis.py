import os
from typing import List, Tuple

import pandas as pd
import torch
from torch.utils.data import DataLoader, Dataset
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    BatchEncoding,
    PreTrainedTokenizerBase,
)


class CommentDataset(Dataset):
    """Custom Dataset for loading a list of text comments."""

    def __init__(self, texts: list[str]):
        self.texts = texts

    def __len__(self) -> int:
        """Return number of samples in the dataset."""

        return len(self.texts)

    def __getitem__(self, idx: int) -> str:
        """Return the text sample at the given index."""

        return self.texts[idx]


def collate_batch(
    batch_texts: List[str], tokenizer: PreTrainedTokenizerBase
) -> BatchEncoding:
    """Tokenize and pad a batch of texts for model input."""

    return tokenizer(batch_texts, return_tensors="pt", truncation=True, padding=True)


def load_model(
    model_path: str = "models/bert_sentiment_vietnamese",
) -> Tuple[PreTrainedTokenizerBase, AutoModelForSequenceClassification, torch.device]:
    """Load tokenizer and model from local or Hugging Face, and move to device."""

    if not os.path.exists(model_path):
        model_name = "hieudinhpro/BERT_Sentiment_Vietnamese"

        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)

        os.makedirs(model_path, exist_ok=True)
        tokenizer.save_pretrained(model_path)
        model.save_pretrained(model_path)
    else:
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForSequenceClassification.from_pretrained(model_path)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    return tokenizer, model, device


def analyze_sentiment(
    df_comments_processed: pd.DataFrame,
    model: AutoModelForSequenceClassification,
    tokenizer: PreTrainedTokenizerBase,
    device: torch.device,
    labels: List[str],
) -> pd.DataFrame:
    """Predict sentiment labels for all comments in the DataFrame."""

    texts = df_comments_processed["comment"].fillna("").tolist()

    dataset = CommentDataset(texts)
    dataloader = DataLoader(
        dataset, batch_size=16, collate_fn=lambda x: collate_batch(x, tokenizer)
    )

    all_preds = []
    with torch.no_grad():
        for batch in dataloader:
            batch = {k: v.to(device) for k, v in batch.items()}
            outputs = model(**batch)
            probs = torch.softmax(outputs.logits, dim=-1)
            preds = torch.argmax(probs, dim=-1)
            all_preds.extend(preds.cpu().tolist())

    df_comments_processed["sentiment"] = [labels[p] for p in all_preds]

    return df_comments_processed


def run_sentiment_analysis(
    df_comments_processed: pd.DataFrame,
    model_path: str = "models/bert_sentiment_vietnamese",
) -> pd.DataFrame:
    """Run sentiment analysis pipeline and return the labeled DataFrame."""

    print("\nRunning sentiment analysis...")
    labels = ["negative", "neutral", "positive"]
    tokenizer, model, device = load_model(model_path)
    return analyze_sentiment(df_comments_processed, model, tokenizer, device, labels)


if __name__ == "__main__":
    df_comments_processed = pd.read_csv(
        "data/processed/facebook_comments_processed.csv"
    )

    df_comments_processed_with_sentiment = run_sentiment_analysis(df_comments_processed)
    print("Sentiment analysis completed successfully.")
    print(df_comments_processed_with_sentiment.head())
