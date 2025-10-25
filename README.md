# Blockchain-Based Product Authenticity Verification System

A complete blockchain implementation for fighting counterfeit products by assigning each product a unique blockchain ID and QR code for verification.

## 🎯 Features

- **Custom Blockchain Implementation**: Built-from-scratch blockchain with proof-of-work
- **Product Registration**: Register products with unique blockchain IDs
- **QR Code Generation**: Automatic QR code creation for each product
- **Verification System**: Scan or enter product ID to verify authenticity
- **Web Interface**: Clean, modern UI for all operations
- **Blockchain Validation**: Ensures blockchain integrity

## 🏗️ Project Structure

```
product-authenticity-blockchain/
│
├── blockchain/
│   ├── __init__.py
│   └── blockchain.py          # Core blockchain logic
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── qr_codes/              # Generated QR codes stored here
│
├── templates/
│   ├── index.html             # Home page
│   ├── register.html          # Product registration
│   ├── verify.html            # Verification input
│   └── product_details.html   # Verification results
│
├── app.py                     # Flask application
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🔧 How It Works

1. **Product Registration**: 
   - Manufacturer enters product details (name, batch, date)
   - System generates unique SHA-256 hash (Product ID)
   - New block is mined and added to blockchain
   - QR code is generated containing verification URL

2. **Verification**:
   - Customer scans QR code or enters Product ID
   - System searches blockchain for matching product
   - Returns product details if authentic, or rejection if fake

3. **Blockchain Security**:
   - Each block contains proof-of-work (mining)
   - Blocks are cryptographically linked
   - Tampering is easily detected via validation

## 🚀 Technologies Used

- **Python 3.8+**
- **Flask**: Web framework
- **hashlib**: Cryptographic hashing
- **qrcode**: QR code generation
- **Pillow**: Image processing

## 📊 API Endpoints

- `GET /` - Home page with all products
- `GET/POST /register` - Register new product
- `GET /verify` - Verification page
- `GET /verify?id=PRODUCT_ID` - Verify specific product
- `GET /api/verify/<product_id>` - JSON API for verification
- `GET /api/blockchain` - View entire blockchain
- `GET /download_qr/<product_id>` - Download QR code

## 🔐 Security Features

- SHA-256 cryptographic hashing
- Proof-of-work mining (difficulty: 4 leading zeros)
- Immutable blockchain structure
- Timestamp validation
- Chain integrity verification

## 📝 License

This project is open source and available for educational purposes.

## 👨‍💻 Author

Built as a demonstration of blockchain technology for product authenticity verification.