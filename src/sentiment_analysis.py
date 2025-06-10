import os
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification


class CommentDataset(Dataset):
    def __init__(self, texts):
        self.texts = texts

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        return self.texts[idx]


def collate_batch(batch_texts, tokenizer):
    """
    Mã hóa và chuẩn hóa batch văn bản để đưa vào mô hình.

    Áp dụng padding, truncation và chuyển sang tensor PyTorch.
    """
    return tokenizer(batch_texts, return_tensors="pt", truncation=True, padding=True)


def load_model(model_path="models/bert_sentiment_vietnamese"):
    """
    Tải mô hình và tokenizer từ HuggingFace, chuyển sang GPU nếu có.

    Trả về tokenizer, mô hình ở chế độ eval, và thiết bị sử dụng.
    """
    if not os.path.exists(model_path):
        model_name = "hieudinhpro/BERT_Sentiment_Vietnamese"

        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)

        os.makedirs(model_path, exist_ok=True)
        tokenizer.save_pretrained(model_path)
        model.save_pretrained(model_path)
    else:
        # Load từ local
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForSequenceClassification.from_pretrained(model_path)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    return tokenizer, model, device


def analyze_sentiment(input_path, output_path, model, tokenizer, device, labels):
    """
    Phân tích cảm xúc của bình luận trong file CSV.
    Đọc dữ liệu, mã hóa văn bản, dự đoán nhãn cảm xúc và lưu kết quả.
    """
    df = pd.read_csv(input_path)
    texts = df['comment_text_remove_emojis'].fillna("").tolist()

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

    df['sentiment'] = [labels[p] for p in all_preds]
    df.to_csv(output_path, index=False)

    return df


def run_sentiment_analysis(
    input_path="data/processed/facebook_comments_processed.csv",
    output_path="data/processed/facebook_comments_processed_with_sentiment.csv",
    model_path="models/bert_sentiment_vietnamese"
):
    """Chạy phân tích cảm xúc trên bình luận Facebook"""
    print("\nRunning sentiment analysis...")
    labels = ['negative', 'neutral', 'positive']
    tokenizer, model, device = load_model(model_path)
    return analyze_sentiment(input_path, output_path, model, tokenizer, device, labels)


if __name__ == "__main__":
    df = run_sentiment_analysis()
    print("Sentiment analysis completed successfully.")
    print(df.head())
