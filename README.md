# Phân Tích Cảm Xúc Bài Viết Facebook (Tiếng Việt)

Đây là một ứng dụng giúp thu thập bài viết từ Facebook, phân tích cảm xúc tiếng Việt và trực quan hóa kết quả bằng biểu đồ và WordCloud. Ứng dụng được xây dựng bằng Python và Streamlit, có thể chạy trực tiếp bằng Python hoặc trong Docker.

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

### Cách 2: Sử dụng Docker Hub (Khuyến nghị)

**Chạy trực tiếp từ Docker Hub**:
```bash
docker run -p 8501:8501 hako1106/fb-sentiment-app:1.0.0
```

### Cách 3: Sử dụng Docker

**Bước 1**: Build image
```bash
docker build -t fb-sentiment-app .
```

**Bước 2**: Chạy container
```bash
docker run -p 8501:8501 fb-sentiment-app
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

![Minh họa ứng dụng phân tích cảm xúc](assets/demo.gif)

## Đóng góp và phản hồi

Bạn có thể:
- Tạo issue
- Gửi pull request
- Liên hệ qua email: thanhako1106@gmail.com
