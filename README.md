# Phân Tích Cảm Xúc Bài Viết Facebook (Tiếng Việt)

Đây là một ứng dụng giúp thu thập bài viết từ Facebook, phân tích cảm xúc tiếng Việt bằng mô hình `hieudinhpro/BERT_Sentiment_Vietnamese` và trực quan hóa kết quả bằng biểu đồ và WordCloud. Ứng dụng được xây dựng bằng Python và Streamlit, có thể chạy trực tiếp bằng Python hoặc trong Docker.

## Cấu trúc thư mục

```
.
├── assets/
│   └── demo.gif               # File GIF minh họa ứng dụng
├── data/                      # Dữ liệu thu thập và xử lý (xuất hiện khi chạy ứng dụng)
├── models/                    # Lưu mô hình phân tích (xuất hiện khi chạy ứng dụng)
├── notebooks/                 # Các notebook thử nghiệm
├── src/                       # Mã nguồn xử lý
│   ├── data_processing.py         # Làm sạch và xử lý văn bản
│   ├── facebook_crawling.py       # Thu thập bài viết từ Facebook
│   ├── sentiment_analysis.py      # Dự đoán cảm xúc
│   ├── sentiment_charts.py        # Vẽ biểu đồ trực quan
│   └── main.py                    # Tùy chọn: chạy xử lý độc lập
├── app.py                    # Ứng dụng Streamlit chính
├── requirements.txt          # Thư viện cần thiết
├── Dockerfile                # Thiết lập Docker
├── docker-compose.yml        # Cấu hình Docker Compose
├── .dockerignore             # Bỏ qua file không cần trong Docker
├── .gitignore                # Bỏ qua file không cần trong Git
├── vietnamese_stopwords.txt  # Danh sách từ dừng tiếng Việt
└── README.md                 # Tài liệu hướng dẫn sử dụng
```

## Cách sử dụng

### Cách 1: Chạy trực tiếp bằng Python

**Bước 1**: Cài đặt thư viện
```bash
pip install -r requirements.txt
```

**Bước 2**: Chạy ứng dụng
```bash
streamlit run app.py
```

### Cách 2: Sử dụng Docker Compose (Khuyến nghị)

**Bước 1**: Pull image từ Docker Hub
```bash
docker pull thanhnghds/fb-sentiment-app:latest
```

**Bước 2**: Chạy ứng dụng
```bash
docker-compose up -d
```

**Bước 3**: Dừng ứng dụng (nếu cần)
```bash
docker-compose down
```

### Cách 3: Chạy trực tiếp từ Docker Hub
```bash
docker run -p 8501:8501 thanhnghds/fb-sentiment-app:latest
```

### Sau khi thực hiện thành công 1 trong 3 cách trên, truy cập địa chỉ: http://localhost:8501

## Tính năng chính

- Nhập link bài viết Facebook qua textarea hoặc file .txt / .csv
- Tự động thu thập nội dung bài viết bằng Playwright
- Phân tích cảm xúc: tích cực, tiêu cực, trung tính
- Trực quan hóa kết quả:
  - Biểu đồ tổng hợp tương tác: like, comment, share theo bài đăng
  - Biểu đồ phân bố cảm xúc
  - WordCloud theo từng cảm xúc

## Yêu cầu hệ thống

- Python 3.11
- Google Chrome (dành cho Playwright)
- Docker (nếu sử dụng container)

## Demo

Ứng dụng phân tích cảm xúc bình luận Facebook với dữ liệu mẫu từ chiến dịch quảng cáo laptop của TGDĐ (đầu 6/2025). Dữ liệu được lấy ngày 14/6/2025. Kết quả cho thấy xu hướng cảm xúc khách hàng cho chiến dịch này là khá tiêu cực.
![Minh họa ứng dụng phân tích cảm xúc](assets/demo.gif)

## Đóng góp và phản hồi

Bạn có thể:
- Tạo issue
- Gửi pull request
- Liên hệ qua email: thanhngh.ds@gmail.com
